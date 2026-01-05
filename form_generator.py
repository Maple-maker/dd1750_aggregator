from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from typing import Dict, List
import io

class DD1750Generator:
    """Generate clean DD1750 forms with proper pagination"""
    
    ITEMS_PER_PAGE = 18
    
    # Layout coordinates (in points, 1 inch = 72 points)
    HEADER_Y = 180
    TABLE_START_Y = 250
    TABLE_END_Y = 700
    ROW_HEIGHT = 24
    
    # Column X positions
    COL_BOX = 40
    COL_STOCK = 100
    COL_NOMEN = 250
    COL_UNIT = 580
    COL_QTY_INIT = 620
    COL_QTY_RUN = 670
    COL_QTY_TOTAL = 720
    
    def generate_merged_form(self, items: List[Dict], admin_data: Dict) -> bytes:
        """Generate merged DD1750 PDF with proper pagination"""
        output = io.BytesIO()
        
        # Calculate pages needed
        total_items = len(items)
        total_pages = (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        # Create PDF with multiple pages
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(output, pagesize=letter)
        
        for page_num in range(total_pages):
            # Get items for this page
            start_idx = page_num * self.ITEMS_PER_PAGE
            end_idx = min(start_idx + self.ITEMS_PER_PAGE, total_items)
            page_items = items[start_idx:end_idx]
            
            # Draw the page
            self._draw_page(c, page_items, admin_data, page_num + 1, total_pages)
            
            # Add new page if not last
            if page_num < total_pages - 1:
                c.showPage()
        
        c.save()
        output.seek(0)
        return output.getvalue()
    
    def _draw_page(self, c: canvas.Canvas, items: List[Dict], 
                   admin_data: Dict, page_num: int, total_pages: int):
        """Draw a single DD1750 page"""
        width, height = letter
        
        # Draw form header and borders
        self._draw_form_structure(c, width, height)
        
        # Draw admin information (only on first page or all pages as needed)
        self._draw_admin_info(c, admin_data)
        
        # Draw page number
        self._draw_page_number(c, page_num, total_pages)
        
        # Draw items
        self._draw_items_table(c, items)
        
        # Draw certification section
        self._draw_certification(c)
    
    def _draw_form_structure(self, c: canvas.Canvas, width: float, height: float):
        """Draw the basic DD1750 form structure"""
        c.setFont("Helvetica-Bold", 10)
        
        # Form title
        c.drawString(inch * 1.0, height - inch * 0.8, "PACKING LIST")
        c.setFont("Helvetica", 8)
        c.drawString(inch * 5.0, height - inch * 0.8, "DD FORM 1750, SEP 70 (EG)")
        
        # Draw main box border
        c.setLineWidth(1)
        c.rect(inch * 0.5, self.TABLE_END_Y, width - inch, height - inch * 1.5 - self.TABLE_END_Y)
        
        # Draw table header
        c.setFont("Helvetica-Bold", 7)
        c.drawString(self.COL_BOX, self.TABLE_START_Y, "BOX")
        c.drawString(self.COL_BOX, self.TABLE_START_Y + 8, "NO.")
        
        c.drawString(self.COL_STOCK, self.TABLE_START_Y, "CONTENTS - STOCK")
        c.drawString(self.COL_STOCK, self.TABLE_START_Y + 8, "NUMBER AND")
        c.drawString(self.COL_STOCK, self.TABLE_START_Y + 16, "NOMENCLATURE")
        
        c.drawString(self.COL_UNIT, self.TABLE_START_Y, "UNIT")
        c.drawString(self.COL_UNIT, self.TABLE_START_Y + 8, "OF")
        c.drawString(self.COL_UNIT, self.TABLE_START_Y + 16, "ISSUE")
        
        c.drawString(self.COL_QTY_INIT, self.TABLE_START_Y, "QUANTITIES REQUIRED")
        c.drawString(self.COL_QTY_INIT, self.TABLE_START_Y + 8, "INITIAL")
        c.drawString(self.COL_QTY_INIT, self.TABLE_START_Y + 16, "OPERATION")
        
        c.drawString(self.COL_QTY_RUN, self.TABLE_START_Y + 8, "RUNNING")
        c.drawString(self.COL_QTY_RUN, self.TABLE_START_Y + 16, "SPARES")
        
        c.drawString(self.COL_QTY_TOTAL, self.TABLE_START_Y + 8, "TOTAL")
        
        # Draw header line
        c.line(inch * 0.5, self.TABLE_START_Y - 5, width - inch * 0.5, self.TABLE_START_Y - 5)
    
    def _draw_admin_info(self, c: canvas.Canvas, admin_data: Dict):
        """Draw admin information in header section"""
        c.setFont("Helvetica-Bold", 7)
        
        # Field labels
        c.drawString(inch * 0.6, self.HEADER_Y - 20, "PACKED BY:")
        c.drawString(inch * 0.6, self.HEADER_Y - 40, "NO. BOXES:")
        c.drawString(inch * 0.6, self.HEADER_Y - 60, "REQUISITION NO.:")
        c.drawString(inch * 0.6, self.HEADER_Y - 80, "ORDER NO.:")
        c.drawString(inch * 4.5, self.HEADER_Y - 60, "DATE:")
        
        # Field values
        c.setFont("Helvetica", 8)
        if admin_data.get('packed_by'):
            c.drawString(inch * 1.5, self.HEADER_Y - 20, admin_data['packed_by'])
        if admin_data.get('no_boxes'):
            c.drawString(inch * 1.5, self.HEADER_Y - 40, admin_data['no_boxes'])
        if admin_data.get('requisition_no'):
            c.drawString(inch * 2.2, self.HEADER_Y - 60, admin_data['requisition_no'])
        if admin_data.get('order_no'):
            c.drawString(inch * 1.5, self.HEADER_Y - 80, admin_data['order_no'])
        if admin_data.get('date'):
            c.drawString(inch * 5.0, self.HEADER_Y - 60, admin_data['date'])
    
    def _draw_page_number(self, c: canvas.Canvas, page_num: int, total_pages: int):
        """Draw page number in format: PAGE X OF Y"""
        c.setFont("Helvetica", 8)
        page_text = f"PAGE {page_num} OF {total_pages}"
        c.drawString(inch * 5.0, self.HEADER_Y, page_text)
    
    def _draw_items_table(self, c: canvas.Canvas, items: List[Dict]):
        """Draw items in the table"""
        c.setFont("Helvetica", 7)
        
        for idx, item in enumerate(items):
            y_pos = self.TABLE_START_Y - 20 - (idx * self.ROW_HEIGHT)
            
            if y_pos < self.TABLE_END_Y:
                break  # Don't draw below table
            
            # Draw row line
            c.line(inch * 0.5, y_pos - 12, inch * 7.5, y_pos - 12)
            
            # Draw item data
            if item.get('box_no'):
                c.drawString(self.COL_BOX, y_pos, item['box_no'])
            
            if item.get('stock_number'):
                c.drawString(self.COL_STOCK, y_pos, item['stock_number'])
            
            if item.get('nomenclature'):
                c.drawString(self.COL_STOCK + 80, y_pos, item['nomenclature'])
            
            if item.get('unit_issue'):
                c.drawString(self.COL_UNIT, y_pos, item['unit_issue'])
            
            if item.get('qty_init'):
                c.drawString(self.COL_QTY_INIT, y_pos, item['qty_init'])
            
            if item.get('qty_run'):
                c.drawString(self.COL_QTY_RUN, y_pos, item['qty_run'])
            
            # Calculate total
            try:
                init_qty = float(item['qty_init']) if item.get('qty_init') else 0
                run_qty = float(item['qty_run']) if item.get('qty_run') else 0
                total = init_qty + run_qty
                if total > 0:
                    c.drawString(self.COL_QTY_TOTAL, y_pos, str(int(total)))
            except (ValueError, TypeError):
                pass
    
    def _draw_certification(self, c: canvas.Canvas):
        """Draw certification section at bottom"""
        c.setFont("Helvetica", 7)
        y_pos = self.TABLE_END_Y - 30
        
        cert_text = (
            "I CERTIFY THAT THE ABOVE ARTICLES ARE PROPERLY PACKED AND MARKED. "
            "I FURTHER CERTIFY THAT THE ARTICLES HAVE BEEN RECEIVED FROM THE "
            "INDIVIDUALS LISTED ABOVE AS HAVING DRAWN THEM."
        )
        
        # Word wrap certification text
        words = cert_text.split()
        line = ""
        x_pos = inch * 0.6
        y_pos = self.TABLE_END_Y - 20
        
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 7) < inch * 6.5:
                line = test_line
            else:
                c.drawString(x_pos, y_pos, line)
                line = word + " "
                y_pos -= 10
        
        if line:
            c.drawString(x_pos, y_pos, line)
        
        # Signature lines
        y_pos -= 25
        c.line(inch * 0.6, y_pos, inch * 3.0, y_pos)
        c.drawString(inch * 0.6, y_pos - 10, "TYPED NAME AND TITLE")
        
        c.line(inch * 3.5, y_pos, inch * 6.0, y_pos)
        c.drawString(inch * 3.5, y_pos - 10, "SIGNATURE")
