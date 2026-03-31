import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QRadioButton, QStackedWidget, QMessageBox, 
    QLineEdit, QComboBox, QScrollArea, QFrame, QButtonGroup, 
    QGridLayout, QFormLayout, QSpacerItem, QSizePolicy, QListWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# ==========================================
# 1. APPLICATION STYLESHEET (QSS - HUD STYLE)
# ==========================================
STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a1128, stop:0.5 #1c2541, stop:1 #2a415a);
}
QWidget {
    font-family: "Segoe UI", "Roboto", sans-serif;
}
QLabel#Title {
    color: #00E5FF;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
}
QLabel#Subtitle {
    color: #FFD700;
    font-size: 20px;
    font-weight: bold;
}
QLabel#QuestionText {
    background-color: rgba(10, 25, 47, 0.8);
    color: #FFD700;
    font-size: 22px;
    font-weight: bold;
    border: 2px solid #00E5FF;
    border-radius: 15px;
    padding: 20px;
}
QPushButton {
    background-color: #0077b6;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0096c7;
    border: 1px solid #00E5FF;
}
QPushButton#ActionButton {
    background-color: #ff9f1c;
    color: white;
}
QPushButton#ActionButton:hover {
    background-color: #ffbf69;
}
QPushButton#HUDButton {
    background-color: rgba(10, 25, 47, 0.8);
    border: 2px solid #00E5FF;
    border-radius: 20px;
    color: white;
    font-size: 16px;
    padding: 20px;
    text-align: left;
}
QPushButton#HUDButton:hover {
    background-color: rgba(0, 229, 255, 0.2);
    border: 2px solid #FFD700;
    color: #FFD700;
}
QPushButton#HUDButton:checked {
    background-color: rgba(0, 229, 255, 0.5);
    border: 2px solid #FFD700;
    color: #FFD700;
    font-weight: bold;
}
QRadioButton {
    color: white;
    font-size: 16px;
}
QRadioButton::indicator {
    width: 20px;
    height: 20px;
}
QLineEdit, QComboBox {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid #00E5FF;
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
}
QComboBox QAbstractItemView {
    background-color: #1c2541;
    color: white;
    selection-background-color: #00E5FF;
}
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
"""

# ==========================================
# 2. STATE MANAGER (MOCK DATABASE)
# ==========================================
DB_FILE = "bank.json"

class AppState:
    def __init__(self):
        self.banks = {
            "ALL": [],
            "WARMUP": {"Mặc định": []},
            "LAW": {"Mặc định": []},
            "THEORY": {"Mặc định": []},
            "FEEDBACK": {"Mặc định": []}
        }
        self.selected_exams = {
            "WARMUP": "Mặc định",
            "LAW": "Mặc định",
            "THEORY": "Mặc định",
            "FEEDBACK": "Mặc định"
        }
        self.load_db()
        
    def load_db(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "banks" in data and isinstance(data["banks"], dict):
                        self.banks["ALL"] = data["banks"].get("ALL", [])
                        for cat in ["WARMUP", "LAW", "THEORY", "FEEDBACK"]:
                            self.banks[cat] = {"Mặc định": data["banks"].get(cat, [])}
                        if "exams" in data and isinstance(data["exams"], list):
                            for exam in data["exams"]:
                                exam_name = exam.get("name", "Mặc định")
                                for cat in ["WARMUP", "LAW", "THEORY", "FEEDBACK"]:
                                    if cat in exam:
                                        self.banks[cat][exam_name] = exam[cat]
                    else:
                        for k in ["WARMUP", "LAW", "THEORY", "FEEDBACK"]:
                            if k in data:
                                if isinstance(data[k], list):
                                    self.banks[k] = {"Mặc định": data[k]}
                                else:
                                    self.banks[k] = data[k]
                        if "ALL" in data:
                            self.banks["ALL"] = data["ALL"]
            except Exception:
                pass
        
        for k in ["WARMUP", "LAW", "THEORY", "FEEDBACK"]:
            if k not in self.banks:
                self.banks[k] = {"Mặc định": []}
        if "ALL" not in self.banks:
            self.banks["ALL"] = []
            
    def get_exam(self, category):
        exam_name = self.selected_exams.get(category, "Mặc định")
        return self.banks.get(category, {}).get(exam_name, [])
        
    def get_exam_names(self, category):
        return list(self.banks.get(category, {}).keys())
                
    def save_db(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.banks, f, ensure_ascii=False, indent=4)
            
    def is_empty(self):
        return len(self.banks.get("ALL", [])) == 0 and len(self.banks.get("LAW", {}).get("Mặc định", [])) == 0

    def populate_mock(self):
        # Màn hình 4: Khởi động (Mã độc)
        self.banks["WARMUP"]["Mặc định"] = [
            {"q": "Mã độc (Malware) là gì?", "opts": ["Phần mềm độc hại phá hoại hệ thống", "Phần mềm tăng tốc máy tính", "Trình duyệt web", "Phần mềm diệt virus"], "ans": 0, "user_ans": -1},
            {"q": "Ransomware hoạt động như thế nào?", "opts": ["Xóa file rác", "Mã hóa dữ liệu và tống tiền", "Chạy quảng cáo", "Tự động tải game"], "ans": 1, "user_ans": -1},
            {"q": "Loại mã độc nào tự nhân bản lan truyền qua mạng?", "opts": ["Trojan", "Spyware", "Worm (Sâu máy tính)", "Adware"], "ans": 2, "user_ans": -1},
            {"q": "Trojan xâm nhập máy tính bằng cách nào?", "opts": ["Ngụy trang thành phần mềm hợp pháp", "Lây qua dây cắm điện", "Tự sinh ra từ ổ cứng", "Qua sóng radio"], "ans": 0, "user_ans": -1},
            {"q": "Cách phòng chống mã độc hiệu quả nhất?", "opts": ["Rút dây mạng", "Không dùng máy tính", "Dùng phần mềm Anti-virus và cập nhật OS", "Xóa hệ điều hành"], "ans": 2, "user_ans": -1}
        ]
        # Màn hình 5: Bài thi Luật
        self.banks["LAW"]["Mặc định"] = [
            {"q": "Luật An ninh mạng của Việt Nam có hiệu lực từ năm nào?", "opts": ["2018", "2019", "2020", "2021"], "ans": 1, "user_ans": -1},
            {"q": "Hành vi nào bị nghiêm cấm trên không gian mạng?", "opts": ["Phát tán chương trình tin học gây hại", "Đọc báo trực tuyến", "Gửi email cho bạn bè", "Học trực tuyến"], "ans": 0, "user_ans": -1}
        ]
        # Màn hình 7: Bài thi Lý thuyết
        self.banks["THEORY"]["Mặc định"] = [
            {"q": "Giao thức nào dùng để duyệt web bảo mật?", "opts": ["HTTP", "FTP", "HTTPS", "SMTP"], "ans": 2, "user_ans": -1},
            {"q": "Mật khẩu nào sau đây được coi là mạnh nhất?", "opts": ["123456", "password", "Abc@123456!", "admin123"], "ans": 2, "user_ans": -1}
        ]
        # Màn hình 9: Đánh giá hệ thống
        self.banks["FEEDBACK"]["Mặc định"] = [
            {"q": "Bạn thấy giao diện mô phỏng HUD này thế nào?", "opts": ["Rất hiện đại (A+)", "Khá đẹp", "Bình thường", "Cần cải thiện"], "ans": 0, "user_ans": -1},
            {"q": "Hệ thống có dễ thao tác không?", "opts": ["Rất dễ", "Khá dễ", "Bình thường", "Khó"], "ans": 0, "user_ans": -1}
        ]
        
        self.banks["ALL"] = (
            self.banks["WARMUP"]["Mặc định"] + 
            self.banks["LAW"]["Mặc định"] + 
            self.banks["THEORY"]["Mặc định"] + 
            self.banks["FEEDBACK"]["Mặc định"]
        )
        
        self.save_db()

state = AppState()

# ==========================================
# 3. BASE & COMMON SCREENS
# ==========================================
class BaseScreen(QWidget):
    """Lớp cơ sở cho các màn hình, cung cấp tính năng dịch chung."""
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        
    def translate_ui(self):
        QMessageBox.information(
            self, "Dịch thuật / Translation", 
            "Mô phỏng: Nội dung trên màn hình này đã được chuyển sang Tiếng Anh\n\n(Mockup: Content has been translated to English)"
        )


# ==========================================
# CUSTOM AGREEMENT OPTION WIDGET
# ==========================================
class AgreementOptionWidget(QFrame):
    toggled = pyqtSignal(bool)
    
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.is_selected = False
        
        self.setObjectName("AgreementOption")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(60)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        self.checkbox = QLabel()
        self.checkbox.setFixedSize(24, 24)
        self.checkbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.checkbox)
        layout.addSpacing(12)
        
        self.lbl_text = QLabel(text)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.lbl_text, 1)
        
        self.hover_state = False
        self.update_style()
        
    def setText(self, text):
        self.lbl_text.setText(text)
        
    def setChecked(self, checked):
        if self.is_selected != checked:
            self.is_selected = checked
            self.update_style()
            self.toggled.emit(self.is_selected)
            
    def isChecked(self):
        return self.is_selected
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_selected:
                self.setChecked(True)
            
    def enterEvent(self, event):
        self.hover_state = True
        self.update_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_state = False
        self.update_style()
        super().leaveEvent(event)
        
    def update_style(self):
        primary_cyan = "#00E5FF"
        bg_dark = "transparent"
        
        if self.is_selected:
            bg_color = "rgba(0, 229, 255, 0.3)"
            border_color = primary_cyan
            checkbox_bg = primary_cyan
            checkbox_border = primary_cyan
            self.checkbox.setText("✔")
            self.checkbox.setStyleSheet(f"color: white; font-weight: bold; font-size: 16px; background-color: {checkbox_bg}; border: 2px solid {checkbox_border}; border-radius: 4px;")
        else:
            if self.hover_state:
                bg_color = "rgba(0, 229, 255, 0.1)"
                border_color = "rgba(255, 255, 255, 0.3)"
            else:
                bg_color = bg_dark
                border_color = "rgba(255, 255, 255, 0.3)"
            
            checkbox_bg = "transparent"
            checkbox_border = primary_cyan
            self.checkbox.setText("")
            self.checkbox.setStyleSheet(f"background-color: {checkbox_bg}; border: 2px solid {checkbox_border}; border-radius: 4px;")
            
        self.setStyleSheet(f"""
            QFrame#AgreementOption {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 15px;
            }}
            QLabel {{
                color: white;
                font-weight: normal; 
                font-size: 18px;
                border: none;
                background: transparent;
            }}
        """)


# Màn hình 1: Giới thiệu & Quy định
class ScreenIntro(BaseScreen):
    def __init__(self, main_app):
        super().__init__(main_app)
        main_layout = QVBoxLayout(self)
        
        # Wrapper chính giữa
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("GIỚI THIỆU VỀ QUY ĐỊNH CỦA HỆ THỐNG")
        lbl_title.setObjectName("Title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(lbl_title)
        
        center_layout.addSpacing(30)
        
        lbl_desc = QLabel(
            "Hệ thống kiểm tra, đánh giá năng lực là nền tảng phần mềm được xây dựng\n"
            "nhằm tổ chức các bài kiểm tra, thu thập kết quả và phân tích mức độ đáp ứng\n"
            "yêu cầu về kiến thức, kỹ năng của người tham gia.\n\n"
            "Hệ thống hỗ trợ quản lý ngân hàng câu hỏi, tổ chức thi trực tuyến, chấm điểm\n"
            "tự động và tổng hợp kết quả một cách nhanh chóng, chính xác...."
        )
        lbl_desc.setStyleSheet("color: white; font-size: 18px; line-height: 1.5;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        center_layout.addWidget(lbl_desc)
        
        center_layout.addSpacing(20)
        
        btn_trans = QPushButton("Phiên dịch sang Tiếng Anh")
        btn_trans.setFixedWidth(250)
        btn_trans.setStyleSheet("background-color: #81b214; color: white; font-weight: bold; font-size: 16px; border-radius: 5px; padding: 10px;")
        btn_trans.clicked.connect(self.translate_ui)
        center_layout.addWidget(btn_trans, alignment=Qt.AlignmentFlag.AlignLeft)
        
        center_layout.addSpacing(30)
        
        self.radio_accept = AgreementOptionWidget("Chấp nhận và đồng ý với những điều lệ của hệ thống......")
        self.radio_reject = AgreementOptionWidget("Từ chối và không đồng ý với những điều lệ của hệ thống....")
        
        self.radio_accept.toggled.connect(self.check_radio_accept)
        self.radio_reject.toggled.connect(self.check_radio_reject)
        
        v_radio_layout = QVBoxLayout()
        v_radio_layout.setSpacing(15)
        v_radio_layout.addWidget(self.radio_accept)
        v_radio_layout.addWidget(self.radio_reject)
        center_layout.addLayout(v_radio_layout)
        
        # Đưa khối giữa vào 1 hbox để giới hạn 2 bên (giúp khối nội dung luôn nằm ở tâm)
        h_wrapper = QHBoxLayout()
        h_wrapper.addStretch()
        h_wrapper.addWidget(center_widget)
        h_wrapper.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(h_wrapper)
        main_layout.addStretch()
        
        # Action layout - Nằm góc dưới, full chiều ngang
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(50, 0, 50, 50)
        
        self.btn_exit = QPushButton("Quay lại Menu")
        self.btn_exit.setObjectName("ActionButton")
        self.btn_exit.setFixedSize(160, 50)
        self.btn_exit.clicked.connect(lambda: self.main_app.switch_screen(1))
        
        self.btn_next = QPushButton("Tiếp theo")
        self.btn_next.setObjectName("ActionButton")
        self.btn_next.setStyleSheet("QPushButton:disabled { background-color: #555555; color: #aaaaaa; }")
        self.btn_next.setFixedSize(150, 50)
        self.btn_next.clicked.connect(self.start_test)
        self.btn_next.setDisabled(True)
        
        btn_layout.addWidget(self.btn_exit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_next)
        
        main_layout.addLayout(btn_layout)
        
    def check_radio_accept(self, checked):
        if checked:
            self.radio_reject.setChecked(False)
            self.btn_next.setEnabled(True)

    def check_radio_reject(self, checked):
        if checked:
            self.radio_accept.setChecked(False)
            self.btn_next.setEnabled(False)
            QMessageBox.information(self, "Thông báo", "BÀI THI ĐÃ KẾT THÚC")

    def reset_radios(self):
        self.radio_accept.setChecked(False)
        self.radio_reject.setChecked(False)
        self.btn_next.setEnabled(False)

    def start_test(self):
        if state.is_empty():
            state.populate_mock()
            QMessageBox.information(self, "Tạo dữ liệu", "Hệ thống đã tự động tạo Mockup dữ liệu vì ngân hàng câu hỏi trống.")
        
        self.main_app.switch_screen(11) # Chuyển sang ScreenChooseExam



# Màn hình 2: Lựa chọn tính năng
class ScreenMenu(BaseScreen):
    def __init__(self, main_app):
        super().__init__(main_app)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("LỰA CHỌN TÍNH NĂNG")
        lbl_title.setObjectName("Title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        layout.addSpacing(30)
        
        btn_create = QPushButton("Tạo câu hỏi")
        btn_create.setFixedSize(400, 80)
        btn_create.clicked.connect(lambda: self.main_app.switch_screen(2))
        layout.addWidget(btn_create, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(20)
        
        btn_exam = QPushButton("Tạo đề thi")
        btn_exam.setFixedSize(400, 80)
        btn_exam.clicked.connect(lambda: self.main_app.switch_screen(10)) # Màn hình mới
        layout.addWidget(btn_exam, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(20)
        
        btn_test = QPushButton("Mô phỏng thi trắc nghiệm")
        btn_test.setFixedSize(400, 80)
        btn_test.clicked.connect(self.start_test)
        layout.addWidget(btn_test, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def start_test(self):
        # Reset toàn bộ câu trả lời của người dùng trước khi làm bài mới
        for cat in state.banks:
            if cat == "ALL":
                for q in state.banks["ALL"]:
                    q["user_ans"] = -1
            else:
                for exam_name, questions in state.banks[cat].items():
                    for q in questions:
                        q["user_ans"] = -1
                
        # Chuyển sang màn hình giới thiệu (Intro)
        intro_screen = self.main_app.stack.widget(0)
        
        # Reset lại trạng thái các nút
        intro_screen.reset_radios()
        
        self.main_app.switch_screen(0)


# Màn hình 3: Tạo câu hỏi
class ScreenCreateQuestion(BaseScreen):
    def __init__(self, main_app):
        super().__init__(main_app)
        layout = QHBoxLayout(self)
        
        # Cột Trái: Form nhập liệu
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        lbl_title = QLabel("TẠO CÂU HỎI")
        lbl_title.setObjectName("Title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_title)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.inp_q = QLineEdit()
        self.inp_a = QLineEdit()
        self.inp_b = QLineEdit()
        self.inp_c = QLineEdit()
        self.inp_d = QLineEdit()
        
        # Make the inputs taller and font larger for better visibility (especially on macOS)
        for inp in [self.inp_q, self.inp_a, self.inp_b, self.inp_c, self.inp_d]:
            inp.setMinimumHeight(55)
            inp.setMinimumWidth(450)
            inp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            inp.setStyleSheet("font-size: 16px; padding: 5px 15px;")
        
        self.cb_ans = QComboBox()
        self.cb_ans.addItems(["A", "B", "C", "D"])
        self.cb_ans.setMinimumHeight(55)
        self.cb_ans.setMinimumWidth(450)
        self.cb_ans.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cb_ans.setStyleSheet("font-size: 16px; padding: 5px 15px;")
        
        def add_row(label, widget):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: white; font-weight: bold;")
            form_layout.addRow(lbl, widget)
            
        add_row("Câu hỏi:", self.inp_q)
        add_row("Đáp án A:", self.inp_a)
        add_row("Đáp án B:", self.inp_b)
        add_row("Đáp án C:", self.inp_c)
        add_row("Đáp án D:", self.inp_d)
        add_row("Đáp án Đúng:", self.cb_ans)
        
        left_layout.addLayout(form_layout)
        left_layout.addSpacing(20)
        
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("Làm mới")
        btn_new.clicked.connect(self.clear_form)
        
        btn_save = QPushButton("Lưu câu hỏi")
        btn_save.setObjectName("ActionButton")
        btn_save.clicked.connect(self.save_question)
        
        btn_delete = QPushButton("Xóa")
        btn_delete.setStyleSheet("background-color: #d62828;")
        btn_delete.clicked.connect(self.delete_question)
        
        btn_layout.addWidget(btn_new)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_delete)
        left_layout.addLayout(btn_layout)
        
        left_layout.addStretch()
        btn_back = QPushButton("Quay lại màn hình chính")
        btn_back.clicked.connect(lambda: self.main_app.switch_screen(1))
        left_layout.addWidget(btn_back)
        
        # Cột Phải: Danh sách câu hỏi
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        lbl_list = QLabel("Danh sách câu hỏi")
        lbl_list.setStyleSheet("color: #FFD700; font-size: 18px; font-weight: bold;")
        lbl_list.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(lbl_list)
        
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm kiếm câu hỏi...")
        self.inp_search.setStyleSheet("color: white; border: 1px solid #00E5FF; padding: 5px;")
        self.inp_search.textChanged.connect(self.refresh_list)
        right_layout.addWidget(self.inp_search)
        
        self.q_list = QListWidget()
        list_style = """
            QListWidget { background-color: rgba(10, 25, 47, 0.8); color: white; border: 1px solid #00E5FF; border-radius: 5px; padding: 5px; }
            QListWidget::item { padding: 5px; }
            QListWidget::item:selected { background-color: rgba(255, 255, 255, 0.2); color: white; font-weight: bold; border-radius: 3px; border-left: 3px solid #00E5FF; }
        """
        self.q_list.setStyleSheet(list_style)
        self.q_list.itemClicked.connect(self.load_selected_question)
        right_layout.addWidget(self.q_list)
        
        layout.addWidget(left_widget, stretch=2)
        layout.addWidget(right_widget, stretch=1)
        
        self.current_edit_idx = -1

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_list()
        
    def refresh_list(self):
        from PyQt6.QtWidgets import QListWidgetItem
        self.q_list.clear()
        search_kw = self.inp_search.text().lower()
        for idx, q in enumerate(state.banks.get("ALL", [])):
            if search_kw in q['q'].lower():
                item = QListWidgetItem(q['q'])
                item.setData(Qt.ItemDataRole.UserRole, idx)
                self.q_list.addItem(item)
            
    def clear_form(self):
        self.current_edit_idx = -1
        self.inp_q.clear()
        self.inp_a.clear()
        self.inp_b.clear()
        self.inp_c.clear()
        self.inp_d.clear()
        self.cb_ans.setCurrentIndex(0)
        self.q_list.clearSelection()
        
    def load_selected_question(self, item):
        self.current_edit_idx = item.data(Qt.ItemDataRole.UserRole)
        q_data = state.banks["ALL"][self.current_edit_idx]
        
        self.inp_q.setText(q_data['q'])
        self.inp_a.setText(q_data['opts'][0])
        self.inp_b.setText(q_data['opts'][1])
        self.inp_c.setText(q_data['opts'][2])
        self.inp_d.setText(q_data['opts'][3])
        self.cb_ans.setCurrentIndex(q_data['ans'])
        
    def save_question(self):
        q = self.inp_q.text().strip()
        opts = [self.inp_a.text().strip(), self.inp_b.text().strip(), self.inp_c.text().strip(), self.inp_d.text().strip()]
        if not q or not all(opts):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ câu hỏi và 4 đáp án!")
            return
            
        q_data = {
            "q": q,
            "opts": opts,
            "ans": self.cb_ans.currentIndex(),
            "user_ans": -1
        }
        
        if self.current_edit_idx == -1:
            state.banks["ALL"].append(q_data)
            QMessageBox.information(self, "Thành công", "Đã thêm câu hỏi mới!")
        else:
            state.banks["ALL"][self.current_edit_idx] = q_data
            QMessageBox.information(self, "Thành công", "Đã cập nhật câu hỏi!")
            
        state.save_db()
        self.refresh_list()
        self.clear_form()
        
    def delete_question(self):
        if self.current_edit_idx == -1:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn 1 câu hỏi để xóa!")
            return
            
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa câu hỏi này khỏi thư viện?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            state.banks["ALL"].pop(self.current_edit_idx)
            state.save_db()
            self.refresh_list()
            self.clear_form()


# Màn hình 10: Tạo Đề thi
class ScreenCreateExam(BaseScreen):
    def __init__(self, main_app):
        super().__init__(main_app)
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("TẠO ĐỀ THI")
        lbl_title.setObjectName("Title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Chọn loại bài thi
        cat_layout = QHBoxLayout()
        lbl_cat = QLabel("Chọn loại đề thi:")
        lbl_cat.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        self.cb_cat = QComboBox()
        self.cb_cat.addItems(["Bài thi làm quen (Warmup)", "Bài thi Luật", "Bài thi lý thuyết", "Câu hỏi đánh giá hệ thống"])
        self.cb_cat.setFixedWidth(300)
        self.cb_cat.currentIndexChanged.connect(self.on_cat_changed)
        cat_layout.addStretch()
        cat_layout.addWidget(lbl_cat)
        cat_layout.addWidget(self.cb_cat)
        cat_layout.addStretch()
        layout.addLayout(cat_layout)
        
        # Chọn đề thi
        exam_layout = QHBoxLayout()
        lbl_exam = QLabel("Chọn đề thi:")
        lbl_exam.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        self.cb_exam = QComboBox()
        self.cb_exam.setFixedWidth(300)
        self.cb_exam.currentIndexChanged.connect(self.refresh_lists)
        
        btn_new_exam = QPushButton("+ Tạo đề thi mới")
        btn_new_exam.setObjectName("ActionButton")
        btn_new_exam.clicked.connect(self.create_exam)
        
        btn_del_exam = QPushButton("Xóa đề thi")
        btn_del_exam.setStyleSheet("background-color: #d62828;")
        btn_del_exam.clicked.connect(self.delete_exam)
        
        exam_layout.addStretch()
        exam_layout.addWidget(lbl_exam)
        exam_layout.addWidget(self.cb_exam)
        exam_layout.addWidget(btn_new_exam)
        exam_layout.addWidget(btn_del_exam)
        exam_layout.addStretch()
        layout.addLayout(exam_layout)
        
        layout.addSpacing(20)
        
        # Khu vực ghép đề
        lists_layout = QHBoxLayout()
        
        # Left: ALL questions
        left_layout = QVBoxLayout()
        lbl_all = QLabel("Thư viện câu hỏi (ALL)")
        lbl_all.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 16px;")
        lbl_all.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_all)
        
        self.inp_search_all = QLineEdit()
        self.inp_search_all.setPlaceholderText("Tìm kiếm câu hỏi...")
        self.inp_search_all.setStyleSheet("color: white; border: 1px solid #00E5FF; padding: 5px; border-radius: 3px;")
        self.inp_search_all.textChanged.connect(self.refresh_lists)
        left_layout.addWidget(self.inp_search_all)
        
        self.list_all = QListWidget()
        list_style_all = """
            QListWidget { background-color: rgba(10, 25, 47, 0.8); color: white; border: 1px solid #00E5FF; padding: 5px; }
            QListWidget::item { padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1); }
            QListWidget::item:selected { background-color: rgba(255, 255, 255, 0.2); color: white; font-weight: bold; border-left: 3px solid #00E5FF; }
        """
        self.list_all.setStyleSheet(list_style_all)
        left_layout.addWidget(self.list_all)
        lists_layout.addLayout(left_layout, stretch=2)
        
        # Middle: Buttons
        mid_layout = QVBoxLayout()
        mid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_add = QPushButton(">> Thêm")
        self.btn_add.clicked.connect(self.add_to_exam)
        self.btn_remove = QPushButton("<< Bỏ")
        self.btn_remove.setStyleSheet("background-color: #d62828;")
        self.btn_remove.clicked.connect(self.remove_from_exam)
        
        mid_layout.addWidget(self.btn_add)
        mid_layout.addSpacing(20)
        mid_layout.addWidget(self.btn_remove)
        lists_layout.addLayout(mid_layout, stretch=1)
        
        # Right: Exam questions
        right_layout = QVBoxLayout()
        lbl_exam_qs = QLabel("Câu hỏi trong đề thi")
        lbl_exam_qs.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 16px;")
        lbl_exam_qs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(lbl_exam_qs)
        
        self.list_exam = QListWidget()
        list_style_exam = """
            QListWidget { background-color: rgba(10, 25, 47, 0.8); color: white; border: 1px solid #00FF00; padding: 5px; }
            QListWidget::item { padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1); }
            QListWidget::item:selected { background-color: rgba(255, 255, 255, 0.2); color: white; font-weight: bold; border-left: 3px solid #00FF00; }
        """
        self.list_exam.setStyleSheet(list_style_exam)
        right_layout.addWidget(self.list_exam)
        lists_layout.addLayout(right_layout, stretch=2)
        
        layout.addLayout(lists_layout)
        
        layout.addSpacing(20)
        
        btn_back = QPushButton("Quay lại màn hình chính")
        btn_back.setFixedWidth(300)
        btn_back.clicked.connect(lambda: self.main_app.switch_screen(1))
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.on_cat_changed()
        
    def get_current_cat_key(self):
        cat_map = {"Bài thi làm quen (Warmup)": "WARMUP", "Bài thi Luật": "LAW", "Bài thi lý thuyết": "THEORY", "Câu hỏi đánh giá hệ thống": "FEEDBACK"}
        return cat_map[self.cb_cat.currentText()]
        
    def get_current_exam_name(self):
        return self.cb_exam.currentText() or "Mặc định"
        
    def on_cat_changed(self):
        cat = self.get_current_cat_key()
        self.cb_exam.blockSignals(True)
        self.cb_exam.clear()
        self.cb_exam.addItems(state.get_exam_names(cat))
        self.cb_exam.blockSignals(False)
        self.refresh_lists()
        
    def create_exam(self):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, 'Tạo đề thi mới', 'Nhập tên đề thi:')
        if ok and text.strip():
            text = text.strip()
            cat = self.get_current_cat_key()
            if text in state.banks[cat]:
                QMessageBox.warning(self, "Lỗi", "Tên đề thi đã tồn tại!")
                return
            state.banks[cat][text] = []
            state.save_db()
            self.on_cat_changed()
            self.cb_exam.setCurrentText(text)
            
    def delete_exam(self):
        cat = self.get_current_cat_key()
        exam = self.get_current_exam_name()
        if exam == "Mặc định":
            QMessageBox.warning(self, "Lỗi", "Không thể xóa đề thi Mặc định!")
            return
            
        reply = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa đề thi '{exam}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del state.banks[cat][exam]
            state.save_db()
            self.on_cat_changed()

    def refresh_lists(self):
        from PyQt6.QtWidgets import QListWidgetItem
        self.list_all.clear()
        self.list_exam.clear()
        
        cat = self.get_current_cat_key()
        exam_name = self.get_current_exam_name()
        
        exam_info = state.banks.get(cat, {}).get(exam_name, [])
        exam_qs = [q['q'] for q in exam_info]
        search_kw = hasattr(self, 'inp_search_all') and self.inp_search_all.text().lower() or ""
        
        for idx, q in enumerate(state.banks.get("ALL", [])):
            if q['q'] not in exam_qs and search_kw in q['q'].lower():
                item = QListWidgetItem(q['q'])
                item.setData(Qt.ItemDataRole.UserRole, idx)
                self.list_all.addItem(item)
            
        for idx, q in enumerate(exam_info):
            item = QListWidgetItem(f"Câu {idx+1}: {q['q']}")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.list_exam.addItem(item)
            
    def add_to_exam(self):
        selected = self.list_all.currentItem()
        if not selected:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn 1 câu hỏi từ Thư viện!")
            return
            
        all_idx = selected.data(Qt.ItemDataRole.UserRole)
        q_data = state.banks["ALL"][all_idx]
        
        cat = self.get_current_cat_key()
        exam_name = self.get_current_exam_name()
        exam_info = state.banks.get(cat, {}).get(exam_name, [])
        exam_qs = [q['q'] for q in exam_info]
        if q_data['q'] in exam_qs:
            QMessageBox.warning(self, "Lỗi", "Câu hỏi này đã có trong đề thi!")
            return
            
        import copy
        q_copy = copy.deepcopy(q_data)
        q_copy["user_ans"] = -1
        
        if exam_name not in state.banks.get(cat, {}):
            if cat not in state.banks:
                state.banks[cat] = {}
            state.banks[cat][exam_name] = []
        state.banks[cat][exam_name].append(q_copy)
        state.save_db()
        self.refresh_lists()
        
    def remove_from_exam(self):
        selected = self.list_exam.currentItem()
        if not selected:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn 1 câu hỏi từ Đề thi để gỡ bỏ!")
            return
            
        exam_idx = selected.data(Qt.ItemDataRole.UserRole)
        cat = self.get_current_cat_key()
        exam_name = self.get_current_exam_name()
        
        state.banks[cat][exam_name].pop(exam_idx)
        state.save_db()
        self.refresh_lists()


# ==========================================
# CUSTOM ANSWER OPTION WIDGET
# ==========================================
class AnswerOptionWidget(QFrame):
    clicked = pyqtSignal(int)
    
    def __init__(self, index, letter="A", text="", parent=None):
        super().__init__(parent)
        self.index = index
        self.is_selected = False
        
        self.setObjectName("AnswerOption")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(60)
        
        # 1. Container Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        # 2. Checkbox (Thành phần 1)
        self.checkbox = QLabel()
        self.checkbox.setFixedSize(24, 24)
        self.checkbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkbox.setObjectName("AnswerCheckbox")
        layout.addWidget(self.checkbox)
        
        layout.addSpacing(12)
        
        # 3. Ký tự A, B, C, D (Thành phần 2)
        self.lbl_letter = QLabel(f"{letter}.")
        self.lbl_letter.setObjectName("AnswerLetter")
        self.lbl_letter.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.lbl_letter)
        
        layout.addSpacing(8)
        
        # 4. Nội dung đáp án (Thành phần 3)
        self.lbl_text = QLabel(text)
        self.lbl_text.setObjectName("AnswerText")
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(self.lbl_text, 1)
        
        self.hover_state = False
        self.update_style()
        
    def setText(self, text):
        self.lbl_text.setText(text)
        
    def setChecked(self, checked):
        if self.is_selected != checked:
            self.is_selected = checked
            self.update_style()
            
    def isChecked(self):
        return self.is_selected
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(True)
            self.clicked.emit(self.index)
            
    def enterEvent(self, event):
        self.hover_state = True
        self.update_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_state = False
        self.update_style()
        super().leaveEvent(event)
        
    def update_style(self):
        primary_cyan = "#00E5FF"
        primary_gold = "#FFD700"
        bg_dark = "rgba(10, 25, 47, 0.8)"
        
        if self.is_selected:
            bg_color = "rgba(0, 229, 255, 0.3)" # Lớp màu cực nhạt cùng tone
            border_color = primary_cyan
            checkbox_bg = primary_cyan
            checkbox_border = primary_cyan
            self.checkbox.setText("✔")
            self.checkbox.setStyleSheet(f"color: white; font-weight: bold; font-size: 16px; background-color: {checkbox_bg}; border: 2px solid {checkbox_border}; border-radius: 4px;")
            text_color = primary_gold
        else:
            if self.hover_state:
                bg_color = "rgba(0, 229, 255, 0.1)" # Xám rất nhạt
                border_color = primary_gold
                text_color = primary_gold
            else:
                bg_color = bg_dark # Cùng màu nền khung câu hỏi
                border_color = primary_cyan
                text_color = primary_gold
            
            checkbox_bg = "transparent"
            checkbox_border = primary_cyan
            self.checkbox.setText("")
            self.checkbox.setStyleSheet(f"background-color: {checkbox_bg}; border: 2px solid {checkbox_border}; border-radius: 4px;")
            
        self.setStyleSheet(f"""
            QFrame#AnswerOption {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 15px;
            }}
            QLabel#AnswerLetter {{
                color: {text_color};
                font-weight: bold;
                font-size: 16px;
                border: none;
                background: transparent;
            }}
            QLabel#AnswerText {{
                color: {text_color};
                font-weight: bold;
                font-size: 16px;
                border: none;
                background: transparent;
            }}
        """)


# Hỗ trợ hiển thị bài thi trắc nghiệm (Dùng chung cho Warmup, Law, Theory, Feedback)
class TestScreen(BaseScreen):
    def __init__(self, main_app, category, title, next_sc=None, review_sc=None, is_warmup=False):
        super().__init__(main_app)
        self.category = category
        self.next_sc = next_sc
        self.review_sc = review_sc
        self.is_warmup = is_warmup
        self.curr_idx = 0
        
        layout = QVBoxLayout(self)
        
        # Header Frame
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setStyleSheet("""
            QFrame#HeaderFrame {
                background: transparent;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 16, 0, 16)
        header_layout.setSpacing(12)
        
        # 1. Section Name (Pill Badge)
        self.lbl_badge = QLabel()
        self.lbl_badge.setObjectName("SectionBadge")
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_badge.setStyleSheet("""
            QLabel#SectionBadge {
                background-color: #EEF2FF;
                color: #4338CA;
                font-size: 22px;
                font-weight: 800;
                padding: 10px 24px;
                border-radius: 20px;
            }
        """)
        
        badge_container = QHBoxLayout()
        badge_container.addStretch()
        badge_container.addWidget(self.lbl_badge)
        badge_container.addStretch()
        header_layout.addLayout(badge_container)
        
        # 3. Progress Indicator
        self.progress_layout = QHBoxLayout()
        self.progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_layout.setSpacing(8)
        header_layout.addLayout(self.progress_layout)
        
        # Question Progress Label
        self.lbl_q_progress = QLabel()
        self.lbl_q_progress.setStyleSheet("color: #A0AEC0; font-size: 15px; font-weight: bold;")
        self.lbl_q_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.lbl_q_progress)

        layout.addWidget(header_frame)
        
        # HUD Question box
        self.lbl_q = QLabel("Question Text")
        self.lbl_q.setObjectName("QuestionText")
        self.lbl_q.setWordWrap(True)
        self.lbl_q.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_q.setMinimumHeight(120)
        layout.addWidget(self.lbl_q)
        
        layout.addSpacing(10)
        
        btn_trans = QPushButton("Phiên dịch sang Tiếng Anh")
        btn_trans.setFixedWidth(250)
        btn_trans.setStyleSheet("background-color: #81b214; color: white; font-weight: bold; font-size: 16px; border-radius: 5px; padding: 10px;")
        btn_trans.clicked.connect(self.translate_ui)
        layout.addWidget(btn_trans, alignment=Qt.AlignmentFlag.AlignLeft)
        
        layout.addSpacing(24)
        
        # Vertical Answer List
        vbox_opts = QVBoxLayout()
        vbox_opts.setSpacing(15)
        self.btn_opts = []
        letters = ["A", "B", "C", "D"]
        for i in range(4):
            opt_widget = AnswerOptionWidget(index=i, letter=letters[i], text="")
            opt_widget.clicked.connect(self.on_answer_clicked)
            self.btn_opts.append(opt_widget)
            vbox_opts.addWidget(opt_widget)
            
        layout.addLayout(vbox_opts)
        layout.addStretch()
        
        # Footer Action Buttons
        footer = QHBoxLayout()
        
        # Logic nút Kết thúc / Bỏ qua (warmup) / Tiếp theo
        if self.category == "FEEDBACK":
            end_text = "Xem kết quả thi"
        elif self.category == "LAW":
            end_text = "Kết thúc bài thi Luật và xem kết quả"
        elif self.category == "THEORY":
            end_text = "Kết thúc bài thi Lý thuyết và xem kết quả"
        else:
            end_text = "Kết thúc bài thi"
            
        self.btn_end = QPushButton(end_text)
        self.btn_end.setStyleSheet("background-color: #d62828;")
        self.btn_end.clicked.connect(self.end_test)
        footer.addWidget(self.btn_end)
        
        footer.addStretch()
        
        self.btn_skip = None
        if self.is_warmup:
            self.btn_skip = QPushButton("Bỏ qua bài thi thử")
            self.btn_skip.clicked.connect(self.skip_warmup)
            footer.addWidget(self.btn_skip)
            
        footer.addStretch()
        
        self.btn_next = QPushButton("Tiếp theo")
        self.btn_next.setObjectName("ActionButton")
        self.btn_next.clicked.connect(self.next_question)
        footer.addWidget(self.btn_next)
        
        self.btn_confirm = QPushButton("Xác nhận")
        self.btn_confirm.setObjectName("ActionButton")
        self.btn_confirm.clicked.connect(self.confirm_review)
        self.btn_confirm.hide()
        footer.addWidget(self.btn_confirm)
        
        layout.addLayout(footer)

    def confirm_review(self):
        if self.review_sc is not None:
            self.main_app.stack.widget(self.review_sc).populate_list()
            self.main_app.switch_screen(self.review_sc)

    def load_question(self, idx, is_review=False):
        if idx < 0 or idx >= len(state.get_exam(self.category)):
            return
            
        if is_review:
            self.btn_end.hide()
            self.btn_next.hide()
            if self.btn_skip is not None: self.btn_skip.hide()
            self.btn_confirm.show()
        else:
            self.btn_end.show()
            self.btn_next.show()
            if self.btn_skip is not None: self.btn_skip.show()
            self.btn_confirm.hide()
        
        self.curr_idx = idx
        q_data = state.get_exam(self.category)[idx]
        
        cat_info = {
            "WARMUP": ("🎯 CÁC CÂU HỎI KHÔNG TÍNH ĐIỂM ĐỂ LÀM QUEN PHẦN MỀM", 0),
            "LAW": ("📖 BÀI THI LUẬT", 1),
            "THEORY": ("🧠 BÀI THI LÝ THUYẾT", 2),
            "FEEDBACK": ("💬 ĐÁNH GIÁ HỆ THỐNG (KHÔNG TÍNH ĐIỂM)", 3)
        }
        title_text, section_idx = cat_info.get(self.category, ("📝 BÀI THI", 0))
        
        self.lbl_badge.setText(title_text)
        
        total_q = len(state.get_exam(self.category))
        
        while self.progress_layout.count():
            item = self.progress_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        for i in range(total_q):
            dot = QFrame()
            dot.setMinimumSize(4, 6)
            dot.setMaximumSize(40, 6)
            dot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if i == idx:
                dot.setStyleSheet("background-color: #00E5FF; border-radius: 3px;")  # Active
            elif i < idx:
                dot.setStyleSheet("background-color: rgba(0, 229, 255, 0.4); border-radius: 3px;") # Passed
            else:
                dot.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); border-radius: 3px;") # Upcoming
            self.progress_layout.addWidget(dot)
                
        self.lbl_q_progress.setText(f"Câu hỏi {idx+1} / {total_q}")
        
        self.lbl_q.setText(f"Câu {idx+1}. {q_data['q']}")
        
        for i in range(4):
            self.btn_opts[i].setText(q_data['opts'][i])
            self.btn_opts[i].setChecked(False)
        
        if q_data['user_ans'] != -1:
            self.btn_opts[q_data['user_ans']].setChecked(True)
            
    def on_answer_clicked(self, ans_idx):
        for opt in self.btn_opts:
            if opt.index != ans_idx:
                opt.setChecked(False)
        state.get_exam(self.category)[self.curr_idx]["user_ans"] = ans_idx

    def end_test(self):
        if self.is_warmup:
            msg = "Bạn có chắc chắn muốn kết thúc bài thi khởi động?"
        elif self.category == "LAW":
            msg = "Bạn có chắc chắn muốn kết thúc bài thi Luật và chuyển sang phần tiếp theo?"
        elif self.category == "THEORY":
            msg = "Bạn có chắc chắn muốn kết thúc bài thi Lý thuyết và chuyển sang phần tiếp theo?"
        else:
            msg = "Bạn có chắc chắn muốn kết thúc bài thi ở đây?"
            
        reply = QMessageBox.question(self, "Xác nhận", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_warmup:
                QMessageBox.warning(self, "Finish", "BÀI THI KẾT THÚC (Quay về Menu)")
                self.main_app.switch_screen(1) # Back to menu
            else:
                if self.review_sc is not None:
                    # Tới Review Screen
                    self.main_app.stack.widget(self.review_sc).populate_list()
                    self.main_app.switch_screen(self.review_sc)
                elif self.next_sc is not None:
                    # Bài Feedback nhảy thẳng qua KQ
                    self.main_app.switch_screen(self.next_sc)
                    
    def skip_warmup(self):
        reply = QMessageBox.question(
            self, "Bỏ qua", "Bạn đã hiểu rõ về quy định và muốn vào bài thi chính thức?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes and self.next_sc is not None:
            self.main_app.go_to_test(self.next_sc, 0)
            
    def next_question(self):
        max_idx = len(state.get_exam(self.category)) - 1
        
        if self.curr_idx >= max_idx:
            if self.category in ["LAW", "THEORY"]:
                QMessageBox.information(
                    self, 
                    "Thông báo", 
                    "Bạn đã trả lời hết câu hỏi của bài thi, vui lòng chọn Kết thúc bài thi để chuyển sang phần tiếp theo"
                )
                return
                
            if self.is_warmup and self.next_sc is not None:
                r2 = QMessageBox.question(self, "Bài thi chính thức", "Bạn có muốn chuyển sang bài thi chính thức?", 
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if r2 == QMessageBox.StandardButton.Yes:
                    self.main_app.go_to_test(self.next_sc, 0)
            else:
                self.end_test()
            return
            
        if self.category == "FEEDBACK":
            reply = QMessageBox.StandardButton.Yes
        else:
            reply = QMessageBox.question(
                self, "Chuyển câu", "Bạn có muốn chuyển sang câu hỏi tiếp theo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        if reply == QMessageBox.StandardButton.No: return
        
        self.load_question(self.curr_idx + 1)


# Màn hình Xem lại (Cho Luật & Lý thuyết)
class ReviewScreen(BaseScreen):
    def __init__(self, main_app, category, title, test_sc_idx, next_sc_idx):
        super().__init__(main_app)
        self.category = category
        self.test_sc_idx = test_sc_idx
        self.next_sc_idx = next_sc_idx
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.box = QFrame()
        self.box.setObjectName("ReviewBox")
        self.box.setStyleSheet("QFrame#ReviewBox { background-color: rgba(10, 25, 47, 0.9); border: 2px solid #00E5FF; border-radius: 15px; }")
        self.box.setFixedSize(800, 600)
        
        layout = QVBoxLayout(self.box)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("Title")
        lbl_title.setStyleSheet("border: none; background: transparent; color: #00E5FF; font-size: 24px; font-weight: bold;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Scroll area for review items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget#ScrollContent { background: transparent; }")
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(10)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        # Footer inside the box
        footer = QHBoxLayout()
        footer.addStretch()
        
        if self.category == "LAW":
            end_btn_text = "Kết thúc bài thi Luật và chuyển sang phần tiếp theo"
        elif self.category == "THEORY":
            end_btn_text = "Kết thúc bài thi Lý thuyết và chuyển sang phần tiếp theo"
        else:
            end_btn_text = "Kết thúc bài thi và chuyển sang phần tiếp theo"
            
        btn_end = QPushButton(end_btn_text)
        btn_end.setObjectName("ActionButton")
        btn_end.setStyleSheet("padding: 10px 30px; border-radius: 8px; font-weight: bold; font-size: 16px;")
        btn_end.clicked.connect(self.finish_review)
        footer.addWidget(btn_end)
        
        layout.addLayout(footer)
        main_layout.addWidget(self.box)
        
    def populate_list(self):
        # Clear old items
        for i in reversed(range(self.list_layout.count())):
            widget = self.list_layout.itemAt(i).widget()
            if widget is not None: widget.setParent(None)
            
        for idx, q_data in enumerate(state.get_exam(self.category)):
            row = QFrame()
            row.setStyleSheet("background-color: rgba(0,0,0,100); border-radius: 8px; border: 1px solid #00E5FF;")
            r_lay = QVBoxLayout(row)
            r_lay.setContentsMargins(15, 15, 15, 15)
            r_lay.setSpacing(10)
            
            lbl_q = QLabel(f"Câu {idx+1}: {q_data['q']}")
            lbl_q.setStyleSheet("border: none; color: white; font-size: 16px;")
            lbl_q.setWordWrap(True)
            lbl_q.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            r_lay.addWidget(lbl_q)
            
            ans_lay = QHBoxLayout()
            if q_data['user_ans'] != -1:
                ans_text = q_data['opts'][q_data['user_ans']]
                ans_str = f"{['A', 'B', 'C', 'D'][q_data['user_ans']]}: {ans_text}"
            else:
                ans_str = "Chưa làm"
            lbl_ans = QLabel(f"Đã chọn: {ans_str}")
            lbl_ans.setStyleSheet("border: none; color: #FFD700; font-weight: bold; font-size: 15px;")
            lbl_ans.setWordWrap(True)
            lbl_ans.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            ans_lay.addWidget(lbl_ans, stretch=1)
            
            btn_re = QPushButton("Xem lại")
            btn_re.setFixedWidth(100)
            btn_re.setStyleSheet("background-color: #0096c7; color: white; border-radius: 5px; padding: 5px; border: none; font-weight: bold;")
            # Use default argument binding (_i=idx) in lambda to capture loop variable cleanly!
            btn_re.clicked.connect(lambda _, _i=idx: self.main_app.go_to_test(self.test_sc_idx, _i, is_review=True))
            ans_lay.addWidget(btn_re)
            
            r_lay.addLayout(ans_lay)
            
            self.list_layout.addWidget(row)
            
    def finish_review(self):
        msg = "Bạn có chắc chắn muốn thao tác chuyển sang phần tiếp theo?"
        reply = QMessageBox.question(self, "Xác nhận", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.next_sc_idx is not None:
                # Nếu là thi tiếp, gọi load_question cho màn thi đó
                tgt = self.main_app.stack.widget(self.next_sc_idx)
                if hasattr(tgt, "load_question"):
                    tgt.load_question(0)
            self.main_app.switch_screen(self.next_sc_idx)


# Màn hình 11: Chọn đề thi con
class ScreenChooseExam(BaseScreen):
    def __init__(self, main_app):
        super().__init__(main_app)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("CHỌN ĐỀ THI")
        lbl_title.setObjectName("Title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        layout.addSpacing(30)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.cb_warmup = QComboBox()
        self.cb_law = QComboBox()
        self.cb_theory = QComboBox()
        self.cb_feedback = QComboBox()
        
        for cb in [self.cb_warmup, self.cb_law, self.cb_theory, self.cb_feedback]:
            cb.setMinimumHeight(45)
            cb.setMinimumWidth(300)
            cb.setStyleSheet("font-size: 16px; padding: 5px 15px;")
            
        def add_row(label, widget):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
            form_layout.addRow(lbl, widget)
            
        add_row("Bài thi làm quen (Warmup):", self.cb_warmup)
        add_row("Bài thi Luật:", self.cb_law)
        add_row("Bài thi Lý thuyết:", self.cb_theory)
        add_row("Câu hỏi đánh giá hệ thống:", self.cb_feedback)
        
        h_wrapper = QHBoxLayout()
        h_wrapper.addStretch()
        h_wrapper.addLayout(form_layout)
        h_wrapper.addStretch()
        layout.addLayout(h_wrapper)
        
        layout.addSpacing(40)
        
        btn_layout = QHBoxLayout()
        btn_back = QPushButton("Quay lại")
        btn_back.clicked.connect(lambda: self.main_app.switch_screen(1))
        btn_back.setFixedSize(160, 50)
        
        btn_start = QPushButton("Bắt đầu làm bài")
        btn_start.setObjectName("ActionButton")
        btn_start.setFixedSize(200, 50)
        btn_start.clicked.connect(self.start_exam)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_back)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_start)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    def showEvent(self, event):
        super().showEvent(event)
        def refresh_cb(cb, cat):
            cb.clear()
            names = state.get_exam_names(cat)
            cb.addItems(names)
            curr = state.selected_exams.get(cat, "Mặc định")
            if curr in names:
                cb.setCurrentText(curr)
                
        refresh_cb(self.cb_warmup, "WARMUP")
        refresh_cb(self.cb_law, "LAW")
        refresh_cb(self.cb_theory, "THEORY")
        refresh_cb(self.cb_feedback, "FEEDBACK")
        
    def start_exam(self):
        state.selected_exams["WARMUP"] = self.cb_warmup.currentText()
        state.selected_exams["LAW"] = self.cb_law.currentText()
        state.selected_exams["THEORY"] = self.cb_theory.currentText()
        state.selected_exams["FEEDBACK"] = self.cb_feedback.currentText()
        
        test_screen = self.main_app.stack.widget(3)
        test_screen.load_question(0)
        self.main_app.switch_screen(3)


# Màn hình 10: Xem Kết quả
class ScreenResults(BaseScreen):
    def __init__(self, main_app):
        super().__init__(main_app)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lbl_title = QLabel("CHÚC MỪNG BẠN ĐÃ HOÀN THÀNH BÀI THI")
        lbl_title.setObjectName("Title")
        lbl_title.setStyleSheet("color: #FFD700; font-size: 30px; margin-top: 20px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        layout.addSpacing(10)
        
        self.lbl_law = QLabel("Bài thi Luật: -- / -- đ | Sai: --")
        self.lbl_law.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.lbl_law.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_law)
        
        self.lbl_theory = QLabel("Bài thi Lý thuyết: -- / -- đ | Sai: --")
        self.lbl_theory.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.lbl_theory.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_theory)
        
        layout.addSpacing(20)
        
        # Scroll area for detailed results
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        layout.addSpacing(20)
        
        # Bottom exit button
        btn_layout = QHBoxLayout()
        btn_exit = QPushButton("Về Menu Chính")
        btn_exit.setObjectName("ActionButton")
        btn_exit.setFixedSize(200, 50)
        btn_exit.clicked.connect(lambda: self.main_app.switch_screen(1))
        btn_layout.addStretch()
        btn_layout.addWidget(btn_exit)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addSpacing(20)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.calc_scores()
        self.populate_details()
        
    def calc_scores(self):
        for cat, lbl in [("LAW", self.lbl_law), ("THEORY", self.lbl_theory)]:
            bank = state.get_exam(cat)
            if not bank: continue
            
            total = len(bank)
            correct = sum(1 for q in bank if q['user_ans'] == q['ans'])
            wrong = total - correct
            
            name = "Bài thi Luật" if cat == "LAW" else "Bài thi Lý thuyết"
            lbl.setText(f"{name}: {correct} / {total} đúng | {wrong} sai")

    def populate_details(self):
        # Clear old items
        for i in reversed(range(self.list_layout.count())):
            widget = self.list_layout.itemAt(i).widget()
            if widget is not None: widget.setParent(None)
            
        for cat, cat_name in [("LAW", "BÀI THI LUẬT"), ("THEORY", "BÀI THI LÝ THUYẾT")]:
            bank = state.get_exam(cat)
            if not bank: continue
            
            # Category Header
            cat_lbl = QLabel(f"--- {cat_name} ---")
            cat_lbl.setStyleSheet("color: #00E5FF; font-size: 18px; font-weight: bold; margin-top: 15px;")
            self.list_layout.addWidget(cat_lbl)
            
            for idx, q_data in enumerate(bank):
                row = QFrame()
                row.setStyleSheet("background-color: rgba(0,0,0,100); border-radius: 8px; border: 1px solid #445566; margin-bottom: 5px;")
                v_lay = QVBoxLayout(row)
                
                # Question textual details
                lbl_q = QLabel(f"Câu {idx+1}: {q_data['q']}")
                lbl_q.setStyleSheet("border: none; color: white; font-weight: bold; font-size: 16px;")
                lbl_q.setWordWrap(True)
                v_lay.addWidget(lbl_q)
                
                # User's answer
                ans_labels = ["A", "B", "C", "D"]
                u_idx = q_data['user_ans']
                if u_idx != -1:
                    u_ans_str = f"{ans_labels[u_idx]}: {q_data['opts'][u_idx]}"
                else:
                    u_ans_str = "Chưa làm"
                    
                is_correct = (u_idx == q_data['ans'])
                color_user = "#00FF00" if is_correct else "#FF3333"
                
                lbl_u_ans = QLabel(f"Đáp án bạn chọn: {u_ans_str}")
                lbl_u_ans.setStyleSheet(f"border: none; color: {color_user}; font-size: 14px;")
                lbl_u_ans.setWordWrap(True)
                v_lay.addWidget(lbl_u_ans)
                
                # Correct Answer (Show only if user got it wrong or didn't answer)
                if not is_correct:
                    c_idx = q_data['ans']
                    c_ans_str = f"{ans_labels[c_idx]}: {q_data['opts'][c_idx]}"
                    lbl_c_ans = QLabel(f"Đáp án đúng: {c_ans_str}")
                    lbl_c_ans.setStyleSheet("border: none; color: #00FF00; font-size: 14px; font-style: italic;")
                    lbl_c_ans.setWordWrap(True)
                    v_lay.addWidget(lbl_c_ans)
                
                self.list_layout.addWidget(row)


# ==========================================
# 4. TRÌNH QUẢN LÝ ỨNG DỤNG - MAIN APP
# ==========================================
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation HUD Quiz App")
        self.setMinimumSize(1000, 700)
        
        # Áp dụng QSS tổng
        self.setStyleSheet(STYLESHEET)
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        
        # Chỉ số các màn hình
        # 0: Intro
        # 1: Menu
        # 2: Create Bank
        # 3: Warmup
        # 4: Law Test
        # 5: Law Review
        # 6: Theory Test
        # 7: Theory Review
        # 8: Feedback Test
        # 9: Results
        
        self.stack.addWidget(ScreenIntro(self))         # 0
        self.stack.addWidget(ScreenMenu(self))          # 1
        self.stack.addWidget(ScreenCreateQuestion(self))    # 2
        
        self.stack.addWidget(TestScreen(self, "WARMUP", "KHỞI ĐỘNG: GIAO DIỆN AI LÀ TRIỆU PHÚ", is_warmup=True, next_sc=4)) # 3
        
        self.stack.addWidget(TestScreen(self, "LAW", "BÀI THI LUẬT CHÍNH THỨC", review_sc=5)) # 4
        self.stack.addWidget(ReviewScreen(self, "LAW", "BẢNG XEM LẠI: BÀI THI LUẬT", test_sc_idx=4, next_sc_idx=6)) # 5
        
        self.stack.addWidget(TestScreen(self, "THEORY", "BÀI THI LÝ THUYẾT", review_sc=7)) # 6
        self.stack.addWidget(ReviewScreen(self, "THEORY", "BẢNG XEM LẠI: LÝ THUYẾT", test_sc_idx=6, next_sc_idx=8)) # 7
        
        # Screen Feedback (không có Review, chạy thẳng Result)
        self.stack.addWidget(TestScreen(self, "FEEDBACK", "ĐÁNH GIÁ HỆ THỐNG", is_warmup=False, next_sc=9)) # 8
        
        self.stack.addWidget(ScreenResults(self)) # 9
        
        self.stack.addWidget(ScreenCreateExam(self)) # 10
        self.stack.addWidget(ScreenChooseExam(self)) # 11
        
        self.stack.setCurrentIndex(1)
        
    def switch_screen(self, idx):
        self.stack.setCurrentIndex(idx)
        
    def go_to_test(self, screen_idx, question_idx, is_review=False):
        test_screen = self.stack.widget(screen_idx)
        if hasattr(test_screen, "load_question"):
            try:
                test_screen.load_question(question_idx, is_review)
            except TypeError:
                test_screen.load_question(question_idx)
        self.stack.setCurrentIndex(screen_idx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Kích hoạt font đẹp mượt
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    window = MainApp()
    window.show()
    sys.exit(app.exec())
