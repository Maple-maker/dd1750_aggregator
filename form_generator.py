from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io

class DD1750Generator:
    ITEMS_PER_PAGE = 18
    ROW_HEIGHT = 24
    
    def generate_merged_form(self, items, admin_data):
        output = io.BytesIO()
        total_items = len(items)
        total_pages = max(1, (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        
        c = canvas.Canvas(output, pagesize=letter)
        
        for page_num in range(total_pages):
            start_idx = page_num * self.ITEMS_PER_PAGE
            end_idx = min(start_idx + self.ITEMS_PER_PAGE, total_items)
            page_items = items[start_idx:end_idx]
            
            self._draw_page(c, page_items, admin_data, page_num + 1, total_pages)
            if page_num < total_pages - 1:
                c.showPage()
        
        c.save()
        output.seek(0)
        return output.getvalue()
    
    def _draw_page(self, c, items, admin_data, page_num, total_pages):
        width, height = letter
        
        # Draw title
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch * 1.0, height - inch * 0.8, "PACKING LIST")
        c.setFont("Helvetica", 9)
        c.drawString(inch * 5.0, height - inch * 0.8, "DD FORM 1750, SEP 70 (EG)")
        
        # Draw admin info section
        y_pos = height - inch * 1.5
        
        c.setFont("Helvetica-Bold", 8)
        
        # Field labels
        c.drawString(inch * 0.5, y_pos, "PACKED BY:")
        c.drawString(inch * 0.5, y_pos - 20, "NO. BOXES:")
        c.drawString(inch * 0.5, y_pos - 40, "REQUISITION NO.:")
        c.drawString(inch * 0.5, y_pos - 60, "ORDER NO.:")
        c.drawString(inch * 4.0, y_pos - 40, "DATE:")
        
        # Field values
        c.setFont("Helvetica", 9)
        if admin_data.get('packed_by'):
            c.drawString(inch * 1.5, y_pos, admin_data['packed_by'][:50])
        if admin_data.get('no_boxes'):
            c.drawString(inch * 1.5, y_pos - 20, admin_data['no_boxes'])
        if admin_data.get('requisition_no'):
            c.drawString(inch * 2.2, y_pos - 40, admin_data['requisition_no'][:30])
        if admin_data.get('order_no'):
            c.drawString(inch * 1.5, y_pos - 60, admin_data['order_no'][:30])
        if admin_data.get('date'):
            c.drawString(inch * 4.5, y_pos - 40, admin_data['date'])
        
        # Page number
        c.drawString(inch * 5.0, height - inch * 1.3, f"PAGE {page_num} OF {total_pages}")
        
        # Draw table header
        table_y = height - inch * 3.0
        c.setFont("Helvetica-Bold", 8)
        c.drawString(inch * 0.5, table_y, "BOX")
        c.drawString(inch * 0.5, table_y + 10, "NO.")
        
        c.drawString(inch * 1.0, table_y, "CONTENTS - STOCK NUMBER")
        c.drawString(inch * 1.0, table_y + 10, "AND NOMENCLATURE")
        
        c.drawString(inch * 6.5, table_y, "UNIT")
        c.drawString(inch * 6.5, table_y + 10, "OF")
        c.drawString(inch * 6.5, table_y + 18, "ISSUE")
        
        c.drawString(inch * 7.2, table_y, "QTY")
        
        # Header line
        c.setLineWidth(1)
        c.line(inch * 0.4, table_y - 10, inch * 7.5, table_y - 10)
        
        # Draw items
        c.setFont("Helvetica", 8)
        for idx, item in enumerate(items):
            item_y = table_y - 35 - (idx * self.ROW_HEIGHT)
            
            if item_y < inch * 2.0:
                break
            
            # Row line
            c.setLineWidth(0.5)
            c.line(inch * 0.4, item_y - 15, inch * 7.5, item_y - 15)
            
            # Box number
            if item.get('box_no'):
                c.drawString(inch * 0.5, item_y, item['box_no'])
            
            # Stock number and nomenclature
            item_text = ""
            if item.get('stock_number'):
                item_text = item['stock_number']
            if item.get('nomenclature'):
                if item_text:
                    item_text += " "
                item_text += item['nomenclature']
            
            # Wrap text if too long
            if len(item_text) > 55:
                item_text = item_text[:55] + "..."
            
            c.drawString(inch * 1.0, item_y, item_text)
            
            # Unit of issue
            if item.get('unit_issue'):
                c.drawString(inch * 6.5, item_y, item['unit_issue'])
            
            # Quantity
            try:
                qty = int(item.get('qty_init', 1))
                c.drawString(inch * 7.2, item_y, str(qty))
            except:
                c.drawString(inch * 7.2, item_y, "1")
