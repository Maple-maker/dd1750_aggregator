from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io

class DD1750Generator:
    ITEMS_PER_PAGE = 18
    
    def generate_merged_form(self, items, admin_data):
        output = io.BytesIO()
        total_pages = max(1, (len(items) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        
        c = canvas.Canvas(output, pagesize=letter)
        
        for page_num in range(total_pages):
            start_idx = page_num * self.ITEMS_PER_PAGE
            end_idx = min(start_idx + self.ITEMS_PER_PAGE, len(items))
            page_items = items[start_idx:end_idx]
            
            self._draw_page(c, page_items, admin_data, page_num + 1, total_pages)
            if page_num < total_pages - 1:
                c.showPage()
        
        c.save()
        output.seek(0)
        return output.getvalue()
    
    def _draw_page(self, c, items, admin_data, page_num, total_pages):
        width, height = letter
        c.setFont("Helvetica-Bold", 10)
        c.drawString(inch * 1.0, height - inch * 0.8, "PACKING LIST")
        c.setFont("Helvetica", 8)
        c.drawString(inch * 5.0, height - inch * 0.8, "DD FORM 1750, SEP 70 (EG)")
        
        if admin_data.get('packed_by'):
            c.drawString(inch * 0.6, height - inch * 2.2, admin_data['packed_by'])
        c.drawString(inch * 5.0, height - inch * 1.5, f"PAGE {page_num} OF {total_pages}")
        
        c.setFont("Helvetica-Bold", 7)
        c.drawString(inch * 0.6, height - inch * 3.0, "BOX NO.")
        c.drawString(inch * 1.2, height - inch * 3.0, "CONTENTS")
        c.line(inch * 0.5, height - inch * 3.1, inch * 7.5, height - inch * 3.1)
        
        c.setFont("Helvetica", 7)
        for idx, item in enumerate(items):
            y_pos = height - inch * 3.5 - (idx * 24)
            if item.get('box_no'):
                c.drawString(inch * 0.6, y_pos, item['box_no'])
            if item.get('nomenclature'):
                c.drawString(inch * 1.2, y_pos, item['nomenclature'][:40])
            c.line(inch * 0.5, y_pos - 15, inch * 7.5, y_pos - 15)
