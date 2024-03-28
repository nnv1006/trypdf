import sys

from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, \
    QGraphicsLineItem, QGraphicsRectItem, QGraphicsSimpleTextItem, QSlider
from PyQt5.QtCore import Qt
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTRect, LTLine, LTChar

class MainWindow(QMainWindow):
    def __init__(self, elements, original_page_size):
        super().__init__()
        self.setWindowTitle("PDF Elements Viewer")
        self.setGeometry(100, 100, original_page_size[0], original_page_size[1])

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Создаем графическую сцену и представление
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        # Создаем ползунок масштабирования
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(1)
        self.scale_slider.setMaximum(500)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.update_scale)
        layout.addWidget(self.scale_slider)

        # Отображаем элементы на графической сцене
        self.elements = elements
        self.original_page_size = original_page_size
        self.update_scene()

    def update_scene(self):
        self.scene.clear()
        scale_factor = self.scale_slider.value() / 100.0

        for element in self.elements:
            if isinstance(element, LTTextBoxHorizontal):
                self.display_text(element, self.original_page_size[1], scale_factor)
            elif isinstance(element, LTLine):
                self.display_line(element, self.original_page_size[1], scale_factor)
            elif isinstance(element, LTRect):
                self.display_rect(element, self.original_page_size[1], scale_factor)

    def update_scale(self):
        self.update_scene()

    def update_scene(self):
            self.scene.clear()
            scale_factor = self.scale_slider.value() / 100.0

            for element in self.elements:
                if isinstance(element, LTTextBoxHorizontal):
                    self.display_text(element, self.original_page_size[1], scale_factor)
                elif isinstance(element, LTLine):
                    self.display_line(element, self.original_page_size[1], scale_factor)
                elif isinstance(element, LTRect):
                    self.display_rect(element, self.original_page_size[1], scale_factor)






    def display_text(self, text_element, page_height, scale_factor):
        
        id = QFontDatabase.addApplicationFont("gosttypeb.ttf")
        _fontstr = QFontDatabase.applicationFontFamilies(id)[0]
        _font = QFont(_fontstr, round(8*scale_factor))
        text_item = QGraphicsSimpleTextItem(text_element.get_text())
        text_item.setPos(text_element.x0 * scale_factor, page_height - text_element.y1 * scale_factor)
        text_item.setFont(_font)
        self.scene.addItem(text_item)

    def display_line(self, line_element, page_height, scale_factor):
        line_item = QGraphicsLineItem(line_element.x0 * scale_factor, page_height - line_element.y0 * scale_factor,
                                      line_element.x1 * scale_factor, page_height - line_element.y1 * scale_factor)
        self.scene.addItem(line_item)

    def display_rect(self, rect_element, page_height, scale_factor):
        rect_item = QGraphicsRectItem(rect_element.x0 * scale_factor, page_height - rect_element.y1 * scale_factor,
                                      (rect_element.x1 - rect_element.x0) * scale_factor,
                                      (rect_element.y1 - rect_element.y0) * scale_factor)
        self.scene.addItem(rect_item)


def parse_pdf(input_path):
    elements = []
    for page_num, page_layout in enumerate(extract_pages(input_path), 1):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                elements.append(element)
            elif isinstance(element, LTLine):
                elements.append(element)
            elif isinstance(element, LTRect):
                elements.append(element)
        break
    return elements

def get_original_page_size(input_path):
    with open(input_path, 'rb') as file:
        reader = PdfReader(file)
        page = reader.pages[0]
        width = int(page.mediabox[2])
        height = int(page.mediabox[3])
    return width, height

def main():
    input_path = "input.pdf"  # Путь к вашему PDF-файлу
    elements = parse_pdf(input_path)


    original_page_size = get_original_page_size(input_path)

    app = QApplication(sys.argv)
    window = MainWindow(elements, original_page_size)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()