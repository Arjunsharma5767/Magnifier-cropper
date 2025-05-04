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
  display: none; /* Ensure this is toggled dynamically */
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

    <button id="process-btn">Process Selection</button>
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
cconst dropArea = document.getElementById('drop-area');
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
    
    // If we switch back to the original tab and there's an active selection, make sure it's visible
    if (tabId === 'original' && selectionActive) {
      selectionBox.style.display = 'block';
    }
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

  // Properly reset selection state
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
  
  // Ensure selection is marked as active if dimensions are valid
  if (newWidth >= 10 && newHeight >= 10) {
    selectionActive = true;
  }
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
  
  // Keep selection box visible if it's active
  if (selectionActive) {
    selectionBox.style.display = 'block';
  }
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
  
  // Keep selection box visible if it's active
  if (selectionActive) {
    selectionBox.style.display = 'block';
  }
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

// Selection mode checkbox listener
selectionModeCheckbox.addEventListener('change', function () {
  if (this.checked) {
    // Enable selection mode
    enableSelectionMode();
  } else {
    // Disable selection mode
    disableSelectionMode();
  }
});

function enableSelectionMode() {
  // Change cursor to indicate selection mode
  magnifiedContainer.style.cursor = 'crosshair';

  // Add event listeners for selection functionality
  magnifiedContainer.addEventListener('mousedown', startSelection);
  magnifiedContainer.addEventListener('touchstart', startSelectionTouch, { passive: false });
  document.addEventListener('mousemove', updateSelection);
  document.addEventListener('touchmove', updateSelectionTouch, { passive: false });
  document.addEventListener('mouseup', endSelection);
  document.addEventListener('touchend', endSelection);

  // Display the selection box if there's an active selection
  if (selectionActive) {
    selectionBox.style.display = 'block';
  }
}

function disableSelectionMode() {
  // Change cursor back to default
  magnifiedContainer.style.cursor = 'grab';

  // Remove event listeners for selection functionality
  magnifiedContainer.removeEventListener('mousedown', startSelection);
  magnifiedContainer.removeEventListener('touchstart', startSelectionTouch);
  document.removeEventListener('mousemove', updateSelection);
  document.removeEventListener('touchmove', updateSelectionTouch);
  document.removeEventListener('mouseup', endSelection);
  document.removeEventListener('touchend', endSelection);

  // Keep the selection box visible if there's an active selection
  if (selectionActive) {
    selectionBox.style.display = 'block';
  } else {
    selectionBox.style.display = 'none'; // Hide the selection box if inactive
  }
}

// FIXED: Start selection function
function startSelection(e) {
  // Don't start selecting if we're already resizing
  if (isResizing) return;
  
  // We need to prevent default to avoid image dragging conflicts
  e.preventDefault();
  
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
  
  // Update selection active status to false until a proper selection is made
  selectionActive = false;
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
  
  // Update selection active status to false until a proper selection is made
  selectionActive = false;
}

// FIXED: Update selection function
function updateSelection(e) {
  if (!isSelecting || isResizing) return;
  
  // Get current mouse position relative to container
  const containerRect = magnifiedContainer.getBoundingClientRect();
  const mouseX = Math.max(0, Math.min(e.clientX - containerRect.left, containerRect.width));
  const mouseY = Math.max(0, Math.min(e.clientY - containerRect.top, containerRect.height));
  
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
  const touchX = Math.max(0, Math.min(touch.clientX - containerRect.left, containerRect.width));
  const touchY = Math.max(0, Math.min(touch.clientY - containerRect.top, containerRect.height));
  
  // Update current selection
  selectionCurrentX = touchX;
  selectionCurrentY = touchY;
  
  // Calculate selection box dimensions
  updateSelectionBox();
}

function updateSelectionBox() {
  // Get container dimensions
  const containerRect = magnifiedContainer.getBoundingClientRect();

  // Calculate top-left corner and dimensions
  const left = Math.max(0, Math.min(selectionStartX, selectionCurrentX));
  const top = Math.max(0, Math.min(selectionStartY, selectionCurrentY));
  const width = Math.min(containerRect.width - left, Math.abs(selectionCurrentX - selectionStartX));
  const height = Math.min(containerRect.height - top, Math.abs(selectionCurrentY - selectionStartY));

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
  const width = parseInt(selectionBox.style.width) || 0;
  const height = parseInt(selectionBox.style.height) || 0;

  if (width >= 10 && height >= 10) {
    selectionActive = true;
    selectionBox.style.display = 'block'; // Ensure it stays visible
  } else {
    selectionActive = false;
    selectionBox.style.display = 'none'; // Hide invalid selection
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
  if (!imageData) return;
  
  // Create a download link
  const downloadLink = document.createElement('a');
  
  // Use the current state of the image (with any grayscale filter applied)
  if (grayscaleCheckbox.checked) {
    // If grayscale is applied, we need to create a grayscale version of the image
    const canvas = document.createElement('canvas');
    const img = new Image();
    img.onload = function() {
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.filter = 'grayscale(100%)';
      ctx.drawImage(img, 0, 0);
      
      // Set download attributes
      downloadLink.href = canvas.toDataURL('image/png');
      downloadLink.download = 'magnified-image.png';
      downloadLink.click();
    };
    img.src = imageData;
  } else {
    // No grayscale, just download the original
    downloadLink.href = imageData;
    downloadLink.download = 'original-image.png';
    downloadLink.click();
  }
});

croppedDownloadBtn.addEventListener('click', function() {
  if (!croppedImageData) return;
  
  // Create a download link
  const downloadLink = document.createElement('a');
  
  // Use the current state of the image (with any grayscale filter applied)
  if (croppedGrayscaleCheckbox.checked) {
    // If grayscale is applied, we need to create a grayscale version of the image
    const canvas = document.createElement('canvas');
    const img = new Image();
    img.onload = function() {
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.filter = 'grayscale(100%)';
      ctx.drawImage(img, 0, 0);
      
      // Set download attributes
      downloadLink.href = canvas.toDataURL('image/png');
      downloadLink.download = 'cropped-image.png';
      downloadLink.click();
    };
    img.src = croppedImageData;
  } else {
    // No grayscale, just download the cropped image
    downloadLink.href = croppedImageData;
    downloadLink.download = 'cropped-image.png';
    downloadLink.click();
  }
});

newImageBtn.addEventListener('click', function() {
  // Reset state and go back to upload section
  imageData = null;
  croppedImageData = null;
  magnifiedImage.src = '';
  croppedImage.src = '';
  selectionActive = false;
  selectionBox.style.display = 'none';
  
  uploadSection.style.display = 'block';
  magnifierSection.style.display = 'none';
  croppedTab.style.display = 'none';
  
  // Reset file input
  fileInput.value = '';
});

backToOriginalBtn.addEventListener('click', function() {
  // Switch back to the original tab
  tabs[0].click();
});

// Add keyboard zoom controls for accessibility
magnifiedContainer.addEventListener('keydown', function(e) {
  if (e.key === '+' || e.key === '=') {
    if (currentScale < 10) {
      currentScale += 0.1;
      intensitySlider.value = currentScale.toFixed(1);
      intensityValue.textContent = currentScale.toFixed(1);
      zoomInfo.textContent = `Current zoom: ${currentScale.toFixed(1)}x`;
      magnifiedImage.style.transform = `scale(${currentScale})`;
    }
  } else if (e.key === '-') {
    if (currentScale > 0.2) {
      currentScale -= 0.1;
      intensitySlider.value = currentScale.toFixed(1);
      intensityValue.textContent = currentScale.toFixed(1);
      zoomInfo.textContent = `Current zoom: ${currentScale.toFixed(1)}x`;
      magnifiedImage.style.transform = `scale(${currentScale})`;
    }
  }
});

document.querySelector('#cropped-tab-content #magnified-image-container').addEventListener('keydown', function(e) {
  if (e.key === '+' || e.key === '=') {
    if (croppedCurrentScale < 10) {
      croppedCurrentScale += 0.1;
      croppedIntensitySlider.value = croppedCurrentScale.toFixed(1);
      croppedIntensityValue.textContent = croppedCurrentScale.toFixed(1);
      croppedZoomInfo.textContent = `Current zoom: ${croppedCurrentScale.toFixed(1)}x`;
      croppedImage.style.transform = `scale(${croppedCurrentScale})`;
    }
  } else if (e.key === '-') {
    if (croppedCurrentScale > 0.2) {
      croppedCurrentScale -= 0.1;
      croppedIntensitySlider.value = croppedCurrentScale.toFixed(1);
      croppedIntensityValue.textContent = croppedCurrentScale.toFixed(1);
      croppedZoomInfo.textContent = `Current zoom: ${croppedCurrentScale.toFixed(1)}x`;
      croppedImage.style.transform = `scale(${croppedCurrentScale})`;
    }
  }
});

// Add mouse wheel zoom for enhanced usability
magnifiedContainer.addEventListener('wheel', function(e) {
  e.preventDefault();
  
  if (e.deltaY < 0) {
    // Zoom in
    if (currentScale < 10) {
      currentScale += 0.1;
      currentScale = Math.min(10, currentScale);
    }
  } else {
    // Zoom out
    if (currentScale > 0.2) {
      currentScale -= 0.1;
      currentScale = Math.max(0.2, currentScale);
    }
  }
  
  currentScale = parseFloat(currentScale.toFixed(1));
  intensitySlider.value = currentScale;
  intensityValue.textContent = currentScale;
  zoomInfo.textContent = `Current zoom: ${currentScale}x`;
  magnifiedImage.style.transform = `scale(${currentScale})`;
});

document.querySelector('#cropped-tab-content #magnified-image-container').addEventListener('wheel', function(e) {
  e.preventDefault();
  
  if (e.deltaY < 0) {
    // Zoom in
    if (croppedCurrentScale < 10) {
      croppedCurrentScale += 0.1;
      croppedCurrentScale = Math.min(10, croppedCurrentScale);
    }
  } else {
    // Zoom out
    if (croppedCurrentScale > 0.2) {
      croppedCurrentScale -= 0.1;
      croppedCurrentScale = Math.max(0.2, croppedCurrentScale);
    }
  }
  
  croppedCurrentScale = parseFloat(croppedCurrentScale.toFixed(1));
  croppedIntensitySlider.value = croppedCurrentScale;
  croppedIntensityValue.textContent = croppedCurrentScale;
  croppedZoomInfo.textContent = `Current zoom: ${croppedCurrentScale}x`;
  croppedImage.style.transform = `scale(${croppedCurrentScale})`;
});

// Add touch pinch zoom
let initialDistance = 0;
let initialScale = 1;

magnifiedContainer.addEventListener('touchstart', function(e) {
  if (e.touches.length === 2) {
    e.preventDefault();
    initialDistance = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    );
    initialScale = currentScale;
  }
}, { passive: false });

magnifiedContainer.addEventListener('touchmove', function(e) {
  if (e.touches.length === 2) {
    e.preventDefault();
    const currentDistance = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    );
    
    const scaleFactor = currentDistance / initialDistance;
    let newScale = initialScale * scaleFactor;
    
    // Constrain scale
    newScale = Math.min(Math.max(newScale, 0.2), 10);
    newScale = parseFloat(newScale.toFixed(1));
    
    currentScale = newScale;
    intensitySlider.value = currentScale;
    intensityValue.textContent = currentScale;
    zoomInfo.textContent = `Current zoom: ${currentScale}x`;
    magnifiedImage.style.transform = `scale(${currentScale})`;
  }
}, { passive: false });

// Initialize the app with event listeners for accessibility
function initAccessibility() {
  // Add focus outline to all interactive elements
  const interactiveElements = document.querySelectorAll('button, input, a, [tabindex="0"]');
  interactiveElements.forEach(el => {
    el.addEventListener('focus', function() {
      this.style.outline = '2px solid #4285f4';
    });
    el.addEventListener('blur', function() {
      this.style.outline = '';
    });
  });
  
  // Add ARIA labels where needed
  magnifiedContainer.setAttribute('aria-label', 'Image viewer area - use mouse to drag image, scroll to zoom');
  intensitySlider.setAttribute('aria-label', 'Zoom level control');
  grayscaleCheckbox.setAttribute('aria-label', 'Toggle grayscale mode');
  selectionModeCheckbox.setAttribute('aria-label', 'Toggle selection mode for cropping');
  
  // Add keyboard instructions
  const keyboardInstructions = document.createElement('div');
  keyboardInstructions.className = 'keyboard-instructions';
  keyboardInstructions.setAttribute('aria-live', 'polite');
  keyboardInstructions.innerHTML = `
    <details>
      <summary>Keyboard controls</summary>
      <ul>
        <li>Use + and - keys to zoom in and out</li>
        <li>Press Tab to navigate between controls</li>
        <li>When selection mode is active, use arrow keys to move selection</li>
      </ul>
    </details>
  `;
  document.querySelector('.controls-section').appendChild(keyboardInstructions);
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', initAccessibility);




      
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
