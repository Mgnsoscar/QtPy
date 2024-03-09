from typing import Literal, Dict, Union, Optional
from QtPy import myBaseWidget, myFrame, myLabel, myWindow, myDropdownMenu, myStack, myRotateableFrame
from PyQt5.QtWidgets import QApplication, QWidget, QStackedLayout, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QBrush, QResizeEvent, QTransform, QLinearGradient, QPen, QPixmap
from PyQt5.QtCore import QRectF, Qt, QPropertyAnimation, QEasingCurve, QVariantAnimation, QTimer, QPoint, QPointF
import sys
from functools import partial
import copy
import random
from paintable_objects import Plane, Target_box

class Backend:
    
    pass


class Frontend(myWindow):
    
    def __init__(self):
        
        # Init window
        super().__init__(
            window_width = 1000,
            window_height = 1000
        )
        self.top_menu = menu_bar(
            parent = self.central_widget,
            backend = None
        )
        self.main_stack = myStack(
            parent = self.central_widget,
            object_name = "main_stack",
            add_to_parent_layout = True
        )
                
        self.page_2 = page_2(
            parent = self.main_stack
        )

        #self.set_new_target(
        #    new_angle  = 0,
        #    left_force_target=1.,
        #    right_force_target=-1.,
        #    animation_duration=3000
        #)
        #self.set_plane_rotation(0, 1000)

        #self.showcase()
        
        #self.set_left_indicator_height(1, 1000)
        #self.set_right_indicator_height(-1, 1000)
        
    def showcase(self) -> None:
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.move_targets_showcase())
        
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(lambda: self.move_targets_showcase2())
        

        # Set the interval to 10,000 milliseconds (10 seconds)
        self.timer.start(2000)  
        self.timer2.start(5000)

    def move_targets_showcase(self):
        
        leftind = random.uniform(-1.0, 1.0)
        rightind = leftind * -1        
        self.set_left_indicator_height(leftind, 1000)
        self.set_right_indicator_height(rightind, 1000)
        
        plane_angle = random.uniform(-60., 60.)
        self.set_plane_rotation(plane_angle, 1000)
        
        plane_pos = QPointF(
            random.uniform(-1., 1.),
            random.uniform(-1., 1.)
        )
        self.set_plane_position(
            plane_pos.x(),
            plane_pos.y(),
            1000
        )
    
    def move_targets_showcase2(self):
        
        left = random.uniform(-1.0,1.0)
        right = left * -1
        
        angle = random.uniform(-60.0, 60.0)
        tb_pos = QPointF(
            random.uniform(-1., 1.),
            random.uniform(-1., 1.)
        )
        height = random.uniform(-1.0, 1.0)
        
        self.set_new_target(
            angle, 
            tb_pos.x(),
            tb_pos.y(),
            left, 
            right, 
            1000
        )
  
    def set_plane_position(self, new_x: float, new_y: float, duration: int) -> None:
        self.page_2.center_frame.animate_plane_position(
            end_x = new_x,
            end_y = new_y,
            duration = duration
        )
    
    def set_target_box_position(self, new_x: float, new_y: float, angle: float, duration: int) -> None:
        self.page_2.center_frame.animate_target_box_position(
            end_x = new_x,
            end_y = new_y,
            duration = duration
        )
      
    def set_new_target(self, 
            new_angle: Union[float, int],
            tb_x: float,
            tb_y: float,
            left_force_target: Union[float, int], 
            right_force_target: Union[float, int],
            animation_duration: int
    ) -> None:
        """Moves the target box for the plane, as well as the target boxes in 
        the left and right indicators.

        Args:
            new_angle (float | int): Angle of the target box for the plane.
            left_force_target (float | int): Vertical position of the left 
            indicator target box. Expressed as a percentage,
            meaning 1 is the highest position, 0.5 is the middle, and 0 is the bottom.
            right_force_target (float | int): Vertical position of the right indicator target box. 
            Expressed same as left_force_target.
        """
        
        self.set_target_box_position(
            tb_x, tb_y, animation_duration
        )
        self.set_ta
        
        self.page_2.left_indicator.animate_target_box_position(
            new_position = left_force_target,
            duration = animation_duration
        )
        self.page_2.right_indicator.animate_target_box_position(
            new_position = right_force_target,
            duration = animation_duration
        )

    def set_plane_rotation(self, new_angle: Union[float, int], animation_duration: int) -> None:
        self.page_2.center_frame.animate_plane_rotation(
            end_angle = new_angle,
            duration  = animation_duration
        )

    def set_left_indicator_height(self, new_height: Union[float, int], duration) -> None:
        self.page_2.left_indicator.animate_indicator_position(
            new_height, duration
        )

    def set_right_indicator_height(self, new_height: Union[float, int], duration) -> None:
        self.page_2.right_indicator.animate_indicator_position(
            new_height, duration
        )
        
class menu_bar(myFrame):
    
    ports_menu: myDropdownMenu
    
    def __init__(self, parent: myFrame, backend: Backend) -> None:
        
        super().__init__(
            parent = parent,
            object_name = "menu_frame",
            add_to_parent_layout = True,
            layout_type = "horizontal"
        )
        self.setContentsMargins(0, 0, 0, 0) 
        self.setMaximumHeight(30)
    
        self.ports_menu = myDropdownMenu(
            parent = self,
            object_name = "ports_menu",
            add_to_parent_layout = True
        )
        self.ports_menu.addItem("Test...")
      
class page_2(myFrame):
                      
    def __init__(self, parent: myStack) -> None:
        
        super().__init__(
            parent = parent,
            object_name = "page_2",
            layout_type = "horizontal"
        )    
        parent.addWidget(self)
        self.set_layout_alignment("center")
        
        # Stretch on left side of screen
        self.layout().addStretch()
        
        # Init left indicator
        self.left_indicator = indicator(
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
        self.right_indicator = indicator(
            parent = self,
            object_name = "right_indicator"
        )
        
        # Add stretch between right indicator and right edge
        self.layout().addStretch()

class indicator(myFrame):
    """The indicator bars that are placed next to the plane on each side. Contains
    functions that paints, moves and animates the height of the indicator bar, as well as the position of
    the target boxes in which the user should try to keep the indicator bars within. Function that
    calculates and returns the difference between the indicator bar position and the center of the target box
    is implemented in the get_accuracy() function.
    """
    indicator_height: int
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
        
        # Init indicator height and color. 0.0 is at the bottom center, 1.0 at top, and 
        # - 1.0 is at the bottom
        self.__indicator_position = 0.0     # Initialize the indicator height variable
        self.indicator_color = QColor( # Base color of indicator bar is green
            0, 255, 0, 200
        )
        self.__target_box_position = 0.0 
        self.target_box_height = self.height() / 5
        
        # Difference in indicator position and target box center greater than
        # this will just keep the color red
        self.max_difference = 30
        
        #self.setFixedWidth(50)
        self.setMaximumHeight(500)
        self.setMinimumHeight(300)
        self.setFixedWidth(50)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Sets the height of the indicator box depending on the height of the frame.
        """
        self.target_box_height = self.height() / 5

    @property
    def target_box_top(self) -> float:
        """Return the absolute positional value of the top of the target box.

        Returns:
            float: Number representing the absolute top position of the target box.
        """
        center_position = (self.height() - self.target_box_height) * 0.5
        scaling_factor = self.__target_box_position * (center_position - 10)
        return center_position - scaling_factor

    @property
    def target_box_center(self) -> float:
        """Return the absolute positional value of the center of the target box.

        Returns:
            float: Number representing the absolute center position of the target box.
        """  
        return (
            self.target_box_top + (self.target_box_height/2)
        )      

    @property
    def target_box_bottom(self) -> float:
        """Return the absolute positional value of the bottom of the target box.

        Returns:
            float: Number representing the absolute bottom position of the target box.
        """
        return (
            self.target_box_top + self.target_box_height
        )
        
    @property
    def absolute_indicator_position(self) -> float:
        """Return the absolute positional value of indicator.

        Returns:
            float: Number representing the absolute position of the
            indicator.
        """      
        center_position = self.height() * 0.5
        scaling_factor = self.__indicator_position * (center_position - 10)
        return center_position - scaling_factor
    
    @property
    def relative_indicator_position(self) -> float:
        """Returns the relavtive indicator position as a float between
        1.0 and -1.0, where 0.0 is the center, 1.0 is the top, and
        -1.0 is the bottom
        """
        return self.__indicator_position

    @relative_indicator_position.setter
    def relative_indicator_position(self, new_value: Union[float, int]) -> None:
        """Sets the relative position of the indicator. Has to be a float between 1.0 and 
        -1.0, where 1.0 is the top, and -1.0 is the bottom

        Args:
            new_value (Union[float, int]): The new relative position, between 1.0 and -1.0
        """
        if -1.0 <= new_value <=1.0:
            self.__indicator_position = new_value
        else: 
            self.__indicator_position = -1.0 if new_value < -1 else 1.0
        
    @property
    def target_box_position(self) -> float:
        """Fetches the relative position of the target box, where 1.0 is the highest
        position, and -1.0 is the lowest position.

        Returns:
            float: The relative position of the target box.
        """
        return self.__target_box_position

    @target_box_position.setter
    def target_box_position(self, new_value: float) -> None:
        if -1.0 <= new_value <=1.0:
            self.__target_box_position = new_value
        else:
            self.__target_box_position = -1.0 if new_value < -1.0 else 1.0

    def get_accuracy(self) -> float:
        """Calculates the difference between the top of the indicator bar and the center
        of the target box. If negative, the indicator is lower, and vica versa.

        Returns:
            float: Difference between the top of the indicator bar and the center
        of the target box.
        """
        return self.absolute_indicator_position - self.target_box_center

    def set_indicator_color(self) -> None:
        """From the difference between the middle of the target box and the top of 
        the indicator bar, calculate and set the color of both.
        """
            
        difference = abs(
            self.absolute_indicator_position - self.target_box_center
        )
            
        color_change = difference/self.max_difference
        if difference > self.max_difference:
            color_change = 1
                        
        self.indicator_color.setGreen(
            255 - int(255 * color_change)
        )
        self.indicator_color.setRed(
            0 + int(255 * color_change)
        )

    def set_indicator_position(self, position: Union[float, int]) -> None:
        """Set the height of the indicator bar, and then set the color of 
        both it and the target box. -1.0 is the lowest position and 1.0 is the highest.

        Args:
            height (float): The new height of the indicator bar, from 1.0 to -1.0.
        """
        self.relative_indicator_position = position
        self.set_indicator_color()
        self.update()

    def set_target_box_position(self, position: Union[float, int]) -> None:
        """Set the position of the target box and update the color scheme.
        -1.0 is the lowest, and 1.0 is the highest.

        Args:
            height (float): The new position of the indicator bar. From -1.0 to 1.0.
        """
        self.target_box_position = position
        self.set_indicator_color()
        self.update()

    def paintEvent(self, event) -> None:
        """Paints the indicator bar and the target box.
        """
        # Fetch some values to decrease how many times these needs to
        # be calculated
        target_box_top = self.target_box_top
        target_box_center = self.target_box_center
        target_box_bottom = self.target_box_bottom
            
        # Initialize the painter event
        super().paintEvent(event) 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)     
        
        # Draw a transparent rectangle around the entire frame
        painter.setBrush(Qt.transparent)
        rect = QRectF(
            10, 
            10, 
            self.width() - 20, 
            self.height() - 20
        )
        painter.drawRoundedRect(rect, 0, 0)

        # Create a gradient
        gradient = QLinearGradient(
            0, 
            target_box_top, 
            0, 
            target_box_bottom
        )
        # Copy the QColor object from self.indicator_color and
        # change alpha values to use in the gradient
        center_color = copy.copy(self.indicator_color)
        center_color.setAlpha(255)
        
        edge_color = copy.copy(center_color)
        edge_color.setAlpha(0)

        gradient.setColorAt(0, edge_color)
        gradient.setColorAt(0.5, center_color)
        gradient.setColorAt(1, edge_color)
        
        # Create the target box and set color to the gradient
        painter.setBrush(gradient) 
        painter.setPen(Qt.transparent)
        rect = QRectF( 
            10, 
            target_box_top, 
            self.width() -20, 
            self.target_box_height
        )
        painter.drawRect(rect) # Draw the target box
        
        # Draw a black line through the center of the target box
        painter.setPen(Qt.black) 
        painter.drawLine( 
            10, 
            target_box_center, 
            self.width() - 10 , 
            target_box_center
        )
        
        painter.setBrush(self.indicator_color) # Set color
        # Define points of a triangle
        p1 = QPoint(0, self.absolute_indicator_position + 10)
        p2 = QPoint(10, self.absolute_indicator_position)
        p3 = QPoint(0, self.absolute_indicator_position - 10)
        triangle = [p1, p2, p3]
        painter.drawPolygon(triangle)
        
        # Define points of a triangle
        p1 = QPoint(self.width(), self.absolute_indicator_position + 10)
        p2 = QPoint(self.width() - 10, self.absolute_indicator_position)
        p3 = QPoint(self.width(), self.absolute_indicator_position - 10)
        triangle = [p1, p2, p3]
        painter.drawPolygon(triangle)
        
        if abs(self.absolute_indicator_position - self.target_box_center) < 10:
            # Define points of a triangle
            p1 = QPoint(0, self.absolute_indicator_position + 5)
            p2 = QPoint(5, self.absolute_indicator_position)
            p3 = QPoint(0, self.absolute_indicator_position - 5)
            triangle = [p1, p2, p3]
            painter.drawPolygon(triangle)
            
            painter.setBrush(Qt.green)
            # Define points of a triangle
            p1 = QPoint(self.width(), self.absolute_indicator_position + 5)
            p2 = QPoint(self.width() - 5, self.absolute_indicator_position)
            p3 = QPoint(self.width(), self.absolute_indicator_position - 5)
            triangle = [p1, p2, p3]
            painter.drawPolygon(triangle)

        
        # Create the indicator bar
        #rect = QRectF(
        #    10, 
        #    indicator_top, 
        #    self.width() -20, 
        #    self.height()
        #)
        #painter.setBrush(self.indicator_color) # Set color 
        #painter.drawRect(rect) # Draw the indicator bar

    def animate_indicator_position(self, 
        new_height: Union[float, int], 
        duration: int
    ) -> None:
        """Animates the height movement and color change of the indicator bar, where
        0 is the lowest, and 1 is the highest height of the indicator bar

        Args:
            new_height (float): The new height of the indicator bar, from 0.0 to 1.1.
            duration (int): Duration of the animation in ms.
        """
        
        self.indicator_animation = QVariantAnimation(self)
        self.indicator_animation.setDuration(duration)  # Animation duration in milliseconds
        #self.indicator_animation.setEasingCurve(QEasingCurve.BezierSpline)
        self.indicator_animation.setStartValue(self.relative_indicator_position)
        self.indicator_animation.setEndValue(float(new_height))  # End height of the rectangle
        self.indicator_animation.valueChanged.connect(self.set_indicator_position)
        self.indicator_animation.start()    
    
    def animate_target_box_position(self, 
        new_position: Union[float, int], 
        duration: int
    ) -> None:
        """Animates the movement of the target box position.

        Args:
            new_position (float): The new position of the target box, where 0 is the lowest, and
            1 is the highst position.
            duration (int): The duration of the animation in ms.
        """
        
        self.target_box_animation = QVariantAnimation(self)
        self.target_box_animation.setDuration(duration)  # Animation duration in milliseconds
        self.target_box_animation.setEasingCurve(QEasingCurve.OutBack)
        self.target_box_animation.setStartValue(self.target_box_position)
        self.target_box_animation.setEndValue(float(new_position))  # End position of the box
        self.target_box_animation.valueChanged.connect(self.set_target_box_position)
        self.target_box_animation.start()    
            
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
        self.max_target_box_difference = 15.0
        
    
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
        
        

        self.plane = Plane(parent = self)
        self.plane.y_offset = 39
        self.plane.set_rotation_angle(0.)
        self.plane.set_y_position(1)

        self.target_box = Target_box(self, self.plane)
        self.target_box.y_offset = 0
        self.target_box.y_position = 0
        
        self.animate_plane_rotation(60, 1000)
        self.animate_target_box_rotation(-60, 1000)
   
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

    def animate_target_box_position(self, end_x: float, end_y: int, duration: int) -> None:
        """Starts the animation that rotates the plane to a new angle.

            Args:
                end_angle (float): The angle at which the animation ends.
                duration (int): Duration of the animation in ms.
            """
            
        self.tbplane_animation = QVariantAnimation(self)
        self.tbplane_animation.setDuration(duration)  # Animation duration in milliseconds
        self.tbplane_animation.setEasingCurve(QEasingCurve.BezierSpline)
        self.tbplane_animation.setStartValue(
            QPointF(self.target_box.x_position, self.target_box.y_position)
        )
        self.tbplane_animation.setEndValue(
            QPointF(end_x, end_y)
        )
        self.tbplane_animation.valueChanged.connect(
            partial(self.set_target_box_position)
        )
        self.tbplane_animation.start()

    def animate_target_box_rotation(self, end_angle: float, duration: int) -> None:
        """
        Starts the animation that rotates the target box around the plane.
        """
        """Starts the animation that rotates the target box around the plane
        to a new angle.

            Args:
                end_angle (float): The angle at which the animation ends.
                duration (int): The duration of the animation in ms.
            """
        self.target_box_animation = QVariantAnimation(self)
        self.target_box_animation.setDuration(duration)  # Animation duration in milliseconds
        self.target_box_animation.setEasingCurve(QEasingCurve.OutBack)
        self.target_box_animation.setStartValue(
            self.target_box.rotation_angle()
        )
        self.target_box_animation.setEndValue(float(end_angle))
        self.target_box_animation.valueChanged.connect(
            partial(self.target_box.set_rotation_angle)
        )
        self.target_box_animation.start()
 
    def animate_plane_position(self, end_x: float, end_y: float, duration: int) -> None:
        """Starts the animation that rotates the plane to a new angle.

            Args:
                end_angle (float): The angle at which the animation ends.
                duration (int): Duration of the animation in ms.
            """
            
        self.plane_animation = QVariantAnimation(self)
        self.plane_animation.setDuration(duration)  # Animation duration in milliseconds
        self.plane_animation.setEasingCurve(QEasingCurve.BezierSpline)
        self.plane_animation.setStartValue(
            QPointF(self.plane.x_position, self.plane.y_position)
        )
        self.plane_animation.setEndValue(
            QPointF(end_x, end_y)
        )
        self.plane_animation.valueChanged.connect(
            partial(self.set_plane_position)
        )
        self.plane_animation.start()

    def animate_plane_rotation(self, end_angle: float, duration: int) -> None:
        """Starts the animation that rotates the plane to a new angle.

            Args:
                end_angle (float): The angle at which the animation ends.
                duration (int): Duration of the animation in ms.
            """
            
        self.plane_animation = QVariantAnimation(self)
        self.plane_animation.setDuration(duration)  # Animation duration in milliseconds
        self.plane_animation.setEasingCurve(QEasingCurve.BezierSpline)
        self.plane_animation.setStartValue(self.plane.rotation_angle())
        self.plane_animation.setEndValue(float(end_angle))
        self.plane_animation.valueChanged.connect(
            partial(self.plane.set_rotation_angle)
        )
        self.plane_animation.start()
 


if __name__ == "__main__":

    application = QApplication(sys.argv)
    ja = Frontend()
    ja.show()
    sys.exit(application.exec_())