import pdfplumber

class DD1750Parser:
    def parse_admin_pdf(self, pdf_bytes):
        admin_data = {'packed_by': None, 'no_boxes': None, 'requisition_no': None, 'order_no': None, 'date': None}
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                page = pdf.pages[0]
                text = page.extract_text() or ""
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if "PACKED BY" in line:
                        if ":" in line:
                            parts = line.split(":")
                            if len(parts) > 1:
                                admin_data['packed_by'] = parts[1].strip()[:50]
                    elif "REQUISITION" in line and "NO" in line:
                        idx = line.find("NO") + 2
                        if idx < len(line):
                            admin_data['requisition_no'] = line[idx:].strip()[:30]
                    elif "ORDER" in line and "NO" in line:
                        idx = line.find("NO") + 2
                        if idx < len(line):
                            admin_data['order_no'] = line[idx:].strip()[:30]
        except:
            pass
        return admin_data
    
    def parse_items_pdf(self, pdf_bytes):
        items = []
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    lines = text.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        words = line.split()
                        if not words:
                            continue
                        
                        first_word = words[0]
                        
                        if first_word.isdigit():
                            box_num = first_word
                            rest_of_line = ' '.join(words[1:])
                            
                            items.append({
                                'box_no': box_num,
                                'stock_number': '',
                                'nomenclature': rest_of_line[:80],
                                'unit_issue': 'EA',
                                'qty_init': '1',
                                'qty_run': '0'
                            })
                        elif items and first_word[0].isdigit():
                            items[-1]['nomenclature'] += " " + line[:80]
        
        except Exception as e:
            print(f"Parse error: {e}")
        
        print(f"Extracted {len(items)} items")
        return items
