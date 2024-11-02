from flask import Flask, request, render_template, redirect, url_for, send_file
from PIL import Image, ImageEnhance
import os
import zipfile

app = Flask(__name__)

ORIGINAL_PATH = 'static/original'
COMPRESSED_PATH = 'static/compressed'
ZIP_PATH = 'static/downloads'

os.makedirs(ORIGINAL_PATH, exist_ok=True)
os.makedirs(COMPRESSED_PATH, exist_ok=True)
os.makedirs(ZIP_PATH, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    images = request.files.getlist('images')
    quality = int(request.form.get('quality', 20))
    brightness = float(request.form.get('brightness', 1.0))
    contrast = float(request.form.get('contrast', 1.0))
    saturation = float(request.form.get('saturation', 1.0))
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)

    original_files = []
    compressed_files = []

    for image_file in images:
        try:
            with Image.open(image_file) as img:
                original_filename = os.path.join(ORIGINAL_PATH, image_file.filename)
                img.save(original_filename)
                original_files.append(original_filename)

                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)

                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)

                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)

                if width and height:
                    img = img.resize((int(width), int(height)), Image.LANCZOS)

                compressed_filename = os.path.join(COMPRESSED_PATH, f"compressed_{image_file.filename}")
                img.save(compressed_filename, format='JPEG', quality=quality)
                compressed_files.append(compressed_filename)

        except Exception as e:
            print(f"Error processing image {image_file.filename}: {e}")

    zip_filename = os.path.join(ZIP_PATH, 'images.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in original_files:
            zipf.write(file, os.path.basename(file))
        for file in compressed_files:
            zipf.write(file, os.path.basename(file))

    return redirect(url_for('download_and_redirect', zipfile='images.zip'))

@app.route('/download_and_redirect')
def download_and_redirect():
    zipfile_name = request.args.get('zipfile')
    return render_template('download_success.html', zipfile=zipfile_name)

@app.route('/compare')
def compare():
    original_images = os.listdir(ORIGINAL_PATH)
    compressed_images = os.listdir(COMPRESSED_PATH)
    image_pairs = list(zip(original_images, compressed_images))

    return render_template('compare.html', image_pairs=image_pairs)

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(os.path.join(ZIP_PATH, filename), as_attachment=True, download_name='images.zip', mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)