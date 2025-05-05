import os
import cv2
import numpy as np
from flask import Flask, request, send_from_directory, render_template_string, url_for, redirect, jsonify
from werkzeug.utils import secure_filename
import base64
import io
from PIL import Image

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
.button.process {
  background: #ea4335;
}
.button.process:hover {
  background: #d33426;
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
#selection-box {
  position: absolute;
  border: 2px dashed #ea4335;
  background-color: rgba(234, 67, 53, 0.2);
  pointer-events: none;
  display: none;
}
#cropped-image-container {
  margin-top: 30px;
}
#cropped-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}
.tab {
  padding: 10px 20px;
  background: #f0f0f0;
  border-radius: 5px 5px 0 0;
  cursor: pointer;
  margin: 0 5px;
  font-weight: 600;
}
.tab.active {
  background: #4285f4;
  color: white;
}
.tab-content {
  display: none;
}
.tab-content.active {
  display: block;
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
    <div id="upload-section">
      <div class="upload-area" id="drop-area" onclick="document.getElementById('file-input').click()">
        <div class="upload-icon">📁</div>
        <p>Click to select or drag and drop an image</p>
      </div>
      <input type="file" id="file-input" name="image" accept="image/*">
    </div>
    
    <div id="magnifier-section" style="display: none;">
      <div class="tabs">
        <div class="tab active" data-tab="original">Original Image</div>
        <div class="tab" data-tab="cropped" id="cropped-tab" style="display: none;">Cropped Image</div>
      </div>
      
      <div id="original-tab-content" class="tab-content active">
        <div class="control-panel">
          <div class="slider-container">
            <label for="intensity">Magnification Level: <span id="intensity-value">1</span>x</label>
            <input type="range" id="intensity" name="intensity" class="slider" min="1" max="5" value="1" step="0.1">
          </div>
          <div class="checkbox-container">
            <input type="checkbox" id="grayscale" name="grayscale">
            <label for="grayscale">Convert to Grayscale</label>
          </div>
          <div class="checkbox-container">
            <input type="checkbox" id="selection-mode" name="selection-mode">
            <label for="selection-mode">Enable Selection Mode</label>
          </div>
          <div class="instructions">
            <p>Drag to pan around the image. Use the slider to zoom in. Enable selection mode and drag to select an area for cropping.</p>
          </div>
        </div>
        
        <div id="magnified-image-container" class="no-select">
          <div class="loading" id="loading-indicator">Processing...</div>
          <img id="magnified-image" src="">
          <div id="selection-box"></div>
        </div>
        <div id="zoom-info">Current zoom: 1.0x</div>
        
        <div class="action-buttons">
          <button id="process-btn" class="button process">✂️ Crop Selected Area</button>
          <button id="download-btn" class="button download">⬇️ Download Magnified Image</button>
          <button id="new-image-btn" class="button">⏪ Upload New Image</button>
        </div>
      </div>
      
      <div id="cropped-tab-content" class="tab-content">
        <div class="control-panel">
          <div class="slider-container">
            <label for="cropped-intensity">Magnification Level: <span id="cropped-intensity-value">1</span>x</label>
            <input type="range" id="cropped-intensity" name="cropped-intensity" class="slider" min="1" max="5" value="1" step="0.1">
          </div>
          <div class="checkbox-container">
            <input type="checkbox" id="cropped-grayscale" name="cropped-grayscale">
            <label for="cropped-grayscale">Convert to Grayscale</label>
          </div>
          <div class="instructions">
            <p>Drag to pan around the cropped image. Use the slider to zoom in.</p>
          </div>
        </div>
        
        <div id="cropped-image-container" class="no-select">
          <div class="loading" id="cropped-loading-indicator">Processing...</div>
          <img id="cropped-image" src="">
        </div>
        <div id="cropped-zoom-info">Current zoom: 1.0x</div>
        
        <div class="action-buttons">
          <button id="cropped-download-btn" class="button download">⬇️ Download Cropped Image</button>
          <button id="back-to-original-btn" class="button">⏪ Back to Original</button>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    // DOM Elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.getElementById('upload-section');
    const magnifierSection = document.getElementById('magnifier-section');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const croppedTab = document.getElementById('cropped-tab');
    
    // Original image elements
    const intensitySlider = document.getElementById('intensity');
    const intensityValue = document.getElementById('intensity-value');
    const grayscaleCheckbox = document.getElementById('grayscale');
    const selectionModeCheckbox = document.getElementById('selection-mode');
    const magnifiedImage = document.getElementById('magnified-image');
    const magnifiedContainer = document.getElementById('magnified-image-container');
    const selectionBox = document.getElementById('selection-box');
    const zoomInfo = document.getElementById('zoom-info');
    const processBtn = document.getElementById('process-btn');
    const downloadBtn = document.getElementById('download-btn');
    const newImageBtn = document.getElementById('new-image-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Cropped image elements
    const croppedIntensitySlider = document.getElementById('cropped-intensity');
    const croppedIntensityValue = document.getElementById('cropped-intensity-value');
    const croppedGrayscaleCheckbox = document.getElementById('cropped-grayscale');
    const croppedImage = document.getElementById('cropped-image');
    const croppedContainer = document.getElementById('cropped-image-container');
    const croppedZoomInfo = document.getElementById('cropped-zoom-info');
    const croppedDownloadBtn = document.getElementById('cropped-download-btn');
    const backToOriginalBtn = document.getElementById('back-to-original-btn');
    const croppedLoadingIndicator = document.getElementById('cropped-loading-indicator');
    
    // Variables for dragging
    let isDragging = false;
    let startX, startY, startLeft, startTop;
    let currentScale = 1.0;
    let croppedCurrentScale = 1.0;
    let originalImageWidth, originalImageHeight;
    let croppedImageWidth, croppedImageHeight;
    let imageData = null;
    let croppedImageData = null;
    
    // Variables for selection
    let isSelecting = false;
    let selectionStartX, selectionStartY;
    let selectionBox = document.getElementById('selection-box');
    let selectionActive = false;
    
    // Tab switching
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabId = tab.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to current tab and content
        tab.classList.add('active');
        document.getElementById(`${tabId}-tab-content`).classList.add('active');
      });
    });
    
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
      
      // Reset selection
      selectionBox.style.display = 'none';
      selectionModeCheckbox.checked = false;
      selectionActive = false;
      
      // Hide cropped tab
      croppedTab.style.display = 'none';
      tabs[0].classList.add('active');
      tabs[1].classList.remove('active');
      tabContents[0].classList.add('active');
      tabContents[1].classList.remove('active');
      
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
        
        // Set up dragging
        setupDragging();
      };
      img.src = imageUrl;
    }
    
    // Set up dragging functionality
    function setupDragging() {
      // Mouse events for dragging
      magnifiedContainer.addEventListener('mousedown', startDragging);
      document.addEventListener('mousemove', dragImage);
      document.addEventListener('mouseup', stopDragging);
      
      // Touch events for dragging
      magnifiedContainer.addEventListener('touchstart', startDraggingTouch);
      document.addEventListener('touchmove', dragImageTouch);
      document.addEventListener('touchend', stopDragging);
      
      // Set up cropped image dragging
      croppedContainer.addEventListener('mousedown', startCroppedDragging);
      document.addEventListener('mousemove', dragCroppedImage);
      document.addEventListener('mouseup', stopCroppedDragging);
      
      croppedContainer.addEventListener('touchstart', startCroppedDraggingTouch);
      document.addEventListener('touchmove', dragCroppedImageTouch);
      document.addEventListener('touchend', stopCroppedDragging);
    }
    
    // Dragging functionality for original image
    function startDragging(e) {
      if (selectionModeCheckbox.checked) return; // Don't drag in selection mode
      
      e.preventDefault();
      isDragging = true;
      
      // Get the current position of the image
      const transform = window.getComputedStyle(magnifiedImage).getPropertyValue('transform');
      const matrix = new DOMMatrix(transform);
      
      // Get the starting position of the mouse
      startX = e.clientX;
      startY = e.clientY;
      
      // Get the current left and top values (from transform matrix or from style)
      startLeft = parseInt(magnifiedImage.style.left) || 0;
      startTop = parseInt(magnifiedImage.style.top) || 0;
    }
    
    function startDraggingTouch(e) {
      if (selectionModeCheckbox.checked) return; // Don't drag in selection mode
      
      if (e.touches.length === 1) {
        e.preventDefault();
        isDragging = true;
        
        const touch = e.touches[0];
        
        // Get the starting position of the touch
        startX = touch.clientX;
        startY = touch.clientY;
        
        // Get the current left and top values
        startLeft = parseInt(magnifiedImage.style.left) || 0;
        startTop = parseInt(magnifiedImage.style.top) || 0;
      }
    }
    
    function dragImage(e) {
      if (!isDragging) return;
      
      // Calculate the new position
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      
      let newLeft = startLeft + dx;
      let newTop = startTop + dy;
      
      // Calculate constraints to keep image within view
      const containerWidth = magnifiedContainer.clientWidth;
      const containerHeight = magnifiedContainer.clientHeight;
      const imageWidth = originalImageWidth * currentScale;
      const imageHeight = originalImageHeight * currentScale;
      
      // Set constraints so image doesn't go too far out of view
      // Allow dragging as long as at least part of the image is visible
      const minLeft = Math.min(0, containerWidth - imageWidth);
      const maxLeft = 0;
      const minTop = Math.min(0, containerHeight - imageHeight);
      const maxTop = 0;
      
      // Apply constraints
      newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
      newTop = Math.max(minTop, Math.min(maxTop, newTop));
      
      // Update image position
      magnifiedImage.style.left = `${newLeft}px`;
      magnifiedImage.style.top = `${newTop}px`;
    }
    
    function dragImageTouch(e) {
      if (!isDragging) return;
      
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        
        // Calculate the new position
        const dx = touch.clientX - startX;
        const dy = touch.clientY - startY;
        
        let newLeft = startLeft + dx;
        let newTop = startTop + dy;
        
        // Calculate constraints to keep image within view
        const containerWidth = magnifiedContainer.clientWidth;
        const containerHeight = magnifiedContainer.clientHeight;
        const imageWidth = originalImageWidth * currentScale;
        const imageHeight = originalImageHeight * currentScale;
        
        // Set constraints so image doesn't go too far out of view
        const minLeft = Math.min(0, containerWidth - imageWidth);
        const maxLeft = 0;
        const minTop = Math.min(0, containerHeight - imageHeight);
        const maxTop = 0;
        
        // Apply constraints
        newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
        newTop = Math.max(minTop, Math.min(maxTop, newTop));
        
        // Update image position
        magnifiedImage.style.left = `${newLeft}px`;
        magnifiedImage.style.top = `${newTop}px`;
      }
    }
    
    function stopDragging() {
      isDragging = false;
    }
    
    // Dragging functionality for cropped image
    let isCroppedDragging = false;
    let croppedStartX, croppedStartY, croppedStartLeft, croppedStartTop;
    
    function startCroppedDragging(e) {
      e.preventDefault();
      isCroppedDragging = true;
      
      // Get the starting position of the mouse
      croppedStartX = e.clientX;
      croppedStartY = e.clientY;
      
      // Get the current left and top values
      croppedStartLeft = parseInt(croppedImage.style.left) || 0;
      croppedStartTop = parseInt(croppedImage.style.top) || 0;
    }
    
    function startCroppedDraggingTouch(e) {
      if (e.touches.length === 1) {
        e.preventDefault();
        isCroppedDragging = true;
        
        const touch = e.touches[0];
        
        // Get the starting position of the touch
        croppedStartX = touch.clientX;
        croppedStartY = touch.clientY;
        
        // Get the current left and top values
        croppedStartLeft = parseInt(croppedImage.style.left) || 0;
        croppedStartTop = parseInt(croppedImage.style.top) || 0;
      }
    }
    
    function dragCroppedImage(e) {
      if (!isCroppedDragging) return;
      
      // Calculate the new position
      const dx = e.clientX - croppedStartX;
      const dy = e.clientY - croppedStartY;
      
      let newLeft = croppedStartLeft + dx;
      let newTop = croppedStartTop + dy;
      
      // Calculate constraints to keep image within view
      const containerWidth = croppedContainer.clientWidth;
      const containerHeight = croppedContainer.clientHeight;
      const imageWidth = croppedImageWidth * croppedCurrentScale;
      const imageHeight = croppedImageHeight * croppedCurrentScale;
      
      // Set constraints so image doesn't go too far out of view
      const minLeft = Math.min(0, containerWidth - imageWidth);
      const maxLeft = 0;
      const minTop = Math.min(0, containerHeight - imageHeight);
      const maxTop = 0;
      
      // Apply constraints
      newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
      newTop = Math.max(minTop, Math.min(maxTop, newTop));
      
      // Update image position
      croppedImage.style.left = `${newLeft}px`;
      croppedImage.style.top = `${newTop}px`;
    }
    
    function dragCroppedImageTouch(e) {
      if (!isCroppedDragging) return;
      
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        
        // Calculate the new position
        const dx = touch.clientX - croppedStartX;
        const dy = touch.clientY - croppedStartY;
        
        let newLeft = croppedStartLeft + dx;
        let newTop = croppedStartTop + dy;
        
        // Calculate constraints to keep image within view
        const containerWidth = croppedContainer.clientWidth;
        const containerHeight = croppedContainer.clientHeight;
        const imageWidth = croppedImageWidth * croppedCurrentScale;
        const imageHeight = croppedImageHeight * croppedCurrentScale;
        
        // Set constraints so image doesn't go too far out of view
        const minLeft = Math.min(0, containerWidth - imageWidth);
        const maxLeft = 0;
        const minTop = Math.min(0, containerHeight - imageHeight);
        const maxTop = 0;
        
        // Apply constraints
        newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
        newTop = Math.max(minTop, Math.min(maxTop, newTop));
        
        // Update image position
        croppedImage.style.left = `${newLeft}px`;
        croppedImage.style.top = `${newTop}px`;
      }
    }
    
    function stopCroppedDragging() {
      isCroppedDragging = false;
    }
    
    // Setup Cropped Image
    function setupCroppedImage(imageUrl) {
      // Show cropped tab
      croppedTab.style.display = 'block';
      
      // Reset zoom and position for cropped image
      croppedCurrentScale = 1.0;
      croppedIntensitySlider.value = 1;
      croppedIntensityValue.textContent = '1';
      croppedZoomInfo.textContent = 'Current zoom: 1.0x';
      
      // Load cropped image
      const img = new Image();
      img.onload = function() {
        croppedImageWidth = this.width;
        croppedImageHeight = this.height;
        
        // Set initial cropped image
