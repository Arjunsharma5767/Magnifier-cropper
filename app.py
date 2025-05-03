import os
import cv2
import numpy as np
from flask import Flask, request, send_from_directory, render_template_string, url_for, redirect, jsonify
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# ========== CSS ==========
CSS_STYLE = """
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  margin: 0;
  padding: 0;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
.container {
  background: white;
  width: 90%;
  max-width: 1000px;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
  text-align: center;
}
h1 {
  color: #333;
  margin-bottom: 30px;
  font-weight: 700;
  font-size: 2.2rem;
}
.upload-area {
  border: 2px dashed #ccc;
  border-radius: 10px;
  padding: 30px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.upload-area:hover {
  border-color: #4285f4;
  background-color: #f8f9fa;
}
.upload-icon {
  font-size: 48px;
  color: #4285f4;
  margin-bottom: 10px;
}
input[type="file"] {
  display: none;
}
.control-panel {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
}
.button {
  padding: 12px 24px;
  background: #4285f4;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  margin: 10px 5px;
}
.button:hover {
  background: #3367d6;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.button.download {
  background: #34a853;
}
.button.download:hover {
  background: #2d9249;
}
.slider-container {
  margin: 20px 0;
  text-align: left;
}
.slider-container label {
  display: block;
  margin-bottom: 8px;
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
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4285f4;
  cursor: pointer;
}
.image-container {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.image-wrapper {
  display: flex;
  justify-content: space-around;
  width: 100%;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.image-box {
  margin: 10px;
  text-align: center;
}
.image-box h3 {
  margin-bottom: 10px;
  color: #555;
}
img {
  max-width: 350px;
  max-height: 350px;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}
img:hover {
  transform: scale(1.03);
}
.back-link {
  display: block;
  margin-top: 20px;
  color: #4285f4;
  text-decoration: none;
  font-weight: 600;
}
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}
.checkbox-container {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin: 15px 0;
  padding: 5px;
}
.checkbox-container input[type="checkbox"] {
  display: inline-block;
  width: 18px;
  height: 18px;
  margin-right: 10px;
  cursor: pointer;
}
.checkbox-container label {
  font-weight: 600;
  color: #555;
  cursor: pointer;
}
.magnifier-container {
  position: relative;
  max-width: 700px;
  margin: 0 auto;
  overflow: hidden;
  border: 2px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.magnifier-image {
  width: 100%;
  display: block;
  cursor: move;
}
.image-preview {
  max-width: 100%;
  max-height: 400px;
  margin: 0 auto 20px;
  display: block;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
#magnified-image-container {
  width: 100%;
  height: 400px;
  overflow: hidden;
  position: relative;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  margin-top: 20px;
}
#magnified-image {
  position: absolute;
  transform-origin: top left;
  cursor: move;
}
.no-select {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}
#zoom-info {
  margin-top: 10px;
  font-weight: bold;
  color: #4285f4;
}
.instructions {
  margin: 15px 0;
  padding: 10px;
  background: #f0f7ff;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #555;
}
.loading {
  display: none;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #4285f4;
  font-size: 1.5rem;
  background: rgba(255,255,255,0.8);
  padding: 15px 30px;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
"""

# ========== INDEX HTML ==========
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Real-time Image Magnifier</title>
  <style>{{ css }}</style>
</head>
<body>
  <div class="container">
    <h1>🔍 Real-time Image Magnifier</h1>
    <div id="upload-section">
      <div class="upload-area" id="drop-area" onclick="document.getElementById('file-input').click()">
        <div class="upload-icon">📁</div>
        <p>Click to select or drag and drop an image</p>
      </div>
      <input type="file" id="file-input" name="image" accept="image/*">
    </div>
    
    <div id="magnifier-section" style="display: none;">
      <div class="control-panel">
        <div class="slider-container">
          <label for="intensity">Magnification Level: <span id="intensity-value">1</span>x</label>
          <input type="range" id="intensity" name="intensity" class="slider" min="1" max="5" value="1" step="0.1">
        </div>
        <div class="checkbox-container">
          <input type="checkbox" id="grayscale" name="grayscale">
          <label for="grayscale">Convert to Grayscale</label>
        </div>
        <div class="instructions">
          <p>Drag to pan around the image. Use the slider to zoom in and out.</p>
        </div>
      </div>
      
      <div id="magnified-image-container" class="no-select">
        <div class="loading" id="loading-indicator">Processing...</div>
        <img id="magnified-image" src="">
      </div>
      <div id="zoom-info">Current zoom: 1.0x</div>
      
      <div class="action-buttons">
        <button id="download-btn" class="button download">⬇️ Download Magnified Image</button>
        <button id="new-image-btn" class="button">⏪ Upload New Image</button>
      </div>
    </div>
  </div>
  
  <script>
    // DOM Elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.getElementById('upload-section');
    const magnifierSection = document.getElementById('magnifier-section');
    const intensitySlider = document.getElementById('intensity');
    const intensityValue = document.getElementById('intensity-value');
    const grayscaleCheckbox = document.getElementById('grayscale');
    const magnifiedImage = document.getElementById('magnified-image');
    const magnifiedContainer = document.getElementById('magnified-image-container');
    const zoomInfo = document.getElementById('zoom-info');
    const downloadBtn = document.getElementById('download-btn');
    const newImageBtn = document.getElementById('new-image-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Variables for dragging
    let isDragging = false;
    let startX, startY, startLeft, startTop;
    let currentScale = 1.0;
    let originalImageWidth, originalImageHeight;
    let imageData = null;
    
    // Event Listeners for drag and drop
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
    
    // File Upload Handling
    dropArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);
    
    function handleDrop(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length) {
        handleFiles(files);
      }
    }
    
    function handleFileSelect(e) {
      const files = e.target.files;
      if (files.length) {
        handleFiles(files);
      }
    }
    
    function handleFiles(files) {
      if (files[0].type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
          imageData = e.target.result;
          setupMagnifier(imageData);
        };
        reader.readAsDataURL(files[0]);
      } else {
        alert("Please select an image file.");
      }
    }
    
    // Setup Magnifier
    function setupMagnifier(imageUrl) {
      // Switch from upload to magnifier view
      uploadSection.style.display = 'none';
      magnifierSection.style.display = 'block';
      
      // Reset zoom and position
      currentScale = 1.0;
      intensitySlider.value = 1;
      intensityValue.textContent = '1';
      zoomInfo.textContent = 'Current zoom: 1.0x';
      
      // Load image
      const img = new Image();
      img.onload = function() {
        originalImageWidth = this.width;
        originalImageHeight = this.height;
        
        // Set initial image
        magnifiedImage.src = imageUrl;
        magnifiedImage.style.width = '100%';
        magnifiedImage.style.height = 'auto';
        magnifiedImage.style.top = '0';
        magnifiedImage.style.left = '0';
        magnifiedImage.style.transform = 'scale(1)';
        
        // Apply grayscale if needed
        applyGrayscale();
      };
      img.src = imageUrl;
    }
    
    // Magnification Control
    intensitySlider.addEventListener('input', updateMagnification);
    grayscaleCheckbox.addEventListener('change', applyGrayscale);
    
    function updateMagnification() {
      currentScale = parseFloat(intensitySlider.value);
      intensityValue.textContent = currentScale.toFixed(1);
      zoomInfo.textContent = `Current zoom: ${currentScale.toFixed(1)}x`;
      
      // Apply transform
      magnifiedImage.style.transform = `scale(${currentScale})`;
      
      // Center the image when zooming
      centerImage();
    }
    
    function centerImage() {
      const containerWidth = magnifiedContainer.clientWidth;
      const containerHeight = magnifiedContainer.clientHeight;
      
      // Calculate scaled image dimensions
      const scaledWidth = originalImageWidth * currentScale;
      const scaledHeight = originalImageHeight * currentScale;
      
      // Center the image
      let leftPos = (containerWidth - scaledWidth) / 2;
      let topPos = (containerHeight - scaledHeight) / 2;
      
      // Ensure the image doesn't get positioned outside the viewable area
      leftPos = Math.min(0, Math.max(leftPos, containerWidth - scaledWidth));
      topPos = Math.min(0, Math.max(topPos, containerHeight - scaledHeight));
      
      magnifiedImage.style.left = `${leftPos}px`;
      magnifiedImage.style.top = `${topPos}px`;
    }
    
    // Grayscale Control
    function applyGrayscale() {
      loadingIndicator.style.display = 'block';
      
      // Small timeout to allow loading indicator to appear
      setTimeout(() => {
        if (grayscaleCheckbox.checked) {
          magnifiedImage.style.filter = 'grayscale(100%)';
        } else {
          magnifiedImage.style.filter = 'none';
        }
        loadingIndicator.style.display = 'none';
      }, 100);
    }
    
    // Image Download
    downloadBtn.addEventListener('click', downloadImage);
    
    function downloadImage() {
      // Create a canvas to draw the magnified image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = function() {
        // Set canvas size to the scaled image size
        canvas.width = img.width * currentScale;
        canvas.height = img.height * currentScale;
        
        // Apply grayscale if needed
        if (grayscaleCheckbox.checked) {
          ctx.filter = 'grayscale(100%)';
        }
        
        // Draw the scaled image
        ctx.scale(currentScale, currentScale);
        ctx.drawImage(img, 0, 0);
        
        // Create download link
        const link = document.createElement('a');
        link.download = 'magnified_image.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
      };
      
      img.src = imageData;
    }
    
    // Reset to upload new image
    newImageBtn.addEventListener('click', resetToUpload);
    
    function resetToUpload() {
      uploadSection.style.display = 'block';
      magnifierSection.style.display = 'none';
      fileInput.value = '';
    }
    
    // Dragging functionality
    magnifiedImage.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);
    
    // Touch support
    magnifiedImage.addEventListener('touchstart', startDragTouch);
    document.addEventListener('touchmove', dragTouch);
    document.addEventListener('touchend', endDrag);
    
    function startDrag(e) {
      e.preventDefault();
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      startLeft = parseInt(window.getComputedStyle(magnifiedImage).left) || 0;
      startTop = parseInt(window.getComputedStyle(magnifiedImage).top) || 0;
      magnifiedImage.style.cursor = 'grabbing';
    }
    
    function startDragTouch(e) {
      if (e.touches.length === 1) {
        isDragging = true;
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        startLeft = parseInt(window.getComputedStyle(magnifiedImage).left) || 0;
        startTop = parseInt(window.getComputedStyle(magnifiedImage).top) || 0;
      }
    }
    
    function drag(e) {
      if (!isDragging) return;
      e.preventDefault();
      
      const x = e.clientX;
      const y = e.clientY;
      const containerWidth = magnifiedContainer.clientWidth;
      const containerHeight = magnifiedContainer.clientHeight;
      
      // Calculate how far the mouse has moved
      const deltaX = x - startX;
      const deltaY = y - startY;
      
      // Calculate new position
      let newLeft = startLeft + deltaX;
      let newTop = startTop + deltaY;
      
      // Calculate boundaries based on scaled image size
      const scaledWidth = originalImageWidth * currentScale;
      const scaledHeight = originalImageHeight * currentScale;
      
      // Prevent moving the image too far
      newLeft = Math.min(0, Math.max(newLeft, containerWidth - scaledWidth));
      newTop = Math.min(0, Math.max(newTop, containerHeight - scaledHeight));
      
      // Apply new position
      magnifiedImage.style.left = `${newLeft}px`;
      magnifiedImage.style.top = `${newTop}px`;
    }
    
    function dragTouch(e) {
      if (!isDragging) return;
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        const x = touch.clientX;
        const y = touch.clientY;
        const containerWidth = magnifiedContainer.clientWidth;
        const containerHeight = magnifiedContainer.clientHeight;
        
        // Calculate how far the touch has moved
        const deltaX = x - startX;
        const deltaY = y - startY;
        
        // Calculate new position
        let newLeft = startLeft + deltaX;
        let newTop = startTop + deltaY;
        
        // Calculate boundaries based on scaled image size
        const scaledWidth = originalImageWidth * currentScale;
        const scaledHeight = originalImageHeight * currentScale;
        
        // Prevent moving the image too far
        newLeft = Math.min(0, Math.max(newLeft, containerWidth - scaledWidth));
        newTop = Math.min(0, Math.max(newTop, containerHeight - scaledHeight));
        
        // Apply new position
        magnifiedImage.style.left = `${newLeft}px`;
        magnifiedImage.style.top = `${newTop}px`;
      }
    }
    
    function endDrag() {
      isDragging = false;
      magnifiedImage.style.cursor = 'move';
    }
  </script>
</body>
</html>
"""

# ========== ROUTES ==========
@app.route('/', methods=['GET'])
def index():
    return render_template_string(INDEX_HTML, css=CSS_STYLE)

# Route to serve static files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Helper function to process image using OpenCV
def process_image(image_data, intensity=1.0, grayscale=False):
    # Decode the base64 image
    try:
        # Strip the header
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None, "Failed to decode image"
        
        # Convert to grayscale if requested
        if grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        # Convert back to base64
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode('utf-8'), None
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None, str(e)

if __name__ == '__main__':
    app.run(debug=True)
