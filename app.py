from flask import Flask, request, send_file, render_template_string
from io import BytesIO
from pdf_parser import DD1750Parser
from form_generator import DD1750Generator
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>DD1750 Merger</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .upload-section { border: 2px dashed #3498db; padding: 30px; margin: 20px 0; border-radius: 8px; }
        input[type="file"] { margin: 10px 0; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .error { color: #e74c3c; }
    </style>
</head>
<body>
    <h1>DD1750 PDF Merger</h1>
    <p>Upload two DD1750 forms - one with items, one with admin information. We'll merge them cleanly without spillage.</p>
    
    <form action="/merge" method="post" enctype="multipart/form-data">
        <div class="upload-section">
            <h3>Items PDF</h3>
            <p>Upload DD1750 with items filled in</p>
            <input type="file" name="items_pdf" accept=".pdf" required>
        </div>
        
        <div class="upload-section">
            <h3>Admin PDF</h3>
            <p>Upload DD1750 with admin info (Packed By, No. Boxes, Requisition No., Order No., Date)</p>
            <input type="file" name="admin_pdf" accept=".pdf" required>
        </div>
        
        <button type="submit">Merge PDFs</button>
    </form>
    
    {% if error %}
    <p class="error">{{ error }}</p>
    {% endif %}
</body>
</html>
    ''')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    if 'items_pdf' not in request.files or 'admin_pdf' not in request.files:
        return render_template_string('''
<!DOCTYPE html>
<html><body><p class="error">Please upload both PDFs</p><a href="/">Back</a></body></html>
        '''), error="Both files required"
    
    items_file = request.files['items_pdf']
    admin_file = request.files['admin_pdf']
    
    try:
        # Parse both PDFs
        parser = DD1750Parser()
        
        items_data = parser.parse_items_pdf(items_file.read())
        admin_data = parser.parse_admin_pdf(admin_file.read())
        
        # Generate merged PDF
        generator = DD1750Generator()
        merged_pdf = generator.generate_merged_form(items_data, admin_data)
        
        # Send file
        output = BytesIO(merged_pdf)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='DD1750_Merged.pdf'
        )
        
    except Exception as e:
        app.logger.error(f"Merge error: {str(e)}")
        return render_template_string('''
<!DOCTYPE html>
<html><body><p class="error">Error: {{ error }}</p><a href="/">Back</a></body></html>
        '''), error=str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
