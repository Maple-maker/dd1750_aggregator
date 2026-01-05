import pdfplumber

class DD1750Parser:
    def parse_admin_pdf(self, pdf_bytes):
        admin_data = {'packed_by': None, 'no_boxes': None, 'requisition_no': None, 'order_no': None, 'date': None}
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                page = pdf.pages[0]
                text = page.extract_text() or ""
                
                # Try to find PACKED BY
                if "PACKED BY" in text:
                    idx = text.find("PACKED BY")
                    after = text[idx + 9:].strip()
                    if after:
                        admin_data['packed_by'] = after[:50].split('\n')[0].strip()
                
                # Try to find NO. BOXES
                if "NO. BOXES" in text:
                    idx = text.find("NO. BOXES")
                    after = text[idx + 10:].strip()
                    if after:
                        admin_data['no_boxes'] = after[:10].split('\n')[0].strip()
                
                # Try to find REQUISITION NO.
                if "REQUISITION NO." in text:
                    idx = text.find("REQUISITION NO.")
                    after = text[idx + 15:].strip()
                    if after:
                        admin_data['requisition_no'] = after[:30].split('\n')[0].strip()
                
                # Try to find ORDER NO.
                if "ORDER NO." in text or "ORDER NO" in text:
                    idx = max(text.find("ORDER NO."), text.find("ORDER NO"))
                    after = text[idx + 9:].strip()
                    if after:
                        admin_data['order_no'] = after[:30].split('\n')[0].strip()
                
                # Try to find DATE
                if "DATE" in text:
                    parts = text.split("DATE")
                    for i, part in enumerate(parts[1:], 1):
                        candidate = part.strip()[:15].split('\n')[0].strip()
                        if candidate and len(candidate) > 5:
                            admin_data['date'] = candidate
                            break
        except Exception as e:
            print(f"Admin parse error: {e}")
        
        return admin_data
    
    def parse_items_pdf(self, pdf_bytes):
        items = []
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    
                    # Try table extraction first
                    tables = page.extract_tables()
                    if tables and len(tables) > 0:
                        table = tables[0]
                        
                        # Skip header row (first row)
                        for row_idx, row in enumerate(table[1:], 1):
                            if not row or len(row) < 3:
                                continue
                            
                            box_no = str(row[0]).strip() if row[0] else ""
                            
                            # Skip rows without box numbers
                            if not box_no or box_no.lower() in ['box', 'no.', 'number']:
                                continue
                            
                            # Extract stock number and nomenclature
                            stock_number = str(row[1]).strip() if row[1] else ""
                            nomenclature = str(row[2]).strip() if row[2] else ""
                            
                            # Clean up data
                            stock_number = stock_number.replace('\n', ' ')
                            nomenclature = nomenclature.replace('\n', ' ')
                            
                            items.append({
                                'box_no': box_no,
                                'stock_number': stock_number,
                                'nomenclature': nomenclature,
                                'unit_issue': 'EA',
                                'qty_init': '1',
                                'qty_run': '0'
                            })
                    
                    # Fallback: parse text directly
                    if not items:
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            # Look for lines that look like items (start with number)
                            if line and any(char.isdigit() for char in line[:10]):
                                parts = line.split(' ', 1)
                                if len(parts) >= 2:
                                    box_num = parts[0].strip()
                                    if box_num.isdigit():
                                        items.append({
                                            'box_no': box_num,
                                            'stock_number': '',
                                            'nomenclature': parts[1][:80],
                                            'unit_issue': 'EA',
                                            'qty_init': '1',
                                            'qty_run': '0'
                                        })
        
        except Exception as e:
            print(f"Items parse error: {e}")
        
        print(f"Extracted {len(items)} items")
        return items
