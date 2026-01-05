import pdfplumber

class DD1750Parser:
    def parse_admin_pdf(self, pdf_bytes):
        admin_data = {'packed_by': None, 'no_boxes': None, 'requisition_no': None, 'order_no': None, 'date': None}
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                page = pdf.pages[0]
                text = page.extract_text() or ""
                if "PACKED BY" in text:
                    parts = text.split("PACKED BY")[1].split("NO. BOXES")[0].strip()
                    admin_data['packed_by'] = parts[:50]
                if "REQUISITION NO." in text:
                    parts = text.split("REQUISITION NO.")[1].split("ORDER")[0].strip()
                    admin_data['requisition_no'] = parts[:20]
                if "ORDER NO." in text:
                    parts = text.split("ORDER NO.")[1].split("\n")[0].strip()
                    admin_data['order_no'] = parts[:20]
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
                                items.append({
                                    'box_no': str(row[0]).strip() if row[0] else "",
                                    'stock_number': str(row[1]).strip() if row[1] else "",
                                    'nomenclature': str(row[2]).strip() if row[2] else "",
                                    'unit_issue': 'EA',
                                    'qty_init': '1',
                                    'qty_run': '0'
                                })
        except:
            pass
        return items
