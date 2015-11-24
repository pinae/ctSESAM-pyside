#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
import math


class PasswordStrengthSelector(QtGui.QWidget, object):
    strength_changed = QtCore.Signal((int, int))

    """
    This Widget is used for selecting a password strength. The x direction implies the length of the password while
    the y direction expresses the complexity in 6 steps.
    """
    def __init__(self):
        super(PasswordStrengthSelector, self).__init__()
        self.setMinimumSize(8, 8)
        self.min_length = 4
        self.max_length = 10
        self.length = 0
        self.complexity = -1
        self.color_matrix = []
        self.digit_count = 10
        self.lower_count = 36
        self.upper_count = 36
        self.extra_count = 24
        self.calculate_width()

    def set_min_length(self, min_length):
        """
        Sets the minimum password length. This also changes the minimum size of the widget.

        :param min_length: minimum password length
        :type min_length: int
        """
        self.min_length = min_length
        self.calculate_width()

    def set_max_length(self, max_length):
        """
        Sets the maximum password length. This also changes the minimum size of the widget.

        :param max_length: maximum password length
        :type max_length: int
        """
        self.max_length = max_length
        self.calculate_width()

    def set_extra_count(self, extra_count):
        """
        Sets the number of extra characters. This is used for the coloring.

        :param extra_count: number of extra characters
        :type extra_count: int
        """
        self.extra_count = extra_count
        self.calculate_width()
        self.repaint()

    def calculate_width(self):
        """
        Calculate the minimum width and the color matrix
        """
        self.setMinimumWidth(self.max_length - self.min_length)
        self.color_matrix = []
        complexity = [self.digit_count,
                      self.lower_count,
                      self.upper_count,
                      self.digit_count + self.lower_count,
                      self.lower_count + self.upper_count,
                      self.lower_count + self.upper_count + self.digit_count,
                      self.lower_count + self.upper_count + self.digit_count + self.extra_count]
        complexity.reverse()
        for i in range(self.max_length-self.min_length+1):
            line = []
            for comp in complexity:
                s = 20
                tianhe2_years = (pow(comp, (i+self.min_length))*0.4/3120000)/(60*60*24*365)
                strength_red = 1-s/(s+math.log(tianhe2_years+1, 50))
                strength_green = 1-s/(s+math.log(tianhe2_years+1, 1.2))
                color = QtGui.QColor(int(round(215*(1.0-strength_red))), int(round(190*strength_green)), 0)
                line.append(color)
            self.color_matrix.append(line)

    def paintEvent(self, *args):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        size = self.size()
        x_coords = [0, size.width()-1]
        for i in range(1, self.max_length-self.min_length+1):
            x_coords.insert(-1, int(round(i*(size.width()-1)/(self.max_length-self.min_length+1))))
        y_coords = [0, size.height()-1]
        for i in range(1, 7):
            y_coords.insert(-1, int(round(i*(size.height()-1)/7)))
        for i in range(1, len(x_coords)):
            for j in range(1, len(y_coords)):
                color = self.color_matrix[i-1][j-1]
                pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                qp.setBrush(color)
                qp.drawRect(x_coords[i-1], y_coords[j-1], x_coords[i]-x_coords[i-1],  y_coords[j]-y_coords[j-1])
        pen = QtGui.QPen(QtGui.QColor(140, 140, 140), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(QtCore.Qt.NoBrush)
        qp.drawRect(0, 0, size.width()-1, size.height()-1)
        if self.length > 0 and self.complexity >= 0:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setBrush(QtCore.Qt.NoBrush)
            qp.drawRect(x_coords[self.length-self.min_length],
                        y_coords[6-self.complexity],
                        x_coords[self.length-self.min_length+1]-x_coords[self.length-self.min_length],
                        y_coords[7-self.complexity]-y_coords[6-self.complexity])

    def mousePressEvent(self, event):
        size = self.size()
        self.length = max(
            self.min_length,
            min(self.max_length,
                int(math.floor(event.pos().x()/(size.width()-2) *
                    (self.max_length-self.min_length+1) +
                    self.min_length))))
        self.complexity = max(0, min(6, int(math.floor(7-event.pos().y()/(size.height()-2)*7))))
        self.repaint()
        self.strength_changed.emit(self.complexity, self.length)

    def mouseMoveEvent(self, event):
        self.mousePressEvent(event)

    def get_length(self):
        """
        Returns the selected length. If no length is selected it returns 0.

        :return: selected length
        :rtype: int
        """
        return self.length

    def set_length(self, length):
        """
        Sets the length. If smaller than min_length or negative or bigger than max_length the selection is removed.

        :param length: new length or 0 for no selection
        :type length: int
        """
        if self.min_length <= length <= self.max_length:
            self.length = length
        else:
            self.length = 0
            self.complexity = -1
        self.repaint()
        self.strength_changed.emit(self.complexity, self.length)

    def get_complexity(self):
        """
        Returns the complexity or -1 if nothing is selected.

        :return: selected complexity
        :rtype: int
        """
        return self.complexity

    def set_complexity(self, complexity):
        """
        Sets the complexity if in the range 0-6 or removes the selection otherwise.

        :param complexity: complexity if in the range 0-6
        :type complexity: int
        """
        if 0 <= complexity <= 6:
            self.complexity = complexity
        else:
            self.complexity = -1
            self.length = 0
        self.repaint()
        self.strength_changed.emit(self.complexity, self.length)
