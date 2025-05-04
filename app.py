import os
import base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

CSS_STYLE = """
/* (Keep the existing CSS styles unchanged) */
"""

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Image Magnifier & Cropper</title>
<style>{{ css }}</style>
</head>
<body>
<!-- (Keep the existing HTML structure unchanged) -->
<script>
// Previous JavaScript code with the following key changes:

function setupMagnifier(imageUrl) {
  // ... existing code ...
  const img = new Image();
  img.onload = function() {
    originalImageWidth = this.width;
    originalImageHeight = this.height;
    magnifiedImage.src = imageUrl;
    // Removed conflicting width/height styles
    magnifiedImage.style.top = '0px';
    magnifiedImage.style.left = '0px';
    magnifiedImage.style.transform = 'scale(1)';
    applyGrayscale();
    setupDragging();
  };
  img.src = imageUrl;
}

// Updated download handlers
downloadBtn.addEventListener('click', () => {
  if (!imageData) return;
  
  const container = document.getElementById('magnified-image-container');
  const canvas = document.createElement('canvas');
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  const ctx = canvas.getContext('2d');
  
  const scale = currentScale;
  const left = parseInt(magnifiedImage.style.left) || 0;
  const top = parseInt(magnifiedImage.style.top) || 0;
  
  const img = new Image();
  img.onload = function() {
    const sourceX = Math.max(0, -left / scale);
    const sourceY = Math.max(0, -top / scale);
    const sourceWidth = Math.min(container.clientWidth / scale, originalImageWidth - sourceX);
    const sourceHeight = Math.min(container.clientHeight / scale, originalImageHeight - sourceY);
    
    ctx.drawImage(
      img,
      sourceX,
      sourceY,
      sourceWidth,
      sourceHeight,
      0,
      0,
      container.clientWidth,
      container.clientHeight
    );
    
    if (grayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i+1] + data[i+2]) / 3;
        data[i] = avg;
        data[i+1] = avg;
        data[i+2] = avg;
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    const dataUrl = canvas.toDataURL('image/png');
    downloadImage(dataUrl, 'magnified-image.png');
  };
  img.src = imageData;
});

croppedDownloadBtn.addEventListener('click', () => {
  if (!croppedImageData) return;
  
  const container = document.getElementById('cropped-image-container');
  const canvas = document.createElement('canvas');
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  const ctx = canvas.getContext('2d');
  
  const scale = croppedCurrentScale;
  const left = parseInt(croppedImage.style.left) || 0;
  const top = parseInt(croppedImage.style.top) || 0;
  
  const img = new Image();
  img.onload = function() {
    const sourceX = Math.max(0, -left / scale);
    const sourceY = Math.max(0, -top / scale);
    const sourceWidth = Math.min(container.clientWidth / scale, croppedImageWidth - sourceX);
    const sourceHeight = Math.min(container.clientHeight / scale, croppedImageHeight - sourceY);
    
    ctx.drawImage(
      img,
      sourceX,
      sourceY,
      sourceWidth,
      sourceHeight,
      0,
      0,
      container.clientWidth,
      container.clientHeight
    );
    
    if (croppedGrayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i+1] + data[i+2]) / 3;
        data[i] = avg;
        data[i+1] = avg;
        data[i+2] = avg;
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    const dataUrl = canvas.toDataURL('image/png');
    downloadImage(dataUrl, 'cropped-image.png');
  };
  img.src = croppedImageData;
});

// Remaining JavaScript code unchanged...
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, css=CSS_STYLE)

if __name__ == '__main__':
    app.run(debug=True)
