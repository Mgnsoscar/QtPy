from typing import Literal, Dict, Union, Optional
from QtPy import myFrame
from PyQt5.QtGui import QPixmap, QPainter, QTransform, QBrush, QColor
from PyQt5.QtCore import QRectF, QPoint, QPointF
import math
import numpy as np


class Paintable_object(object):

    parent: myFrame
    __relative_x_pos: float
    __relative_y_pos: float
    __rotation_angle: float
    y_offset: float
    x_offset: float
     
    def __init__(self) -> None:
        self.__rotation_angle = 0.
        self.__relative_x_pos = 0.
        self.__relative_y_pos = 0.
        self.x_offset = 0.
        self.y_offset = 0.
     

    def rotation_angle(self) -> float:
        return self.__rotation_angle
    
    def set_rotation_angle(self, new_rotation: float) -> None:
        
        if new_rotation <= -90.:
            new_rotation = -90.
        elif new_rotation >= 90.:
            new_rotation = 90.
        
        self.__rotation_angle = new_rotation
        self.parent.update()

    def y_position(self) -> float:
        return self.__relative_y_pos
    
    def set_y_position(self, new_y_position: float) -> None:
            
        if new_y_position <= -1. or new_y_position >= 1. :
            new_y_position /= abs(new_y_position)
              
        self.__relative_y_pos = new_y_position
        self.parent.update()

    def x_position(self) -> float:
        return self.__relative_x_pos
        
    def set_x_position(self, new_x_position: float) -> None:
            
        if new_x_position <= -1. or new_x_position >= 1. :
            new_x_position /= abs(new_x_position)
              
        self.__relative_x_pos = new_x_position
        self.parent.update()
        
    def max_displacement_from_center(self) -> float:
            
        parent_center = self.get_parent_center()
        max_upwards_displacement = (
            parent_center.y()
            - np.sin(60/(2*np.pi)) * self.width() * 0.5
            - self.y_offset
        )
        
        max_downwards_displacement = (
            parent_center.y()
            - np.sin(60/(2*np.pi)) * self.width() * 0.5
            + self.y_offset
        )
        
        displacement_selector = {
            1  : self.__relative_y_pos * max_upwards_displacement,
            0  : 0.,
            -1 : self.__relative_y_pos * max_downwards_displacement 
        }
        return displacement_selector[math.copysign(1, self.__relative_y_pos)]
              
    def get_x_displacement_from_center(self,
        left_margin: Optional[float] = 0,
        right_margin: Optional[float] = 0,
        top_margin: Optional[float] = 0,
        bottom_margin: Optional[float] = 0
    ) -> float:
        
        centered_coordinates = self.get_centered_coordinates(
            left_margin,
            right_margin,
            top_margin,
            bottom_margin
        )
        max_horizontal_displacement = (
            centered_coordinates.x()
            - self.width() / 2
        )
        horizontal_displacement_from_center = (
            max_horizontal_displacement
            * self.__relative_x_pos
        )
        return horizontal_displacement_from_center
            
    def get_parent_center(self)-> QPoint:
        """Return the coordinate in the center of the parent frame.

        Returns:
            QPoint: Parent frame's center point.
        """

        return QPoint(
            self.parent.width() / 2,
            self.parent.height() / 2
        )
        
    def get_absolute_center(self):
        pass 
        #TODO

    def get_painter(self, painter: QPainter) -> QPainter:
        
        parent_center = self.get_parent_center()
               
        # Create new transform and move it to the center
        transform = QTransform()
        transform.translate(
            parent_center.x(),
            parent_center.y() - self.max_displacement_from_center()
        )
        
        # Rotate the grid
        transform.rotate(self.rotation_angle())
        
        # Then move the transform back to make the object's center 
        # appear in the transform point
        transform.translate(
            - self.width() / 2, 
            - self.height() / 2
        )
        
        painter.setTransform(transform)
        
        return painter
    
class Plane(QPixmap, Paintable_object):

    __slots__ = (
            "parent",
            "__relative_y_pos",
            "relative_x_pos"
            "x_offset",
            "y_offset",
            "__rotation_angle"                        
        )
    
    parent: myFrame

    
    def __init__(self, parent: myFrame) -> None:
          
        QPixmap.__init__(self, "resources/images/fly_new.png")
        self.parent = parent
        Paintable_object.__init__(self)
    
    def draw(self, painter: QPainter) -> None:
        
        sketch = self.get_painter(painter)
        
        sketch.drawPixmap(
            -self.x_offset,
            -self.y_offset,
            self
        )
    
class Target_box(Paintable_object):
    
    def __init__(self, parent, plane: Plane) -> None:
        
        self.plane = plane
        self.parent = parent
        self.__height = plane.height() * 0.15
        self.__width = plane.width() * 1.4
        self.__color = QColor(0, 255, 0, 200)
        
        Paintable_object.__init__(self)
    
    def height(self) -> float:
        return self.__height
    def width(self) -> float:
        return self.__width
    
    def draw(self, painter: QPainter):
        
        sketch = self.get_painter(painter)
        parent_center = self.get_parent_center()
        
        self.set_color(30)
        painter.setBrush(self.__color)
        painter.drawRoundedRect(
            QRectF(
                0,
                0,
                self.__width,
                self.__height
            ),
            30, # x-radius
            30  # y-radius
        )
        transform = QTransform()
        painter.setTransform(transform)
        painter.drawLine(
            0,
            parent_center.y(),
            self.parent.width(),
            parent_center.y()
        )
        
        painter.drawLine(
            parent_center.x(),
            0,
            parent_center.x(),
            self.parent.height()
        )
    
    def set_color(self, max_difference: float) -> QColor:
        """Calculate the angular difference between the target box and the plane.
            From this, calculate the color of the target box. Totally green if the rotation is equal,
            then gradually towards red the greater the angular divergence.
            """
            
        angular_difference = abs(self.rotation_angle()- self.plane.rotation_angle())
        height_difference = None
            
        color_change = angular_difference/max_difference
        if angular_difference > max_difference:
            color_change = 1
        
        self.__color.setGreen(
            255 - int(255 * color_change)
        )
        self.__color.setRed(
            0 + int(255 * color_change)
        )
        
        self.parent.update()