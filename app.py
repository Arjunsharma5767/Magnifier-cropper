import os
import base64
from flask import Flask, request, jsonify, render_template_string
from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")  # Use render_template to render the HTML file
if __name__ == "__main__":
    app.run(debug=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload




@app.route('/')
def index():
    return render_template_string(INDEX_HTML, css=CSS_STYLE)

@app.route('/crop', methods=['POST'])
def crop_image():
    try:
        # Get the image data and crop coordinates
        image_data = request.form.get('image_data')
        x = int(request.form.get('x'))
        y = int(request.form.get('y'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        
        # Check if coordinates are valid
        if width <= 0 or height <= 0:
            return jsonify({'success': False, 'error': 'Invalid crop dimensions'})
        
        # Process the base64 image data
        if image_data.startswith('data:image'):
            # Extract the base64 part from data URL
            image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        import io
        from PIL import Image
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Crop the image
        cropped_image = image.crop((x, y, x + width, y + height))
        
        # Convert back to base64
        buffer = io.BytesIO()
        cropped_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Return the cropped image as a data URL
        return jsonify({
            'success': True,
            'cropped_image': f'data:image/png;base64,{img_str}'
        })
    
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible from other machines on the network
    app.run(host='0.0.0.0', port=5000, debug=True)
