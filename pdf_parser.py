import pdfplumber

class DD1750Parser:
    def parse_admin_pdf(self, pdf_bytes):
        admin_data = {'packed_by': None, 'no_boxes': None, 'requisition_no': None, 'order_no': None, 'date': None}
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                page = pdf.pages[0]
                text = page.extract_text() or ""
                if "PACKED BY" in text:
                    idx = text.find("PACKED BY")
                    after = text[idx + 9:].strip()
                    if after:
                        admin_data['packed_by'] = after[:50].split('\n')[0].strip()
                if "REQUISITION NO." in text:
                    idx = text.find("REQUISITION NO.")
                    after = text[idx + 15:].strip()
                    if after:
                        admin_data['requisition_no'] = after[:30].split('\n')[0].strip()
                if "ORDER NO." in text:
                    idx = text.find("ORDER NO.")
                    after = text[idx + 9:].strip()
                    if after:
                        admin_data['order_no'] = after[:30].split('\n')[0].strip()
        except:
            pass
        return admin_data
    
    def parse_items_pdf(self, pdf_bytes):
        items = []
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        for row in tables[0][1:]:
                            if row and len(row) >= 3:
                                box_no = str(row[0]).strip() if row[0] else ""
                                if box_no and box_no.lower() not in ['box', 'no.', 'number']:
                                    items.append({
                                        'box_no': box_no,
                                        'stock_number': str(row[1]).strip() if row[1] else "",
                                        'nomenclature': str(row[2]).strip() if row[2] else "",
                                        'unit_issue': 'EA',
                                        'qty_init': '1',
                                        'qty_run': '0'
                                    })
        except:
            pass
        return items
