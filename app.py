import os
import cv2
import numpy as np
from flask import Flask, request, send_from_directory, render_template_string, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# ========== CSS ==========
CSS_STYLE = """
body {
  font-family: 'Arial', sans-serif;
  background: #f0f2f5;
  margin: 0;
  padding: 20px;
  min-height: 100vh;
}
.container {
  background: white;
  width: 95%;
  max-width: 800px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  margin: 0 auto;
}
h1, h3 {
  color: #333;
  margin-bottom: 20px;
}
.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  cursor: pointer;
}
.upload-area:hover {
  border-color: #4285f4;
  background-color: #f8f9fa;
}
input[type="file"] {
  display: none;
}
.control-panel {
  margin: 15px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}
.button {
  padding: 8px 16px;
  background: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  margin: 8px 5px;
}
.button:hover {
  background: #3367d6;
}
.button.download {
  background: #34a853;
}
.select-container {
  margin: 10px 0;
  text-align: left;
}
.select-container label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
}
.select-container select {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: white;
}
.image-container {
  margin-top: 20px;
}
.image-wrapper {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  margin-bottom: 15px;
}
.image-box {
  margin: 8px;
  text-align: center;
}
img {
  max-width: 300px;
  max-height: 300px;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.slider-container {
  margin: 15px 0;
  text-align: left;
}
.slider-container label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
}
.slider {
  width: 100%;
  height: 5px;
  border-radius: 5px;
  -webkit-appearance: none;
  background: #ddd;
  outline: none;
}
.image-editor {
  position: relative;
  margin: 20px auto;
  max-width: 500px;
}
.canvas-container {
  position: relative;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}
#preview-canvas {
  display: block;
  max-width: 100%;
}
.crop-box {
  position: absolute;
  border: 2px dashed #4285f4;
  background-color: rgba(66, 133, 244, 0.1);
  cursor: move;
}
.crop-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: #4285f4;
  border-radius: 50%;
}
.handle-nw { top: -5px; left: -5px; cursor: nw-resize; }
.handle-ne { top: -5px; right: -5px; cursor: ne-resize; }
.handle-sw { bottom: -5px; left: -5px; cursor: sw-resize; }
.handle-se { bottom: -5px; right: -5px; cursor: se-resize; }
.tool-options {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}
.tool-section {
  flex: 1;
  min-width: 150px;
  margin: 0 5px;
}
hr {
  margin: 20px 0; 
  border: 0; 
  border-top: 1px solid #eee;
}
@media (max-width: 600px) {
  .container {
    padding: 15px;
  }
  img {
    max-width: 100%;
    height: auto;
  }
  .image-wrapper {
    flex-direction: column;
    align-items: center;
  }
  .tool-section {
    min-width: 100%;
    margin: 5px 0;
  }
}
"""

# ========== INDEX HTML ==========
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Image Magnifier & Cropper</title>
  <style>{{ css }}</style>
</head>
<body>
  <div class="container">
    <h1>🔍 Image Magnifier & Cropper</h1>
    <form id="upload-form" action="/" method="POST" enctype="multipart/form-data">
      <div class="upload-area" id="drop-area" onclick="document.getElementById('file-input').click()">
        <div style="font-size: 36px; color: #4285f4; margin-bottom: 8px;">📁</div>
        <p>Click to select or drag and drop an image</p>
      </div>
      <input type="file" id="file-input" name="image" accept="image/*" required>
      <div class="control-panel">
        <div class="select-container">
          <label for="tool">Select Tool:</label>
          <select id="tool" name="tool">
            <option value="magnify">Magnify Area</option>
            <option value="crop">Crop Image</option>
          </select>
        </div>
        
        <div class="tool-options">
          <div class="tool-section" id="magnify-options">
            <div class="slider-container">
              <label for="magnification">Magnification Level: <span id="mag-value">2</span>x</label>
              <input type="range" id="magnification" name="magnification" min="1.5" max="5" value="2" step="0.5" class="slider">
            </div>
            <div class="select-container">
              <label for="mag-shape">Magnification Shape:</label>
              <select id="mag-shape" name="mag_shape">
                <option value="circle">Circle</option>
                <option value="rectangle">Rectangle</option>
              </select>
            </div>
          </div>
          
          <div class="tool-section" id="crop-options" style="display: none;">
            <div class="select-container">
              <label for="crop-ratio">Aspect Ratio:</label>
              <select id="crop-ratio" name="crop_ratio">
                <option value="free">Free Form</option>
                <option value="1:1">1:1 (Square)</option>
                <option value="4:3">4:3</option>
                <option value="16:9">16:9</option>
                <option value="3:2">3:2</option>
              </select>
            </div>
          </div>
        </div>
        
        <button type="submit" class="button">Upload & Process</button>
      </div>
    </form>
  </div>
  
  <script>
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const toolSelect = document.getElementById('tool');
    const magnifyOptions = document.getElementById('magnify-options');
    const cropOptions = document.getElementById('crop-options');
    const magSlider = document.getElementById('magnification');
    const magValue = document.getElementById('mag-value');
    
    // Update magnification value display when slider is moved
    magSlider.addEventListener('input', function() {
      magValue.textContent = this.value;
    });
    
    // Toggle tool options based on selection
    toolSelect.addEventListener('change', function() {
      if (this.value === 'magnify') {
        magnifyOptions.style.display = 'block';
        cropOptions.style.display = 'none';
      } else {
        magnifyOptions.style.display = 'none';
        cropOptions.style.display = 'block';
      }
    });
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
      dropArea.style.borderColor = '#4285f4';
      dropArea.style.backgroundColor = '#f0f7ff';
    }
    
    function unhighlight() {
      dropArea.style.borderColor = '#ccc';
      dropArea.style.backgroundColor = 'transparent';
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length) {
        fileInput.files = files;
      }
    }
  </script>
</body>
</html>
"""

# ========== EDITOR HTML ==========
EDITOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Image Editor</title>
  <style>{{ css }}</style>
</head>
<body>
  <div class="container">
    <h1>{{ tool_title }}</h1>
    
    <div class="image-editor">
      <div class="canvas-container" id="canvas-container">
        <canvas id="preview-canvas"></canvas>
        {% if tool == 'crop' %}
        <div class="crop-box" id="crop-box">
          <div class="crop-handle handle-nw" id="handle-nw"></div>
          <div class="crop-handle handle-ne" id="handle-ne"></div>
          <div class="crop-handle handle-sw" id="handle-sw"></div>
          <div class="crop-handle handle-se" id="handle-se"></div>
        </div>
        {% endif %}
      </div>
      
      <div class="control-panel">
        {% if tool == 'magnify' %}
        <div class="slider-container">
          <label for="magnification">Magnification Level: <span id="mag-value">{{ magnification }}</span>x</label>
          <input type="range" id="magnification" min="1.5" max="5" value="{{ magnification }}" step="0.5" class="slider">
        </div>
        
        <div class="select-container">
          <label for="mag-shape">Magnification Shape:</label>
          <select id="mag-shape">
            <option value="circle" {% if mag_shape == 'circle' %}selected{% endif %}>Circle</option>
            <option value="rectangle" {% if mag_shape == 'rectangle' %}selected{% endif %}>Rectangle</option>
          </select>
        </div>
        {% endif %}
        
        {% if tool == 'crop' %}
        <div class="select-container">
          <label for="crop-ratio">Aspect Ratio:</label>
          <select id="crop-ratio">
            <option value="free" {% if crop_ratio == 'free' %}selected{% endif %}>Free Form</option>
            <option value="1:1" {% if crop_ratio == '1:1' %}selected{% endif %}>1:1 (Square)</option>
            <option value="4:3" {% if crop_ratio == '4:3' %}selected{% endif %}>4:3</option>
            <option value="16:9" {% if crop_ratio == '16:9' %}selected{% endif %}>16:9</option>
            <option value="3:2" {% if crop_ratio == '3:2' %}selected{% endif %}>3:2</option>
          </select>
        </div>
        {% endif %}
        
        <form action="/process" method="POST" id="process-form">
          <input type="hidden" name="filename" value="{{ filename }}">
          <input type="hidden" name="tool" value="{{ tool }}">
          <input type="hidden" name="params" id="params-input">
          <button type="submit" class="button">Apply & Save</button>
          <a href="/" class="button" style="background-color: #ea4335;">Cancel</a>
        </form>
      </div>
    </div>
  </div>
  
  <script>
    // Get canvas and image elements
    const canvas = document.getElementById('preview-canvas');
    const ctx = canvas.getContext('2d');
    
    // Image data
    const imageSrc = "{{ url_for('uploaded_file', filename=filename) }}";
    const img = new Image();
    let imgWidth, imgHeight, canvasWidth, canvasHeight;
    let scale = 1;
    
    // Tool parameters
    const tool = "{{ tool }}";
    {% if tool == 'magnify' %}
    let magnification = {{ magnification }};
    let magShape = "{{ mag_shape }}";
    let magSize = 100; // Size of magnifier in pixels
    let magX = 0, magY = 0;
    const magSlider = document.getElementById('magnification');
    const magValue = document.getElementById('mag-value');
    const magShapeSelect = document.getElementById('mag-shape');
    
    // Update magnification value
    magSlider.addEventListener('input', function() {
      magnification = parseFloat(this.value);
      magValue.textContent = this.value;
      if (magnification < 1.5) magnification = 1.5;
      drawImage();
    });
    
    // Update magnifier shape
    magShapeSelect.addEventListener('change', function() {
      magShape = this.value;
      drawImage();
    });
    {% endif %}
    
    {% if tool == 'crop' %}
    // Crop parameters
    const cropBox = document.getElementById('crop-box');
    const handleNW = document.getElementById('handle-nw');
    const handleNE = document.getElementById('handle-ne');
    const handleSW = document.getElementById('handle-sw');
    const handleSE = document.getElementById('handle-se');
    const cropRatioSelect = document.getElementById('crop-ratio');
    
    let cropRatio = "{{ crop_ratio }}";
    let cropX = 50, cropY = 50;
    let cropWidth = 200, cropHeight = 200;
    let isDragging = false;
    let dragHandle = null;
    let startX, startY, startCropX, startCropY, startCropWidth, startCropHeight;
    
    // Update crop ratio
    cropRatioSelect.addEventListener('change', function() {
      cropRatio = this.value;
      if (cropRatio !== 'free') {
        const [width, height] = cropRatio.split(':').map(Number);
        const ratio = width / height;
        cropHeight = cropWidth / ratio;
        updateCropBoxPosition();
      }
    });
    
    // Crop box mouse events
    cropBox.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);
    cropBox.addEventListener('touchstart', startDrag);
    document.addEventListener('touchmove', drag);
    document.addEventListener('touchend', endDrag);
    
    // Handle mouse events
    handleNW.addEventListener('mousedown', function(e) { startDrag(e, 'nw'); });
    handleNE.addEventListener('mousedown', function(e) { startDrag(e, 'ne'); });
    handleSW.addEventListener('mousedown', function(e) { startDrag(e, 'sw'); });
    handleSE.addEventListener('mousedown', function(e) { startDrag(e, 'se'); });
    
    // Handle touch events
    handleNW.addEventListener('touchstart', function(e) { startDrag(e, 'nw'); });
    handleNE.addEventListener('touchstart', function(e) { startDrag(e, 'ne'); });
    handleSW.addEventListener('touchstart', function(e) { startDrag(e, 'sw'); });
    handleSE.addEventListener('touchstart', function(e) { startDrag(e, 'se'); });
    
    function startDrag(e, handle) {
      e.preventDefault();
      isDragging = true;
      dragHandle = handle || 'move';
      
      if (e.type === 'touchstart') {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
      } else {
        startX = e.clientX;
        startY = e.clientY;
      }
      
      startCropX = cropX;
      startCropY = cropY;
      startCropWidth = cropWidth;
      startCropHeight = cropHeight;
    }
    
    function drag(e) {
      if (!isDragging) return;
      e.preventDefault();
      
      let deltaX, deltaY;
      if (e.type === 'touchmove') {
        deltaX = e.touches[0].clientX - startX;
        deltaY = e.touches[0].clientY - startY;
      } else {
        deltaX = e.clientX - startX;
        deltaY = e.clientY - startY;
      }
      
      if (dragHandle === 'move') {
        cropX = Math.max(0, Math.min(canvasWidth - cropWidth, startCropX + deltaX));
        cropY = Math.max(0, Math.min(canvasHeight - cropHeight, startCropY + deltaY));
      } else {
        let newWidth = startCropWidth;
        let newHeight = startCropHeight;
        
        if (dragHandle === 'nw' || dragHandle === 'sw') {
          newWidth = startCropWidth - deltaX;
          cropX = startCropX + deltaX;
        } else {
          newWidth = startCropWidth + deltaX;
        }
        
        if (dragHandle === 'nw' || dragHandle === 'ne') {
          newHeight = startCropHeight - deltaY;
          cropY = startCropY + deltaY;
        } else {
          newHeight = startCropHeight + deltaY;
        }
        
        // Maintain aspect ratio if needed
        if (cropRatio !== 'free') {
          const [width, height] = cropRatio.split(':').map(Number);
          const ratio = width / height;
          
          if (dragHandle === 'nw' || dragHandle === 'se') {
            newHeight = newWidth / ratio;
          } else {
            newWidth = newHeight * ratio;
          }
          
          if (dragHandle === 'nw') {
            cropX = startCropX + startCropWidth - newWidth;
            cropY = startCropY + startCropHeight - newHeight;
          } else if (dragHandle === 'ne') {
            cropY = startCropY + startCropHeight - newHeight;
          } else if (dragHandle === 'sw') {
            cropX = startCropX + startCropWidth - newWidth;
          }
        }
        
        cropWidth = Math.max(50, newWidth);
        cropHeight = Math.max(50, newHeight);
      }
      
      updateCropBoxPosition();
    }
    
    function endDrag() {
      isDragging = false;
    }
    
    function updateCropBoxPosition() {
      cropBox.style.left = cropX + 'px';
      cropBox.style.top = cropY + 'px';
      cropBox.style.width = cropWidth + 'px';
      cropBox.style.height = cropHeight + 'px';
    }
    {% endif %}
    
    // Submit form with parameters
    document.getElementById('process-form').addEventListener('submit', function(e) {
      const paramsInput = document.getElementById('params-input');
      const params = {};
      
      {% if tool == 'magnify' %}
      params.magnification = magnification;
      params.mag_shape = magShape;
      params.mag_size = magSize;
      params.mag_x = magX / scale;
      params.mag_y = magY / scale;
      {% endif %}
      
      {% if tool == 'crop' %}
      params.crop_x = Math.round(cropX / scale);
      params.crop_y = Math.round(cropY / scale);
      params.crop_width = Math.round(cropWidth / scale);
      params.crop_height = Math.round(cropHeight / scale);
      {% endif %}
      
      paramsInput.value = JSON.stringify(params);
    });
    
    // Load and display image
    img.onload = function() {
      imgWidth = img.width;
      imgHeight = img.height;
      
      // Scale image to fit container
      const container = document.getElementById('canvas-container');
      const maxWidth = Math.min(500, window.innerWidth - 40);
      
      if (imgWidth > maxWidth) {
        scale = maxWidth / imgWidth;
        canvasWidth = maxWidth;
        canvasHeight = imgHeight * scale;
      } else {
        canvasWidth = imgWidth;
        canvasHeight = imgHeight;
      }
      
      canvas.width = canvasWidth;
      canvas.height = canvasHeight;
      container.style.width = canvasWidth + 'px';
      container.style.height = canvasHeight + 'px';
      
      {% if tool == 'magnify' %}
      // Set initial magnification position
      magX = canvasWidth / 2;
      magY = canvasHeight / 2;
      
      // Add event listeners for magnifier
      canvas.addEventListener('mousemove', updateMagnifier);
      canvas.addEventListener('touchmove', updateMagnifierTouch);
      {% endif %}
      
      {% if tool == 'crop' %}
      // Set initial crop box size and position
      cropX = canvasWidth * 0.1;
      cropY = canvasHeight * 0.1;
      cropWidth = canvasWidth * 0.8;
      cropHeight = canvasHeight * 0.8;
      
      // Apply aspect ratio if specified
      if (cropRatio !== 'free') {
        const [width, height] = cropRatio.split(':').map(Number);
        const ratio = width / height;
        cropHeight = cropWidth / ratio;
      }
      
      updateCropBoxPosition();
      {% endif %}
      
      drawImage();
    };
    
    img.src = imageSrc;
    
    {% if tool == 'magnify' %}
    function updateMagnifier(e) {
      const rect = canvas.getBoundingClientRect();
      magX = e.clientX - rect.left;
      magY = e.clientY - rect.top;
      drawImage();
    }
    
    function updateMagnifierTouch(e) {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      magX = e.touches[0].clientX - rect.left;
      magY = e.touches[0].clientY - rect.top;
      drawImage();
    }
    {% endif %}
    
    function drawImage() {
      // Clear canvas and draw image
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
      
      {% if tool == 'magnify' %}
      // Draw magnifier
      ctx.save();
      
      if (magShape === 'circle') {
        // Create circular clip path
        ctx.beginPath();
        ctx.arc(magX, magY, magSize/2, 0, Math.PI * 2);
        ctx.clip();
      } else {
        // Create rectangular clip path
        ctx.beginPath();
        ctx.rect(magX - magSize/2, magY - magSize/2, magSize, magSize);
        ctx.clip();
      }
      
      // Draw magnified image
      const zoomX = magX - (magX / magnification);
      const zoomY = magY - (magY / magnification);
      ctx.drawImage(img, 
                    zoomX / scale, zoomY / scale, 
                    canvasWidth / magnification, canvasHeight / magnification,
                    0, 0, canvasWidth, canvasHeight);
      
      // Draw border around magnifier
      if (magShape === 'circle') {
        ctx.beginPath();
        ctx.arc(magX, magY, magSize/2, 0, Math.PI * 2);
        ctx.strokeStyle = '#4285f4';
        ctx.lineWidth = 2;
        ctx.stroke();
      } else {
        ctx.strokeStyle = '#4285f4';
        ctx.lineWidth = 2;
        ctx.strokeRect(magX - magSize/2, magY - magSize/2, magSize, magSize);
      }
      
      ctx.restore();
      {% endif %}
    }
  </script>
</body>
</html>
"""

# ========== RESULT HTML ==========
RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Processing Result</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{{ css }}</style>
</head>
<body>
    <div class="container">
        <h1>✨ {{ tool_title }} Result</h1>
        
        <div class="image-container">
            <div class="image-wrapper">
                <div class="image-box">
                    <h3>Original</h3>
                    <img src="{{ url_for('uploaded_file', filename=filename) }}" alt="Original">
                </div>
                <div class="image-box">
                    <h3>Processed</h3>
                    <img src="{{ url_for('processed_file', filename=filename) }}" alt="Processed">
                </div>
            </div>
        </div>
        
        <div class="action-buttons">
            <a href="{{ url_for('download_file', filename=filename) }}" class="button download">Download Processed Image</a>
            <a href="/" class="button">Process Another Image</a>
        </div>
    </div>
</body>
</html>
"""

# ========== IMAGE PROCESSING ==========
def apply_magnification(input_path, output_path, params):
    """
    Apply magnification effect to a specific area of an image
    
    Parameters:
    - input_path: Path to the input image
    - output_path: Path to save the processed image
    - params: Dictionary containing magnification parameters
    """
    try:
        # Read the image
        image = cv2.imread(input_path)
        
        if image is None:
            raise ValueError(f"Failed to load image from {input_path}")
        
        # Get magnification parameters
        magnification = float(params.get('magnification', 2.0))
        mag_shape = params.get('mag_shape', 'circle')
        mag_size = int(params.get('mag_size', 100))
        mag_x = int(params.get('mag_x', image.shape[1] // 2))
        mag_y = int(params.get('mag_y', image.shape[0] // 2))
        
        # Create a copy of the original image
        result = image.copy()
        
        # Calculate the region to magnify
        height, width = image.shape[:2]
        mag_radius = mag_size // 2
        
        # Create a mask for the magnified area
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if mag_shape == 'circle':
            cv2.circle(mask, (mag_x, mag_y), mag_radius, 255, -1)
        else:  # rectangle
            cv2.rectangle(mask, 
                        (mag_x - mag_radius, mag_y - mag_radius),
                        (mag_x + mag_radius, mag_y + mag_radius),
                        255, -1)
        
        # Apply magnification
        # Calculate the center of the magnified region
        center_x = mag_x
        center_y = mag_y
        
        # For each pixel in the magnified area
        for y in range(max(0, mag_y - mag_radius), min(height, mag_y + mag_radius)):
            for x in range(max(0, mag_x - mag_radius), min(width, mag_x + mag_radius)):
                if mask[y, x] > 0:
                    # Calculate the source pixel for magnification
                    source_x = int(center_x + (x - center_x) / magnification)
                    source_y = int(center_y + (y - center_y) / magnification)
                    
                    # Check if the source pixel is within bounds
                    if 0 <= source_x < width and 0 <= source_y < height:
                        result[y, x] = image[source_y, source_x]
        
        # Draw border around the magnified area
        if mag_shape == 'circle':
            cv2.circle(result, (mag_x, mag_y), mag_radius, (0, 140, 255), 2)
        else:  # rectangle
            cv2.rectangle(result, 
                          (mag_x - mag_radius, mag_y - mag_radius),
                          (mag_x + mag_radius, mag_y + mag_radius),
                          (0, 140, 255), 2)

        # Save the processed image
        cv2.imwrite(output_path, result)
    except Exception as e:
        print(f"Error applying magnification: {e}")

def apply_crop(input_path, output_path, params):
    """
    Crop a specific area of an image
    
    Parameters:
    - input_path: Path to the input image
    - output_path: Path to save the processed image
    - params: Dictionary containing crop parameters
    """
    try:
        # Read the image
        image = cv2.imread(input_path)
        
        if image is None:
            raise ValueError(f"Failed to load image from {input_path}")
        
        # Get crop parameters
        crop_x = int(params.get('crop_x', 0))
        crop_y = int(params.get('crop_y', 0))
        crop_width = int(params.get('crop_width', image.shape[1]))
        crop_height = int(params.get('crop_height', image.shape[0]))
        
        # Perform cropping
        cropped_image = image[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
        
        # Save the processed image
        cv2.imwrite(output_path, cropped_image)
    except Exception as e:
        print(f"Error applying crop: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['image']
        tool = request.form['tool']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Redirect to the editor page
        return redirect(f'/editor?filename={filename}&tool={tool}')
    
    return render_template_string(INDEX_HTML, css=CSS_STYLE)

@app.route('/editor')
def editor():
    filename = request.args.get('filename')
    tool = request.args.get('tool')
    tool_title = "Magnify Area" if tool == 'magnify' else "Crop Image"
    magnification = 2.0 if tool == 'magnify' else None
    mag_shape = 'circle' if tool == 'magnify' else None
    crop_ratio = 'free' if tool == 'crop' else None
    
    return render_template_string(EDITOR_HTML, css=CSS_STYLE, filename=filename, tool=tool, 
                                  tool_title=tool_title, magnification=magnification, 
                                  mag_shape=mag_shape, crop_ratio=crop_ratio)

@app.route('/process', methods=['POST'])
def process():
    filename = request.form['filename']
    tool = request.form['tool']
    params = request.form.get('params')
    params = json.loads(params) if params else {}

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)

    if tool == 'magnify':
        apply_magnification(input_path, output_path, params)
    elif tool == 'crop':
        apply_crop(input_path, output_path, params)

    return redirect(f'/result?filename={filename}&tool={tool}')

@app.route('/result')
def result():
    filename = request.args.get('filename')
    tool = request.args.get('tool')
    tool_title = "Magnification" if tool == 'magnify' else "Crop"
    
    return render_template_string(RESULT_HTML, css=CSS_STYLE, filename=filename, tool_title=tool_title)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
