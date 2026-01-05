from flask import Flask, request, send_file, render_template_string
from io import BytesIO
import os
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'App is working'}

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>DD1750 Merger</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .upload-section { border: 2px dashed #3498db; padding: 30px; margin: 20px 0; background: #f8f9fa; }
        input[type="file"] { margin: 10px 0; width: 100%; padding: 10px; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; cursor: pointer; font-size: 16px; width: 100%; }
    </style>
</head>
<body>
    <h1>DD1750 PDF Merger</h1>
    <p>Upload two DD1750 forms - one with items, one with admin info</p>
    
    <form action="/merge" method="post" enctype="multipart/form-data">
        <div class="upload-section">
            <h3>Items PDF</h3>
            <input type="file" name="items_pdf" accept=".pdf" required>
        </div>
        
        <div class="upload-section">
            <h3>Admin PDF</h3>
            <input type="file" name="admin_pdf" accept=".pdf" required>
        </div>
        
        <button type="submit">Merge PDFs</button>
    </form>
</body>
</html>
    ''')

@app.route('/merge', methods=['POST'])
def merge():
    try:
        if 'items_pdf' not in request.files or 'admin_pdf' not in request.files:
            return 'Both files required', 400
        
        items_file = request.files['items_pdf']
        admin_file = request.files['admin_pdf']
        
        doc_admin = fitz.open(stream=admin_file.read(), filetype="pdf")
        doc_items = fitz.open(stream=items_file.read(), filetype="pdf")
        
        output = BytesIO()
        
        # Copy admin pages first
        merged_doc = fitz.open()
        
        for admin_page in doc_admin:
            new_page = merged_doc.new_page(width=admin_page.rect.width, height=admin_page.rect.height)
            new_page.show_pdf_page(admin_page.rect, doc_admin, admin_page.number)
        
        # Now paste items content on top
        for items_page in doc_items:
            if items_page.number < len(merged_doc):
                # Define the table area to copy (coordinates based on DD1750)
                rect_items = fitz.Rect(40, 250, 550, 750)
                rect_admin = fitz.Rect(40, 250, 550, 750)
                
                # Overlay the items content
                merged_doc[items_page.number].show_pdf_page(
                    rect_admin, 
                    doc_items, 
                    items_page.number,
                    clip=rect_items
                )
        
        merged_doc.save(output)
        merged_doc.close()
        
        output.seek(0)
        return send_file(output, mimetype='application/pdf', as_attachment=True,
