from __future__ import annotations

import json
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QDateTime, QPoint, QRect, QSize, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QGraphicsDropShadowEffect,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


def get_data_file() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "dday_data.json"
    return Path(__file__).with_name("dday_data.json")


DATA_FILE = get_data_file()


def get_icon_file() -> Path:
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    return base_dir / "assets" / "company_tracker.ico"
MINI_WIDTH = 305
MINI_HEIGHT = 170
EXPANDED_WIDTH = 920
EXPANDED_HEIGHT = 620
SCREEN_MARGIN = 20
MIN_RESIZE_WIDTH = 260
MAX_RESIZE_WIDTH = 1280
RESIZE_MARGIN = 10
MINI_BASE_HEIGHT = 150
MINI_ITEM_HEIGHT = 62
MINI_MAX_HEIGHT = 420


@dataclass
class CompanyEntry:
    id: str
    name: str
    interview_at: str
    memo: str = ""
    interview_info: str = ""
    link: str = ""

    @property
    def interview_datetime(self) -> datetime:
        return datetime.fromisoformat(self.interview_at)


class CompanyListWidget(QListWidget):
    orderChanged = pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.orderChanged.emit()


class CompanyCard(QWidget):
    def __init__(self, company: CompanyEntry):
        super().__init__()
        self.company_id = company.id
        self.name_label = QLabel(company.name)
        self.countdown_label = QLabel("")
        self.when_label = QLabel("")

        self.name_label.setObjectName("cardTitle")
        self.countdown_label.setObjectName("cardCountdown")
        self.when_label.setObjectName("cardWhen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 1, 14, 1)
        layout.setSpacing(4)
        layout.addWidget(self.name_label)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.when_label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(6, 12, 22, 60))
        self.setGraphicsEffect(shadow)

        self.update_content(company)

    def update_content(self, company: CompanyEntry):
        self.name_label.setText(company.name)
        self.countdown_label.setText(format_countdown(company.interview_datetime))
        self.when_label.setText(company.interview_datetime.strftime("%Y-%m-%d %H:%M"))


class AddCompanyDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("회사 추가")
        self.setModal(True)
        self.resize(360, 120)
        self.is_dark_mode = bool(getattr(parent, "is_dark_mode", True))

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("예: OpenAI Korea")

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addDays(1))

        form = QFormLayout()
        form.addRow("회사명", self.name_edit)
        form.addRow("면접 일시", self.datetime_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.apply_dialog_style()

    def apply_dialog_style(self):
        if self.is_dark_mode:
            self.setStyleSheet(
                """
                QDialog {
                    background-color: rgba(18, 24, 36, 245);
                    color: #eef3fb;
                }
                QLabel {
                    color: #eef3fb;
                }
                QLineEdit, QDateTimeEdit {
                    color: #f4f7fd;
                    background-color: rgba(255, 255, 255, 18);
                    border: 1px solid rgba(255, 255, 255, 36);
                    border-radius: 12px;
                    padding: 10px 12px;
                }
                QLineEdit:focus, QDateTimeEdit:focus {
                    border: 1px solid rgba(91, 165, 255, 0.95);
                    background-color: rgba(255, 255, 255, 22);
                }
                QPushButton {
                    color: #f5f8ff;
                    background-color: rgba(255, 255, 255, 14);
                    border: 1px solid rgba(255, 255, 255, 32);
                    border-radius: 12px;
                    padding: 8px 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 20);
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QDialog {
                    background-color: rgba(248, 250, 255, 245);
                    color: #1b2638;
                }
                QLabel {
                    color: #1b2638;
                }
                QLineEdit, QDateTimeEdit {
                    color: #132033;
                    background-color: rgba(255, 255, 255, 220);
                    border: 1px solid rgba(180, 190, 205, 0.8);
                    border-radius: 12px;
                    padding: 10px 12px;
                }
                QLineEdit:focus, QDateTimeEdit:focus {
                    border: 1px solid rgba(91, 165, 255, 0.95);
                }
                QPushButton {
                    color: #132033;
                    background-color: rgba(255, 255, 255, 210);
                    border: 1px solid rgba(180, 190, 205, 0.85);
                    border-radius: 12px;
                    padding: 8px 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 235);
                }
                """
            )

    def get_company_data(self) -> tuple[str, datetime] | None:
        if self.exec() != QDialog.DialogCode.Accepted:
            return None

        name = self.name_edit.text().strip()
        dt = self.datetime_edit.dateTime().toPyDateTime()
        return name, dt

    def accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "입력 필요", "회사명을 입력해야 합니다.")
            return
        super().accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.companies: list[CompanyEntry] = []
        self.company_widgets: dict[str, CompanyCard] = {}
        self.expanded = False
        self.is_dark_mode = True
        self.always_on_top = True
        self.drag_offset: QPoint | None = None
        self.resize_edge: str | None = None
        self.resize_start_geometry: QRect | None = None
        self.resize_start_global: QPoint | None = None
        self._loading_detail = False
        self._positioned_once = False
        self.mini_width = MINI_WIDTH
        self.mini_height = MINI_HEIGHT
        self.expanded_width = EXPANDED_WIDTH
        self.expanded_height = EXPANDED_HEIGHT

        self.setWindowTitle("Company Tracker")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(MINI_WIDTH, MINI_HEIGHT)

        self.build_ui()
        self.load_data()
        self.refresh_list()
        self.apply_mode()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_countdowns)
        self.timer.start(1000)

    def build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)
        self.outer_layout = outer_layout

        self.container = QFrame()
        self.container.setObjectName("container")
        outer_layout.addWidget(self.container)

        root_layout = QVBoxLayout(self.container)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)
        self.root_layout = root_layout

        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        self.title_bar = title_bar
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        self.title_layout = title_layout

        self.handle_label = QLabel("COMPANY TRACKER")
        self.handle_label.setObjectName("handleLabel")

        self.pin_check = QCheckBox("항상 위")
        self.pin_check.setChecked(True)
        self.pin_check.toggled.connect(self.toggle_always_on_top)

        self.theme_button = QPushButton("다크 모드")
        self.theme_button.clicked.connect(self.toggle_theme)

        self.add_button = QPushButton("+ 추가")
        self.add_button.clicked.connect(self.add_company)

        self.sort_button = QPushButton("임박순 정렬")
        self.sort_button.clicked.connect(self.sort_by_dday)

        self.expand_button = QPushButton("확장")
        self.expand_button.clicked.connect(self.toggle_expand)

        self.close_button = QPushButton("닫기")
        self.close_button.clicked.connect(self.close)

        title_layout.addWidget(self.handle_label, 1)
        title_layout.addWidget(self.pin_check)
        title_layout.addWidget(self.theme_button)
        title_layout.addWidget(self.add_button)
        title_layout.addWidget(self.sort_button)
        title_layout.addWidget(self.expand_button)
        title_layout.addWidget(self.close_button)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)

        self.list_widget = CompanyListWidget()
        self.list_widget.setObjectName("companyList")
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_widget.orderChanged.connect(self.sync_companies_from_list_order)

        self.detail_panel = QFrame()
        self.detail_panel.setObjectName("detailPanel")
        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setContentsMargins(14, 14, 14, 14)
        detail_layout.setSpacing(10)

        detail_title = QLabel("상세 정보")
        detail_title.setObjectName("panelTitle")

        self.detail_name = QLineEdit()
        self.detail_name.setPlaceholderText("회사명")
        self.detail_name.editingFinished.connect(self.save_detail_changes)

        self.detail_datetime = QDateTimeEdit()
        self.detail_datetime.setCalendarPopup(True)
        self.detail_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.detail_datetime.dateTimeChanged.connect(self.save_detail_changes)

        self.detail_link = QLineEdit()
        self.detail_link.setPlaceholderText("채용 공고 / 화상 면접 링크")
        self.detail_link.editingFinished.connect(self.save_detail_changes)

        self.detail_info = QPlainTextEdit()
        self.detail_info.setPlaceholderText("면접 장소, 준비물, 면접관 정보 등을 적어두세요.")
        self.detail_info.textChanged.connect(self.save_detail_changes)

        self.detail_memo = QPlainTextEdit()
        self.detail_memo.setPlaceholderText("자유 메모")
        self.detail_memo.textChanged.connect(self.save_detail_changes)

        self.delete_button = QPushButton("선택 회사 삭제")
        self.delete_button.clicked.connect(self.delete_selected_company)

        detail_layout.addWidget(detail_title)
        detail_layout.addWidget(QLabel("회사명"))
        detail_layout.addWidget(self.detail_name)
        detail_layout.addWidget(QLabel("면접 일시"))
        detail_layout.addWidget(self.detail_datetime)
        detail_layout.addWidget(QLabel("링크"))
        detail_layout.addWidget(self.detail_link)
        detail_layout.addWidget(QLabel("면접 정보"))
        detail_layout.addWidget(self.detail_info, 1)
        detail_layout.addWidget(QLabel("메모"))
        detail_layout.addWidget(self.detail_memo, 1)
        detail_layout.addWidget(self.delete_button)

        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.detail_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        root_layout.addWidget(title_bar)
        root_layout.addWidget(self.splitter, 1)

        self.apply_styles()
        self.apply_effects()
        self.apply_mode()

    def apply_styles(self):
        if self.is_dark_mode:
            stylesheet = """
            QWidget {
                color: #eef3fb;
                font-size: 13px;
            }
            #container {
                background-color: rgba(12, 17, 28, 226);
                border: 1px solid rgba(255, 255, 255, 34);
                border-radius: 28px;
            }
            #titleBar {
                background: transparent;
            }
            #handleLabel {
                color: rgba(243, 247, 255, 0.94);
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.8px;
            }
            QPushButton, QCheckBox, QLineEdit, QDateTimeEdit, QPlainTextEdit, QListWidget {
                border-radius: 16px;
            }
            QPushButton {
                color: #f5f8ff;
                background-color: rgba(255, 255, 255, 14);
                border: 1px solid rgba(255, 255, 255, 32);
                padding: 9px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 20);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 26);
            }
            QCheckBox {
                color: #edf4ff;
                padding: 7px 10px;
                background-color: rgba(255, 255, 255, 12);
                border: 1px solid rgba(255, 255, 255, 30);
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.28);
                background-color: rgba(255, 255, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(98, 171, 255, 0.95);
                border: 1px solid rgba(98, 171, 255, 1.0);
            }
            QListWidget {
                background-color: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 28);
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                margin: 4px 0;
                border-radius: 18px;
            }
            QListWidget::item:selected {
                background-color: rgba(100, 167, 255, 54);
            }
            #detailPanel {
                background-color: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 28);
                border-radius: 24px;
            }
            #panelTitle {
                color: #f4f7fd;
                font-size: 16px;
                font-weight: 700;
            }
            QLabel {
                color: rgba(234, 241, 251, 0.88);
            }
            QLineEdit, QDateTimeEdit, QPlainTextEdit {
                color: #f4f7fd;
                background-color: rgba(255, 255, 255, 12);
                border: 1px solid rgba(255, 255, 255, 28);
                padding: 11px 13px;
                selection-background-color: rgba(94, 166, 255, 0.32);
            }
            QLineEdit:focus, QDateTimeEdit:focus, QPlainTextEdit:focus {
                border: 1px solid rgba(91, 165, 255, 0.95);
                background-color: rgba(255, 255, 255, 18);
            }
            #cardTitle {
                color: #f4f7fd;
                font-size: 15px;
                font-weight: 700;
            }
            #cardCountdown {
                color: #8fc6ff;
                font-size: 14px;
                font-weight: 700;
            }
            #cardWhen {
                color: rgba(230, 238, 248, 0.62);
            }
            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                margin: 6px 2px 6px 0;
            }
            QScrollBar::handle:vertical {
                min-height: 28px;
                border-radius: 5px;
                background: rgba(196, 208, 225, 0.2);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QSplitter::handle {
                background: transparent;
            }
            """
        else:
            stylesheet = """
            QWidget {
                color: #f6f7fb;
                font-size: 13px;
            }
            #container {
                background-color: rgba(232, 238, 247, 210);
                border: 1px solid rgba(255, 255, 255, 155);
                border-radius: 28px;
            }
            #titleBar {
                background: transparent;
            }
            #handleLabel {
                color: rgba(20, 28, 43, 0.88);
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.8px;
            }
            QPushButton, QCheckBox, QLineEdit, QDateTimeEdit, QPlainTextEdit, QListWidget {
                border-radius: 16px;
            }
            QPushButton {
                color: #132033;
                background-color: rgba(255, 255, 255, 185);
                border: 1px solid rgba(202, 212, 226, 0.95);
                padding: 9px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 215);
            }
            QPushButton:pressed {
                background-color: rgba(220, 229, 241, 230);
            }
            QCheckBox {
                color: #203049;
                padding: 7px 10px;
                background-color: rgba(255, 255, 255, 170);
                border: 1px solid rgba(202, 212, 226, 0.95);
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid rgba(84, 99, 122, 0.25);
                background-color: rgba(255, 255, 255, 0.72);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(92, 168, 255, 0.95);
                border: 1px solid rgba(92, 168, 255, 1.0);
            }
            QListWidget {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(205, 214, 228, 0.92);
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                margin: 4px 0;
                border-radius: 18px;
            }
            QListWidget::item:selected {
                background-color: rgba(136, 193, 255, 64);
            }
            #detailPanel {
                background-color: rgba(255, 255, 255, 155);
                border: 1px solid rgba(205, 214, 228, 0.92);
                border-radius: 24px;
            }
            #panelTitle {
                color: #19263a;
                font-size: 16px;
                font-weight: 700;
            }
            QLabel {
                color: rgba(24, 36, 54, 0.88);
            }
            QLineEdit, QDateTimeEdit, QPlainTextEdit {
                color: #132033;
                background-color: rgba(255, 255, 255, 225);
                border: 1px solid rgba(194, 205, 220, 0.95);
                padding: 11px 13px;
                selection-background-color: rgba(94, 166, 255, 0.28);
            }
            QLineEdit:focus, QDateTimeEdit:focus, QPlainTextEdit:focus {
                border: 1px solid rgba(91, 165, 255, 0.9);
                background-color: rgba(255, 255, 255, 240);
            }
            #cardTitle {
                color: #162235;
                font-size: 15px;
                font-weight: 700;
            }
            #cardCountdown {
                color: #2377d8;
                font-size: 14px;
                font-weight: 700;
            }
            #cardWhen {
                color: rgba(22, 34, 53, 0.58);
            }
            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                margin: 6px 2px 6px 0;
            }
            QScrollBar::handle:vertical {
                min-height: 28px;
                border-radius: 5px;
                background: rgba(84, 101, 124, 0.22);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QSplitter::handle {
                background: transparent;
            }
            """
        self.setStyleSheet(stylesheet)
        self.theme_button.setText("라이트 모드" if self.is_dark_mode else "다크 모드")

    def apply_effects(self):
        container_shadow = QGraphicsDropShadowEffect(self)
        container_shadow.setBlurRadius(42)
        container_shadow.setOffset(0, 18)
        container_shadow.setColor(QColor(8, 13, 22, 90) if self.is_dark_mode else QColor(27, 44, 74, 70))
        self.container.setGraphicsEffect(container_shadow)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._positioned_once:
            self.position_top_right()
            self._positioned_once = True

    def position_top_right(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        available = screen.availableGeometry()
        x = available.right() - self.width() - SCREEN_MARGIN
        y = available.top() + SCREEN_MARGIN
        self.move(x, y)

    def apply_mode(self):
        current_top_right = self.geometry().topRight()

        if self.expanded:
            self.outer_layout.setContentsMargins(12, 12, 12, 12)
            self.root_layout.setContentsMargins(16, 16, 16, 16)
            self.root_layout.setSpacing(12)
            self.title_layout.setSpacing(8)

            self.title_bar.setVisible(True)
            self.splitter.setVisible(True)
            self.detail_panel.setVisible(True)
            self.pin_check.setVisible(True)
            self.theme_button.setVisible(True)
            self.add_button.setVisible(True)
            self.sort_button.setVisible(True)
            self.close_button.setVisible(True)
            self.handle_label.setVisible(True)

            self.expand_button.setText("축소")
            self.expand_button.setMaximumWidth(88)
            self.expand_button.setMinimumSize(0, 0)

            self.setMinimumSize(520, 420)
            self.setMaximumSize(16777215, 16777215)
            self.resize(self.expanded_width, self.expanded_height)
            self.splitter.setSizes([300, 540])
        else:
            self.outer_layout.setContentsMargins(10, 10, 10, 10)
            self.root_layout.setContentsMargins(14, 14, 14, 14)
            self.root_layout.setSpacing(10)
            self.title_layout.setSpacing(8)

            self.handle_label.setVisible(True)
            self.pin_check.setVisible(False)
            self.theme_button.setVisible(False)
            self.add_button.setVisible(True)
            self.sort_button.setVisible(False)
            self.close_button.setVisible(False)
            self.detail_panel.setVisible(False)
            self.splitter.setVisible(True)
            self.title_bar.setVisible(True)

            self.expand_button.setText("확장")
            self.add_button.setText("+")
            self.add_button.setMaximumWidth(42)
            self.expand_button.setMaximumWidth(62)
            self.expand_button.setMinimumSize(0, 0)

            mini_height = self.calculate_mini_height()
            self.setFixedSize(MINI_WIDTH, mini_height)

        self.move(current_top_right.x() - self.width(), self.y())

    def calculate_mini_height(self) -> int:
        visible_items = max(1, self.list_widget.count())
        return min(MINI_MAX_HEIGHT, MINI_BASE_HEIGHT + (visible_items * MINI_ITEM_HEIGHT))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.resize_edge = edge
                self.resize_start_geometry = self.geometry()
                self.resize_start_global = event.globalPosition().toPoint()
                event.accept()
                return
        if event.button() == Qt.MouseButton.LeftButton and self.is_in_drag_handle(event.pos()):
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resize_edge and self.resize_start_geometry and self.resize_start_global:
            self.perform_resize(event.globalPosition().toPoint())
            event.accept()
            return
        if self.drag_offset and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()
            return
        self.update_cursor(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.resize_edge = None
        self.resize_start_geometry = None
        self.resize_start_global = None
        self.update_cursor(event.pos())
        super().mouseReleaseEvent(event)

    def is_in_drag_handle(self, pos: QPoint) -> bool:
        title_height = self.handle_label.parentWidget().geometry().height() + 12
        return pos.y() <= title_height

    def toggle_expand(self):
        self.expanded = not self.expanded
        self.apply_mode()
        if self.expanded and self.list_widget.currentItem():
            self.load_selected_company_into_detail()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_styles()
        self.apply_effects()

    def toggle_always_on_top(self, checked: bool):
        self.always_on_top = checked
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def add_company(self):
        dialog = AddCompanyDialog(self)
        result = dialog.get_company_data()
        if not result:
            return

        name, interview_dt = result
        company = CompanyEntry(
            id=str(uuid.uuid4()),
            name=name,
            interview_at=interview_dt.isoformat(timespec="minutes"),
        )
        self.companies.append(company)
        self.add_company_item(company)
        self.save_data()
        self.list_widget.setCurrentRow(self.list_widget.count() - 1)
        if not self.expanded:
            self.expanded = True
            self.apply_mode()

    def get_resize_edge(self, pos: QPoint) -> str | None:
        if pos.x() <= RESIZE_MARGIN:
            return "left"
        if pos.x() >= self.width() - RESIZE_MARGIN:
            return "right"
        return None

    def update_cursor(self, pos: QPoint):
        edge = self.get_resize_edge(pos)
        if edge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif not self.drag_offset:
            self.unsetCursor()

    def perform_resize(self, current_global: QPoint):
        if not self.resize_edge or not self.resize_start_geometry or not self.resize_start_global:
            return

        delta_x = current_global.x() - self.resize_start_global.x()
        start_geometry = self.resize_start_geometry
        min_width = self.minimum_target_width()

        if self.resize_edge == "right":
            new_width = max(min_width, min(MAX_RESIZE_WIDTH, start_geometry.width() + delta_x))
            self.setGeometry(start_geometry.x(), start_geometry.y(), new_width, start_geometry.height())
        else:
            new_width = max(min_width, min(MAX_RESIZE_WIDTH, start_geometry.width() - delta_x))
            new_x = start_geometry.right() - new_width + 1
            self.setGeometry(new_x, start_geometry.y(), new_width, start_geometry.height())

        if self.expanded:
            self.expanded_width = self.width()
        else:
            self.mini_width = self.width()

    def minimum_target_width(self) -> int:
        return 520 if self.expanded else MIN_RESIZE_WIDTH

    def add_company_item(self, company: CompanyEntry):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, company.id)
        item.setSizeHint(QSize(0, 82))

        card = CompanyCard(company)
        self.company_widgets[company.id] = card

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, card)

    def refresh_list(self):
        self.list_widget.clear()
        self.company_widgets.clear()
        for company in self.companies:
            self.add_company_item(company)
        if self.list_widget.count() > 0 and self.expanded:
            self.list_widget.setCurrentRow(0)
        else:
            self.clear_detail_panel()

    def refresh_countdowns(self):
        for company in self.companies:
            card = self.company_widgets.get(company.id)
            if card:
                card.update_content(company)

    def get_selected_company(self) -> CompanyEntry | None:
        item = self.list_widget.currentItem()
        if not item:
            return None
        company_id = item.data(Qt.ItemDataRole.UserRole)
        return next((company for company in self.companies if company.id == company_id), None)

    def on_selection_changed(self):
        company = self.get_selected_company()
        if not company:
            self.clear_detail_panel()
            return
        if not self.expanded:
            self.expanded = True
            self.apply_mode()
        self.load_selected_company_into_detail()

    def load_selected_company_into_detail(self):
        company = self.get_selected_company()
        self._loading_detail = True
        if not company:
            self.clear_detail_panel()
            self._loading_detail = False
            return

        self.detail_name.setText(company.name)
        self.detail_datetime.setDateTime(QDateTime.fromString(company.interview_at, Qt.DateFormat.ISODate))
        self.detail_link.setText(company.link)
        self.detail_info.setPlainText(company.interview_info)
        self.detail_memo.setPlainText(company.memo)
        self._loading_detail = False

    def clear_detail_panel(self):
        self._loading_detail = True
        self.detail_name.clear()
        self.detail_datetime.setDateTime(QDateTime.currentDateTime())
        self.detail_link.clear()
        self.detail_info.clear()
        self.detail_memo.clear()
        self._loading_detail = False

    def save_detail_changes(self):
        if self._loading_detail:
            return

        company = self.get_selected_company()
        if not company:
            return

        company.name = self.detail_name.text().strip() or company.name
        company.interview_at = self.detail_datetime.dateTime().toPyDateTime().isoformat(timespec="minutes")
        company.link = self.detail_link.text().strip()
        company.interview_info = self.detail_info.toPlainText()
        company.memo = self.detail_memo.toPlainText()

        card = self.company_widgets.get(company.id)
        if card:
            card.update_content(company)
        self.save_data()

    def delete_selected_company(self):
        company = self.get_selected_company()
        if not company:
            return

        answer = QMessageBox.question(
            self,
            "삭제 확인",
            f"'{company.name}' 항목을 삭제하시겠습니까?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.companies = [entry for entry in self.companies if entry.id != company.id]
        self.refresh_list()
        self.save_data()

    def sort_by_dday(self):
        self.companies.sort(key=lambda company: company.interview_datetime)
        self.refresh_list()
        self.save_data()

    def sync_companies_from_list_order(self):
        company_ids = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            company_ids.append(item.data(Qt.ItemDataRole.UserRole))

        company_map = {company.id: company for company in self.companies}
        self.companies = [company_map[company_id] for company_id in company_ids if company_id in company_map]
        self.save_data()

    def load_data(self):
        if not DATA_FILE.exists():
            return
        try:
            raw_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            self.companies = [CompanyEntry(**item) for item in raw_data]
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            QMessageBox.warning(self, "로드 실패", "저장된 데이터를 읽지 못해 빈 상태로 시작합니다.")
            self.companies = []

    def save_data(self):
        try:
            DATA_FILE.write_text(
                json.dumps([asdict(company) for company in self.companies], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            QMessageBox.warning(self, "저장 실패", "데이터 저장에 실패했습니다.")


def format_countdown(target: datetime) -> str:
    now = datetime.now()
    delta = target - now
    total_seconds = int(delta.total_seconds())
    future = total_seconds >= 0
    abs_seconds = abs(total_seconds)

    days, remainder = divmod(abs_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    prefix = "D-" if future else "D+"
    return f"{prefix}{days} {hours:02}:{minutes:02}:{seconds:02}"


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Company Tracker")
    app.setFont(QFont("SF Pro Display", 10))
    app.setStyle("Fusion")
    icon_file = get_icon_file()
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(229, 236, 246))
    app.setPalette(palette)

    window = MainWindow()
    if icon_file.exists():
        window.setWindowIcon(QIcon(str(icon_file)))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
