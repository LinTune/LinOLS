import time
from PyQt6.QtCore import QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QTableView, QHeaderView, QGridLayout, QPushButton, \
    QLabel, QLineEdit, QSizePolicy, QSpacerItem, QTableWidget, QListWidget, QVBoxLayout, QMenu, QMessageBox
from PyQt6.QtGui import QAction, QGuiApplication, QColor, QKeyEvent, QKeySequence, QShortcut, QFont, QIcon
from PyQt6.QtCore import Qt, QPoint
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os

class LinOLS(QMainWindow):
    def __init__(self):
        super().__init__()

        from text_view import TextView
        from Module_2D import Mode2D
        from text_addons import TextAddons
        from Module_3D import Mode3D
        from maps import Maps_Utility
        from potential_maps.potential_maps import Potential_maps_manager
        from canva_3d.canva_3d_window import TkWindowManager
        from ui_components.toolbar import ToolbarWidget

        self.setWindowTitle("LinOLS")

        self.logo_icon = QIcon("icon.ico")

        self.setWindowIcon(self.logo_icon)

        self.setMinimumWidth(1300)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        window_width = 1500
        window_height = 600

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(x, y, window_width, window_height)

        self.text_view_ = TextView(self)
        self.mode2d = Mode2D(self)
        self.text_addons = TextAddons(self)
        self.mode3d = Mode3D(self)
        self.maps = Maps_Utility(self)
        self.potential_maps_manager = Potential_maps_manager(self)
        self.tk_win_manager = TkWindowManager(self)
        self.toolbar_widget = ToolbarWidget(self)

        '''General variables'''
        self.file_path = "" # file path of the loaded file
        self.last_file_name = ""  # last used file name for saving the file
        self.columns = 20 # num of columns
        self.num_rows = 55 # num of rows for 2d
        self.unpacked = [] # all original numbers
        self.low_high = True  # low_high or high_low
        self.current_values = []  # current values in text and 2d view

        '''Text view variables'''
        self.return_text = False # used for returning to previous value
        self.tab1_selected = True # true when tab1 is selected

        '''2d variables'''
        self.current_frame = 0 # current 2d frame
        self.percentage_num = 0 # percentage number in 2d
        self.display_sel = False # flag to control whether selection should be displayed in 2d
        self.sel_start = 0 # start of the selection
        self.sel_end = 0 # end of selection
        self.red_line = None  # a red line in 2d
        self.num_rows = 55 # number of rows displayed in 2d
        self.sync_2d_scroll = False # sync 2d to text
        self.disable_2d_canvas = True # disable drawing canvas when not in 2d tab

        '''Find dialog variables'''
        self.found_valuesx_values = [] # all found values
        self.found_values_counter = 0 # how many values where found

        '''Difference dialog variables'''
        self.differences = [] # all differences
        self.differences_color = [] # color of all differences
        self.ori_values = [] # all ori values for differences
        self.index_differences = [] # indexes of all differences

        '''Shift variables'''
        self.start_time = 0 # start time for shifting values
        self.values = [] # values for shift in text view
        self.shift_count = 0 # count of shift
        self.end_time = 0 # end time for shifting

        '''Maps variables'''
        self.map_list_counter = 0  # number of maps
        self.start_index_maps = []  # start indexes for created/imported maps
        self.end_index_maps = []  # end indexes for created/imported maps
        self.maps_names = []  # all map names for created/imported maps
        self.signed_values = False  # 3d signed values
        self.map_decimal = False  # do map values in 3d have decimal numbers
        self.x_axis_decimal = False  # do x-axis values have a decimal numbers
        self.y_axis_decimal = False  # do y-axis values have a decimal numbers

        '''3D variables'''
        self.num_rows_3d = 15
        self.num_columns_3d = 20
        self.column_width_3d = 55
        self.map_opened = False

        self.original = []
        self.original_x = []
        self.original_y = []

        for i in range(self.num_rows_3d):
            row = []
            self.original_y.append(i + 1)
            for x in range(self.num_columns_3d):
                row.append(0)
            self.original.append(row)

        for i in range(self.num_columns_3d):
            self.original_x.append(i + 1)

        self.x_values = []  # current 3d x-axis values
        self.y_values = []  # current 3d y-axis values
        self.map_values = []  # current 3d map values

        self.new_width = 0  # new width of entry boxes in 3d

        self.focused_3d_tab = False

        '''Potential maps variables'''
        self.potential_maps_start = [] # all potential maps start indexes
        self.potential_maps_end = [] # all potential maps end indexes
        self.potential_maps_names = [] # all potential maps names

        self.potential_map_added = False # for checking if potential map has been added successfully
        self.potential_map_index = None

        '''Custom Dialogs'''
        self.dialog_terminate = True

        self.setStyleSheet("background-color: #333; color: white;")

        self.setup_ui()

    def setup_ui(self):
        self.create_menu_bar()

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }

            QTabBar::tab {
                background: #343434;
                color: white;
                border: 1px solid #444;
                border-radius: 2px;
                padding: 2px;
                margin-right: 2px;
                min-width: 40px;
            }

            QTabBar::tab:selected {
                background: #3c3c3c;
                border: 1px solid #666;
            }

            QTabBar::tab:hover {
                background: #404040;
            }
        """)

        self.tabs.currentChanged.connect(self.text_addons.on_tab_changed)

        self.tab1 = QWidget()
        self.tab1.setStyleSheet("border: 0;")
        self.tab2 = QWidget()
        self.tab2.setStyleSheet("border: 0;")
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tabs.addTab(self.tab1, "Text")
        self.tabs.addTab(self.tab2, "2D")
        self.tabs.addTab(self.tab3, "3D")
        self.tabs.addTab(self.tab4, "Maps")

        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab4()

        self.create_shortcut(self.tab1, "Ctrl+F")
        self.create_shortcut(self.tab2, "Ctrl+F")

        self.create_shortcut(self.tab1, "Ctrl+G")
        self.create_shortcut(self.tab2, "Ctrl+G")

        self.create_shortcut(self.tab1, "Shift+5")
        self.create_shortcut(self.tab3, "Shift+5")

        self.create_shortcut(self.tab1, "w")
        self.create_shortcut(self.tab1, "m")
        self.create_shortcut(self.tab1, "Ctrl+Left")
        self.create_shortcut(self.tab1, "Ctrl+Right")

        self.create_shortcut(self.tab1, "k")

        self.create_shortcut(self.tab1, "n")
        self.create_shortcut(self.tab1, "v")
        self.create_shortcut(self.tab1, "Ctrl+U")
        self.create_shortcut(self.tab1, "e")
        self.create_shortcut(self.tab1, "l")

        self.create_shortcut(self.tab1, "Ctrl+Z")
        self.create_shortcut(self.tab1, "Ctrl+Y")

        self.create_shortcut(self.tab1, "Ctrl+C")
        self.create_shortcut(self.tab1, "Ctrl+V")

        self.create_shortcut(self.tab1, "Ctrl+S")

        self.create_shortcut(self.tab3, "Ctrl+C")
        self.create_shortcut(self.tab3, "Ctrl+V")

        self.create_shortcut(self.tab3, "Ctrl+Shift+C")
        self.create_shortcut(self.tab3, "Ctrl+Shift+V")

        self.create_shortcut(self.tab3, "Alt+Return")

        self.create_shortcut(self.tab3, "Ctrl+R")

        self.clean_up()

    def create_shortcut(self, tab, key_sequence):
        shortcut = QShortcut(QKeySequence(key_sequence), tab)
        shortcut.activated.connect(lambda: self.on_shortcut_activated(key_sequence, tab))

    def on_shortcut_activated(self, key_sequence, tab):
        if key_sequence == "Ctrl+F":
            self.text_addons.open_find_dialog()
        elif key_sequence == "Ctrl+G":
            self.text_addons.open_hex_address_dialog()
        elif key_sequence == "Shift+5":
            if tab == self.tab1:
                self.text_addons.open_value_dialog()
            elif tab == self.tab3:
                self.maps.value_changer_dialog()
        elif key_sequence == "w":
            self.text_addons.adjust_columns("-")
        elif key_sequence == "m":
            self.text_addons.adjust_columns("+")
        elif key_sequence == "k":
            self.maps.add_map()
        elif key_sequence == "n":
            self.mode2d.value_changes_skipping(True)
        elif key_sequence == "v":
            self.mode2d.value_changes_skipping(False)
        elif key_sequence == "Ctrl+U":
            self.text_addons.open_difference_dialog()
        elif key_sequence == "e":
            self.mode2d.first_last_changed_value(True)
        elif key_sequence == "l":
            self.mode2d.first_last_changed_value(False)
        elif key_sequence == "Ctrl+Z":
            if tab == self.tab1:
                self.model.undo_changes()
        elif key_sequence == "Ctrl+Y":
            if tab == self.tab1:
                self.model.redo_changes()
        elif key_sequence == "Ctrl+C":
            if tab == self.tab1:
                self.text_addons.copy_values(False)
            elif tab == self.tab3:
                self.mode3d.copy_selected_3d()
        elif key_sequence == "Ctrl+V":
            if tab == self.tab1:
                self.text_addons.paste_values()
            elif tab == self.tab3:
                self.mode3d.paste_selected()
        elif key_sequence == "Ctrl+Shift+C":
            self.mode3d.copy_map()
        elif key_sequence == "Ctrl+Shift+V":
            self.mode3d.paste_map()
        elif key_sequence == "Alt+Return":
            self.maps.map_properties_dialog("map")
        elif key_sequence == "Ctrl+R":
            self.tk_win_manager.open_tkinter_window()
        elif key_sequence == "Ctrl+Left":
            self.text_addons.shift_values("+")
        elif key_sequence == "Ctrl+Right":
            self.text_addons.shift_values("-")
        elif key_sequence == "Ctrl+S":
            self.text_view_.save_file()

    def setup_bottom_row(self, main_layout):
        text_layout = QGridLayout()
        text_layout.setContentsMargins(0, 0, 0, 5)
        text_layout.setHorizontalSpacing(0)
        text_layout.setVerticalSpacing(0)

        self.sel_label = QLabel("Selected: 0", self)
        self.sel_label.setStyleSheet("""
                    color: white;
                    font-family: 'Roboto', sans-serif;
                    font-size: 12px;
                    font-weight: 650;
                    padding-left: 10px;
                    padding-right: 10px;
                """)

        self.value_label = QLabel("Ori: 00000", self)
        self.value_label.setStyleSheet("""
                    color: white;
                    font-family: 'Roboto', sans-serif;
                    font-size: 12px;
                    font-weight: 650;
                    padding-left: 10px;
                """)

        self.value_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        svg_arrow_right = """
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 40 40" stroke-width="4" stroke="white" class="size-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 18h20m0 0l-6 6m6-6l-6-6" />
                    </svg>
                """

        icon = self.toolbar_widget.svg_to_icon(svg_arrow_right)

        arrow_label = QLabel()
        arrow_label.setPixmap(icon.pixmap(16, 16))

        self.difference_label = QLabel("00000  (0.00%)", self)
        self.difference_label.setStyleSheet("""
                    color: white;
                    font-family: 'Roboto', sans-serif;
                    font-size: 12px;
                    font-weight: 650;
                    padding-right: 10px;
                """)

        self.difference_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.entry_shift = QLabel(f"Shift: {self.shift_count:02}", self)
        self.entry_shift.setStyleSheet("""
                    font-family: 'Roboto';
                    font-size: 12px;
                    font-weight: 650;
                    color: white;
                    padding-left: 10px;
                    padding-right: 5px;
                """)

        self.entry_shift.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.entry_col = QLabel(f"Columns: {self.columns:02}", self)
        self.entry_col.setStyleSheet("""
                    font-family: 'Roboto';
                    font-size: 12px;
                    font-weight: 650;
                    color: white;
                    padding-right: 10px;        
                """)

        self.entry_col.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        text_layout.addWidget(self.sel_label, 0, 0)
        text_layout.addWidget(self.value_label, 0, 1)
        text_layout.addWidget(arrow_label, 0, 2)
        text_layout.addWidget(self.difference_label, 0, 3)
        text_layout.addWidget(self.entry_shift, 0, 4)
        text_layout.addWidget(self.entry_col, 0, 5)

        main_layout.addLayout(text_layout, 2, 0, 1, 2)

        text_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

    def setup_tab1(self):
        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setHorizontalSpacing(0)
        main_layout.setVerticalSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self.toolbar_widget, 0, 0)

        self.table_view = CustomTableView(self)
        main_layout.addWidget(self.table_view, 1, 0)

        font = QFont("Cantarell", 10)
        self.table_view.setFont(font)

        self.table_view.setStyleSheet("""
            QTableView {
                background-color: #333;
                padding-left: 10px;
                padding-right: 10px;
            }
            QTableView::item:selected {
                background-color: #5b9bf8;
                color: white;
            }
            QHeaderView::section {
                background-color: #363636;
                color: white;
            } 
        """)

        self.model = QTableModel(self.unpacked, self)
        self.table_view.setModel(self.model)

        self.table_view.horizontalHeader().setVisible(False)

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.table_view.verticalHeader().setFixedWidth(60) # change width of x-axis

        self.setup_bottom_row(main_layout)

        self.tab1.setLayout(main_layout)

    def setup_tab2(self):
        main_layout = QGridLayout()

        left_grid_layout = QGridLayout()

        left_grid_layout.setContentsMargins(0, 0, 0, 0)
        left_grid_layout.setHorizontalSpacing(10)
        left_grid_layout.setVerticalSpacing(10)

        mid_grid_layout = QGridLayout()

        mid_grid_layout.setContentsMargins(0, 0, 0, 0)
        mid_grid_layout.setHorizontalSpacing(10)
        mid_grid_layout.setVerticalSpacing(10)

        right_grid_layout = QGridLayout()

        mid_grid_layout.setContentsMargins(0, 0, 0, 0)
        mid_grid_layout.setHorizontalSpacing(10)
        mid_grid_layout.setVerticalSpacing(10)

        button_style = """
        QPushButton {
            background-color: #444;
            color: white;
            font-family: 'Roboto', sans-serif;
            font-size: 11px;
            font-weight: 650;
            padding: 6px;
            border: none;
            border-radius: 5px;
            min-width: 50px;
        }
        QPushButton:hover {
            background-color: #666;
            color: #fff;
        }
        QPushButton:pressed{
            background-color: #444;
            color: white;
        }
        """

        outside_button_style = """
        QPushButton {
            background-color: #444;
            color: white;
            font-family: 'Roboto', sans-serif;
            font-size: 11px;
            font-weight: 650;
            padding: 6px;                    
            border: none;
            border-radius: 5px;
            min-width: 75px;
        }
        QPushButton:hover {
            background-color: #666;
            color: #fff;
        }
        QPushButton:pressed{
            background-color: #444;
            color: white;
        }
        """

        operation_style = """
        QPushButton {
            background-color: #444;
            color: white;
            font-family: 'Roboto', sans-serif;
            font-size: 12px;
            font-weight: 650;
            padding: 6px;                    
            border: none;
            border-radius: 5px;
            min-width: 10px;
        }
        QPushButton:hover {
            background-color: #666;
            color: #fff;
        }
        QPushButton:pressed{
            background-color: #444;
            color: white;
        }
        """

        btn_left = QPushButton("<", self.tab2)
        btn_left.setStyleSheet(button_style)
        btn_left.clicked.connect(self.mode2d.prev_page)

        btn_fast_left = QPushButton("<<", self.tab2)
        btn_fast_left.setStyleSheet(button_style)
        btn_fast_left.clicked.connect(lambda: self.mode2d.fast_movement("left"))

        btn_1 = QPushButton("Find Dialog", self.tab2)
        btn_1.setStyleSheet(outside_button_style)
        btn_1.clicked.connect(self.text_addons.open_find_dialog)

        btn_percentage_1 = QPushButton("%", self.tab2)
        btn_percentage_1.setStyleSheet(operation_style)
        btn_percentage_1.clicked.connect(lambda: self.mode2d.percentage(True, ""))
        btn_percentage_1.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        btn_minus = QPushButton("-", self.tab2)
        btn_minus.setStyleSheet(operation_style)
        btn_minus.clicked.connect(lambda: self.mode2d.percentage(False, "-"))
        btn_minus.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.entry_percentage = QLineEdit("00", self.tab2)
        self.entry_percentage.setStyleSheet("""
            border: 2px;
            border-radius: 6px;
            font-family: 'Roboto';
            font-size: 12px;
            font-weight: 680;
            background-color: #555;
            height: 25px;
            width: 25px;
            color: white;
        """)

        self.entry_percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.entry_percentage.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        btn_plus = QPushButton("+", self.tab2)
        btn_plus.setStyleSheet(operation_style)
        btn_plus.clicked.connect(lambda: self.mode2d.percentage(False, "+"))
        btn_plus.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        btn_percentage_2 = QPushButton("%", self.tab2)
        btn_percentage_2.setStyleSheet(operation_style)
        btn_percentage_2.clicked.connect(lambda: self.mode2d.percentage(True, ""))
        btn_percentage_2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.value_btn_2d = QPushButton("Value: 00000", self.tab2)
        self.value_btn_2d.setStyleSheet(outside_button_style)

        btn_fast_right = QPushButton(">>", self.tab2)
        btn_fast_right.setStyleSheet(button_style)
        btn_fast_right.clicked.connect(lambda: self.mode2d.fast_movement("right"))

        btn_right = QPushButton(">", self.tab2)
        btn_right.setStyleSheet(button_style)
        btn_right.clicked.connect(self.mode2d.next_page)

        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)

        self.fig.patch.set_facecolor('#333')
        self.ax.set_facecolor('#333')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')

        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvas(self.fig)

        self.canvas.setStyleSheet("border: 0;")

        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.canvas.mpl_connect("button_press_event", self.mode2d.on_canvas_click)
        self.canvas.mpl_connect("key_press_event", self.mode2d.on_key_press_2d)

        left_grid_layout.addWidget(btn_left, 0, 0)
        left_grid_layout.addWidget(btn_fast_left, 0, 1)

        mid_grid_layout.addWidget(btn_1, 0, 0)

        spacer = QSpacerItem(25, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        mid_grid_layout.addItem(spacer, 0, 1)

        mid_grid_layout.addWidget(btn_percentage_1, 0, 2)
        mid_grid_layout.addWidget(btn_minus, 0, 3)
        mid_grid_layout.addWidget(self.entry_percentage, 0, 4)
        mid_grid_layout.addWidget(btn_plus, 0, 5)
        mid_grid_layout.addWidget(btn_percentage_2, 0, 6)

        mid_grid_layout.addItem(spacer, 0, 7)

        mid_grid_layout.addWidget(self.value_btn_2d, 0, 8)

        right_grid_layout.addWidget(btn_fast_right, 0, 0)
        right_grid_layout.addWidget(btn_right, 0, 1)


        main_layout.addWidget(self.canvas, 0, 0, 1, 2)
        main_layout.addLayout(left_grid_layout, 1, 0, 1, 2)
        main_layout.addLayout(mid_grid_layout, 1, 0, 1, 2)
        main_layout.addLayout(right_grid_layout, 1, 0, 1, 2)

        left_grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        mid_grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_grid_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.tab2.setLayout(main_layout)

    def setup_tab3(self):
        main_layout = QGridLayout()

        left_grid_layout = QGridLayout()

        left_grid_layout.setContentsMargins(0, 0, 0, 0)
        left_grid_layout.setHorizontalSpacing(10)
        left_grid_layout.setVerticalSpacing(10)

        mid_grid_layout = QGridLayout()

        mid_grid_layout.setContentsMargins(0, 0, 0, 0)
        mid_grid_layout.setHorizontalSpacing(10)
        mid_grid_layout.setVerticalSpacing(10)

        right_grid_layout = QGridLayout()

        mid_grid_layout.setContentsMargins(0, 0, 0, 0)
        mid_grid_layout.setHorizontalSpacing(10)
        mid_grid_layout.setVerticalSpacing(10)

        button_style = """
        QPushButton {
            background-color: #444;
            color: white;
            font-family: 'Roboto', sans-serif;
            font-size: 11px;
            font-weight: 650;
            padding: 6px;
            border: none;
            border-radius: 5px;
            min-width: 65px;
        }
        QPushButton:hover {
            background-color: #666;
            color: #fff;
        }
        QPushButton:pressed{
            background-color: #444;
            color: white;
        }
        """

        btn0 = QPushButton("Copy Map", self)
        btn0.setStyleSheet(button_style)
        btn0.clicked.connect(self.mode3d.copy_map)

        btn1 = QPushButton("Copy Selected", self)
        btn1.setStyleSheet(button_style)
        btn1.clicked.connect(self.mode3d.copy_selected_3d)

        btn4 = QPushButton("Update", self)
        btn4.setStyleSheet(button_style)
        btn4.clicked.connect(self.maps.update_3d_from_text)

        self.diff_btn_3d = QPushButton("Diff: 00000", self)
        self.diff_btn_3d.setStyleSheet(button_style)

        self.diff_btn_per_3d = QPushButton("Diff: 0.00%", self)
        self.diff_btn_per_3d.setStyleSheet(button_style)

        self.ori_val_btn_3d = QPushButton("Ori: 00000", self)
        self.ori_val_btn_3d.setStyleSheet(button_style)

        write_map_btn = QPushButton("Write Map", self)
        write_map_btn.setStyleSheet(button_style)
        write_map_btn.clicked.connect(self.maps.write_map)

        btn12 = QPushButton("Paste Selected", self)
        btn12.setStyleSheet(button_style)
        btn12.clicked.connect(self.mode3d.paste_selected)

        btn13 = QPushButton("Paste Map", self)
        btn13.setStyleSheet(button_style)
        btn13.clicked.connect(self.mode3d.paste_map)

        left_grid_layout.addWidget(btn0, 0, 0)
        left_grid_layout.addWidget(btn1, 0, 1)

        mid_grid_layout.addWidget(btn4, 0, 0)
        mid_grid_layout.addWidget(self.diff_btn_3d, 0, 1)
        mid_grid_layout.addWidget(self.diff_btn_per_3d, 0, 2)
        mid_grid_layout.addWidget(self.ori_val_btn_3d, 0, 3)
        mid_grid_layout.addWidget(write_map_btn, 0, 4)

        right_grid_layout.addWidget(btn12, 0, 0)
        right_grid_layout.addWidget(btn13, 0, 1)

        self.box_layout = CustomTableWidget(self)

        self.box_layout.setRowCount(self.num_rows_3d)
        self.box_layout.setColumnCount(self.num_columns_3d)

        self.box_layout.setStyleSheet("""
            QTableView {
                background-color: #333;
                color: white;
            }
            QTableView::item:selected {
                background-color: #5b9bf8;
                color: white;
            }
            QHeaderView::section {
                background-color: #363636;
                color: white;
            } 
        """)

        font = QFont("Cantarell", 10)
        self.box_layout.setFont(font)

        self.box_layout.itemChanged.connect(self.mode3d.validate_cell_input)
        self.box_layout.itemSelectionChanged.connect(self.mode3d.on_selection_3d)

        self.mode3d.set_default()

        self.box_layout.horizontalHeader().sectionDoubleClicked.connect(self.mode3d.edit_horizontal_header)
        self.box_layout.verticalHeader().sectionDoubleClicked.connect(self.mode3d.edit_vertical_header)

        self.box_layout.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.box_layout.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.box_layout.verticalHeader().setFixedWidth(55)

        main_layout.addWidget(self.box_layout, 0, 0, 1, 2)

        main_layout.addLayout(left_grid_layout, 1, 0, 1, 2)
        main_layout.addLayout(mid_grid_layout, 1, 0, 1, 2)
        main_layout.addLayout(right_grid_layout, 1, 0, 1, 2)

        left_grid_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        mid_grid_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        right_grid_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.tab3.setLayout(main_layout)

    def setup_tab4(self):
        self.map_list = CustomListBox(self)
        self.map_list.setStyleSheet("background-color: #333; color: white; font-size: 10pt;")
        self.map_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.map_list.itemDoubleClicked.connect(self.maps.on_double_click)

        layout = QVBoxLayout(self.tab4)
        layout.addWidget(self.map_list)

        self.tab4.setLayout(layout)


    def create_menu_bar(self):
        menubar = self.menuBar()

        menu_bar_style = ("""
            QMenuBar {
                background-color: #333;
                color: white;
            }
            QMenuBar::item {
                background-color: #333;
                color: white;
                padding: 10px;
            }
            QMenuBar::item:selected {
                background-color: #555;
                color: white;
            }
            QMenuBar::item:pressed {
                background-color: #777;
                color: white;
            }

            QMenu {
                background-color: #333;
                color: white;
            }
            QMenu::item {
                background-color: #333;
                color: white;
            }
            QMenu::item:selected {
                background-color: #555;
                color: white;
            }
            QMenu::item:pressed {
                background-color: #777;
                color: white;
            }
        """)

        menubar.setStyleSheet(menu_bar_style)

        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.text_view_.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save (Ctrl+S)", self)
        save_action.triggered.connect(self.text_view_.save_file)
        file_menu.addAction(save_action)

        options_menu = menubar.addMenu("Options")

        find_action = QAction("Find", self)
        options_menu.addAction(find_action)
        find_action.triggered.connect(self.text_addons.open_find_dialog)

        import_action = QAction("Import", self)
        options_menu.addAction(import_action)
        import_action.triggered.connect(self.text_addons.import_file)

        difference_action = QAction("Difference", self)
        options_menu.addAction(difference_action)
        difference_action.triggered.connect(self.text_addons.open_difference_dialog)

        value_changer_action = QAction("Value Changer", self)
        options_menu.addAction(value_changer_action)
        value_changer_action.triggered.connect(self.text_addons.open_value_dialog)

        find_hex_action = QAction("Find Hex Address", self)
        options_menu.addAction(find_hex_action)
        find_hex_action.triggered.connect(self.text_addons.open_hex_address_dialog)

        restart_map_search = QAction("Restart Map Search", self)
        options_menu.addAction(restart_map_search)
        restart_map_search.triggered.connect(lambda: self.maps.start_potential_map_search(True))

        map_pack_menu = menubar.addMenu("Mappack")

        import_map_pack_action = QAction("Import Mappack", self)
        map_pack_menu.addAction(import_map_pack_action)
        import_map_pack_action.triggered.connect(self.maps.import_map)

        export_map_pack_action = QAction("Export Mappack", self)
        map_pack_menu.addAction(export_map_pack_action)
        export_map_pack_action.triggered.connect(self.maps.export_map)

        sort_map_pack_action = QAction("Sort Mappack", self)
        map_pack_menu.addAction(sort_map_pack_action)
        sort_map_pack_action.triggered.connect(self.maps.sort_maps)

    def clean_up(self):
        file_path = "mappack.mp"
        if os.path.exists(file_path):
            os.remove(file_path)

    def closeEvent(self, event):
        if self.file_path:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle("Save Changes?")
            msg_box.setText("Do you really want to exit without saving?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            response = msg_box.exec()

            if response == QMessageBox.StandardButton.Yes:
                self.exit_app()
            else:
                event.ignore()
        else:
            self.exit_app()

    def exit_app(self):
        self.tk_win_manager.kill_tkinter_window()
        time.sleep(0.001)
        self.clean_up()
        self.close()

class QTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.linols = parent
        self._data = [list(row) for row in data]
        self._vertical_header_labels = []
        self.undo_stack = []
        self.redo_stack = []

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index: QModelIndex, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row()][index.column()]
            return f"{value:05}" if value is not None else ""

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        value = self._data[index.row()][index.column()]

        if role == Qt.ItemDataRole.ForegroundRole:
            color = self.linols.text_addons.highlight_difference(value, index.row(), index.column())
            if color == "blue":
                return QColor(Qt.GlobalColor.blue)
            elif color == "red":
                return QColor(Qt.GlobalColor.red)
            elif color == "default":
                return QColor(Qt.GlobalColor.white)

        if role == Qt.ItemDataRole.BackgroundRole: # highlight user maps
            index = (index.row() * self.linols.columns) + index.column()

            if self.linols.map_list_counter > 0:
                # user creted maps
                for i in range(len(self.linols.start_index_maps)):
                    down_limit = self.linols.start_index_maps[i] + self.linols.shift_count
                    up_limit = self.linols.end_index_maps[i] + self.linols.shift_count
                    if down_limit <= index <= up_limit:
                        return QColor(133, 215, 242, 150) # light blue

            # potential maps
            for i in range(len(self.linols.potential_maps_start)):
                down_limit = self.linols.potential_maps_start[i]
                up_limit = self.linols.potential_maps_end[i]
                if down_limit <= index <= up_limit:
                    return QColor(1, 133, 123, 150) # teal green

    def setData(self, index: QModelIndex, value, role):
        if role == Qt.ItemDataRole.EditRole:
            row, col = index.row(), index.column()
            try:
                new_value = int(value)
                old_value = self._data[row][col]
                if (new_value < 0) or (new_value > 65535):
                    self._data[row][col] = self.linols.text_addons.revert_value(row, col)
                else:
                    self._data[row][col] = new_value
                    self.redraw_canvas_2d(row, col, new_value)
                self.undo_stack.append((row, col, old_value))
                self.redo_stack.clear()
                self.dataChanged.emit(index, index)
            except ValueError:
                return False
        return True

    def redraw_canvas_2d(self, row, col, value):
        self.linols.current_values = list(self.linols.current_values)
        index = (row * self.linols.columns) + col

        self.linols.current_values[index] = value

        self.linols.sync_2d_scroll = True
        self.linols.mode2d.draw_canvas(self.linols)

    def flags(self, index: QModelIndex):
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def set_data(self, data):
        self._data = [list(row) for row in data]
        self.layoutChanged.emit()

    def setVerticalHeaderLabels(self, labels):
        self._vertical_header_labels = labels
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, self.rowCount() - 1)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return self._vertical_header_labels[section] if section < len(self._vertical_header_labels) else ""
        return super().headerData(section, orientation, role)

    def flags(self, index: QModelIndex):
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def get_all_data(self):
        return self._data

    def undo_changes(self):
        if not self.linols.file_path:
            QMessageBox.warning(self.linols, "Warning", "No file is currently open. Please open a file first.")
            return

        if not self.undo_stack:
            return

        row, col, old_value = self.undo_stack.pop()

        current_value = self._data[row][col]
        self.redo_stack.append((row, col, current_value))

        self._data[row][col] = old_value

        index = self.index(row, col)
        self.dataChanged.emit(index, index)

    def redo_changes(self):
        if not self.linols.file_path:
            QMessageBox.warning(self.linols, "Warning", "No file is currently open. Please open a file first.")
            return

        if not self.redo_stack:
            return

        row, col, old_value = self.redo_stack.pop()

        current_value = self._data[row][col]
        self.undo_stack.append((row, col, current_value))

        self._data[row][col] = old_value

        index = self.index(row, col)
        self.dataChanged.emit(index, index)

class CustomTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.linols = parent
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

        font = QFont("Cantarell", 10)
        self.verticalHeader().setFont(font)

    def on_scroll(self):
        if not self.linols.tab1_selected:
            return

        # Calculate the first visible row index by checking the geometry of each row
        visible_rect = self.viewport().geometry()
        first_visible_row = self.indexAt(visible_rect.topLeft()).row()

        frame_before = self.linols.current_frame

        index = first_visible_row * self.linols.columns
        frame = self.linols.num_rows * self.linols.columns
        frames_num = index // frame
        self.linols.current_frame = frames_num * frame

        if frame_before != self.linols.current_frame:
            self.linols.sync_2d_scroll = True
            self.linols.mode2d.draw_canvas(self.linols)

    def get_first_visible_index(self):
        visible_rect = self.viewport().geometry()
        first_visible_row = self.indexAt(visible_rect.topLeft()).row()
        index = first_visible_row * self.linols.columns

        return index

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() in [Qt.Key.Key_PageUp, Qt.Key.Key_PageDown]: # Track when Page Up or Page Down is pressed
            self.on_scroll()

    def keyReleaseEvent(self, event):
        self.linols.text_addons.on_selection()
        super().keyReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.linols.text_addons.on_selection()
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.on_right_click(event)
        super().mousePressEvent(event)

    def on_right_click(self, event):
        selection_model = self.linols.table_view.selectionModel()
        selected_indexes_count = len(selection_model.selectedIndexes())

        if selected_indexes_count < 1:
            return

        right_menu = QMenu(self.parent())

        copy_text = QAction("Copy (Ctrl+C)", self)
        paste_text = QAction("Paste (Ctrl+V)", self)
        undo_text = QAction("Undo (Ctrl+Z)", self)
        redo_text = QAction("Redo (Ctrl+Y)", self)
        open_map_action = QAction("Open Map", self)
        add_map = QAction("Add map (k)")
        text_to_2d = QAction("Text to 2D")

        copy_hex = QAction("Copy Hex Address", self)
        add_potential_map_action = QAction("Add Potential Map", self)
        remove_potential_map_action = QAction("Remove Potential Map", self)

        copy_text.triggered.connect(lambda: self.linols.text_addons.copy_values(False))
        paste_text.triggered.connect(self.linols.text_addons.paste_values)
        undo_text.triggered.connect(self.linols.model.undo_changes)
        redo_text.triggered.connect(self.linols.model.redo_changes)
        open_map_action.triggered.connect(self.linols.maps.open_map_right_click)
        add_map.triggered.connect(self.linols.maps.add_map)
        text_to_2d.triggered.connect(lambda: self.linols.mode2d.text_to_2d(self.linols))

        copy_hex.triggered.connect(self.linols.text_addons.copy_hex_address)
        add_potential_map_action.triggered.connect(self.linols.maps.add_potential_map)
        remove_potential_map_action.triggered.connect(self.linols.maps.remove_potential_map)

        right_menu.addAction(copy_text)
        right_menu.addAction(paste_text)
        right_menu.addAction(undo_text)
        right_menu.addAction(redo_text)
        right_menu.addAction(open_map_action)
        right_menu.addAction(add_map)
        right_menu.addAction(text_to_2d)

        right_menu.addSeparator()

        right_menu.addAction(copy_hex)
        right_menu.addAction(add_potential_map_action)
        right_menu.addAction(remove_potential_map_action)

        pos = event.globalPosition().toPoint()

        right_menu.exec(pos)

    def keyPressEvent(self, event):
        if event.key() == 16777274: # check if the F11 is pressed
            self.on_f11_pressed()
        else:
            super().keyPressEvent(event)

    def on_f11_pressed(self):
        selection_model = self.linols.table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        temp_list = list(self.linols.current_values)

        for item in selected_indexes:
            row = item.row()
            col = item.column()

            index = (row * self.linols.columns) + col
            index_unpacked = index - self.linols.shift_count

            temp_list[index] = self.linols.unpacked[index_unpacked]

        self.linols.current_values = temp_list

        rows = [self.linols.current_values[i:i + self.linols.columns] for i in
                range(0, len(self.linols.current_values) - self.linols.columns, self.linols.columns)]  # get values by rows

        remaining_elements = len(self.linols.current_values) % self.linols.columns  # last row offset

        if remaining_elements:
            last_row = list(self.linols.current_values[-remaining_elements:]) + [None] * (
                    self.linols.columns - remaining_elements)  # last row values
            rows.append(last_row)

        self.linols.model.set_data(rows)
        self.linols.model.layoutChanged.emit()

        self.linols.text_view_.set_labels_y_axis()
        self.linols.text_view_.set_column_width()

        selection_model.clearSelection()

class CustomListBox(QListWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.ui.maps.remove_item)
        context_menu.addAction(remove_action)

        show_action = QAction("Show in Text", self)
        show_action.triggered.connect(self.ui.maps.show_map_in_text)
        context_menu.addAction(show_action)

        context_menu.exec(event.globalPos())

class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = parent

        font = QFont("Cantarell", 10)
        self.verticalHeader().setFont(font)
        self.horizontalHeader().setFont(font)

        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.showHorizontalHeaderContextMenu)

        self.verticalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self.showVerticalHeaderContextMenu)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        copy_map_action = QAction("Copy Map (Ctrl+Shift+C)", self)
        context_menu.addAction(copy_map_action)
        copy_map_action.triggered.connect(self.ui.mode3d.copy_map)

        copy_selected_action = QAction("Copy selected (Ctrl+C)", self)
        context_menu.addAction(copy_selected_action)
        copy_selected_action.triggered.connect(self.ui.mode3d.copy_selected_3d)

        paste_map_action = QAction("Paste Map (Ctrl+Shift+V)", self)
        context_menu.addAction(paste_map_action)
        paste_map_action.triggered.connect(self.ui.mode3d.paste_map)

        paste_selected_action = QAction("Paste selected (Ctrl+V)", self)
        context_menu.addAction(paste_selected_action)
        paste_selected_action.triggered.connect(self.ui.mode3d.paste_selected)

        show_in_3d_action = QAction("Show in 3D (Ctrl+R)", self)
        context_menu.addAction(show_in_3d_action)
        show_in_3d_action.triggered.connect(self.ui.tk_win_manager.open_tkinter_window)

        context_menu.addSeparator()

        action_prop = QAction("Map Properties (Alt+Enter)", self)
        context_menu.addAction(action_prop)
        action_prop.triggered.connect(lambda: self.ui.maps.map_properties_dialog("map"))

        action_sign_values = QAction("Sign Values 3D", self)
        context_menu.addAction(action_sign_values)
        action_sign_values.triggered.connect(self.ui.maps.sign_values)

        value_dialog_action = QAction("Value Dialog", self)
        context_menu.addAction(value_dialog_action)
        value_dialog_action.triggered.connect(self.ui.maps.value_changer_dialog)

        context_menu.exec(event.globalPos())

    def showHorizontalHeaderContextMenu(self, pos: QPoint):
        context_menu = QMenu(self)
        action = context_menu.addAction(f"X-Axis Properties")
        action.triggered.connect(lambda: self.ui.maps.map_properties_dialog("x"))
        context_menu.exec(self.horizontalHeader().mapToGlobal(pos))

    def showVerticalHeaderContextMenu(self, pos: QPoint):
        context_menu = QMenu(self)
        action = context_menu.addAction(f"Y-Axis Properties")
        action.triggered.connect(lambda: self.ui.maps.map_properties_dialog("y"))
        context_menu.exec(self.verticalHeader().mapToGlobal(pos))

    def keyPressEvent(self, event):
        if event.key() == 16777274:  # check if the F11 is pressed
            self.on_f11_pressed()
        else:
            super().keyPressEvent(event)

    def on_f11_pressed(self):
        selected_items = self.selectedItems()

        for item in selected_items:
            row = item.row()
            col = item.column()

            self.ui.mode3d.set_ori_value(row, col)

        self.clearSelection()