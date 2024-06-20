import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QRect

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_selecting = False
        self.selection_complete = False 
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_color = QColor(200, 200, 200, 100)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_selecting or self.selection_complete: 
            painter = QPainter(self)
            painter.setPen(QPen(self.selection_color, 2, Qt.SolidLine))
            painter.setBrush(self.selection_color)
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if self.pixmap() is not None:
            self.is_selecting = True
            self.selection_complete = False 
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()
            self.is_selecting = False
            self.selection_complete = True

class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.original_image = None
        self.modified_image = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Image Editor")
        self.setGeometry(100, 100, 1920, 1200)

        self.label = ImageLabel(self)
        self.label.resize(1920, 1150)

        load_button = QPushButton("Load Image", self)
        load_button.clicked.connect(self.load_image)

        save_button = QPushButton("Save Image", self)
        save_button.clicked.connect(self.save_image)

        confirm_button = QPushButton("Confirm Selection", self)
        confirm_button.clicked.connect(self.apply_mask)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(load_button)
        layout.addWidget(confirm_button)
        layout.addWidget(save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.image_path = file_name
            self.original_image = cv2.imread(self.image_path)
            self.modified_image = np.copy(self.original_image)
            self.display_image(self.original_image)

    def save_image(self):
        if self.modified_image is not None:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)")
            if file_name:
                cv2.imwrite(file_name, self.modified_image)
        else:
            print("No modified image to save.")

    def display_image(self, img):
        qformat = QImage.Format_Indexed8 if len(img.shape) == 2 else QImage.Format_RGB888
        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        out_image = out_image.rgbSwapped()
        pixmap = QPixmap.fromImage(out_image)
        scaled_pixmap = pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        self.label.adjustSize()

    def apply_mask(self):
        if self.original_image is not None and not (self.label.start_point == self.label.end_point):
            scale_x = self.original_image.shape[1] / self.label.pixmap().size().width()
            scale_y = self.original_image.shape[0] / self.label.pixmap().size().height()

            pt1 = (int(min(self.label.start_point.x(), self.label.end_point.x()) * scale_x), int(min(self.label.start_point.y(), self.label.end_point.y()) * scale_y))
            pt2 = (int(max(self.label.start_point.x(), self.label.end_point.x()) * scale_x), int(max(self.label.start_point.y(), self.label.end_point.y()) * scale_y))

            result_image = np.zeros(self.original_image.shape, dtype=np.uint8)
            cv2.rectangle(result_image, pt1, pt2, (255, 255, 255), thickness=cv2.FILLED)

            self.modified_image = result_image
            self.display_image(self.modified_image)
        else:
            print("Invalid selection or original image not loaded.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ImageEditor()
    ex.show()
    sys.exit(app.exec_())