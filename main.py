from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem, QGraphicsSimpleTextItem, QSlider, QPushButton
from PyQt5.QtGui import QFont, QWheelEvent, QFontDatabase, QMouseEvent
from PyQt5.QtCore import Qt, QPointF

import sys
from tkinter import filedialog, Tk

from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTRect, LTLine, LTChar
import io


class TextBlock:
    def __init__(self, text, x0, y0, x1, y1, font_size):
        self.text = text
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.font_size = font_size


class LineBlock:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


class RectBlock:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


def get_font_info(element):
    font_size = 0
    for obj in element._objs:
        if isinstance(obj, LTChar):
            font_size = obj.size
            break
    return font_size


def select_pdf_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path


def create_pdf(elements, font_path, original_page_size):
    output_path = "output.pdf"
    pdfmetrics.registerFont(TTFont('custom_font', font_path))
    writer = PdfWriter()
    for page_elements in elements:
        packet = io.BytesIO()
        new_page_size = [original_page_size[1], original_page_size[0]]
        can = canvas.Canvas(packet, pagesize=new_page_size)
        for block in page_elements:
            if isinstance(block, TextBlock):
                can.setFont('custom_font', block.font_size)
                can.drawString(block.x0, block.y0 + 2, block.text)
            elif isinstance(block, LineBlock):
                can.line(block.x0, block.y0, block.x1, block.y1)
            elif isinstance(block, RectBlock):
                can.rect(block.x0, block.y0, block.x1 - block.x0, block.y1 - block.y0)
        can.save()

        packet.seek(0)
        overlay = PdfReader(packet)
        page = overlay.pages[0]
        writer.add_page(page)

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    print("PDF saved successfully.")


class MainWindow(QMainWindow):
    def __init__(self, elements, original_page_size):
        super().__init__()
        self.setWindowTitle("PDF Elements Viewer")
        self.setGeometry(100, 100, original_page_size[0], original_page_size[1] + 50)
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

        # Создаем кнопки для переключения страниц
        self.button_previous = QPushButton("← Предыдущая")
        self.button_previous.clicked.connect(self.show_previous_page)
        layout.addWidget(self.button_previous)
        self.button_next = QPushButton("Следующая →")
        self.button_next.clicked.connect(self.show_next_page)
        layout.addWidget(self.button_next)
        # Создаем кнопки для добавления элементов
        self.button_select_file = QPushButton("Выбрать файл")
        self.button_select_file.clicked.connect(self.select_pdf_file_dialog)
        layout.addWidget(self.button_select_file)
        self.button_save_pdf = QPushButton("Сохранить PDF")
        self.button_save_pdf.clicked.connect(self.save_pdf)
        layout.addWidget(self.button_save_pdf)

        self.button_add_text_block = QPushButton("Добавить текстовый блок")
        self.button_add_text_block.clicked.connect(self.add_text_block)
        layout.addWidget(self.button_add_text_block)

        self.button_add_line = QPushButton("Добавить линию")
        self.button_add_line.clicked.connect(self.add_line)
        layout.addWidget(self.button_add_line)

        # Отображаем элементы на графической сцене
        self.elements = elements
        self.original_page_size = original_page_size
        self.current_page = 0
        self.update_scene()

    def update_scene(self):
        self.scene.clear()
        scale_factor = self.scale_slider.value() / 100.0

        for element in self.elements[self.current_page]:
            if isinstance(element, TextBlock):
                self.display_text(element, self.original_page_size[1], scale_factor)
            elif isinstance(element, LineBlock):
                self.display_line(element, self.original_page_size[1], scale_factor)
            elif isinstance(element, RectBlock):
                self.display_rect(element, self.original_page_size[1], scale_factor)

    def update_scale(self):
        self.update_scene()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() / 120  # Получаем направление прокрутки колеса
        current_scale = self.scale_slider.value()
        new_scale = max(1, min(500, current_scale + delta * 10))
        self.scale_slider.setValue(int(new_scale))

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_scene()

    def show_next_page(self):
        if self.current_page < len(self.elements) - 1:
            self.current_page += 1
            self.update_scene()

    def display_text(self, text_element, page_height, scale_factor):
        id = QFontDatabase.addApplicationFont("gosttypeb.ttf")
        _fontstr = QFontDatabase.applicationFontFamilies(id)[0]
        _font = QFont(_fontstr, int(text_element.font_size - 1))
        text_item = QGraphicsSimpleTextItem(text_element.text)
        text_item.setPos((text_element.x0 + 10) * scale_factor, page_height - text_element.y1 * scale_factor)
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

    def select_pdf_file_dialog(self):
        input_path = select_pdf_file()
        if input_path:
            self.elements = parse_pdf(input_path)
            self.original_page_size = get_original_page_size(input_path)
            self.current_page = 0
            self.update_scene()

    def add_text_block(self):
        self.scene.mousePressEvent = self.text_block_mouse_press_event

    def text_block_mouse_press_event(self, event: QMouseEvent):
        print(1)
        if event.button() == Qt.LeftButton:
            print(1.2)
            x,y = QMouseEvent.pos()
            print(1.3)
            scale_factor = self.scale_slider.value() / 100.0
            x /= scale_factor
            y /= scale_factor
            font_size = 12  # Set default font size
            text_block = TextBlock("Your Text", x, y, font_size)
            print(2)
            self.elements[self.current_page].append(text_block)
            print(3)
            self.display_text(text_block, self.original_page_size[1], scale_factor)
            print(4)
            self.scene.mousePressEvent = None

    def add_line(self):
        self.scene.mousePressEvent = self.line_mouse_press_event
        self.line_start_point = None

    def line_mouse_press_event(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.line_start_point is None:
                self.line_start_point = event.pos()
            else:
                x0 = self.line_start_point.x()
                y0 = self.line_start_point.y()
                x1 = event.pos().x()
                y1 = event.pos().y()
                scale_factor = self.scale_slider.value() / 100.0
                x0 /= scale_factor
                y0 /= scale_factor
                x1 /= scale_factor
                y1 /= scale_factor
                line_block = LineBlock(x0, y0, x1, y1)
                self.elements[self.current_page].append(line_block)
                self.display_line(line_block, self.original_page_size[1], scale_factor)
                self.line_start_point = None
                self.scene.mousePressEvent = None

    def save_pdf(self):
        font_path = "gosttypeb.ttf"
        create_pdf(self.elements, font_path, self.original_page_size)


def parse_pdf(input_path):
    elements = []
    for page_layout in extract_pages(input_path):
        page_elements = []
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_lines in element:
                    text = text_lines.get_text().strip()
                    x0, y0, x1, y1 = text_lines.bbox
                    font_size = get_font_info(text_lines)
                    text_block = TextBlock(text, x0, y0,x1,y1, font_size)
                    page_elements.append(text_block)

            elif isinstance(element, LTLine):
                x0, y0, x1, y1 = element.bbox
                line_block = LineBlock(x0, y0, x1, y1)
                page_elements.append(line_block)
            elif isinstance(element, LTRect):
                x0, y0, x1, y1 = element.bbox
                rect_block = RectBlock(x0, y0, x1, y1)
                page_elements.append(rect_block)
        elements.append(page_elements)
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