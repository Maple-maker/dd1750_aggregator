import pdfplumber
from typing import Dict, List, Optional

class DD1750Parser:
    """Extract data from DD1750 forms without overlap issues"""
    
    # Admin field regions (Y coordinates in points, approximated for standard DD1750)
    ADMIN_REGIONS = {
        'packed_by': {'x_range': (100, 400), 'y_range': (140, 160)},
        'no_boxes': {'x_range': (100, 200), 'y_range': (160, 180)},
        'requisition_no': {'x_range': (100, 300), 'y_range': (180, 200)},
        'order_no': {'x_range': (100, 300), 'y_range': (200, 220)},
        'date': {'x_range': (400, 500), 'y_range': (180, 200)},
    }
    
    # Item table regions
    TABLE_START_Y = 250
    TABLE_END_Y = 700
    ROW_HEIGHT = 24
    
    def parse_admin_pdf(self, pdf_bytes: bytes) -> Dict[str, Optional[str]]:
        """Extract admin fields from admin-filled PDF"""
        admin_data = {
            'packed_by': None,
            'no_boxes': None,
            'requisition_no': None,
            'order_no': None,
            'date': None,
        }
        
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                page = pdf.pages[0]  # Admin info on first page only
                
                for field_name, region in self.ADMIN_REGIONS.items():
                    # Crop region and extract text
                    cropped = page.crop((region['x_range'][0], region['y_range'][0],
                                       region['x_range'][1], region['y_range'][1]))
                    text = cropped.extract_text() or ""
                    admin_data[field_name] = text.strip()
        
        except Exception as e:
            print(f"Admin parsing warning: {e}")
        
        return admin_data
    
    def parse_items_pdf(self, pdf_bytes: bytes) -> List[Dict]:
        """Extract all items from items-filled PDF (handles multiple pages)"""
        items = []
        
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_items = self._extract_items_from_page(page)
                    items.extend(page_items)
        
        except Exception as e:
            print(f"Items parsing error: {e}")
            raise
        
        return items
    
    def _extract_items_from_page(self, page) -> List[Dict]:
        """Extract items from a single page using table detection"""
        items = []
        
        try:
            # Crop to table region
            table_region = page.crop((0, self.TABLE_START_Y, page.width, self.TABLE_END_Y))
            
            # Extract table structure
            tables = table_region.extract_tables()
            
            if not tables:
                return items
            
            table = tables[0]  # First table is the items table
            
            # Skip header row and extract items
            for row in table[1:]:  # Skip header
                if not row or len(row) < 6:
                    continue
                
                # Extract item data
                box_no = str(row[0]).strip() if row[0] else ""
                stock_number = str(row[1]).strip() if row[1] else ""
                nomenclature = str(row[2]).strip() if row[2] else ""
                unit_issue = str(row[3]).strip() if row[3] else ""
                qty_init = str(row[4]).strip() if row[4] else ""
                qty_run = str(row[5]).strip() if row[5] else ""
                
                # Skip empty rows
                if not any([box_no, stock_number, nomenclature]):
                    continue
                
                items.append({
                    'box_no': box_no,
                    'stock_number': stock_number,
                    'nomenclature': nomenclature,
                    'unit_issue': unit_issue,
                    'qty_init': qty_init,
                    'qty_run': qty_run,
                })
        
        except Exception as e:
            print(f"Page parsing warning: {e}")
        
        return items
