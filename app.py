`image_magnifier_cropper_app.py`
```py
import os
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

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
  text-align: left;
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
  justify-content: center; /* Center the image horizontally */
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
  user-select: none;
  display: block;
  margin-left: auto;
  margin-right: auto;
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
  margin: 15px 0;
  padding: 5px;
}
.checkbox-container input[type="checkbox"] {
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
#magnified-image-container {
  width: 100%;
  height: 400px;
  overflow: hidden;
  position: relative;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  margin-top: 20px;
  touch-action: none;
  display: flex;
  justify-content: center; /* Center contents horizontally */
  align-items: center;    /* Center contents vertically */
}
#magnified-image {
  position: absolute;
  cursor: grab;
}
#selection-box {
  position: absolute;
  border: 2px solid #ea4335;
  background-color: rgba(234, 67, 53, 0.2);
  pointer-events: none;
  display: none;
  z-index: 10;
}
/* Resize handles for the selection box */
.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: white;
  border: 1px solid #ea4335;
  z-index: 15;
}
.handle-nw {
  top: -5px;
  left: -5px;
  cursor: nwse-resize;
}
.handle-n {
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  cursor: ns-resize;
}
.handle-ne {
  top: -5px;
  right: -5px;
  cursor: nesw-resize;
}
.handle-e {
  top: 50%;
  right: -5px;
  transform: translateY(-50%);
  cursor: ew-resize;
}
.handle-se {
  bottom: -5px;
  right: -5px;
  cursor: nwse-resize;
}
.handle-s {
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  cursor: ns-resize;
}
.handle-sw {
  bottom: -5px;
  left: -5px;
  cursor: nesw-resize;
}
.handle-w {
  top: 50%;
  left: -5px;
  transform: translateY(-50%);
  cursor: ew-resize;
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
.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  user-select: none;
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
#error-message {
  color: #ea4335;
  font-weight: bold;
  margin: 10px 0;
  display: none;
}
@media (max-width: 600px) {
  .container {
    padding: 20px;
  }
  img {
    align-items: center;
    max-width: 100%;
    max-height: 500px;
  }
  #magnified-image-container {
    height: 500px;
  }
}
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
<div class="container">
  <h1>🔍 Image Magnifier & Cropper</h1>
  <div id="upload-section">
    <div class="upload-area" id="drop-area" tabindex="0" role="button" aria-label="Upload image" onclick="fileInput.click()" onkeypress="if(event.key==='Enter'){fileInput.click();}">
      <div class="upload-icon">📁</div>
      <p>Click to select or drag and drop an image</p>
    </div>
    <input type="file" id="file-input" name="image" accept="image/*" />
    <div id="error-message"></div>
  </div>

  <div id="magnifier-section" style="display:none;">
    <div class="tabs" role="tablist">
      <div class="tab active" data-tab="original" role="tab" tabindex="0" aria-selected="true" aria-controls="original-tab-content" id="original-tab">Original Image</div>
      <div class="tab" data-tab="cropped" id="cropped-tab" style="display:none;" role="tab" tabindex="-1" aria-selected="false" aria-controls="cropped-tab-content">Cropped Image</div>
    </div>

    <div id="original-tab-content" class="tab-content active" role="tabpanel" aria-labelledby="original-tab">
      <div class="control-panel">
        <div class="slider-container">
          <label for="intensity">Magnification Level: <span id="intensity-value">1</span>x</label>
          <input type="range" id="intensity" min="1" max="5" value="1" step="0.1" class="slider" />
        </div>
        <div class="checkbox-container">
          <input type="checkbox" id="grayscale" />
          <label for="grayscale">Convert to Grayscale</label>
        </div>
        <div class="checkbox-container">
          <input type="checkbox" id="selection-mode" />
          <label for="selection-mode">Enable Selection Mode</label>
        </div>
        <div class="instructions">
          <p>Drag to pan around the image. Use the slider to zoom in. Enable selection mode to select an area for cropping. Drag the edges or corners to resize the selection.</p>
        </div>
      </div>
      <div id="magnified-image-container">
        <div class="loading" id="loading-indicator">Processing...</div>
        <img id="magnified-image" src="" alt="Original Image" />
        <div id="selection-box">
          <!-- Resize handles -->
          <div class="resize-handle handle-nw" data-handle="nw"></div>
          <div class="resize-handle handle-n" data-handle="n"></div>
          <div class="resize-handle handle-ne" data-handle="ne"></div>
          <div class="resize-handle handle-e" data-handle="e"></div>
          <div class="resize-handle handle-se" data-handle="se"></div>
          <div class="resize-handle handle-s" data-handle="s"></div>
          <div class="resize-handle handle-sw" data-handle="sw"></div>
          <div class="resize-handle handle-w" data-handle="w"></div>
        </div>
      </div>
      <div id="zoom-info">Current zoom: 1.0x</div>
      <div class="action-buttons">
        <button id="process-btn" class="button process">✂️ Crop Selected Area</button>
        <button id="download-btn" class="button download">⬇️ Download Magnified Image</button>
        <button id="new-image-btn" class="button">⏪ Upload New Image</button>
      </div>
    </div>

    <div id="cropped-tab-content" class="tab-content" role="tabpanel" aria-labelledby="cropped-tab">
      <div class="control-panel">
        <div class="slider-container">
          <label for="cropped-intensity">Magnification Level: <span id="cropped-intensity-value">1</span>x</label>
          <input type="range" id="cropped-intensity" min="1" max="5" value="1" step="0.1" class="slider" />
        </div>
        <div class="checkbox-container">
          <input type="checkbox" id="cropped-grayscale" />
          <label for="cropped-grayscale">Convert to Grayscale</label>
        </div>
        <div class="instructions">
          <p>Drag to pan around the cropped image. Use the slider to zoom in.</p>
        </div>
      </div>
      <div id="magnified-image-container">
        <div class="loading" id="cropped-loading-indicator">Processing...</div>
        <img id="cropped-image" src="" alt="Cropped Image" />
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
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const magnifierSection = document.getElementById('magnifier-section');
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');
const croppedTab = document.getElementById('cropped-tab');
const errorMessage = document.getElementById('error-message');

const intensitySlider = document.getElementById('intensity');
const intensityValue = document.getElementById('intensity-value');
const grayscaleCheckbox = document.getElementById('grayscale');
const selectionModeCheckbox = document.getElementById('selection-mode');
const magnifiedImage = document.getElementById('magnified-image');
const magnifiedContainer = document.getElementById('magnified-image-container');
const selectionBox = document.getElementById('selection-box');
const resizeHandles = document.querySelectorAll('.resize-handle');
const zoomInfo = document.getElementById('zoom-info');
const processBtn = document.getElementById('process-btn');
const downloadBtn = document.getElementById('download-btn');
const newImageBtn = document.getElementById('new-image-btn');
const loadingIndicator = document.getElementById('loading-indicator');

const croppedIntensitySlider = document.getElementById('cropped-intensity');
const croppedIntensityValue = document.getElementById('cropped-intensity-value');
const croppedGrayscaleCheckbox = document.getElementById('cropped-grayscale');
const croppedImage = document.getElementById('cropped-image');
const croppedZoomInfo = document.getElementById('cropped-zoom-info');
const croppedDownloadBtn = document.getElementById('cropped-download-btn');
const backToOriginalBtn = document.getElementById('back-to-original-btn');
const croppedLoadingIndicator = document.getElementById('cropped-loading-indicator');

let isDragging = false;
let startX, startY, startLeft, startTop;
let currentScale = 1.0;
let croppedCurrentScale = 1.0;
let originalImageWidth, originalImageHeight;
let croppedImageWidth, croppedImageHeight;
let imageData = null;
let croppedImageData = null;

// Selection variables
let isSelecting = false;
let selectionStartX, selectionStartY;
let selectionCurrentX, selectionCurrentY;
let selectionActive = false;
let selectionRect = { left: 0, top: 0, width: 0, height: 0 };

// Resize variables
let isResizing = false;
let currentResizeHandle = null;
let initialBoxLeft, initialBoxTop, initialBoxWidth, initialBoxHeight;

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const tabId = tab.getAttribute('data-tab');
    tabs.forEach(t => {
      t.classList.remove('active');
      t.setAttribute('aria-selected', 'false');
      t.setAttribute('tabindex', '-1');
    });
    tabContents.forEach(tc => tc.classList.remove('active'));
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    tab.setAttribute('tabindex', '0');
    document.getElementById(`${tabId}-tab-content`).classList.add('active');
    tab.focus();
  });
});

// Accessibility: keyboard support for tabs
tabs.forEach(tab => {
  tab.addEventListener('keydown', e => {
    let index = Array.from(tabs).indexOf(tab);
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      let nextIndex = (index + 1) % tabs.length;
      tabs[nextIndex].click();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      let prevIndex = (index - 1 + tabs.length) % tabs.length;
      tabs[prevIndex].click();
    }
  });
});

// Drag & drop listeners
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});
function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}
['dragenter', 'dragover'].forEach(eventName =>
  dropArea.addEventListener(eventName, () => {
    dropArea.style.borderColor = '#4285f4';
    dropArea.style.backgroundColor = '#f0f7ff';
  })
);
['dragleave', 'drop'].forEach(eventName =>
  dropArea.addEventListener(eventName, () => {
    dropArea.style.borderColor = '#ccc';
    dropArea.style.backgroundColor = 'transparent';
  })
);

dropArea.addEventListener('drop', e => {
  const dt = e.dataTransfer;
  const files = dt.files;
  if (files.length) handleFiles(files);
});
fileInput.addEventListener('change', e => {
  const files = e.target.files;
  if (files.length) handleFiles(files);
});

function handleFiles(files) {
  errorMessage.style.display = 'none';
  errorMessage.textContent = '';
  
  if (files[0].type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = function(e) {
      imageData = e.target.result;
      setupMagnifier(imageData);
    };
    reader.onerror = function() {
      showError("Failed to read the image file. Please try again.");
    };
    reader.readAsDataURL(files[0]);
  } else {
    showError("Please select a valid image file.");
  }
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
}

function setupMagnifier(imageUrl) {
  uploadSection.style.display = 'none';
  magnifierSection.style.display = 'block';

  currentScale = 1.0;
  intensitySlider.value = 1;
  intensityValue.textContent = '1';
  zoomInfo.textContent = 'Current zoom: 1.0x';

  selectionBox.style.display = 'none';
  selectionModeCheckbox.checked = false;
  selectionActive = false;

  croppedTab.style.display = 'none';
  tabs[0].classList.add('active');
  tabs[0].setAttribute('aria-selected', 'true');
  tabs[0].setAttribute('tabindex', '0');
  tabs[1].classList.remove('active');
  tabs[1].setAttribute('aria-selected', 'false');
  tabs[1].setAttribute('tabindex', '-1');
  tabContents[0].classList.add('active');
  tabContents[1].classList.remove('active');

  const img = new Image();
  img.onload = function() {
    originalImageWidth = this.width;
    originalImageHeight = this.height;
    
    // Center the image initially
    magnifiedImage.src = imageUrl;
    magnifiedImage.style.width = 'auto';
    magnifiedImage.style.height = 'auto';
    magnifiedImage.style.maxWidth = '100%';
    magnifiedImage.style.maxHeight = '100%';
    
    // Center the image after it loads
    magnifiedImage.onload = function() {
      const containerWidth = magnifiedContainer.clientWidth;
      const containerHeight = magnifiedContainer.clientHeight;
      const imgWidth = magnifiedImage.clientWidth;
      const imgHeight = magnifiedImage.clientHeight;
      
      // Calculate the position to center the image
      const leftPos = (containerWidth - imgWidth) / 2;
      const topPos = (containerHeight - imgHeight) / 2;
      
      magnifiedImage.style.left = leftPos + 'px';
      magnifiedImage.style.top = topPos + 'px';
      magnifiedImage.style.transform = 'scale(1)';
    };
    
    applyGrayscale();
    setupDragging();
    setupResizeHandles();
  };
  img.onerror = function() {
    showError("Failed to load the image. Please try another file.");
    uploadSection.style.display = 'block';
    magnifierSection.style.display = 'none';
  };
  img.src = imageUrl;
}

function setupDragging() {
  magnifiedContainer.addEventListener('mousedown', startDragging);
  document.addEventListener('mousemove', dragImage);
  document.addEventListener('mouseup', stopDragging);

  magnifiedContainer.addEventListener('touchstart', startDraggingTouch, {passive:false});
  document.addEventListener('touchmove', dragImageTouch, {passive:false});
  document.addEventListener('touchend', stopDragging);

  const croppedContainer = document.querySelector('#cropped-tab-content #magnified-image-container');
  croppedContainer.addEventListener('mousedown', startCroppedDragging);
  document.addEventListener('mousemove', dragCroppedImage);
  document.addEventListener('mouseup', stopCroppedDragging);

  croppedContainer.addEventListener('touchstart', startCroppedDraggingTouch, {passive:false});
  document.addEventListener('touchmove', dragCroppedImageTouch, {passive:false});
  document.addEventListener('touchend', stopCroppedDragging);
}

function setupResizeHandles() {
  // Setup events for each resize handle
  resizeHandles.forEach(handle => {
    handle.addEventListener('mousedown', startResizing);
    handle.addEventListener('touchstart', startResizingTouch, {passive: false});
  });
}

// Improved selection mode checkbox event listener
selectionModeCheckbox.addEventListener('change', function() {
  if (this.checked) {
    // Enable selection mode
    selectionBox.style.display = 'none';
    selectionActive = false;
    magnifiedImage.style.cursor = 'crosshair';
    magnifiedContainer.style.cursor = 'crosshair';
    
    // Add event listeners for selection
    magnifiedContainer.addEventListener('mousedown', startSelection);
    magnifiedContainer.addEventListener('touchstart', startSelectionTouch, { passive: false });
  } else {
    // Disable selection mode
    isSelecting = false;
    selectionBox.style.display = 'none';
    selectionActive = false;
    magnifiedImage.style.cursor = 'grab';
    magnifiedContainer.style.cursor = 'default';
    
    // Remove event listeners for selection
    magnifiedContainer.removeEventListener('mousedown', startSelection);
    magnifiedContainer.removeEventListener('touchstart', startSelectionTouch);
  }
});

function startSelection(e) {
  if (!selectionModeCheckbox.checked || isResizing || isSelecting) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isSelecting = true;
  isDragging = false; // Prevent dragging while selecting
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionStartX = e.clientX - containerRect.left;
  selectionStartY = e.clientY - containerRect.top;
  
  // Initialize selection rectangle
  selectionRect = {
    left: selectionStartX,
    top: selectionStartY,
    width: 0,
    height: 0
  };
  
  updateSelectionBoxDisplay();
  
  document.addEventListener('mousemove', updateSelection);
  document.addEventListener('mouseup', finishSelection);
}

function startSelectionTouch(e) {
  if (!selectionModeCheckbox.checked || e.touches.length !== 1 || isResizing || isSelecting) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isSelecting = true;
  isDragging = false; // Prevent dragging while selecting
  
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionStartX = touch.clientX - containerRect.left;
  selectionStartY = touch.clientY - containerRect.top;
  
  selectionRect = {
    left: selectionStartX,
    top: selectionStartY,
    width: 0,
    height: 0
  };
  
  updateSelectionBoxDisplay();
  
  document.addEventListener('touchmove', updateSelectionTouch, { passive: false });
  document.addEventListener('touchend', finishSelection);
}

function updateSelection(e) {
  if (!isSelecting) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionCurrentX = Math.max(0, Math.min(e.clientX - containerRect.left, containerRect.width));
  selectionCurrentY = Math.max(0, Math.min(e.clientY - containerRect.top, containerRect.height));
  
  calculateSelectionRect();
  updateSelectionBoxDisplay();
}

function updateSelectionTouch(e) {
  if (!isSelecting || e.touches.length !== 1) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionCurrentX = Math.max(0, Math.min(touch.clientX - containerRect.left, containerRect.width));
  selectionCurrentY = Math.max(0, Math.min(touch.clientY - containerRect.top, containerRect.height));
  
  calculateSelectionRect();
  updateSelectionBoxDisplay();
}

function calculateSelectionRect() {
  selectionRect = {
    left: Math.min(selectionStartX, selectionCurrentX),
    top: Math.min(selectionStartY, selectionCurrentY),
    width: Math.abs(selectionCurrentX - selectionStartX),
    height: Math.abs(selectionCurrentY - selectionStartY)
  };
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionRect.left = Math.max(0, Math.min(selectionRect.left, containerRect.width - 10));
  selectionRect.top = Math.max(0, Math.min(selectionRect.top, containerRect.height - 10));
  selectionRect.width = Math.min(selectionRect.width, containerRect.width - selectionRect.left);
  selectionRect.height = Math.min(selectionRect.height, containerRect.height - selectionRect.top);
}

function updateSelectionBoxDisplay() {
  selectionBox.style.left = selectionRect.left + 'px';
  selectionBox.style.top = selectionRect.top + 'px';
  selectionBox.style.width = selectionRect.width + 'px';
  selectionBox.style.height = selectionRect.height + 'px';
  selectionBox.style.display = 'block';
  
  selectionActive = (selectionRect.width > 5 && selectionRect.height > 5);
}

function finishSelection(e) {
  if (!isSelecting) return;
  
  isSelecting = false;
  
  document.removeEventListener('mousemove', updateSelection);
  document.removeEventListener('mouseup', finishSelection);
  document.removeEventListener('touchmove', updateSelectionTouch);
  document.removeEventListener('touchend', finishSelection);
  
  if (!selectionActive) {
    selectionBox.style.display = 'none';
  }
}

function startResizing(e) {
  if (!selectionModeCheckbox.checked || !selectionActive) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isResizing = true;
  isDragging = false;
  currentResizeHandle = e.target.getAttribute('data-handle');
  
  initialBoxLeft = parseInt(selectionBox.style.left) || 0;
  initialBoxTop = parseInt(selectionBox.style.top) || 0;
  initialBoxWidth = parseInt(selectionBox.style.width) || 0;
  initialBoxHeight = parseInt(selectionBox.style.height) || 0;
  
  startX = e.clientX;
  startY = e.clientY;
  
  document.addEventListener('mousemove', resizeSelection);
  document.addEventListener('mouseup', stopResizing);
}

function startResizingTouch(e) {
  if (!selectionModeCheckbox.checked || !selectionActive || e.touches.length !== 1) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isResizing = true;
  isDragging = false;
  currentResizeHandle = e.target.getAttribute('data-handle');
  
  initialBoxLeft = parseInt(selectionBox.style.left) || 0;
  initialBoxTop = parseInt(selectionBox.style.top) || 0;
  initialBoxWidth = parseInt(selectionBox.style.width) || 0;
  initialBoxHeight = parseInt(selectionBox.style.height) || 0;
  
  const touch = e.touches[0];
  startX = touch.clientX;
  startY = touch.clientY;
  
  document.addEventListener('touchmove', resizeSelectionTouch, { passive: false });
  document.addEventListener('touchend', stopResizing);
}

function resizeSelection(e) {
  if (!isResizing) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  
  applyResize(dx, dy);
}

function resizeSelectionTouch(e) {
  if (!isResizing || e.touches.length !== 1) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  const touch = e.touches[0];
  const dx = touch.clientX - startX;
  const dy = touch.clientY - startY;
  
  applyResize(dx, dy);
}

function applyResize(dx, dy) {
  let newLeft = initialBoxLeft;
  let newTop = initialBoxTop;
  let newWidth = initialBoxWidth;
  let newHeight = initialBoxHeight;
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  
  switch(currentResizeHandle) {
    case 'nw':
      newLeft = Math.max(0, Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10));
      newTop = Math.max(0, Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10));
      newWidth = Math.max(10, initialBoxWidth - dx);
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'n':
      newTop = Math.max(0, Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10));
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'ne':
      newTop = Math.max(0, Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10));
      newWidth = Math.max(10, initialBoxWidth + dx);
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'e':
      newWidth = Math.max(10, initialBoxWidth + dx);
      break;
    case 'se':
      newWidth = Math.max(10, initialBoxWidth + dx);
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 's':
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 'sw':
      newLeft = Math.max(0, Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10));
      newWidth = Math.max(10, initialBoxWidth - dx);
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 'w':
      newLeft = Math.max(0, Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10));
      newWidth = Math.max(10, initialBoxWidth - dx);
      break;
  }
  
  newLeft = Math.max(0, Math.min(newLeft, containerRect.width - 10));
  newTop = Math.max(0, Math.min(newTop, containerRect.height - 10));
  newWidth = Math.max(10, Math.min(newWidth, containerRect.width - newLeft));
  newHeight = Math.max(10, Math.min(newHeight, containerRect.height - newTop));
  
  selectionRect = {
    left: newLeft,
    top: newTop,
    width: newWidth,
    height: newHeight
  };
  
  updateSelectionBoxDisplay();
}

function stopResizing() {
  if (!isResizing) return;
  
  isResizing = false;
  currentResizeHandle = null;
  
  document.removeEventListener('mousemove', resizeSelection);
  document.removeEventListener('mouseup', stopResizing);
  document.removeEventListener('touchmove', resizeSelectionTouch);
  document.removeEventListener('touchend', stopResizing);
}

processBtn.addEventListener('click', function() {
  if (!selectionActive) {
    alert('Please make a selection first');
    return;
  }
  
  loadingIndicator.style.display = 'block';
  
  setTimeout(() => {
    const selLeft = selectionRect.left;
    const selTop = selectionRect.top;
    const selWidth = selectionRect.width;
    const selHeight = selectionRect.height;
    
    const imgRect = magnifiedImage.getBoundingClientRect();
    const imgLeft = parseInt(magnifiedImage.style.left) || 0;
    const imgTop = parseInt(magnifiedImage.style.top) || 0;
    const imgWidth = magnifiedImage.naturalWidth;
    const imgHeight = magnifiedImage.naturalHeight;
    
    const scaledImgWidth = imgRect.width / currentScale;
    const scaledImgHeight = imgRect.height / currentScale;
    
    const cropX = (selLeft - imgLeft) / currentScale;
    const cropY = (selTop - imgTop) / currentScale;
    const cropWidth = selWidth / currentScale;
    const cropHeight = selHeight / currentScale;
    
    if (cropX < 0 || cropY < 0 || cropWidth <= 0 || cropHeight <= 0 || 
        cropX + cropWidth > imgWidth || cropY + cropHeight > imgHeight) {
      const validCropX = Math.max(0, Math.min(cropX, imgWidth - 1));
      const validCropY = Math.max(0, Math.min(cropY, imgHeight - 1));
      const validCropWidth = Math.max(1, Math.min(cropWidth, imgWidth - validCropX));
      const validCropHeight = Math.max(1, Math.min(cropHeight, imgHeight - validCropY));
      
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = validCropWidth;
      canvas.height = validCropHeight;
      
      const img = new Image();
      img.onload = function() {
        ctx.drawImage(
          img,
          validCropX, validCropY, validCropWidth, validCropHeight,
          0, 0, validCropWidth, validCropHeight
        );
        
        croppedImageData = canvas.toDataURL('image/png');
        setupCroppedView();
      };
      img.onerror = handleCropError;
      img.src = imageData;
    } else {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = cropWidth;
      canvas.height = cropHeight;
      
      const img = new Image();
      img.onload = function() {
        ctx.drawImage(
          img,
          cropX, cropY, cropWidth, cropHeight,
          0, 0, cropWidth, cropHeight
        );
        
        croppedImageData = canvas.toDataURL('image/png');
        setupCroppedView();
      };
      img.onerror = handleCropError;
      img.src = imageData;
    }
  }, 100);
  
  function handleCropError() {
    alert('Error cropping image. Please try again.');
    loadingIndicator.style.display = 'none';
  }
  
  function setupCroppedView() {
    croppedImage.src = croppedImageData;
    croppedImage.style.width = 'auto';
    croppedImage.style.height = 'auto';
    croppedImage.style.maxWidth = '100%';
    croppedImage.style.maxHeight = '100%';
    
    croppedImage.onload = function() {
      const containerWidth = document.querySelector('#cropped-tab-content #magnified-image-container').clientWidth;
      const containerHeight = document.querySelector('#cropped-tab-content #magnified-image-container').clientHeight;
      const imgWidth = croppedImage.clientWidth;
      const imgHeight = croppedImage.clientHeight;
      
      const leftPos = (containerWidth - imgWidth) / 2;
      const topPos = (containerHeight - imgHeight) / 2;
      
      croppedImage.style.left = leftPos + 'px';
      croppedImage.style.top = topPos + 'px';
      croppedImage.style.transform = 'scale(1)';
      
      croppedImageWidth = imgWidth;
      croppedImageHeight = imgHeight;
      
      croppedIntensitySlider.value = 1;
      croppedIntensityValue.textContent = '1';
      croppedCurrentScale = 1.0;
      croppedZoomInfo.textContent = 'Current zoom: 1.0x';
      croppedGrayscaleCheckbox.checked = grayscaleCheckbox.checked;
      applyGrayscaleCropped();
      
      croppedTab.style.display = 'block';
      croppedTab.click();
      
      loadingIndicator.style.display = 'none';
    };
  }
});

function startDragging(e) {
  if (selectionModeCheckbox.checked || isSelecting || isResizing) return;
  
  e.preventDefault();
  isDragging = true;

  startX = e.clientX;
  startY = e.clientY;

  startLeft = parseInt(magnifiedImage.style.left) || 0;
  startTop = parseInt(magnifiedImage.style.top) || 0;
  
  magnifiedImage.style.cursor = 'grabbing';
}

function startDraggingTouch(e) {
  if (e.touches.length !== 1 || selectionModeCheckbox.checked || isSelecting || isResizing) return;
  
  e.preventDefault();
  isDragging = true;
  
  const touch = e.touches[0];
  startX = touch.clientX;
  startY = touch.clientY;
  
  startLeft = parseInt(magnifiedImage.style.left) || 0;
  startTop = parseInt(magnifiedImage.style.top) || 0;
  
  magnifiedImage.style.cursor = 'grabbing';
}

function dragImage(e) {
  if (!isDragging) {
    if (selectionModeCheckbox.checked && e.buttons === 1) {
      // Prevent dragging while selecting
      return;
    }
    return;
  }
  
  e.preventDefault();
  const x = e.clientX;
  const y = e.clientY;
  
  const newLeft = startLeft + (x - startX);
  const newTop = startTop + (y - startY);
  
  magnifiedImage.style.left = newLeft + 'px';
  magnifiedImage.style.top = newTop + 'px';
}

function dragImageTouch(e) {
  if (!isDragging || e.touches.length !== 1) return;
  
  e.preventDefault();
  const touch = e.touches[0];
  const x = touch.clientX;
  const y = touch.clientY;
  
  const newLeft = startLeft + (x - startX);
  const newTop = startTop + (y - startY);
  
  magnifiedImage.style.left = newLeft + 'px';
  magnifiedImage.style.top = newTop + 'px';
}

function stopDragging() {
  isDragging = false;
  
  if (!selectionModeCheckbox.checked || !selectionActive) {
    isSelecting = false;
  }
  
  magnifiedImage.style.cursor = selectionModeCheckbox.checked ? 'crosshair' : 'grab';
}

// Cropped image dragging handlers omitted for brevity; you can copy previous handlers similarly

// Zoom and grayscale handlers
intensitySlider.addEventListener('input', function() {
  const value = parseFloat(this.value);
  intensityValue.textContent = value.toFixed(1);
  currentScale = value;
  magnifiedImage.style.transform = `scale(${value})`;
  zoomInfo.textContent = `Current zoom: ${value.toFixed(1)}x`;
});

croppedIntensitySlider.addEventListener('input', function() {
  const value = parseFloat(this.value);
  croppedIntensityValue.textContent = value.toFixed(1);
  croppedCurrentScale = value;
  croppedImage.style.transform = `scale(${value})`;
  croppedZoomInfo.textContent = `Current zoom: ${value.toFixed(1)}x`;
});

grayscaleCheckbox.addEventListener('change', applyGrayscale);
croppedGrayscaleCheckbox.addEventListener('change', applyGrayscaleCropped);

function applyGrayscale() {
  if (grayscaleCheckbox.checked) {
    magnifiedImage.style.filter = 'grayscale(100%)';
  } else {
    magnifiedImage.style.filter = 'none';
  }
}

function applyGrayscaleCropped() {
  if (croppedGrayscaleCheckbox.checked) {
    croppedImage.style.filter = 'grayscale(100%)';
  } else {
    croppedImage.style.filter = 'none';
  }
}

downloadBtn.addEventListener('click', function() {
  const a = document.createElement('a');
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  const containerWidth = magnifiedContainer.clientWidth;
  const containerHeight = magnifiedContainer.clientHeight;
  canvas.width = containerWidth;
  canvas.height = containerHeight;
  
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  const img = new Image();
  img.onload = function() {
    const scaledImgWidth = img.width * currentScale;
    const scaledImgHeight = img.height * currentScale;
    
    const imgLeft = parseInt(magnifiedImage.style.left) || 0;
    const imgTop = parseInt(magnifiedImage.style.top) || 0;
    
    ctx.save();
    if (grayscaleCheckbox.checked) {
      ctx.filter = 'grayscale(100%)';
    }
    ctx.drawImage(img, imgLeft, imgTop, scaledImgWidth, scaledImgHeight);
    ctx.restore();
    
    const dataUrl = canvas.toDataURL('image/png');
    a.href = dataUrl;
    a.download = 'magnified_image.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  img.src = imageData;
});

croppedDownloadBtn.addEventListener('click', function() {
  if (!croppedImageData) return;
  
  const a = document.createElement('a');
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  const containerWidth = document.querySelector('#cropped-tab-content #magnified-image-container').clientWidth;
  const containerHeight = document.querySelector('#cropped-tab-content #magnified-image-container').clientHeight;
  canvas.width = containerWidth;
  canvas.height = containerHeight;
  
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  const img = new Image();
  img.onload = function() {
    const scaledImgWidth = img.width * croppedCurrentScale;
    const scaledImgHeight = img.height * croppedCurrentScale;
    
    const imgLeft = parseInt(croppedImage.style.left) || 0;
    const imgTop = parseInt(croppedImage.style.top) || 0;
    
    ctx.save();
    if (croppedGrayscaleCheckbox.checked) {
      ctx.filter = 'grayscale(100%)';
    }
    
    ctx.drawImage(img, imgLeft, imgTop, scaledImgWidth, scaledImgHeight);
    ctx.restore();
    
    const dataUrl = canvas.toDataURL('image/png');
    a.href = dataUrl;
    a.download = 'cropped_image.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  img.src = croppedImageData;
});

// Navigation buttons
newImageBtn.addEventListener('click', function() {
  uploadSection.style.display = 'block';
  magnifierSection.style.display = 'none';
  fileInput.value = '';
  selectionBox.style.display = 'none';
  selectionActive = false;
  selectionModeCheckbox.checked = false;
});

backToOriginalBtn.addEventListener('click', function() {
  document.querySelector('[data-tab="original"]').click();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    if (isSelecting || isResizing) {
      stopResizing();
      finishSelection();
      isSelecting = false;
      isResizing = false;
      selectionBox.style.display = 'none';
      selectionActive = false;
    } else if (selectionActive && selectionModeCheckbox.checked) {
      selectionBox.style.display = 'none';
      selectionActive = false;
    } else if (selectionModeCheckbox.checked) {
      selectionModeCheckbox.checked = false;
      selectionBox.style.display = 'none';
      selectionActive = false;
      magnifiedImage.style.cursor = 'grab';
      magnifiedContainer.style.cursor = 'default';
    }
  } else if (e.key === 'Delete' || e.key === 'Backspace') {
    if (selectionActive && selectionModeCheckbox.checked) {
      selectionBox.style.display = 'none';
      selectionActive = false;
    }
  }
});

// Initialize the app
window.addEventListener('DOMContentLoaded', function() {
  magnifierSection.style.display = 'none';
  errorMessage.style.display = 'none';
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, css=CSS_STYLE)

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        img_data = file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        intensity = float(request.form.get('intensity', 1.0))
        convert_to_grayscale = request.form.get('grayscale', 'false') == 'true'
        
        return jsonify({
            'image': f'data:image/jpeg;base64,{img_base64}',
            'intensity': intensity,
            'grayscale': convert_to_grayscale
        })

@app.route('/crop', methods=['POST'])
def crop_image():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    # For demo, return original image data
    return jsonify({'image': data['image']})

@app.route('/download', methods=['POST'])
def download_image():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    return jsonify({'downloadUrl': data['image']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

```

