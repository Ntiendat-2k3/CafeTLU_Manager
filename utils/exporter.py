from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))

class PDFExporter:
    @staticmethod
    def export_order(order_id, items, total):
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        filename = os.path.join(downloads_dir, f"order_{order_id}.pdf")
        c = canvas.Canvas(filename, pagesize=A4)

        c.setFont("Arial", 16)
        c.drawString(50, 800, "CAFE TLU")

        c.setFont("Arial", 12)
        c.drawString(50, 780, f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawString(50, 760, f"Mã đơn: #{order_id}")

        y = 700
        c.setFont("Arial-Bold", 12)
        c.drawString(50, y, "Tên món")
        c.drawString(250, y, "Đơn giá")
        c.drawString(350, y, "Số lượng")
        c.drawString(450, y, "Thành tiền")

        for item in items:
            y -= 20
            c.setFont("Arial", 12)
            c.drawString(50, y, f"{item['name']} ({item['size']})")
            c.drawString(250, y, f"{item['price']:,.0f} VND")
            c.drawString(350, y, str(item['quantity']))
            c.drawString(450, y, f"{item['price'] * item['quantity']:,.0f} VND")

        total_text = total.split(":")[1].strip()
        c.setFont("Arial-Bold", 14)
        c.drawString(400, y - 40, f"TỔNG CỘNG: {total_text}")

        c.save()