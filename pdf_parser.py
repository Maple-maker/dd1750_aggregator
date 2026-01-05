import pdfplumber

class DD1750Parser:
    def parse_admin_pdf(self, pdf_bytes):
        admin_data = {'packed_by': None, 'no_boxes': None, 'requisition_no': None, 'order_no': None, 'date': None}
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                page = pdf.pages[0]
                text = page.extract_text() or ""
                
                for line in text.split('\n'):
                    line = line.strip()
                    if "PACKED BY" in line and ":" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            admin_data['packed_by'] = parts[1].strip()[:50]
                    elif "REQUISITION" in line and "NO" in line:
                        parts = line.split("NO")
                        if len(parts) > 1:
                            admin_data['requisition_no'] = parts[1].replace(".", "").strip()[:30]
                    elif "ORDER" in line and "NO" in line:
                        parts = line.split("NO")
                        if len(parts) > 1:
                            admin_data['order_no'] = parts[1].replace(".", "").strip()[:30]
                    elif line.replace(".", "").isdigit() and len(line) >= 8:
                        admin_data['date'] = line[:15]
        except:
            pass
        return admin_data
    
    def parse_items_pdf(self, pdf_bytes):
        items = []
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    
                    tables = page.extract_tables()
                    if tables and len(tables) > 0:
                        table = tables[0]
                        
                        for row in table:
                            if not row or len(row) < 2:
                                continue
                            
                            first_col = str(row[0]).strip() if row[0] else ""
                            
                            if first_col and first_col.replace(".", "").isdigit():
                                items.append({
                                    'box_no': first_col,
                                    'stock_number': '',
                                    'nomenclature': str(row[1]).strip() if row[1] else "",
                                    'unit_issue': 'EA',
                                    'qty_init': '1',
                                    'qty_run': '0'
                                })
                            elif len(items) > 0 and first_col:
                                items[-1]['stock_number'] += " " + first_col
                            elif len(items) > 0 and row[1]:
                                items[-1]['nomenclature'] += " " + str(row[1]).strip()
                    
                    if not items and
