from __future__ import annotations
from PyQt5.QtGui import QPixmap, QTransform, QPainter, QBrush, QColor, QResizeEvent
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtWidgets import (
    QStackedWidget, QFrame, QWidget, 
    QHBoxLayout, QVBoxLayout, QGridLayout, 
    QLayout, QPushButton, QLabel, QMainWindow,
    QApplication, QComboBox
)
from typing import Optional, Literal, Dict, List, Tuple
import traceback
import sys
from functools import partial

class Style_sheet:
    __slots__ = (
        "__parent",
        "object_type",
        "object_name",
        "style_commands",
        "post_bulk_commands"
    )
    __parent: myBaseWidget
    object_type: str
    object_name: str
    style_commands: Dict[str,str]
    post_bulk_commands: Dict[str, List[str, str]]
    def __init__(self, parent: myBaseWidget) -> None:
        
        self.__parent = parent
        self.object_type = parent.widget_type
        self.object_name = parent.objectName()
        self.style_commands = {}
        self.post_bulk_commands = {}
    def update_stylesheet(self, repr: bool = False) -> Optional[str]:
        """Makes a stylesheet from the commands and values stored in the object.
        Assigns this stylesheet to the parent object. This functions doubles as
        the __repr__ function, so if repr = True, the stylesheet doesn't update, and
        the string representation of the stylesheet is returned insted.

        Args:
            repr (bool, optional): True means function is called by the __repr__ function. 
            Defaults to False.

        Returns:
            str: The stylesheet in string format.
        """

        style_sheet = (
            "#" + self.object_name + "{\n"
        )
        for command, value in zip(
            self.style_commands.keys(),
            self.style_commands.values()
        ):
            style_sheet += (
                "\t" + command + ":" + value + "\n"
            )   
        style_sheet += "}\n"
        
        for type, command_and_value in zip(
            self.post_bulk_commands.keys(),
            self.post_bulk_commands.values()
        ):
            style_sheet += (
                f"#{self.__parent.objectName()}:"
                f"{type}{{{command_and_value[0]}:{command_and_value[1]}}}"
            )
        
        if repr:
            return style_sheet
        else:
            self.__parent.setStyleSheet(style_sheet)
    def set_background_color(self, R: int, G: int, B: int, A: int) -> None:
        """Adds the command "background-color:rgba(R,G,B,A);" to the style sheet.

        Args:
            R (int): Value of the red channel from 0-255
            G (int): Value of the green channel from 0-255
            B (int): Value of the blue channel from 0-255
            A (int): Value of the alpha channel from 0-255
        """
        self.style_commands["background-color"] = f"rgba({R}, {G}, {B}, {A});"
        self.update_stylesheet()
    def set_border_radius(self,
        top_left: int,
        top_right: int,
        bottom_right: int,
        bottom_left: int
    ) -> None:
        """Changes the curve radius of each corner of the widget.

        Args:
            top_left (int): Curve of the top left corner.
            top_right (int): Curve of the top right corner.
            bottom_right (int): Curve of the bottom right corner.
            bottom_left (int): Curve of the bottom left corner.
        """
        self.style_commands["border-top-left-radius"] = f"{top_left}px;"
        self.style_commands["border-top-right-radius"] = f"{top_right}px;"
        self.style_commands["border-bottom-right-radius"] = f"{bottom_right}px;"
        self.style_commands["border-bottom-left-radius"] = f"{bottom_left}px;"
        self.update_stylesheet()
    def add_style(self, style: str, value: str) -> None:
        """Add a style to the stylesheet.

        Args:
            style (str): The style to be added/changed, for 
            example: "background-color"
            value (str): Value of the style being added/achanged, for
            example "rgba(0, 0, 0, 0)"
        """
        self.style_commands[f"{style}"] = value
        self.update_stylesheet()
    def __repr__(self) -> str:
        """Uses the string representation of the style sheet gathered from
        update_stylesheet() to print the stylesheet.

        Returns:
            str: String representation of the stylesheet.
        """
        
        return self.update_stylesheet(repr = True)
class myButton_Stylesheet(Style_sheet):
    def __init__(self, parent: myBaseWidget) -> None:
        super().__init__(parent)
        # Set the default look
        self.set_background_color(
            R = 255, B = 255, G = 255, A = 100
        )
        self.set_on_hover_color(
            R = 100, G = 100, B = 100, A = 100
        )
        self.set_on_pressed_color(
            R = 130, G = 130, B = 130, A = 130
        )
        self.set_border_radius(
            top_left = 5, top_right = 5,
            bottom_right = 5, bottom_left = 5
        )
    def set_on_hover_color(self, R: int, G: int, B: int, A: int) -> None:
        self.post_bulk_commands["hover"] = [
            "background-color", 
            f"rgba({R}, {G}, {B}, {A});"
        ]
        self.update_stylesheet() 
    def set_on_pressed_color(self, R: int, G: int, B: int, A: int) -> None:
        self.post_bulk_commands["pressed"] = [
            "background-color", 
            f"rgba({R}, {G}, {B}, {A});"
        ]
        self.update_stylesheet()
class myLabel_Stylesheet(Style_sheet):
    def __init__(self, parent: myBaseWidget) -> None:
        super().__init__(parent)
    def set_text_color(self, R: int, G: int, B: int, A: int) -> None:
        self.style_commands["color"] = f"rgba({R}, {G}, {B}, {A});" 
class myStack_Stylesheet(Style_sheet):
    def __init__(self, parent: myBaseWidget) -> None:
        super().__init__(parent)
class myInput_Stylesheet(Style_sheet):
    def __init__(self, parent: myBaseWidget) -> None:
        super().__init__(parent)
class myDropdownMenu_Stylesheet(Style_sheet):
    def __init__(self, parent: myBaseWidget) -> None:
        super().__init__(parent)

class myBaseWidget(QWidget):
    widget_type: str 
    style_sheet: Style_sheet 
    alignments: Dict[Literal[
        "left", "right", "top", "bottom", "horizontal_center",
        "vertical_center", "center"
        ]
    ] = {
        "left" : Qt.AlignLeft,
        "right" : Qt.AlignRight,
        "top" : Qt.AlignTop,
        "bottom" : Qt.AlignBottom,
        "horizontal_center" : Qt.AlignHCenter,
        "vertical_center" : Qt.AlignVCenter,
        "center" : Qt.AlignCenter
    }
    def __init__(self, 
        parent: myBaseWidget, 
        object_name: Optional[str] = None,
        add_to_parent_layout: Optional[bool] = False
    ) -> None:

        if object_name is None:
            self.setObjectName(
                self._name_after_variable()
        )
        else:
            self.setObjectName(
                object_name
        )       
        if add_to_parent_layout:
            parent.layout().addWidget(self)
    def set_border_radius(self,
        top_left_corner: int,
        top_right_corner: int,
        bottom_right_corner: int,
        bottom_left_corner: int
    ) -> None:
        """Changes the curve radius of each corner of the widget.

        Args:
            top_left_corner (int): Curve of the top left corner.
            top_right_corner (int): Curve of the top right corner.
            bottom_right_corner (int): Curve of the bottom right corner.
            bottom_left_corner (int): Curve of the bottom left corner.
        """
        self.style_sheet.set_border_radius(
            top_left_corner,
            top_right_corner,
            bottom_right_corner,
            bottom_left_corner
        )  
    def _name_after_variable(self) -> str:
        """If an object name for the initialized myFrame is passed, this function will
        do it's best to name the object after the variable that it was initialized into.
        """       
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        variable_name = text[:text.find('=')].strip()
        return variable_name 
class myWindow(QMainWindow):
    def __init__(self,
        window_width: Optional[int] = 1000,
        window_height: Optional[int] = 1000
    ) -> None:
        
        QMainWindow.__init__(self)
        self.resize(window_width, window_height)
        
        self.central_widget = QWidget(
            parent = self
        )
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setLayout(
            QVBoxLayout(self.central_widget)
        )
        self.setCentralWidget(self.central_widget)      
class myFrame(QFrame, myBaseWidget):
    layout_types: Dict[str, QLayout] = {
        "horizontal" : QHBoxLayout,
        "vertical" : QVBoxLayout,
        "grid" : QGridLayout
    }
    quadratic: bool
    def __init__(self,
        parent: myBaseWidget,
        object_name: Optional[str] = None,
        add_to_parent_layout: Optional[bool] = False,
        layout_type: Optional[
            Literal[
                "horizontal",
                "vertical",
                "grid"
            ]
        ] = "horizontal"
    ) -> None:   
        
        # Init QFrame
        QFrame.__init__(self, parent = parent)
        # Init configurations from myBaseWidget
        myBaseWidget.__init__(self,
            parent = parent,
            object_name = object_name,
            add_to_parent_layout = add_to_parent_layout
        )
        self.quadratic = False
        self.widget_type = "Qframe"
        self.style_sheet = Style_sheet(parent = self)   
        # Init layout
        self.setLayout(
            self.__class__.layout_types[layout_type](self)
        )
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)      
    def set_quadratic(self, quadratic: bool) -> None:
        self.quadratic = quadratic
    def resizeEvent(self, event: QResizeEvent):
        # Make sure width and height are equal to force a quadratic shape
        if self.quadratic:
            size = min(event.size().width(), event.size().height())
            self.resize(size, size)
        else:
            self.resize(event.size().width(), event.size().height())
        
    def set_layout_alignment(self,
        alignement_type: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "horizontal_center",
            "vertical_center",
            "center"
        ]
    ) -> None:
        self.layout().setAlignment(
            myBaseWidget.alignments[alignement_type]
        )
    def set_background_image(self, path_to_image: str) -> None:
        """Sets the background image of the frame.

        Args:
            path_to_image (str): The relative path to the image.
        """
        self.style_sheet.add_style(
            "border-image",
            f"url({path_to_image});"
        )
class myButton(QPushButton, myBaseWidget):
    style_sheet: myButton_Stylesheet
    def __init__(
        self,
        parent: myBaseWidget,
        object_name: Optional[str] = None,
        add_to_parent_layout: Optional[bool] = False                 
    ) -> None:
        # Init button
        QPushButton.__init__(self, parent)      
        myBaseWidget.__init__(self,
            parent=parent,
            object_name=object_name,
            add_to_parent_layout=add_to_parent_layout
        )
        self.widget_type = "QPushButton"
        self.style_sheet = myButton_Stylesheet(parent = self)
class myLabel(QLabel, myBaseWidget):
    style_sheet: myLabel_Stylesheet
    image: QPixmap
    rotation_angle: float
    default_style = {
        "color:" : "rgba(255, 255, 255, 255);",
        "background-color:" : "rgba(255, 255, 255, 0);" 
    }
    def __init__(
        self,
        parent: myBaseWidget,
        object_name: Optional[str] = None,
        add_to_parent_layout: Optional[str] = False,
        label_text: Optional[str] = None
    ) -> None:
        
        # Init the label
        QLabel.__init__(self, parent)
        myBaseWidget.__init__(self,
            parent=parent,
            object_name=object_name,
            add_to_parent_layout=add_to_parent_layout
        )
        self.rotation_angle = 0.0
        self.widget_type = "QLabel"
        self.style_sheet = myLabel_Stylesheet(parent = self)       

    def set_image_rotation_angle(self, angle: float) -> None:
        """Sets a rotation of the self.image and updates the widget.

        Args:
            angle (float): Angle at which self.image is displayed.
        """
        self.rotation_angle = angle
        self.update()

    def paintEvent(self, event) -> None:
        """Rotates the displayed self.image QPixmap.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Translate the painter to the center of the label
        painter.translate(self.width() / 2, self.height() / 2)
        # Rotate the painter
        painter.rotate(self.rotation_angle)
        # Draw the rotated image
        painter.drawPixmap(-self.image.width() / 2, -self.image.height() / 2, self.image)
        
        new_size = self.image.size().scaled(self.image.size(), Qt.KeepAspectRatio)
        self.setFixedSize(new_size)

    def add_image(self, path_to_image: str) -> None:
        """Assigns a QPixmap with the image in the path to the self.image variable.

        Args:
            path_to_image (str): Relative path to the image you want displayed
            in the label.
        """
        self.image = QPixmap(path_to_image)
    
class myStack(QStackedWidget, myBaseWidget):
    style_sheet: myStack_Stylesheet
    def __init__(self, 
        parent: myBaseWidget,
        object_name: Optional[str] = None,
        add_to_parent_layout: Optional[bool] = False
    ) -> None:
        # Init the stack
        QStackedWidget.__init__(self, parent)
        myBaseWidget.__init__(self,
            parent=parent,
            object_name=object_name,
            add_to_parent_layout=add_to_parent_layout
        )
        self.widget_type = "QStackedWidget"
        self.style_sheet = myStack_Stylesheet(parent = self)

    def get_widgets_in_stack(self) -> List[myBaseWidget]:
        widgets = []
        for i in range(self.count()):
            widgets.append(self.widget(i))
        return widgets
class myDropdownMenu(QComboBox, myBaseWidget):
    def __init__(self,
        parent: myBaseWidget,
        object_name: Optional[str] = None,
        add_to_parent_layout: Optional[bool] = False
    ) -> None:
        
        QComboBox.__init__(self)
        myBaseWidget.__init__(self,
            parent = parent,
            object_name = object_name,
            add_to_parent_layout = add_to_parent_layout
        )
        self.widget_type = "QComboBox"
        self.style_sheet = myDropdownMenu_Stylesheet(self)
    def text_change_action(self, function_to_call: function) -> None:
        self.currentTextChanged.connect(
            partial(function_to_call)
        )
class myRotateableFrame(QFrame, myBaseWidget):
        
    def __init__(self, 
        parent: myBaseWidget,
        object_name: Optional[str] = None,
        minimum_square_size: Tuple[int, int] = 100,
        add_to_parent_layout: Optional[bool] = False
    ) -> None:
        
        QFrame.__init__(self, parent)
        myBaseWidget.__init__(self,
            parent = parent,
            object_name = object_name,
            add_to_parent_layout = add_to_parent_layout
        )
        
        self.rotation_angle = 0
        self.color = QColor(
            0, 255, 0, alpha = 150
        )
        self.setMinimumSize(
            minimum_square_size,
            minimum_square_size
        )
        

    def paintEvent(self, event):
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))  # Set the color of the frame
        painter.setPen(Qt.NoPen)

        # Create a transformation matrix for rotation
        transform = QTransform()
        transform.rotate(self.rotation_angle)
        painter.setTransform(transform)

        # Draw the rotated frame
        painter.drawRect()

    def setRotation(self, angle):
        self.rotation_angle = angle
        self.update()