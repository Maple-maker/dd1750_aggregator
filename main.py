from flask import Flask, request, send_file, render_template_string, jsonify
from io import BytesIO
import os
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>DD1750 Merger</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .upload-section { border: 2px dashed #3498db; padding: 30px; margin: 20px 0; }
        input[type="file"] { margin: 10px 0; width: 100%; padding: 10px; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; cursor: pointer; font-size: 16px; width: 100%; }
        .error { color: red; background: #ffe6e6; padding: 15px; margin: 10px 0; }
        .success { color: green; background: #e6ffe6; padding: 15px; margin: 10px 0; }
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
    
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    {% if success %}
    <div class="success">{{ success }}</div>
    {% endif %}
</body>
</html>
    ''')

@app.route('/merge', methods=['POST'])
def merge():
    try:
        if 'items_pdf' not in request.files or 'admin_pdf' not in request.files:
            return render_template_string('''
<!DOCTYPE html><body><div class="error">Both files required</div><a href="/">Back</a></body></html>
            '''), error="Both files required"
        
        items_file = request.files['items_pdf']
        admin_file = request.files['admin_pdf']
        
        logger.info(f"Files received: items={items_file.filename}, admin={admin_file.filename}")
        
        # Parse PDFs
        from pdf_parser import DD1750Parser
        parser = DD1750Parser()
        
        items_data = parser.parse_items_pdf(items_file.read())
        admin_data = parser.parse_admin_pdf(admin_file.read())
        
        logger.info(f"Extracted {len(items_data)} items")
        logger.info(f"Admin data: {admin_data}")
        
        if not items_data:
            return render_template_string('''
<!DOCTYPE html><body><div class="error">No items found in items PDF</div><a href="/">Back</a></body></html>
            '''), error="No items found in items PDF"
        
        # Generate merged PDF
        from form_generator import DD1750Generator
        generator = DD1750Generator()
        merged_pdf = generator.generate_merged_form(items_data, admin_data)
        
        output = BytesIO(merged_pdf)
        output.seek(0)
        
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='DD1750_Merged.pdf')
        
    except Exception as e:
        logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
        return render_template_string(f'''
<!DOCTYPE html><body><div class="error">Error: {str(e)}</div><a href="/">Back</a></body></html>
        '''), error=str(e)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
