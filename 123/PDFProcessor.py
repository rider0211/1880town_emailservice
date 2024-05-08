from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import black, white

class PDFProcessor:
    def __init__(self, pagesize=landscape(A4)):
        self.pagesize = pagesize

    def create_text_pdf_with_border_and_background(self, output_path, text, position=(200, 500), max_width=150, font_size=20, background_color=white, border_color=black, border_width=1):
        c = canvas.Canvas(output_path, pagesize=self.pagesize)
        text_object = c.beginText()
        text_object.setFont("Helvetica", font_size)
        text_object.setTextOrigin(position[0], position[1])

        words = text.split(' ')
        lines = []
        line = ''
        text_height = font_size * 1.2  # Rough estimation of line height
        for word in words:
            if c.stringWidth(line + word, "Helvetica", font_size) <= max_width:
                line += word + ' '
            else:
                lines.append(line)
                line = word + ' '
        lines.append(line)

        text_block_height = len(lines) * text_height
        background_height = text_block_height + 5  # Padding
        background_width = max_width + 20  # Padding

        c.setStrokeColor(border_color)
        c.setLineWidth(border_width)
        c.setFillColor(background_color)
        c.rect(position[0] - 20, position[1] - background_height + 20, background_width, background_height, stroke=1, fill=1)

        c.setFillColor(black)
        for line in lines:
            text_object.textLine(line)

        c.drawText(text_object)
        c.save()

    def merge_pdfs(self, base_pdf_path, overlay_pdf_path, output_path):
        base_pdf = PdfReader(base_pdf_path)
        overlay_pdf = PdfReader(overlay_pdf_path)
        writer = PdfWriter()

        for page_number in range(len(base_pdf.pages)):
            page = base_pdf.pages[page_number]
            if page_number < len(overlay_pdf.pages):
                overlay_page = overlay_pdf.pages[page_number]
                page.merge_page(overlay_page)
            writer.add_page(page)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

# Usage
# pdf_processor = PDFProcessor()
# text_pdf = "text_overlay.pdf"
# pdf_processor.create_text_pdf_with_border_and_background(text_pdf, "Hello Emmy, nice to meet you. Your password was 'Otis123'", (150, 560))
# pdf_processor.merge_pdfs("Camel.pdf", text_pdf, "Camel1.pdf")
# pdf_processor.create_text_pdf_with_border_and_background(text_pdf, "Number: 1024", (600, 13))
# pdf_processor.merge_pdfs("Camel1.pdf", text_pdf, "Camel2.pdf")
