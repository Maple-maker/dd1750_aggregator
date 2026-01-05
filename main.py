from flask import Flask, request, send_file, render_template_string
from io import BytesIO
import os
import fitz

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/health')
def health():
    return {'status': 'ok'}

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>DD1750 Merger</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .upload-section { border: 2px dashed #3498db; padding: 30px; margin: 20px 0; }
        input[type="file"] { margin: 10px 0; width: 100%; padding: 10px; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; cursor: pointer; font-size: 16px; width: 100%; }
    </style>
</head>
<body>
    <h1>DD1750 PDF Merger</h1>
    <p>Upload two DD1750 forms</p>
    <form action="/merge" method="post" enctype="multipart/form-data">
        <div class="upload-section">
            <h3>Items PDF</h3>
            <input type="file" name="items_pdf" accept=".pdf" required>
        </div>
        <div class="upload-section">
            <h3>Admin PDF</h3>
            <input type="file" name="admin_pdf" accept=".pdf" required>
        </div>
        <button type="submit">Merge</button>
    </form>
</body>
</html>
    '''

@app.route('/merge', methods=['POST'])
def merge():
    doc_admin = fitz.open(stream=request.files['admin_pdf'].read(), filetype="pdf")
    doc_items = fitz.open(stream=request.files['items_pdf'].read(), filetype="pdf")
    output = BytesIO()
    
    merged = fitz.open()
    for page in doc_admin:
        merged.insert_pdf(doc_admin, from_page=page.number, to_page=page.number)
    
    for page in doc_items:
        if page.number < len(merged):
            merged[page.number].show_pdf_page(merged[page.number].rect, doc_items, page.number)
    
    merged.save(output)
    output.seek(0)
    return send_file(output, mimetype='application/pdf', download_name='merged.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
