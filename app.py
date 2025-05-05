import os
import base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
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
  if (files[0].type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = function(e) {
      imageData = e.target.result;
      setupMagnifier(imageData);
    };
    reader.readAsDataURL(files[0]);
  } else {
    alert('Please select an image file.');
  }
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
  
  document.addEventListener('mousemove', resizeSelection);
  document.addEventListener('touchmove', resizeSelectionTouch, {passive: false});
  document.addEventListener('mouseup', stopResizing);
  document.addEventListener('touchend', stopResizing);
}

function startResizing(e) {
  e.preventDefault();
  e.stopPropagation();
  if (!selectionModeCheckbox.checked) return;
  
  isResizing = true;
  currentResizeHandle = e.target.getAttribute('data-handle');
  
  // Get the initial box dimensions
  initialBoxLeft = parseInt(selectionBox.style.left) || 0;
  initialBoxTop = parseInt(selectionBox.style.top) || 0;
  initialBoxWidth = parseInt(selectionBox.style.width) || 0;
  initialBoxHeight = parseInt(selectionBox.style.height) || 0;
  
  // Get the starting mouse position
  startX = e.clientX;
  startY = e.clientY;
}

function startResizingTouch(e) {
  if (!selectionModeCheckbox.checked || e.touches.length !== 1) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isResizing = true;
  currentResizeHandle = e.target.getAttribute('data-handle');
  
  // Get the initial box dimensions
  initialBoxLeft = parseInt(selectionBox.style.left) || 0;
  initialBoxTop = parseInt(selectionBox.style.top) || 0;
  initialBoxWidth = parseInt(selectionBox.style.width) || 0;
  initialBoxHeight = parseInt(selectionBox.style.height) || 0;
  
  // Get the starting touch position
  const touch = e.touches[0];
  startX = touch.clientX;
  startY = touch.clientY;
}

function resizeSelection(e) {
  if (!isResizing) return;
  e.preventDefault();
  
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  
  // Apply the resize based on which handle is being dragged
  applyResize(dx, dy);
}

function resizeSelectionTouch(e) {
  if (!isResizing || e.touches.length !== 1) return;
  e.preventDefault();
  
  const touch = e.touches[0];
  const dx = touch.clientX - startX;
  const dy = touch.clientY - startY;
  
  // Apply the resize based on which handle is being dragged
  applyResize(dx, dy);
}

function applyResize(dx, dy) {
  let newLeft = initialBoxLeft;
  let newTop = initialBoxTop;
  let newWidth = initialBoxWidth;
  let newHeight = initialBoxHeight;
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  
  // Handle the resize based on which handle is being dragged
  switch(currentResizeHandle) {
    case 'nw': // Northwest
      newLeft = Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10);
      newTop = Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10);
      newWidth = Math.max(10, initialBoxWidth - dx);
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'n': // North
      newTop = Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10);
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'ne': // Northeast
      newTop = Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10);
      newWidth = Math.max(10, initialBoxWidth + dx);
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'e': // East
      newWidth = Math.max(10, initialBoxWidth + dx);
      break;
    case 'se': // Southeast
      newWidth = Math.max(10, initialBoxWidth + dx);
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 's': // South
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 'sw': // Southwest
      newLeft = Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10);
      newWidth = Math.max(10, initialBoxWidth - dx);
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 'w': // West
      newLeft = Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10);
      newWidth = Math.max(10, initialBoxWidth - dx);
      break;
  }
  
  // Constrain to container bounds
  newLeft = Math.max(0, Math.min(newLeft, containerRect.width - newWidth));
  newTop = Math.max(0, Math.min(newTop, containerRect.height - newHeight));
  
  // Apply new dimensions
  selectionBox.style.left = newLeft + 'px';
  selectionBox.style.top = newTop + 'px';
  selectionBox.style.width = newWidth + 'px';
  selectionBox.style.height = newHeight + 'px';
}

function stopResizing() {
  isResizing = false;
  currentResizeHandle = null;
}

function startDragging(e) {
  // Don't start dragging if we're in selection mode or resizing
  if (selectionModeCheckbox.checked || isResizing) return;
  
  e.preventDefault();
  isDragging = true;

  startX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  startY = e.clientY || (e.touches ? e.touches[0].clientY : 0);

  startLeft = parseInt(magnifiedImage.style.left) || 0;
  startTop = parseInt(magnifiedImage.style.top) || 0;
}

function startDraggingTouch(e) {
  // Don't start dragging if we're in selection mode or resizing
  if (selectionModeCheckbox.checked || isResizing) return;
  
  if (e.touches.length === 1) {
    e.preventDefault();
    isDragging = true;

    const touch = e.touches[0];
    startX = touch.clientX;
    startY = touch.clientY;

    startLeft = parseInt(magnifiedImage.style.left) || 0;
    startTop = parseInt(magnifiedImage.style.top) || 0;
  }
}

function dragImage(e) {
  if (!isDragging) return;
  e.preventDefault();

  const clientX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  const clientY = e.clientY || (e.touches ? e.touches[0].clientY : 0);

const dx = clientX - startX;
  const dy = clientY - startY;

  const newLeft = startLeft + dx;
  const newTop = startTop + dy;

  magnifiedImage.style.left = newLeft + 'px';
  magnifiedImage.style.top = newTop + 'px';
}

function dragImageTouch(e) {
  if (!isDragging || e.touches.length !== 1) return;
  e.preventDefault();

  const touch = e.touches[0];
  const dx = touch.clientX - startX;
  const dy = touch.clientY - startY;

  const newLeft = startLeft + dx;
  const newTop = startTop + dy;

  magnifiedImage.style.left = newLeft + 'px';
  magnifiedImage.style.top = newTop + 'px';
}

function stopDragging() {
  isDragging = false;
}

function startCroppedDragging(e) {
  e.preventDefault();
  isDragging = true;

  startX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  startY = e.clientY || (e.touches ? e.touches[0].clientY : 0);

  startLeft = parseInt(croppedImage.style.left) || 0;
  startTop = parseInt(croppedImage.style.top) || 0;
}

function startCroppedDraggingTouch(e) {
  if (e.touches.length === 1) {
    e.preventDefault();
    isDragging = true;

    const touch = e.touches[0];
    startX = touch.clientX;
    startY = touch.clientY;

    startLeft = parseInt(croppedImage.style.left) || 0;
    startTop = parseInt(croppedImage.style.top) || 0;
  }
}

function dragCroppedImage(e) {
  if (!isDragging) return;
  e.preventDefault();

  const clientX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  const clientY = e.clientY || (e.touches ? e.touches[0].clientY : 0);

  const dx = clientX - startX;
  const dy = clientY - startY;

  const newLeft = startLeft + dx;
  const newTop = startTop + dy;

  croppedImage.style.left = newLeft + 'px';
  croppedImage.style.top = newTop + 'px';
}

function dragCroppedImageTouch(e) {
  if (!isDragging || e.touches.length !== 1) return;
  e.preventDefault();

  const touch = e.touches[0];
  const dx = touch.clientX - startX;
  const dy = touch.clientY - startY;

  const newLeft = startLeft + dx;
  const newTop = startTop + dy;

  croppedImage.style.left = newLeft + 'px';
  croppedImage.style.top = newTop + 'px';
}

function stopCroppedDragging() {
  isDragging = false;
}

// Initialize listener for selection mode checkbox
selectionModeCheckbox.addEventListener('change', function() {
  if (this.checked) {
    // Enable selection mode
    magnifiedContainer.style.cursor = 'crosshair';
    magnifiedContainer.addEventListener('mousedown', startSelection);
    magnifiedContainer.addEventListener('touchstart', startSelectionTouch, {passive: false});
    magnifiedContainer.addEventListener('mousemove', updateSelection);
    magnifiedContainer.addEventListener('touchmove', updateSelectionTouch, {passive: false});
    magnifiedContainer.addEventListener('mouseup', endSelection);
    magnifiedContainer.addEventListener('touchend', endSelection);
  } else {
    // Disable selection mode
    magnifiedContainer.style.cursor = 'grab';
    magnifiedContainer.removeEventListener('mousedown', startSelection);
    magnifiedContainer.removeEventListener('touchstart', startSelectionTouch);
    magnifiedContainer.removeEventListener('mousemove', updateSelection);
    magnifiedContainer.removeEventListener('touchmove', updateSelectionTouch);
    magnifiedContainer.removeEventListener('mouseup', endSelection);
    magnifiedContainer.removeEventListener('touchend', endSelection);
    
    // Hide selection box
    selectionBox.style.display = 'none';
    selectionActive = false;
  }
});

function startSelection(e) {
  // Don't start selecting if we're already resizing
  if (isResizing) return;
  
  // Get mouse position relative to container
  const containerRect = magnifiedContainer.getBoundingClientRect();
  const mouseX = e.clientX - containerRect.left;
  const mouseY = e.clientY - containerRect.top;

  // Start selection
  isSelecting = true;
  selectionStartX = mouseX;
  selectionStartY = mouseY;
  selectionCurrentX = mouseX;
  selectionCurrentY = mouseY;

  // Set up selection box
  selectionBox.style.left = selectionStartX + 'px';
  selectionBox.style.top = selectionStartY + 'px';
  selectionBox.style.width = '0';
  selectionBox.style.height = '0';
  selectionBox.style.display = 'block';
}

function startSelectionTouch(e) {
  // Don't start selecting if we're already resizing or if there are multiple touches
  if (isResizing || e.touches.length !== 1) return;
  e.preventDefault();
  
  // Get touch position relative to container
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  const touchX = touch.clientX - containerRect.left;
  const touchY = touch.clientY - containerRect.top;

  // Start selection
  isSelecting = true;
  selectionStartX = touchX;
  selectionStartY = touchY;
  selectionCurrentX = touchX;
  selectionCurrentY = touchY;

  // Set up selection box
  selectionBox.style.left = selectionStartX + 'px';
  selectionBox.style.top = selectionStartY + 'px';
  selectionBox.style.width = '0';
  selectionBox.style.height = '0';
  selectionBox.style.display = 'block';
}

function updateSelection(e) {
  if (!isSelecting || isResizing) return;
  
  // Get current mouse position relative to container
  const containerRect = magnifiedContainer.getBoundingClientRect();
  const mouseX = e.clientX - containerRect.left;
  const mouseY = e.clientY - containerRect.top;
  
  // Update current selection
  selectionCurrentX = mouseX;
  selectionCurrentY = mouseY;
  
  // Calculate selection box dimensions
  updateSelectionBox();
}

function updateSelectionTouch(e) {
  if (!isSelecting || isResizing || e.touches.length !== 1) return;
  e.preventDefault();
  
  // Get current touch position relative to container
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  const touchX = touch.clientX - containerRect.left;
  const touchY = touch.clientY - containerRect.top;
  
  // Update current selection
  selectionCurrentX = touchX;
  selectionCurrentY = touchY;
  
  // Calculate selection box dimensions
  updateSelectionBox();
}

function updateSelectionBox() {
  // Calculate top-left corner and dimensions
  const left = Math.min(selectionStartX, selectionCurrentX);
  const top = Math.min(selectionStartY, selectionCurrentY);
  const width = Math.abs(selectionCurrentX - selectionStartX);
  const height = Math.abs(selectionCurrentY - selectionStartY);
  
  // Update selection box
  selectionBox.style.left = left + 'px';
  selectionBox.style.top = top + 'px';
  selectionBox.style.width = width + 'px';
  selectionBox.style.height = height + 'px';
}

function endSelection() {
  if (!isSelecting) return;
  isSelecting = false;
  
  // Check if selection has a valid size
  const width = parseInt(selectionBox.style.width);
  const height = parseInt(selectionBox.style.height);
  
  if (width < 10 || height < 10) {
    // Selection too small, hide the box
    selectionBox.style.display = 'none';
    selectionActive = false;
  } else {
    selectionActive = true;
  }
}

intensitySlider.addEventListener('input', function() {
  currentScale = parseFloat(this.value);
  intensityValue.textContent = this.value;
  zoomInfo.textContent = `Current zoom: ${this.value}x`;
  
  // Update original image scale
  magnifiedImage.style.transform = `scale(${currentScale})`;
});

croppedIntensitySlider.addEventListener('input', function() {
  croppedCurrentScale = parseFloat(this.value);
  croppedIntensityValue.textContent = this.value;
  croppedZoomInfo.textContent = `Current zoom: ${this.value}x`;
  
  // Update cropped image scale
  croppedImage.style.transform = `scale(${croppedCurrentScale})`;
});

function applyGrayscale() {
  if (grayscaleCheckbox.checked) {
    magnifiedImage.style.filter = 'grayscale(100%)';
  } else {
    magnifiedImage.style.filter = 'none';
  }
}

function applyCroppedGrayscale() {
  if (croppedGrayscaleCheckbox.checked) {
    croppedImage.style.filter = 'grayscale(100%)';
  } else {
    croppedImage.style.filter = 'none';
  }
}

grayscaleCheckbox.addEventListener('change', applyGrayscale);
croppedGrayscaleCheckbox.addEventListener('change', applyCroppedGrayscale);

processBtn.addEventListener('click', function() {
  if (!selectionActive) {
    alert('Please make a selection first.');
    return;
  }
  
  // Show loading indicator
  loadingIndicator.style.display = 'block';
  
  // Get selection dimensions
  const selectionLeft = parseInt(selectionBox.style.left);
  const selectionTop = parseInt(selectionBox.style.top);
  const selectionWidth = parseInt(selectionBox.style.width);
  const selectionHeight = parseInt(selectionBox.style.height);
  
  // Get the actual coordinates in the original image
  const imgRect = magnifiedImage.getBoundingClientRect();
  const containerRect = magnifiedContainer.getBoundingClientRect();
  
  // Calculate position and dimensions relative to the actual image
  const imageLeft = parseInt(magnifiedImage.style.left);
  const imageTop = parseInt(magnifiedImage.style.top);
  
  // Calculate the actual coordinates in the original image (accounting for scaling)
  const actualX = (selectionLeft - imageLeft) / currentScale;
  const actualY = (selectionTop - imageTop) / currentScale;
  const actualWidth = selectionWidth / currentScale;
  const actualHeight = selectionHeight / currentScale;
  
  // Create form data for the server request
  const formData = new FormData();
  formData.append('image_data', imageData);
  formData.append('x', Math.round(actualX));
  formData.append('y', Math.round(actualY));
  formData.append('width', Math.round(actualWidth));
  formData.append('height', Math.round(actualHeight));
  
  // Send the request to crop the image
  fetch('/crop', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Store the cropped image data and setup the cropped tab
      croppedImageData = data.cropped_image;
      setupCroppedImage(data.cropped_image);
      
      // Switch to the cropped tab
      croppedTab.style.display = 'block';
      croppedTab.click();
    } else {
      alert('Error cropping image: ' + data.error);
    }
    loadingIndicator.style.display = 'none';
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error processing image. Please try again.');
    loadingIndicator.style.display = 'none';
  });
});

function setupCroppedImage(imageUrl) {
  // Reset controls
  croppedCurrentScale = 1.0;
  croppedIntensitySlider.value = 1;
  croppedIntensityValue.textContent = '1';
  croppedZoomInfo.textContent = 'Current zoom: 1.0x';
  croppedGrayscaleCheckbox.checked = false;
  
  // Load the image dimensions
  const img = new Image();
  img.onload = function() {
    croppedImageWidth = this.width;
    croppedImageHeight = this.height;
    
    // Set up the cropped image
    croppedImage.src = imageUrl;
    croppedImage.style.width = 'auto';
    croppedImage.style.height = 'auto';
    croppedImage.style.maxWidth = '100%';
    croppedImage.style.maxHeight = '100%';
    croppedImage.style.filter = 'none';
    
    // Center the image after it loads
    croppedImage.onload = function() {
      const containerWidth = document.querySelector('#cropped-tab-content #magnified-image-container').clientWidth;
      const containerHeight = document.querySelector('#cropped-tab-content #magnified-image-container').clientHeight;
      const imgWidth = croppedImage.clientWidth;
      const imgHeight = croppedImage.clientHeight;
      
      // Calculate the position to center the image
      const leftPos = (containerWidth - imgWidth) / 2;
      const topPos = (containerHeight - imgHeight) / 2;
      
      croppedImage.style.left = leftPos + 'px';
      croppedImage.style.top = topPos + 'px';
      croppedImage.style.transform = 'scale(1)';
    };
  };
  img.src = imageUrl;
}

downloadBtn.addEventListener('click', function() {
  // Create a temporary link to download the image
  const link = document.createElement('a');
  
  // Create a canvas to apply current zoom and filters
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Create a new image for processing
  const img = new Image();
  img.onload = function() {
    // Set canvas dimensions to match the zoomed image
    canvas.width = img.width * currentScale;
    canvas.height = img.height * currentScale;
    
    // Draw the image with the current scale
    ctx.scale(currentScale, currentScale);
    ctx.drawImage(img, 0, 0);
    
    // Apply grayscale if needed
    if (grayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
        data[i] = avg;
        data[i + 1] = avg;
        data[i + 2] = avg;
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    // Generate download link
    link.href = canvas.toDataURL('image/png');
    link.download = 'magnified_image.png';
    link.click();
  };
  img.src = imageData;
});

croppedDownloadBtn.addEventListener('click', function() {
  // Create a temporary link to download the image
  const link = document.createElement('a');
  
  // Create a canvas to apply current zoom and filters
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Create a new image for processing
  const img = new Image();
  img.onload = function() {
    // Set canvas dimensions to match the zoomed image
    canvas.width = img.width * croppedCurrentScale;
    canvas.height = img.height * croppedCurrentScale;
    
    // Draw the image with the current scale
    ctx.scale(croppedCurrentScale, croppedCurrentScale);
    ctx.drawImage(img, 0, 0);
    
    // Apply grayscale if needed
    if (croppedGrayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
        data[i] = avg;
        data[i + 1] = avg;
        data[i + 2] = avg;
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    // Generate download link
    link.href = canvas.toDataURL('image/png');
    link.download = 'cropped_image.png';
    link.click();
  };
  img.src = croppedImageData;
});

backToOriginalBtn.addEventListener('click', function() {
  document.querySelector('.tab[data-tab="original"]').click();
});

newImageBtn.addEventListener('click', function() {
  uploadSection.style.display = 'block';
  magnifierSection.style.display = 'none';
  fileInput.value = '';
  croppedTab.style.display = 'none';
});

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  intensityValue.textContent = intensitySlider.value;
  croppedIntensityValue.textContent = croppedIntensitySlider.value;
});
</script>
</body>
</html>
"""

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
