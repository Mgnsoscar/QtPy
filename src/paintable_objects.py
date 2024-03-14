from __future__ import annotations
from typing import Literal, Dict, Union, Optional
from QtPy import myFrame
from PyQt5.QtGui import QPixmap, QPainter, QTransform, QBrush, QColor, QVector3D, QLinearGradient
from PyQt5.QtCore import QRectF, QPoint, QPointF, QVariantAnimation, QEasingCurve, Qt
import math
import numpy as np
from functools import partial
from copy import copy


class Paintable_object(object):

    parent: myFrame
    __relative_x_pos: float
    __relative_y_pos: float
    __rotation_angle: float
    y_offset: int
    x_offset: int
    max_rotation_angle: float
    center: QPoint
     
    def __init__(self) -> None:
        self.__rotation_angle = 0.
        self.__relative_x_pos = 0.
        self.__relative_y_pos = 0.
        self.x_offset = 0.
        self.y_offset = 0.  
        self.max_rotation_angle = 180

    def reset_position(self):
        self.move(
            x_pos = 0,
            y_pos = 0,
            rotation_angle = 0,
            duration = 100
        )

    def rotation_angle(self) -> float:
        return self.__rotation_angle
    
    def set_rotation_angle(self, new_rotation: float) -> None:
        
        if new_rotation <= -self.max_rotation_angle:
            new_rotation = -self.max_rotation_angle
        elif new_rotation >= self.max_rotation_angle:
            new_rotation = self.max_rotation_angle
        
        self.__rotation_angle = new_rotation

    def y_position(self) -> float:
        return self.__relative_y_pos
    
    def set_y_position(self, new_y_position: float) -> None:
            
        if new_y_position <= -1. or new_y_position >= 1. :
            new_y_position /= abs(new_y_position)
              
        self.__relative_y_pos = new_y_position

    def x_position(self) -> float:
        return self.__relative_x_pos
        
    def set_x_position(self, new_x_position: float) -> None:
            
        if new_x_position <= -1. or new_x_position >= 1. :
            new_x_position /= abs(new_x_position)
              
        self.__relative_x_pos = new_x_position
   
    def update_position_and_rotation(self, Vector: QVector3D) -> None:
        self.set_x_position(Vector.x())
        self.set_y_position(Vector.y())
        self.set_rotation_angle(Vector.z())
        if isinstance(self, Target_box): self.set_color(15, 50)
        self.parent.update()
        
    def get_parent_center(self)-> QPoint:
        """Return the coordinate in the center of the parent frame.

        Returns:
            QPoint: Parent frame's center point.
        """

        return QPoint(
            self.parent.width() // 2,
            self.parent.height() // 2
        )
        
    def get_painter(self, painter: QPainter) -> QPainter:
        
        center_point = self.get_center()
        
        transform = QTransform()
        
        transform.translate(
            center_point.x(),
            center_point.y()
        )
        
        # Rotate the grid
        transform.rotate(self.rotation_angle())
        
        
        # Then move the transform back to make the object's center 
        # appear in the transform point
        transform.translate(
            - self.width() / 2, 
            - self.height() / 2
        )
        
        # Assign the transform
        painter.setTransform(transform)   
        
        return painter     

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
        
        self.parent = parent
        QPixmap.__init__(self, "resources/images/fly_new.png")
        Paintable_object.__init__(self) 
           
    def draw(self, painter: QPainter) -> None:
        
        painter = self.get_painter(painter)
        
        painter.drawPixmap(
            - self.x_offset, 
            - self.y_offset, 
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
            0 - self.x_offset,
            self.height() / 2 - self.y_offset,
            self.width() - self.x_offset,
            self.height() / 2 - self.y_offset
        )
        painter.drawLine(
            self.width() / 2 + self.x_offset,
            0 + self.y_offset,
            self.width() / 2 + self.x_offset,
            self.height() + self.y_offset
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
    
    def __init__(self, parent: myFrame) -> None:
        
        Paintable_object.__init__(self)
        
        # Assign parent frame
        self.parent = parent
                
        # Init color
        self.color = QColor( # Base color of indicator bar is green
            0, 255, 0, 200
        )

        # Set max difference between target box center and 
        # indicator arrows before the color is all red
        self.max_difference = self.height()//2
    
    def get_color(self) -> QColor:
        
        color = QColor(0, 255, 0, 200)
        
        difference = abs(
            self.get_center().y() 
            - self.partner.get_center().y()
        )
        
        color_change = difference/self.max_difference
        if color_change > 1: color_change = 1
        
        color.setGreen(
            255 - int(round(255 * color_change, 0 ))
        )
        color.setRed(
            0 + int(round(255 * color_change, 0))
        )
        
        return color
    
    def height(self) -> int: return (0.8 * self.parent.height()) // 4
    
    def width(self) -> int: return int(round(0.6 * self.parent.width(), 0))
    
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
                * (parent_center.x() - self.width() / 2),
                0
            )),
            int(round(
                - self.y_position() 
                * (parent_center.y() - self.height() / 2),
                0
            ))
        )
        
        return transform.map(QPoint(0,0))
    
    def draw(self, painter: QPainter) -> None:
        
        painter = self.get_painter(painter)
        
        # Create a gradient
        gradient = QLinearGradient(
            0, 
            0, 
            0, 
            self.height()
        )
        
        color = self.get_color()
        
        # Copy the QColor object from self.indicator_color and
        # change alpha values to use in the gradient
        center_color = copy(color)
        center_color.setAlpha(255)
        
        edge_color = copy(center_color)
        edge_color.setAlpha(0)

        gradient.setColorAt(0, edge_color)
        gradient.setColorAt(0.5, center_color)
        gradient.setColorAt(1, edge_color)
        
        # Create the target box and set color to the gradient
        painter.setBrush(gradient) 
        painter.setPen(Qt.transparent)
        rect = QRectF( 
            0, 
            0, 
            self.width(), 
            self.height()
        )
        painter.drawRect(rect) # Draw the target box
        
        # Draw a black line through the center of the target box
        painter.setPen(Qt.black) 
        painter.drawLine( 
            0, 
            self.height()//2, 
            self.width() , 
            self.height()//2
        )

    def set_partner(self, partner):
        self.partner = partner

class Indicator_Arrows(Indicator_Target_Box):
    
    def __init__(self, parent: myFrame, partner: Indicator_Target_Box) -> None:
        
        Indicator_Target_Box.__init__(self, parent)
        self.set_partner(partner)
    
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
                * (parent_center.x() - self.width() / 2),
                0
            )),
            int(round(
                - self.y_position() 
                * (parent_center.y() - self.height()  / 2),
                0
            ))
        )
        return transform.map(QPoint(0,0))
  
    def draw(self, painter: QPainter) -> None:
        
        # Find center of parent and translate to that point
        center = self.get_center()
        
        transform = QTransform()
        transform.translate(
            center.x(),
            center.y()
        )
        painter.setTransform(transform)
        
        # Calculate side length of the
        side_length = int(round((self.parent.width()*0.4)//2, 0))
        
        # set the brush color
        painter.setBrush(
            self.get_color()
        )
        
        transform.translate(
            - (self.parent.width()*0.6)//2,
            0
        )
        
        painter.setTransform(transform)
        painter.drawPolygon(
            QPoint(0, 0),
            QPoint(
                -side_length, 
                -side_length),
            QPoint(-side_length, side_length)
        )
        
        transform.translate(
            (self.parent.width()*0.6)//1,
            0
        )
        painter.setTransform(transform)
        painter.drawPolygon(
            QPoint(0, 0),
            QPoint(
                side_length, 
                side_length),
            QPoint(side_length, -side_length)
        )
        
        if abs(center.y() - self.partner.get_center().y()) < 8:
            
            side_length = side_length // 2
            
            transform.translate(
                side_length,
                0
            )
            painter.setTransform(transform)
            painter.drawPolygon(
                QPoint(0, 0),
                QPoint(
                    side_length, 
                    side_length),
                QPoint(side_length, -side_length)
            )
            
            transform.translate(
                -side_length
                -(self.parent.width()*0.6)//1
                - side_length,
                0
            )
            painter.setTransform(transform)
            painter.drawPolygon(
                QPoint(0, 0),
                QPoint(
                    -side_length, 
                    side_length),
                QPoint(-side_length, -side_length)
            )
            