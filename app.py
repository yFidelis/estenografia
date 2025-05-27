from flask import Flask, render_template, request, send_file, send_from_directory
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def str_to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_str(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(char, 2)) for char in chars])

def hide_text_in_image(image_path, output_path, secret_text):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    binary_text = str_to_bin(secret_text) + '1111111111111110'
    idx = 0

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if idx < len(binary_text): r = (r & ~1) | int(binary_text[idx]); idx += 1
            if idx < len(binary_text): g = (g & ~1) | int(binary_text[idx]); idx += 1
            if idx < len(binary_text): b = (b & ~1) | int(binary_text[idx]); idx += 1
            pixels[x, y] = (r, g, b)
            if idx >= len(binary_text): break
        if idx >= len(binary_text): break
    img.save(output_path)

def extract_text_from_image(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    binary_text = ''
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_text += str(r & 1) + str(g & 1) + str(b & 1)
    end_index = binary_text.find('1111111111111110')
    return bin_to_str(binary_text[:end_index]) if end_index != -1 else "Mensagem não encontrada."

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    image_url = ''
    if request.method == 'POST':
        if 'hide' in request.form:
            file = request.files['image']
            text = request.form['message']
            original_path = os.path.join(UPLOAD_FOLDER, 'original.png')
            output_filename = 'output.png'
            output_path = os.path.join(UPLOAD_FOLDER, output_filename)
            file.save(original_path)
            hide_text_in_image(original_path, output_path, text)
            image_url = f"/uploads/{output_filename}"
        elif 'reveal' in request.form:
            file = request.files['image']
            uploaded_path = os.path.join(UPLOAD_FOLDER, 'uploaded.png')
            file.save(uploaded_path)
            message = extract_text_from_image(uploaded_path)
    return render_template('index.html', message=message, image_path=image_url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/download')
def download():
    return send_file(os.path.join(UPLOAD_FOLDER, 'output.png'), as_attachment=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
