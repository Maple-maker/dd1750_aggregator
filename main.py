from flask import Flask, request, send_file, render_template_string
from io import BytesIO
import os
import traceback

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
            return 'Both files required. Please upload both PDFs.', 400
        
        items_file = request.files['items_pdf']
        admin_file = request.files['admin_pdf']
        
        if not items_file or not admin_file:
            return 'Files are empty. Please select valid PDFs.', 400
        
        print(f"Files: items={items_file.filename}, admin={admin_file.filename}")
        
        try:
            from pdf_parser import DD1750Parser
        except ImportError:
            return 'Parser module not found', 500
        
        parser = DD1750Parser()
        items_data = parser.parse_items_pdf(items_file.read())
        admin_data = parser.parse_admin_pdf(admin_file.read())
        
        print(f"Items count: {len(items_data)}")
        print(f"Admin data: {admin_data}")
        
        if not items_data:
            return f'No items found. Please check the items PDF: {items_file.filename}', 400
        
        try:
            from form_generator import DD1750Generator
        except ImportError:
            return 'Generator module not found', 500
        
        generator = DD1750Generator()
        merged_pdf = generator.generate_merged_form(items_data, admin_data)
        
        output = BytesIO(merged_pdf)
        output.seek(0)
        
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='DD1750_Merged.pdf')
    
    except Exception as e:
        error_msg = f'Error: {str(e)}\n{traceback.format_exc()}'
        print(error_msg)
        return f'An error occurred. Please try again or contact support.', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
