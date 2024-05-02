from __future__ import annotations
from QtPy import myFrame
from PyQt5.QtGui import (
    QPixmap, QPainter, QTransform, QBrush, 
    QColor, QVector3D, QLinearGradient, QFont
)
from PyQt5.QtCore import (
    QRectF, QPoint, QPointF, QRect, 
    QVariantAnimation, QEasingCurve, Qt
)
import numpy as np
from copy import copy


class Paintable_object(object):
    """
    A class representing a paintable object with position and rotation attributes.
    """

    parent: myFrame
    __relative_x_pos: float
    __relative_y_pos: float
    __rotation_angle: float
    y_offset: int
    x_offset: int
    max_rotation_angle: float
    center: QPoint
     
    def __init__(self) -> None:
        """
        Initialize the paintable object.
        """
        self.__rotation_angle = 0.
        self.__relative_x_pos = 0.
        self.__relative_y_pos = 0.
        self.x_offset = 0.
        self.y_offset = 0.  
        self.max_rotation_angle = 180

    def reset_position(self):
        """
        Reset the position and rotation of the object.
        """
        self.move(
            x_pos=0,
            y_pos=0,
            rotation_angle=0,
            duration=1
        )

    def rotation_angle(self) -> float:
        """
        Get the rotation angle of the object.

        Returns:
            float: The rotation angle.
        """
        return self.__rotation_angle
    
    def set_rotation_angle(self, new_rotation: float) -> None:
        """
        Set the rotation angle of the object.

        Args:
            new_rotation (float): The new rotation angle.
        """
        if new_rotation <= -self.max_rotation_angle:
            new_rotation = -self.max_rotation_angle
        elif new_rotation >= self.max_rotation_angle:
            new_rotation = self.max_rotation_angle
        
        self.__rotation_angle = new_rotation

    def y_position(self) -> float:
        """
        Get the y-coordinate position of the object.

        Returns:
            float: The y-coordinate position.
        """
        return self.__relative_y_pos
    
    def set_y_position(self, new_y_position: float) -> None:
        """
        Set the y-coordinate position of the object.

        Args:
            new_y_position (float): The new y-coordinate position.
        """
        if new_y_position <= -1. or new_y_position >= 1. :
            new_y_position /= abs(new_y_position)
              
        self.__relative_y_pos = new_y_position

    def x_position(self) -> float:
        """
        Get the x-coordinate position of the object.

        Returns:
            float: The x-coordinate position.
        """
        return self.__relative_x_pos
        
    def set_x_position(self, new_x_position: float) -> None:
        """
        Set the x-coordinate position of the object.

        Args:
            new_x_position (float): The new x-coordinate position.
        """
        if new_x_position <= -1. or new_x_position >= 1. :
            new_x_position /= abs(new_x_position)
              
        self.__relative_x_pos = new_x_position
   
    def update_position_and_rotation(self, Vector: QVector3D) -> None:
        """
        Update the position and rotation of the object.

        Args:
            Vector (QVector3D): The vector containing new position and rotation values.
        """
        self.set_x_position(Vector.x())
        self.set_y_position(Vector.y())
        self.set_rotation_angle(Vector.z())
        if isinstance(self, Target_box): 
            self.set_color(15, 50)
        self.parent.update()
        
    def get_parent_center(self)-> QPoint:
        """
        Return the coordinate in the center of the parent frame.

        Returns:
            QPoint: Parent frame's center point.
        """
        return QPoint(
            self.parent.width() // 2,
            self.parent.height() // 2
        )
        
    def get_painter(self, painter: QPainter) -> QPainter:
        """
        Get the painter object with appropriate transformation applied.

        Args:
            painter (QPainter): The original QPainter object.

        Returns:
            QPainter: The transformed QPainter object.
        """
        center_point = self.get_center()
        
        transform = QTransform()
        transform.translate(
            center_point.x(),
            center_point.y()
        )
        transform.rotate(self.rotation_angle())
        transform.translate(
            - self.width() // 2, 
            - self.height() // 2
        )
        
        painter.setTransform(transform)   
        
        return painter     

    def get_center(self) -> QPoint:
        """
        Calculate the center point of the object.

        Returns:
            QPoint: The center point of the object.
        """
        parent_center = self.get_parent_center()

        transform = QTransform()
        transform.translate(
            parent_center.x(),
            parent_center.y()
        )
        transform.translate(
            int(round(
                self.x_position() 
                * (parent_center.x() - self.width() / 2),
                0
            )),
            int(round(
                - self.y_position() 
                * (parent_center.y() - self.height() / 2 - 39),
                0
            ))
        )
        
        return transform.map(QPoint(0,0))

    def get_position_in_parent_as_float(self) -> QPointF:
        """
        Calculate the position of the object relative to its parent frame.

        Returns:
            QPointF: The position of the object as a floating-point QPointF.
        """
        center = self.get_center()
        parent_center = self.get_parent_center()
        
        y = (parent_center.y() - center.y()) / (parent_center.y()/2)
        x = (parent_center.x() - center.x()) / (parent_center.x()/2)
    
        return QPointF(x, y)
        
    def move(self, 
        x_pos: float, 
        y_pos: float, 
        rotation_angle: float,
        duration: int,
        easing_curve: QEasingCurve = QEasingCurve.BezierSpline
    ) -> None:
            
        self.animation_pos = QVariantAnimation(self.parent)
        self.animation_pos.setDuration(duration)  # Animation duration in milliseconds
        self.animation_pos.setEasingCurve(easing_curve)
        self.animation_pos.setStartValue(
            QVector3D(
                self.x_position(),
                self.y_position(), 
                self.rotation_angle()
            )
        )
        self.animation_pos.setEndValue(
            QVector3D(
                x_pos,
                y_pos,
                rotation_angle
            )
        )
        self.animation_pos.valueChanged.connect(
            self.update_position_and_rotation
        )
        self.animation_pos.start()
class Plane(QPixmap, Paintable_object):
    """
    A class representing a plane object.
    Inherits from QPixmap and Paintable_object.
    """

    __slots__ = (
            "parent",
            "__relative_y_pos",
            "__relative_x_pos",
            "__rotation_angle",
            "max_rotation_angle"
            "x_offset",
            "y_offset",                    
    )
    
    def __init__(self, parent: myFrame) -> None:
        """
        Initialize the plane object.

        Args:
            parent (myFrame): The parent object.
        """
        self.parent = parent
        QPixmap.__init__(self, "resources/images/fly_new.png")
        Paintable_object.__init__(self) 
           
    def draw(self, painter: QPainter) -> None:
        """
        Draw the plane.

        Args:
            painter (QPainter): The QPainter object used for drawing.
        """
        painter = self.get_painter(painter)
        
        # Draw the pixmap representing the plane
        painter.drawPixmap(
            int(round(- self.x_offset,0)), 
            int(round(- self.y_offset,0)), 
            self
        )    
class Target_box(Paintable_object):
    
    __slots__ = (
            "parent",
            "__relative_y_pos",
            "__relative_x_pos",
            "__rotation_angle",
            "max_rotation_angle"
            "x_offset",
            "y_offset",                    
    )
    
    def __init__(self, parent, plane: Plane) -> None:
        
        # Assign top level refferences
        self.plane = plane
        self.parent = parent
        
        # Set default height and width and color
        self.__height: int = int(round(plane.height() * 0.15, 0))
        self.__width: int = int(round(plane.width() * 1.4, 0))
        self.__color = QColor(0, 255, 0, 200)
        
        Paintable_object.__init__(self)

    def get_center(self) -> QPoint:
        # Fetch the parent center coordinates
        parent_center = self.get_parent_center()

        # Create new transform and move it to the center
        transform = QTransform()
        transform.translate(
            parent_center.x(),
            parent_center.y()
        )

        transform.translate(
            int(round(
                self.x_position() 
                * (parent_center.x() - self.plane.width() / 2),
                0
            )),
            int(round(
                - self.y_position() 
                * (parent_center.y() - self.plane.height() / 2 - 39),
                0
            ))
        )
        
        return transform.map(QPoint(0,0))

    def height(self) -> int: return self.__height 
    
    def width(self) -> int: return self.__width
    
    def draw(self, painter: QPainter):
        
        painter = self.get_painter(painter)
                
        # Set color
        self.set_color(
            max_angular_difference = 30., 
            max_radial_difference = 50)
        painter.setBrush(self.__color)
        
        # Draw the target box
        painter.drawRoundedRect(
            QRectF(
                - self.x_offset,
                - self.y_offset,
                self.__width,
                self.__height
            ),
            30, # x-radius
            30  # y-radius
        )
        
        painter.drawLine(
            int(round(0 - self.x_offset,0)),
            int(round(self.height() / 2 - self.y_offset,0)),
            int(round(self.width() - self.x_offset,0)),
            int(round(self.height() / 2 - self.y_offset,0))
        )
        painter.drawLine(
            int(round(self.width() / 2 + self.x_offset,0)),
            int(round(0 + self.y_offset,0)),
            int(round(self.width() / 2 + self.x_offset,0)),
            int(round(self.height() + self.y_offset,0))
        )
            
    def set_color(self, 
        max_angular_difference: float,
        max_radial_difference: float
    ) -> QColor:
        """Calculate the angular difference between the target box and the plane.
            From this, calculate the color of the target box. Totally green if the rotation is equal,
            then gradually towards red the greater the angular divergence.
            """
        
        plane_center = self.plane.get_center()
        target_box_center = self.get_center()
        
        angular_difference = abs(self.rotation_angle()- self.plane.rotation_angle())
        radial_difference = np.sqrt(
            abs(target_box_center.x() - plane_center.x())**2
            + abs(target_box_center.y() - plane_center.y())**2
        )
        
        angular_change = angular_difference/max_angular_difference
        radial_change = radial_difference/max_radial_difference
    
        
        if angular_difference > max_angular_difference:
            angular_change = 1
            radial_change = 1
        if radial_difference > max_radial_difference:
            radial_change = 1
            angular_change = 1
    
        color_change = (angular_change + radial_change) / 2
        
        self.__color.setGreen(
            255 - int(round(255 * color_change, 0 ))
        )
        self.__color.setRed(
            0 + int(round(255 * color_change, 0))
        )
class Indicator_Target_Box(Paintable_object):
    """
    A class representing an indicator target box.
    Inherits from Paintable_object.
    """

    def __init__(self, parent: myFrame) -> None:
        """
        Initialize the indicator target box.

        Args:
            parent (myFrame): The parent object.
        """
        Paintable_object.__init__(self)
        
        # Assign parent frame
        self.parent = parent
                
        # Initialize color
        self.color = QColor(0, 255, 0, 200)  # Base color of indicator bar is green

        # Set max difference between target box center and 
        # indicator arrows before the color is all red
        self.max_difference = self.height() // 2
    
    def get_color(self) -> QColor:
        """
        Get the color of the indicator target box based on the difference between its center and partner's center.

        Returns:
            QColor: The color of the indicator target box.
        """
        color = QColor(0, 255, 0, 200)
        
        difference = abs(
            self.get_center().y() 
            - self.partner.get_center().y()
        )
        
        color_change = difference / self.max_difference
        if color_change > 1:
            color_change = 1
        
        color.setGreen(255 - int(round(255 * color_change, 0)))
        color.setRed(0 + int(round(255 * color_change, 0)))
        
        return color
    
    def height(self) -> int:
        """
        Get the height of the indicator target box.

        Returns:
            int: The height of the indicator target box.
        """
        return (0.8 * self.parent.height()) // 4
    
    def width(self) -> int:
        """
        Get the width of the indicator target box.

        Returns:
            int: The width of the indicator target box.
        """
        return int(round(0.6 * self.parent.width(), 0))
    
    def get_center(self) -> QPoint:
        """
        Get the center point of the indicator target box.

        Returns:
            QPoint: The center point of the indicator target box.
        """
        parent_center = self.get_parent_center()

        transform = QTransform()
        transform.translate(parent_center.x(), parent_center.y())

        transform.translate(
            int(round(
                self.x_position() * (parent_center.x() - self.width() / 2),
                0
            )),
            int(round(
                - self.y_position() * (parent_center.y() - self.height() / 2),
                0
            ))
        )
        
        return transform.map(QPoint(0, 0))
    
    def draw(self, painter: QPainter) -> None:
        """
        Draw the indicator target box.

        Args:
            painter (QPainter): The QPainter object used for drawing.
        """
        painter = self.get_painter(painter)
        
        # Create a gradient for the target box
        gradient = QLinearGradient(0, 0, 0, self.height())
        color = self.get_color()
        
        # Copy the QColor object from self.color and change alpha values for the gradient
        center_color = copy(color)
        center_color.setAlpha(255)
        
        edge_color = copy(center_color)
        edge_color.setAlpha(0)

        gradient.setColorAt(0, edge_color)
        gradient.setColorAt(0.5, center_color)
        gradient.setColorAt(1, edge_color)
        
        # Set the brush with the gradient
        painter.setBrush(gradient) 
        painter.setPen(Qt.transparent)
        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRect(rect)  # Draw the target box
        
        # Draw a black line through the center of the target box
        painter.setPen(Qt.black) 
        painter.drawLine(
            0, int(round(self.height() // 2,0)),
            int(round(self.width(),0)), int(round(self.height() // 2,0))
        )

    def set_partner(self, partner):
        """
        Set the partner object.

        Args:
            partner: The partner object.
        """
        self.partner = partner
class Indicator_Arrows(Indicator_Target_Box):
    """
    A class representing indicator arrows.
    Inherits from Indicator_Target_Box.
    """

    def __init__(self, parent: myFrame, partner: Indicator_Target_Box) -> None:
        """
        Initialize the indicator arrows.

        Args:
            parent (myFrame): The parent object.
            partner (Indicator_Target_Box): The partner object.
        """
        Indicator_Target_Box.__init__(self, parent)
        self.set_partner(partner)
    
    def get_center(self) -> QPoint:
        """
        Get the center point of the indicator arrows.

        Returns:
            QPoint: The center point of the indicator arrows.
        """
        parent_center = self.get_parent_center()

        transform = QTransform()
        transform.translate(parent_center.x(), parent_center.y())

        transform.translate(
            int(round(
                self.x_position() * (parent_center.x() - self.width() / 2),
                0
            )),
            int(round(
                - self.y_position() * (parent_center.y() - self.height() / 2),
                0
            ))
        )
        return transform.map(QPoint(0, 0))
  
    def draw(self, painter: QPainter) -> None:
        """
        Draw the indicator arrows.

        Args:
            painter (QPainter): The QPainter object used for drawing.
        """
        # Find center of parent and translate to that point
        center = self.get_center()
        
        transform = QTransform()
        transform.translate(center.x(), center.y())
        painter.setTransform(transform)
        
        # Calculate side length of the arrows
        side_length = int(round((self.parent.width() * 0.4) // 2, 0))
        
        # Set the brush color
        painter.setBrush(self.get_color())
        
        # Draw the left arrow
        transform.translate(- (self.parent.width() * 0.6) // 2, 0)
        painter.setTransform(transform)
        painter.drawPolygon(
            QPoint(0, 0),
            QPoint(-side_length, -side_length),
            QPoint(-side_length, side_length)
        )
        
        # Draw the right arrow
        transform.translate((self.parent.width() * 0.6) // 1, 0)
        painter.setTransform(transform)
        painter.drawPolygon(
            QPoint(0, 0),
            QPoint(side_length, side_length),
            QPoint(side_length, -side_length)
        )
        
        # Draw additional arrows if the difference between centers is small
        if abs(center.y() - self.partner.get_center().y()) < 8:
            side_length = side_length // 2
            
            # Draw upper left arrow
            transform.translate(side_length, 0)
            painter.setTransform(transform)
            painter.drawPolygon(
                QPoint(0, 0),
                QPoint(side_length, side_length),
                QPoint(side_length, -side_length)
            )
            
            # Draw upper right arrow
            transform.translate(
                -side_length - (self.parent.width() * 0.6) // 1 - side_length,
                0
            )
            painter.setTransform(transform)
            painter.drawPolygon(
                QPoint(0, 0),
                QPoint(-side_length, side_length),
                QPoint(-side_length, -side_length)
            )
class game_text(Paintable_object):
    """
    A class representing game text.
    Inherits from Paintable_object.
    """
    
    def __init__(self, parent) -> None:
        """
        Initialize the game text.

        Args:
            parent: The parent object.
        """
        Paintable_object.__init__(self)
        self.parent = parent
        self.display_text = "Game starting in 10"
        self.font = QFont("Arial", 20, QFont.Bold)
        self.auto_width = False
        self.phrase = None
    
    def set_width(self, text: str) -> None:
        
        self.phrase = text
    
    def auto_adjust(self, input_bool: bool) -> None:
        
        self.auto_width = input_bool

    
    def width(self):
        """
        Get the width of the game text.

        Returns:
            int: The width of the game text.
        """
        return 10
    
    def height(self):
        """
        Get the height of the game text.

        Returns:
            int: The height of the game text.
        """
        return 10
    
    def set_text(self, text): 
        """
        Set the display text.

        Args:
            text (str): The text to display.
        """
        self.display_text = text
        self.parent.update()
    
    def draw(self, painter, coordinate=None):
        """
        Draw the game text.

        Args:
            painter (QPainter): The QPainter object used for drawing.
            coordinate (QPoint, optional): The coordinate to draw the text. Defaults to None.
        """
        if coordinate is None:
            painter = self.get_painter(painter)
        else: 
            transform = QTransform()
            transform.translate(coordinate.x(), coordinate.y())
            painter.setTransform(transform)
        
        transform = painter.transform()
        transform.translate(
            self.width()//2,
            self.height()//2
        )
        painter.setTransform(transform)
        
        painter.setFont(self.font)

        # Set color to white
        painter.setPen(QColor(Qt.transparent))

        if self.auto_width:
            text_width = painter.fontMetrics().width(self.display_text)
        else:
            text_width = painter.fontMetrics().width(self.phrase)
        
        text_height = painter.fontMetrics().height()
        rect_width = round(text_width* 1.3)
        rect_height = round(text_height * 1.3)
        
        transform = painter.transform()
        transform.translate(
            -rect_width//2,
            -rect_height//2
        )
        
        painter.setTransform(transform)
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.drawRoundedRect(0, 0, rect_width, rect_height, 10, 10)

        painter.setPen(Qt.white)
        # Draw text at the center
        painter.drawText(
            (rect_width - text_width) // 2,  
            rect_height - (rect_height - text_height) - 2, 
            self.display_text
        )   
class TextBox(Paintable_object):
    def __init__(self, parent, text, color=QColor(0, 0, 0, 70), rotation_angle=0):
        Paintable_object.__init__(self)
        self.text = text
        self.color = color
        self.rotation_angle = rotation_angle
        self.parent = parent

    def draw(self, painter):
      
        #painter.setRenderHint(QPainter.Antialiasing)
        #painter.translate(self.parent.width()//2, self.parent.height()//2)

        transform = QTransform()
        painter.setTransform(transform)
        # Set color and font for the text box
        painter.setBrush(self.color)
        painter.setFont(QFont("Arial", 16))  # Adjust font style and size as needed

        # Calculate the size of the text to determine the rectangle size
        rect = QRect(0, 0, self.parent.width(), self.parent.height())
        #rect.moveCenter(QPoint(0, 0))

        # Draw the rectangle
        painter.drawRect(rect)
        painter.setPen(QColor(255, 255, 255))  # Set text color, white here
        painter.drawText(rect, Qt.AlignCenter, self.text)
