import pdfplumber
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DD1750Parser:
    """Extract data from DD1750 forms without overlap issues"""
    
    # Admin field regions (Y coordinates in points)
    ADMIN_REGIONS = {
        'packed_by': {'x_range': (50, 350), 'y_range': (650, 680)},
        'no_boxes': {'x_range': (50, 200), 'y_range': (620, 650)},
        'requisition_no': {'x_range': (50, 300), 'y_range': (590, 620)},
        'order_no': {'x_range': (50, 300), 'y_range': (560, 590)},
        'date': {'x_range': (350, 500), 'y_range': (590, 620)},
    }
    
    TABLE_START_Y = 450
    TABLE_END_Y = 150
    ROW_HEIGHT = 20
    
    def __init__(self):
        logger.info("DD1750Parser initialized")
    
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
                logger.info(f"Admin PDF has {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Processing admin page {page_num + 1}")
                    
                    for field_name, region in self.ADMIN_REGIONS.items():
                        try:
                            # Crop region and extract text
                            cropped = page.crop((region['x_range'][0], region['y_range'][0],
                                               region['x_range'][1], region['y_range'][1]))
                            text = cropped.extract_text() or ""
                            cleaned = text.strip()
                            
                            if cleaned and not admin_data[field_name]:
                                admin_data[field_name] = cleaned
                                logger.info(f"Extracted {field_name}: {cleaned[:50]}...")
                        except Exception as e:
                            logger.warning(f"Error extracting {field_name}: {e}")
        
        except Exception as e:
            logger.error(f"Admin parsing error: {e}")
            # Return empty admin data rather than failing
            pass
        
        logger.info(f"Admin data extracted: {admin_data}")
        return admin_data
    
    def parse_items_pdf(self, pdf_bytes: bytes) -> List[Dict]:
        """Extract all items from items-filled PDF"""
        items = []
        
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                logger.info(f"Items PDF has {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Processing items page {page_num + 1}")
                    page_items = self._extract_items_from_page(page)
                    logger.info(f"Found {len(page_items)} items on page {page_num + 1}")
                    items.extend(page_items)
        
        except Exception as e:
            logger.error(f"Items parsing error: {e}")
            raise Exception(f"Failed to parse items PDF: {str(e)}")
        
        logger.info(f"Total items extracted: {len(items)}")
        return items
    
    def _extract_items_from_page(self, page) -> List[Dict]:
        """Extract items from a single page"""
        items = []
        
        try:
            # Try to extract tables
            tables = page.extract_tables()
            
            if not tables or len(tables) == 0:
                logger.warning("No tables found on page, trying alternative method")
                return self._extract_items_fallback(page)
            
            table = tables[0]
            logger.info(f"Table has {len(table)} rows")
            
            # Skip header row (first row) and extract items
            for row_idx, row in enumerate(table[1:], start=2):  # Skip header
                if not row or len(row) < 4:
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
                
                if len(items) >= 100:  # Safety limit
                    logger.warning("Reached item limit of 100")
                    break
        
        except Exception as e:
            logger.warning(f"Table extraction failed: {e}, trying fallback")
            return self._extract_items_fallback(page)
        
        return items
    
    def _extract_items_fallback(self, page) -> List[Dict]:
        """Fallback method: extract text lines and parse items"""
        items = []
        
        try:
            # Extract all text
            text = page.extract_text()
            if not text:
                return items
            
            lines = text.split('\n')
            logger.info(f"Fallback: found {len(lines)} text lines")
            
            # Simple heuristic for item detection
            for line in lines[5:]:  # Skip header lines
                # Skip empty or very short lines
                if len(line.strip()) < 10:
                    continue
                
                # Try to parse as item (basic pattern matching)
                items.append({
                    'box_no': str(len(items) + 1),
                    'stock_number': 'Unknown',
                    'nomenclature': line.strip(),
                    'unit_issue': 'EA',
                    'qty_init': '1',
                    'qty_run': '0',
                })
                
                if len(items) >= 100:
                    break
        
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
        
        return items
