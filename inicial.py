from flask import Flask, request, render_template, send_file
from PIL import Image
import os
from io import BytesIO

# Definindo variáveis globais fora das funções
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'

# Criar diretórios se eles não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Inicializa o aplicativo Flask
app = Flask(__name__)

@app.route('/')
def index():
    # Renderiza a página HTML para upload de imagens
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_image():
    # Verifica se o arquivo foi enviado no request
    if 'image' not in request.files:
        return "No file part", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Salva o arquivo enviado no diretório global
        img_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(img_path)

        try:
            # Abre a imagem usando o PIL
            with Image.open(img_path) as img:
                # Define o formato original da imagem ou usa JPEG como padrão
                original_format = img.format if img.format else 'JPEG'
                compressed_img_io = BytesIO()

                # Comprime a imagem: ajusta para JPEG ou otimiza outros formatos
                if original_format in ['JPEG', 'JPG', 'PNG']:
                    img.save(compressed_img_io, format='JPEG', quality=20)
                else:
                    img.save(compressed_img_io, format=original_format, optimize=True)

                # Reseta o ponteiro do buffer para o início
                compressed_img_io.seek(0)

            # Envia o arquivo comprimido de volta ao usuário para download
            return send_file(
                compressed_img_io,
                mimetype=f'image/{original_format.lower()}',
                as_attachment=True,
                download_name=f"compressed_{file.filename}"
            )
        except Exception as e:
            # Retorna erro no processamento da imagem
            return f"Error processing image: {e}", 500

if __name__ == "__main__":
    # Executa o servidor Flask em modo debug
    app.run(debug=True)