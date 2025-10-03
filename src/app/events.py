from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt

class EventHandler:
    def __init__(self, gui):
        self.gui = gui
        self.gui.canvas.mousePressEvent = self.on_mouse_click
        self.gui.canvas.keyPressEvent = self.on_key_press

    def on_mouse_click(self, event):
        if event.button() == Qt.LeftButton:
            self.add_positive_point(event.pos())
        elif event.button() == Qt.RightButton:
            self.add_negative_point(event.pos())

    def on_key_press(self, event):
        if event.key() == Qt.Key_N:
            self.gui.add_new_object()
        elif event.key() == Qt.Key_Tab:
            self.gui.switch_object()

    def add_positive_point(self, position):
        # Logic to add a positive annotation point
        self.gui.annotation_controller.add_positive_point(position)

    def add_negative_point(self, position):
        # Logic to add a negative annotation point
        self.gui.annotation_controller.add_negative_point(position)