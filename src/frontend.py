from __future__ import annotations
from typing import Literal, Dict, Union, Optional
from QtPy import myFrame, myWindow, myDropdownMenu, myStack, myButton, myLabel
from PyQt5.QtWidgets import QSizePolicy, QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtGui import QKeyEvent, QPaintEvent, QPainter, QColor, QResizeEvent, QTransform
from PyQt5.QtCore import QRectF, Qt, QPoint
from paintable_objects import Plane, Target_box, Indicator_Target_Box, Indicator_Arrows, game_text
from database import DatabaseHandler


class Frontend(myWindow):
    
    def __init__(self, backend):
               
        # Create reference to the backend
        self.backend = backend
        
        # Dictionary of currently pressed keys
        self.keys = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "a" : False,
            "d" : False
        }
        
        # Init window
        super().__init__(
            window_width = 1000,
            window_height = 1000
        )
        self.setFocusPolicy(Qt.WheelFocus)
           
        # Create the top menu
        self.top_menu = menu_bar(
            parent = self.central_widget,
            backend = backend
        )
        
        # Create the main frame where we can select what page is
        # currently visible
        self.main_stack = myStack(
            parent = self.central_widget,
            object_name = "main_stack",
            add_to_parent_layout = True
        )
        
        # Create the menu page
        self.page_1 = page_1(
            parent = self.main_stack,
            top_level = self
        )
        
        # Create the page where the game takes place
        self.page_2 = page_2(
            parent = self.main_stack
        )
        
        # Create references to objects deeper down in levels
        self.plane = self.page_2.center_frame.plane
        self.target_box = self.page_2.center_frame.target_box
        self.left_target_box = self.page_2.left_indicator.target_box
        self.left_indicator = self.page_2.left_indicator.arrows
        self.right_target_box = self.page_2.right_indicator.target_box
        self.right_indicator = self.page_2.right_indicator.arrows
        
    
    def move_left_indicator(self, new_pos: float, duration: int) -> None:
        self.page_2.left_indicator.arrows.move(
            new_pos, 0, 0, duration
        )
    def move_right_indicator(self, new_pos: float, duration: int) -> None:
        self.page_2.right_indicator.arrows.move(
            new_pos, 0, 0, duration
        )
    def move_left_target_box(self, new_pos: float, duration: int) -> None:
        self.page_2.left_indicator.target_box.move(
            new_pos, 0, 0, duration
        )
    def move_right_target_box(self, new_pos: float, duration: int) -> None:
        self.page_2.right_indicator.target_box.move(
            new_pos, 0, 0, duration
        )
    def move_plane_target_box(self,
        new_x: float, 
        new_y: float,
        new_rotation: float,
        duration: int
    ) -> None:
        self.page_2.center_frame.target_box.move(
            new_x, new_y, new_rotation, duration
        )
    def move_plane(self,
        new_x: float, 
        new_y: float,
        new_rotation: float,
        duration: int
    ) -> None:
        self.page_2.center_frame.plane.move(
            new_x, new_y, new_rotation, duration
        )
        
class menu_bar(myFrame):
    
    ports_menu: myDropdownMenu
    
    def __init__(self, parent: myFrame, backend) -> None:
        
        super().__init__(
            parent = parent,
            object_name = "menu_frame",
            add_to_parent_layout = True,
            layout_type = "horizontal"
        )
        self.setContentsMargins(0, 0, 0, 0) 
        self.setMaximumHeight(30)
        self.backend = backend
    
        self.ports_menu = myDropdownMenu(
            parent = self,
            object_name = "ports_menu",
            add_to_parent_layout = True
        )
        
        self.ports_menu.addItem("No sensors connected...")
        ports = self.backend.serial_reader.fetchPorts()
        if len(ports) != 0:
            self.ports_menu.addItems(ports)

        self.ports_menu.currentTextChanged.connect(self.item_clicked)
        
    def item_clicked(self, index):
        
        if self.ports_menu.currentText() != "No sensors connected...":
            self.backend.serial_reader.newPort(self.ports_menu.currentText()[:5])
  
class page_1(myFrame):
    
    def __init__(self, parent: myFrame, top_level: Frontend) -> None:
         
        myFrame.__init__(self, 
            parent = parent,
            object_name = "page_1",
            add_to_parent_layout = True,
            layout_type = "horizontal"
        )
        
        self.layout().addStretch()
        
        frame1 = myFrame(
            parent = self,
            object_name = "temp_frame",
            add_to_parent_layout = True,
            layout_type = "vertical"
        )

        frame1.layout().addStretch()
        
        self.user_list = UserListWidget(
            parent = frame1,
            top_level = top_level
        )
        
        self.start_game_button = myButton(
            parent = frame1,
            object_name = "start_game_button",
            add_to_parent_layout = True
        )
        self.start_game_button.setMinimumSize(
            100, 
            30
        )
        self.start_game_button.setEnabled(False)
        self.start_game_button.setText("Start Game")
        self.start_game_button.clicked.connect(
            top_level.backend.start_game_clicked
        )
        
        frame1.layout().addStretch()
        
        self.layout().addStretch()
            
class page_2(myFrame):
                      
    def __init__(self, parent: myStack) -> None:
        
        super().__init__(
            parent = parent,
            object_name = "page_2",
            layout_type = "horizontal"
        )    
        parent.addWidget(self)
        
        self.set_layout_alignment("center")
        
        self.style_sheet.add_style(
            style = "border-image",
            value = "url(resources/images/skies.jpg)"
        )
        
        # Stretch on left side of screen
        self.layout().addStretch()
        
        # Init left indicator
        self.left_indicator = indicator_frame(
            parent = self,
            object_name = "left_indicator"
        )
        
        # Stretch between left indicator and middle frame
        self.layout().addStretch()
        
        self.center_frame = middle_frame(
            parent = self
        )
        
        # Add stretch between middle frame and right indicator
        self.layout().addStretch()
        
        # Init right indicator
        self.right_indicator = indicator_frame(
            parent = self,
            object_name = "right_indicator"
        )
        
        # Add stretch between right indicator and right edge
        self.layout().addStretch()
        
        self.left_force = game_text(self)
        self.left_force.set_width("1234\tg")
        self.left_force.display_text = "----\tg"
    
        self.right_force = game_text(self)
        self.right_force.set_width("1234\tg")
        self.right_force.display_text = "----\tg"
    
    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        left_ind_pos = self.left_indicator.mapTo(self, QPoint(0, 0))
        right_ind_pos = self.right_indicator.mapTo(self, QPoint(0,0))

        left_ind = left_ind_pos + QPoint(140, 80)
        right_ind = right_ind_pos + QPoint(-140 + self.left_indicator.width(), 80)
        
        self.left_force.font.setPixelSize(20)
        self.right_force.font.setPixelSize(20)
        
        self.left_force.draw(painter, left_ind)
        self.right_force.draw(painter, right_ind)


class indicator_frame(myFrame):
    """The indicator bars that are placed next to the plane on each side. Contains
    functions that paints, moves and animates the height of the indicator bar, as well as the position of
    the target boxes in which the user should try to keep the indicator bars within. Function that
    calculates and returns the difference between the indicator bar position and the center of the target box
    is implemented in the get_accuracy() function.
    """
    indicator_color: QColor
    max_difference: float
    def __init__(self,
        parent: page_2,
        object_name: str,
    ) -> None:
        
        super().__init__(
            parent = parent,
            object_name = object_name,
            layout_type = "vertical",
            add_to_parent_layout = True
        )
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.setMaximumHeight(600)
        self.setMinimumHeight(400)
        self.setFixedWidth(50)
               
        self.target_box = Indicator_Target_Box(self)
        self.arrows = Indicator_Arrows(self, self.target_box)
        self.target_box.set_partner(self.arrows)    
        self.text = game_text(self)               

        
    def get_accuracy(self) -> int:
        return self.arrows.get_center().y() - self.target_box.get_center().y()
    
    def paintEvent(self, event) -> None:
        """Paints the indicator bar and the target box.
        """
            
        # Initialize the painter event
        super().paintEvent(event) 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)     
        
        transform = QTransform()
        transform.translate(
            self.width()//2,
            self.height()//2
        )
        transform.translate(
            - (self.width()*0.6)//2,
            - (self.height()*0.8)//2
        )
        painter.setTransform(transform)
        # Draw a transparent rectangle around the entire frame
        painter.setBrush(Qt.transparent)
        rect = QRectF(
            0, 
            0, 
            int(round(self.width()*0.6, 0)),
            int(round(self.height()*0.8, 0))
        )
        painter.drawRoundedRect(rect, 0, 0)

        self.target_box.draw(painter)
        
        self.arrows.draw(painter)
        
    
class middle_frame(myFrame):
    """The frame where the plane and the plane target box is. Paints these objects and
    has functionality that animates their changes in rotation.
    """          
            
    
    target_box_rotation_angle: int
    target_box_color: QColor
    plane_rotation: int
    max_target_box_difference: float
    def __init__(self, parent: page_2) -> None:
            

        self.target_box_color = QColor(0, 255, 0, 200)
        
        super().__init__(
            parent = parent,
            object_name = "page_2_middle_frame",
            add_to_parent_layout = True,
            layout_type = "vertical"
        )
        self.setSizePolicy(
            QSizePolicy.Expanding, 
            QSizePolicy.Expanding
        )
        
        # Create the plane
        self.plane = Plane(self)
        self.plane.y_offset = 39
        self.text = game_text(self)
        self.text.auto_adjust(True)

        # Create the target box
        self.target_box = Target_box(self, self.plane)

    def resizeEvent(self, event: QResizeEvent):
        """Makes sure the middle frame always fits the plane.
        """
        self.setMinimumWidth(self.plane.width() * 2)
        self.setMinimumHeight(self.plane.width() * 2)

    def paintEvent(self, event) -> None:
        """Paints a rectangle in the middle frame with color and rotation fetched from
            self.target_box_rotation_angle and self-target_box_color.
            """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.target_box.draw(painter)
        self.plane.draw(painter)
        self.text.draw(painter)

class UserListWidget(QWidget):
    def __init__(self, parent: myFrame, top_level: Frontend):
        super().__init__(parent)
        
        # Create reference to the database handler
        self.db_handler: DatabaseHandler = top_level.backend.database_handler
        
        self.parent = parent
        self.top_level = top_level
        self.setWindowTitle('User List')
        self.setMinimumWidth(1000)
        self.setMinimumHeight(500)
        
        master_layout = QVBoxLayout()

        self.current_user_label = QLabel()
        self.current_user_label.setText("Current user: None")
        master_layout.addWidget(self.current_user_label)
        
        layout = QHBoxLayout()
        master_layout.addLayout(layout)
        
        user_list_frame = myFrame(
            parent = self,
            object_name = "user_list_frame",
            layout_type = "vertical"
        )
        layout.addWidget(user_list_frame)
        
        
        self.user_list_widget = QListWidget()
        self.user_list_widget.itemClicked.connect(self.handle_user_click)
        self.user_list_widget.itemSelectionChanged.connect(self.handle_selection_change)
        user_list_frame.layout().addWidget(self.user_list_widget)
                
        # Search and add widgets
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_user)
        search_layout.addWidget(self.search_input)

        self.add_button = QPushButton("Add User")
        self.add_button.clicked.connect(self.add_user)
        self.add_button.setEnabled(False)
        search_layout.addWidget(self.add_button)
        
        self.delete_user_button = QPushButton("Delete User")
        self.delete_user_button.clicked.connect(self.delete_user)
        self.delete_user_button.setEnabled(False)
        search_layout.addWidget(self.delete_user_button)
        search_layout.setContentsMargins(0, 10, 0, 0)

        user_list_frame.layout().addLayout(search_layout)
        
        # Games List Widget
        game_list_frame = myFrame(
            parent = self,
            object_name = "game_list_frame",
            layout_type = "vertical" 
        )
        layout.addWidget(game_list_frame)
        
        self.games_list_widget = QListWidget()
        game_list_frame.layout().addWidget(self.games_list_widget)
        self.games_list_widget.itemSelectionChanged.connect(self.handle_game_selection_change)

        plot_layout = QHBoxLayout()
        #self.search_input = QLineEdit()
        #self.search_input.textChanged.connect(self.search_user)
        #search_layout.addWidget(self.search_input)

        self.plot_game_button = QPushButton("Show game")
        self.plot_game_button.clicked.connect(self.show_game)
        self.plot_game_button.setEnabled(False)
        plot_layout.addWidget(self.plot_game_button)
        
        self.show_progress_button = QPushButton("Show progress")
        self.show_progress_button.clicked.connect(self.show_progress)
        self.show_progress_button.setEnabled(False)
        plot_layout.addWidget(self.show_progress_button)
        plot_layout.setContentsMargins(0, 10, 0, 0)
        
        game_list_frame.layout().addLayout(plot_layout)
        
        export_layout = QHBoxLayout()
        
        self.export_game_button = QPushButton("Export game")
        self.export_game_button.clicked.connect(self.export_game)
        self.export_game_button.setEnabled(False)
        export_layout.addWidget(self.export_game_button)
        
        self.export_progress_button = QPushButton("Export progress")
        self.export_progress_button.clicked.connect(self.export_progress)
        self.export_progress_button.setEnabled(False)
        export_layout.addWidget(self.export_progress_button)
        export_layout.setContentsMargins(0, 10, 0, 0)
        
        game_list_frame.layout().addLayout(export_layout)
        
        
        
        
        self.setLayout(master_layout)

        self.populate_user_list()
        
        self.parent.layout().addWidget(self)
    
    def add_user(self):
        self.db_handler.add_user(self.search_input.text().strip())
        self.search_user()
    
    def delete_user(self):
        selected_items = self.user_list_widget.selectedItems()
        if selected_items:
            user = selected_items[0].data(1)
            reply = QMessageBox.question(self, 
                'Confirmation', 
                f"Are you sure you want to delete user '{user.name}' and all related game statistics?", 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.db_handler.delete_user(user.id)
                self.search_user()
                if user.id == self.top_level.backend.current_user.id:
                    self.current_user_label.setText("Current user: None")
                    self.top_level.backend.current_user = None
                    self.top_level.page_1.start_game_button.setEnabled(False)
        else:
            QMessageBox.information(self, 'No Selection', 'Please select a user to delete.', QMessageBox.Ok)
    
    def search_user(self):
        self.user_list_widget.clear()
        # Assume you have fetched users from the database
        input_text = self.search_input.text().strip().lower()
        users = self.top_level.backend.database_handler.search_users(input_text)
        usernames = [user.name.lower() for user in users]

        for user in users:
            item = QListWidgetItem(str(user))
            item.setData(1, user)  # Set user data for later use
            self.user_list_widget.addItem(item)
                
        if input_text in usernames or len(input_text)<1:
            self.add_button.setEnabled(False)
        else:
            self.add_button.setEnabled(True)

    def populate_user_list(self):
        # Assume you have fetched users from the database
        users = self.top_level.backend.database_handler.fetch_users()
        for user in users:
            item = QListWidgetItem(str(user))
            item.setData(1, user)  # Set user data for later use
            self.user_list_widget.addItem(item)
    
    def populate_games_list(self, games):
        self.games_list_widget.clear()
        nr = 0
        for game in games:
            
            nr += 1
            game.nr = nr
            item = QListWidgetItem(
                f"Game nr. {nr}\n\tTime: {game.timestamp.strftime('%H:%M:%S - %d.%m.%y')}\n"
            )
            item.setData(1, game)
            self.games_list_widget.addItem(item)

    def handle_user_click(self, item):
        user = item.data(1)
        self.populate_games_list(user.games)
        self.top_level.backend.current_user = user
        self.current_user_label.setText(
            f"Current user: {self.top_level.backend.current_user.name}"
        )
        self.top_level.page_1.start_game_button.setEnabled(True)
        self.export_game_button.setEnabled(False)
        self.plot_game_button.setEnabled(False)
        
        if len(user.games) > 1:
            self.show_progress_button.setEnabled(True)
            self.export_progress_button.setEnabled(True)
        else:
            self.show_progress_button.setEnabled(False)
            self.export_progress_button.setEnabled(False)
        
    def handle_selection_change(self) -> None:
        if not self.user_list_widget.selectedItems():
            self.delete_user_button.setEnabled(False)
            self.show_progress_button.setEnabled(False)
            self.games_list_widget.clear()
        else:
            self.delete_user_button.setEnabled(True)

    def show_progress(self) -> None:
        
        current_user = self.user_list_widget.currentItem()
        if current_user is not None:
            user = current_user.data(1)
            self.top_level.backend.plot_progress(user)
   
    def show_game(self):
        current_game = self.games_list_widget.currentItem()
        if current_game is not None:
            game = current_game.data(1)
            self.top_level.backend.plot_game(game)
            
    def handle_game_selection_change(self) -> None:
        if self.games_list_widget.currentItem() is not None:
            self.plot_game_button.setEnabled(True)
            self.export_game_button.setEnabled(True)
        else:
            self.delete_user_button.setEnabled(False)
            self.export_game_button.setEnabled(False)
    
    def export_progress(self):
        pass

    def export_game(self):
        current_game = self.games_list_widget.currentItem()
        if current_game is not None:
            game = current_game.data(1)
            self.top_level.backend.save_game_Excel(game)