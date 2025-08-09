import os
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.process_form import process_form_image

form_bp = Blueprint('form', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@form_bp.route('/process-form', methods=['POST'])
def process_form():
    try:
        # Verificar se um arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
        
        file = request.files['file']
        
        # Verificar se o arquivo tem um nome
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo foi selecionado'}), 400
        
        # Verificar se o arquivo é permitido
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido. Use PNG, JPG ou JPEG.'}), 400
        
        # Salvar o arquivo temporariamente
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Processar o formulário
            result = process_form_image(temp_file_path)
            
            # Verificar se houve erro no processamento
            if result.startswith("Erro:"):
                return jsonify({'error': result}), 500
            
            # Parsear o resultado CSV
            lines = result.strip().split('\n')
            if len(lines) < 2:  # Pelo menos cabeçalho + uma linha de dados
                return jsonify({'products': []}), 200
            
            products = []
            for line in lines[1:]:  # Pular o cabeçalho
                if ',' in line:
                    codigo, quantidade = line.split(',', 1)
                    products.append({
                        'codigo': codigo.strip(),
                        'quantidade': int(quantidade.strip())
                    })
            
            return jsonify({'products': products}), 200
            
        finally:
            # Limpar o arquivo temporário
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@form_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API de processamento de formulários funcionando'}), 200

