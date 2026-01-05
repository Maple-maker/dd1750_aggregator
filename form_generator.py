from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from typing import Dict, List
import io
import logging

logger = logging.getLogger(__name__)

class DD1750Generator:
    """Generate clean DD1750 forms with proper pagination"""
    
    ITEMS_PER_PAGE = 18
    ROW_HEIGHT = 24
    
    def __init__(self):
        logger.info("DD1750Generator initialized")
    
    def generate_merged_form(self, items: List[Dict], admin_data: Dict) -> bytes:
        """Generate merged DD1750 PDF"""
        try:
            output = io.BytesIO()
            
            # Calculate pages needed
            total_items = len(items)
            total_pages = max(1, (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
            
            logger.info(f"Generating {total_pages} pages for {total_items} items")
            
            from reportlab.pdfgen import canvas
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
            logger.info("PDF generated successfully")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def _draw_page(self, c: canvas.Canvas, items: List[Dict], 
                   admin_data: Dict, page_num: int, total_pages: int):
        """Draw a single DD1750 page"""
        try:
            width, height = letter
            
            # Set font
            c.setFont("Helvetica-Bold", 10)
            
            # Form title
            c.drawString(inch * 1.0, height - inch * 0.8, "PACKING LIST")
            c.setFont("Helvetica", 8)
            c.drawString(inch * 5.0, height - inch * 0.8, "DD FORM 1750, SEP 70 (EG)")
            
            # Draw admin info
            self._draw_admin_info(c, admin_data, height)
            
            # Draw page number
            c.setFont("Helvetica", 8)
            c.drawString(inch * 5.0, height - inch * 1.5, f"PAGE {page_num} OF {total_pages}")
            
            # Draw table header
            self._draw_table_header(c, height)
            
            # Draw items
            self._draw_items(c, items, height)
            
        except Exception as e:
            logger.error(f"Page drawing error: {e}")
            raise
    
    def _draw_admin_info(self, c: canvas.Canvas, admin_data: Dict, page_height: float):
        """Draw admin information"""
        c.setFont("Helvetica-Bold", 7)
        
        # Labels
        y_pos = page_height - inch * 2.2
        c.drawString(inch * 0.6, y_pos, "PACKED BY:")
        c.drawString(inch * 0.6, y_pos - 20, "NO. BOXES:")
        c.drawString(inch * 0.6, y_pos - 40, "REQUISITION NO.:")
        c.drawString(inch * 0.6, y_pos - 60, "ORDER NO.:")
        c.drawString(inch * 4.5, y_pos - 40, "DATE:")
        
        # Values
        c.setFont("Helvetica", 8)
        if admin_data.get('packed_by'):
            c.drawString(inch * 1.5, y_pos, admin_data['packed_by'][:50])
        if admin_data.get('no_boxes'):
            c.drawString(inch * 1.5, y_pos - 20, admin_data['no_boxes'])
        if admin_data.get('requisition_no'):
            c.drawString(inch * 2.2, y_pos - 40, admin_data['requisition_no'][:30])
        if admin_data.get('order_no'):
            c.drawString(inch * 1.5, y_pos - 60, admin_data['order_no'][:30])
        if admin_data.get('date'):
            c.drawString(inch * 5.0, y_pos - 40, admin_data['date'])
    
    def _draw_table_header(self, c: canvas.Canvas, page_height: float):
        """Draw table header"""
        y_pos = page_height - inch * 3.0
        
        c.setFont("Helvetica-Bold", 7)
        c.drawString(inch * 0.6, y_pos, "BOX NO.")
        c.drawString(inch * 1.2, y_pos, "CONTENTS - STOCK NUMBER AND NOMENCLATURE")
        c.drawString(inch * 5.5, y_pos, "UNIT")
        c.drawString(inch * 6.0, y_pos, "QTY")
        c.drawString(inch * 6.5, y_pos, "TOTAL")
        
        # Header line
        c.setLineWidth(1)
        c.line(inch * 0.5, y_pos - 10, inch * 7.5, y_pos - 10)
    
    def _draw_items(self, c: canvas.Canvas, items: List[Dict], page_height: float):
        """Draw items in the table"""
        c.setFont("Helvetica", 7)
        
        start_y = page_height - inch * 3.5
        
        for idx, item in enumerate(items):
            y_pos = start_y - (idx * self.ROW_HEIGHT)
            
            if y_pos < inch * 2.0:
                break  # Don't draw below footer
            
            # Row line
            c.line(inch * 0.5, y_pos - 15, inch * 7.5, y_pos - 15)
            
            # Item data
            if item.get('box_no'):
                c.drawString(inch * 0.6, y_pos, item['box_no'])
            
            # Combine stock number and nomenclature
            item_text = ""
            if item.get('stock_number'):
                item_text = item['stock_number']
            if item.get('nomenclature'):
                if item_text:
                    item_text += " "
                item_text += item['nomenclature']
            
            # Truncate if too long
            if len(item_text) > 50:
                item_text = item_text[:50] + "..."
            
            c.drawString(inch * 1.2, y_pos, item_text)
            
            if item.get('unit_issue'):
                c.drawString(inch * 5.5, y_pos, item['unit_issue'])
            
            # Calculate total
            try:
                init_qty = float(item['qty_init']) if item.get('qty_init') else 0
                run_qty = float(item['qty_run']) if item.get('qty_run') else 0
                total = init_qty + run_qty
                if total > 0:
                    c.drawString(inch * 6.5, y_pos, str(int(total)))
            except (ValueError, TypeError):
                pass
