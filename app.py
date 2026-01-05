from flask import Flask, request, send_file, render_template_string, jsonify
from io import BytesIO
import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'dd1750-merger'}), 200

@app.route('/')
def index():
    try:
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>DD1750 Merger</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .upload-section { border: 2px dashed #3498db; padding: 30px; margin: 20px 0; border-radius: 8px; background: #f8f9fa; }
        input[type="file"] { margin: 10px 0; width: 100%; padding: 10px; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background: #2980b9; }
        .error { color:
