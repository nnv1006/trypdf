from tkinter import Tk, filedialog
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTRect, LTLine
import io

class TextBlock:
    def __init__(self, text, x0, y0, x1, y1, page_num):
        self.text = text
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.obj= "Text"
        self.page_num = page_num

class LineBlock:
    def __init__(self, x0, y0, x1, y1, page_num):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.obj = "Line"
        self.page_num = page_num

class RectBlock:
    def __init__(self, x0, y0, x1, y1, page_num):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.obj = "Rect"
        self.page_num = page_num

def parse_pdf(input_path):
    elements = []
    for page_num, page_layout in enumerate(extract_pages(input_path), 1):
        for element in page_layout:

            if isinstance(element, LTTextBoxHorizontal):
                text = element.get_text().strip()
                x0, y0, x1, y1 = element.bbox
                text_block = TextBlock(text, x0, y0, x1, y1, page_num)
                elements.append(text_block)
            elif isinstance(element, LTLine):
                x0, y0, x1, y1 = element.bbox
                line_block = LineBlock(x0, y0, x1, y1, page_num)
                elements.append(line_block)
            elif isinstance(element, LTRect):
                x0, y0, x1, y1 = element.bbox
                rect_block = RectBlock(x0, y0, x1, y1, page_num)
                elements.append(rect_block)
            elif isinstance(element):
                print(element) # выведет как только получим изображение либо другой не описанный объект
        break
    return elements
def select_pdf_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path







def main():
    input_path = select_pdf_file()
    if not input_path:
        print("No file selected.")
        return






if __name__ == "__main__":
    main()