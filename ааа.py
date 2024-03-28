from itertools import groupby
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
    def __init__(self, text, x0, y0, x1, y1, font_size, page_num):
        self.text = text
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.font_size = font_size
        self.page_num = page_num

class LineBlock:
    def __init__(self, x0, y0, x1, y1, page_num):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.page_num = page_num

class RectBlock:
    def __init__(self, x0, y0, x1, y1, page_num):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.page_num = page_num

def get_font_info(element):
    font_size = 0
    for obj in element._objs:
        if isinstance(obj, LTChar):
            font_size = obj.size
            break
        print("ошибка размера шрифта")
        return 10
    return  font_size




def parse_pdf(input_path):
    elements = []
    x=0
    for page_num, page_layout in enumerate(extract_pages(input_path), 1):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_lines in element:
                    text=text_lines.get_text().strip()
                    x0, y0, x1, y1 = text_lines.bbox
                    font_size = get_font_info(text_lines)
                    text_block = TextBlock(text, x0, y0, x1, y1, font_size, page_num)
                    elements.append(text_block)




            elif isinstance(element, LTLine):
                x0, y0, x1, y1 = element.bbox
                line_block = LineBlock(x0, y0, x1, y1, page_num)
                elements.append(line_block)
            elif isinstance(element, LTRect):
                x0, y0, x1, y1 = element.bbox
                rect_block = RectBlock(x0, y0, x1, y1, page_num)
                elements.append(rect_block)
    return elements

def get_original_page_size(input_path):
    with open(input_path, 'rb') as file:
        reader = PdfReader(file)
        page = reader.pages[0]
        width = page.mediabox.height
        height = page.mediabox.width
    return width, height

def create_pdf(elements, font_path, original_page_size):
    output_path=save_pdf_file()
    pdfmetrics.registerFont(TTFont('custom_font', font_path))
    writer = PdfWriter()

    for page_num, page_elements in groupby(elements, key=lambda x: x.page_num):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=original_page_size)
        for block in page_elements:
            if isinstance(block, TextBlock):
                can.setFont('custom_font', block.font_size)
                can.drawString(block.x0, block.y0+2, block.text)
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

def select_pdf_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path

def save_pdf_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfile(filetypes=[("PDF files", "*.pdf")])
    return file_path

def main():
    input_path = select_pdf_file()

    font_path = 'gosttypeb.ttf'

    elements = parse_pdf(input_path)
    original_page_size = get_original_page_size(input_path)
    # Создание PDF-файла с отображением всех элементов
    create_pdf( elements, font_path, original_page_size)
    print("PDF created successfully.")
    # id = QFontDatabase.addApplicationFont("gosttypeb.ttf")
    # _fontstr = QFontDatabase.applicationFontFamilies(id)[0]
    # _font = QFont(_fontstr, 8)
    # app.setFont(_font) установка шрифта в qt
if __name__ == "__main__":
    main()