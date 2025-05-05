import os
import base64
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS  # Added for cross-origin support

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
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

// Improve the selection mode checkbox event listener
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

// Improved selection functions
function startSelection(e) {
  // Only start selection if selection mode is active and not already selecting or resizing
  if (!selectionModeCheckbox.checked || isResizing || isSelecting) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isSelecting = true;
  isDragging = false; // Prevent dragging while selecting
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionStartX = e.clientX - containerRect.left;
  selectionStartY = e.clientY - containerRect.top;
  
  // Initialize selection box at start position with zero size
  selectionRect = {
    left: selectionStartX,
    top: selectionStartY,
    width: 0,
    height: 0
  };
  
  updateSelectionBoxDisplay();
  
  // Add temporary event listeners for tracking the selection
  document.addEventListener('mousemove', updateSelection);
  document.addEventListener('mouseup', finishSelection);
}

function startSelectionTouch(e) {
  // Only handle single touch in selection mode
  if (!selectionModeCheckbox.checked || e.touches.length !== 1 || isResizing || isSelecting) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isSelecting = true;
  isDragging = false; // Prevent dragging while selecting
  
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionStartX = touch.clientX - containerRect.left;
  selectionStartY = touch.clientY - containerRect.top;
  
  // Initialize selection box at start position with zero size
  selectionRect = {
    left: selectionStartX,
    top: selectionStartY,
    width: 0,
    height: 0
  };
  
  updateSelectionBoxDisplay();
  
  // Add temporary event listeners for tracking the selection
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
  // Calculate the correct rectangle coordinates from start and current points
  selectionRect = {
    left: Math.min(selectionStartX, selectionCurrentX),
    top: Math.min(selectionStartY, selectionCurrentY),
    width: Math.abs(selectionCurrentX - selectionStartX),
    height: Math.abs(selectionCurrentY - selectionStartY)
  };
  
  // Make sure selection is within container bounds
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
  
  // Only mark selection as active if it has a meaningful size
  selectionActive = (selectionRect.width > 5 && selectionRect.height > 5);
}

function finishSelection(e) {
  if (!isSelecting) return;
  
  isSelecting = false;
  
  // Remove the temporary event listeners
  document.removeEventListener('mousemove', updateSelection);
  document.removeEventListener('mouseup', finishSelection);
  document.removeEventListener('touchmove', updateSelectionTouch);
  document.removeEventListener('touchend', finishSelection);
  
  // Hide selection box if it's too small
  if (!selectionActive) {
    selectionBox.style.display = 'none';
  }
}

// Improved resize handling functions
function startResizing(e) {
  if (!selectionModeCheckbox.checked || !selectionActive) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isResizing = true;
  isDragging = false; // Prevent dragging while resizing
  currentResizeHandle = e.target.getAttribute('data-handle');
  
  // Get the initial box dimensions
  initialBoxLeft = parseInt(selectionBox.style.left) || 0;
  initialBoxTop = parseInt(selectionBox.style.top) || 0;
  initialBoxWidth = parseInt(selectionBox.style.width) || 0;
  initialBoxHeight = parseInt(selectionBox.style.height) || 0;
  
  // Get the starting mouse position
  startX = e.clientX;
  startY = e.clientY;
  
  // Add temporary event listeners
  document.addEventListener('mousemove', resizeSelection);
  document.addEventListener('mouseup', stopResizing);
}

function startResizingTouch(e) {
  if (!selectionModeCheckbox.checked || !selectionActive || e.touches.length !== 1) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  isResizing = true;
  isDragging = false; // Prevent dragging while resizing
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
  
  // Add temporary event listeners
  document.addEventListener('touchmove', resizeSelectionTouch, { passive: false });
  document.addEventListener('touchend', stopResizing);
}

function resizeSelection(e) {
  if (!isResizing) return;
  
  e.preventDefault();
  e.stopPropagation();
  
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  
  // Apply the resize based on which handle is being dragged
  applyResize(dx, dy);
}

function resizeSelectionTouch(e) {
  if (!isResizing || e.touches.length !== 1) return;
  
  e.preventDefault();
  e.stopPropagation();
  
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
      newLeft = Math.max(0, Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10));
      newTop = Math.max(0, Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10));
      newWidth = Math.max(10, initialBoxWidth - dx);
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'n': // North
      newTop = Math.max(0, Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10));
      newHeight = Math.max(10, initialBoxHeight - dy);
      break;
    case 'ne': // Northeast
      newTop = Math.max(0, Math.min(initialBoxTop + dy, initialBoxTop + initialBoxHeight - 10));
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
      newLeft = Math.max(0, Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10));
      newWidth = Math.max(10, initialBoxWidth - dx);
      newHeight = Math.max(10, initialBoxHeight + dy);
      break;
    case 'w': // West
      newLeft = Math.max(0, Math.min(initialBoxLeft + dx, initialBoxLeft + initialBoxWidth - 10));
      newWidth = Math.max(10, initialBoxWidth - dx);
      break;
  }
  
  // Constrain to container bounds
  newLeft = Math.max(0, Math.min(newLeft, containerRect.width - 10));
  newTop = Math.max(0, Math.min(newTop, containerRect.height - 10));
  newWidth = Math.max(10, Math.min(newWidth, containerRect.width - newLeft));
  newHeight = Math.max(10, Math.min(newHeight, containerRect.height - newTop));
  
  // Update selection rectangle
  selectionRect = {
    left: newLeft,
    top: newTop,
    width: newWidth,
    height: newHeight
  };
  
  // Apply new dimensions
  updateSelectionBoxDisplay();
}

function stopResizing() {
  if (!isResizing) return;
  
  isResizing = false;
  currentResizeHandle = null;
  
  // Remove temporary event listeners
  document.removeEventListener('mousemove', resizeSelection);
  document.removeEventListener('mouseup', stopResizing);
  document.removeEventListener('touchmove', resizeSelectionTouch);
  document.removeEventListener('touchend', stopResizing);
}

// Improved crop function
processBtn.addEventListener('click', function() {
  if (!selectionActive) {
    alert('Please make a selection first');
    return;
  }
  
  loadingIndicator.style.display = 'block';
  
  setTimeout(() => {
    // Get selection box coordinates
    const selLeft = selectionRect.left;
    const selTop = selectionRect.top;
    const selWidth = selectionRect.width;
    const selHeight = selectionRect.height;
    
    // Calculate original image position and dimensions
    const imgRect = magnifiedImage.getBoundingClientRect();
    const imgLeft = parseInt(magnifiedImage.style.left) || 0;
    const imgTop = parseInt(magnifiedImage.style.top) || 0;
    const imgWidth = magnifiedImage.naturalWidth;
    const imgHeight = magnifiedImage.naturalHeight;
    
    // Account for the current scale/zoom level
    const scaledImgWidth = imgRect.width / currentScale;
    const scaledImgHeight = imgRect.height / currentScale;
    
    // Calculate the selection in terms of the original image
    const cropX = (selLeft - imgLeft) / currentScale;
    const cropY = (selTop - imgTop) / currentScale;
    const cropWidth = selWidth / currentScale;
    const cropHeight = selHeight / currentScale;
    
    // Ensure crop dimensions are valid
    if (cropX < 0 || cropY < 0 || cropWidth <= 0 || cropHeight <= 0 || 
        cropX + cropWidth > imgWidth || cropY + cropHeight > imgHeight) {
      console.warn("Crop dimensions invalid, adjusting...");
      // Adjust crop dimensions to valid values
      const validCropX = Math.max(0, Math.min(cropX, imgWidth - 1));
      const validCropY = Math.max(0, Math.min(cropY, imgHeight - 1));
      const validCropWidth = Math.max(1, Math.min(cropWidth, imgWidth - validCropX));
      const validCropHeight = Math.max(1, Math.min(cropHeight, imgHeight - validCropY));
      
      // Create a canvas to crop the image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // Set canvas dimensions to cropped size
      canvas.width = validCropWidth;
      canvas.height = validCropHeight;
      
      // Create an image to draw from
      const img = new Image();
      img.onload = function() {
        // Draw the cropped portion to the canvas
        ctx.drawImage(
          img,
          validCropX, validCropY, validCropWidth, validCropHeight,
          0, 0, validCropWidth, validCropHeight
        );
        
        // Convert canvas to data URL
        croppedImageData = canvas.toDataURL('image/png');
        setupCroppedView();
      };
      img.onerror = handleCropError;
      img.src = imageData;
    } else {
      // Create a canvas to crop the image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // Set canvas dimensions to cropped size
      canvas.width = cropWidth;
      canvas.height = cropHeight;
      
      // Create an image to draw from
      const img = new Image();
      img.onload = function() {
        // Draw the cropped portion to the canvas
        ctx.drawImage(
          img,
          cropX, cropY, cropWidth, cropHeight,
          0, 0, cropWidth, cropHeight
        );
        
        // Convert canvas to data URL
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
    // Setup cropped image view
    croppedImage.src = croppedImageData;
    croppedImage.style.width = 'auto';
    croppedImage.style.height = 'auto';
    croppedImage.style.maxWidth = '100%';
    croppedImage.style.maxHeight = '100%';
    
    // Center the cropped image after it loads
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
      
      // Update cropped image width and height variables
      croppedImageWidth = imgWidth;
      croppedImageHeight = imgHeight;
      
      // Reset cropped view controls
      croppedIntensitySlider.value = 1;
      croppedIntensityValue.textContent = '1';
      croppedCurrentScale = 1.0;
      croppedZoomInfo.textContent = 'Current zoom: 1.0x';
      croppedGrayscaleCheckbox.checked = grayscaleCheckbox.checked;
      applyGrayscaleCropped();
      
      // Show cropped tab
      croppedTab.style.display = 'block';
      croppedTab.click();
      
      loadingIndicator.style.display = 'none';
    };
  }
});

// Improved drag functions for better interaction with selection
function startDragging(e) {
  // Don't start dragging if we're in selection mode or currently selecting/resizing
  if (selectionModeCheckbox.checked || isSelecting || isResizing) return;
  
  e.preventDefault();
  isDragging = true;

  startX = e.clientX;
  startY = e.clientY;

  startLeft = parseInt(magnifiedImage.style.left) || 0;
  startTop = parseInt(magnifiedImage.style.top) || 0;
  
  // Change cursor to indicate dragging
  magnifiedImage.style.cursor = 'grabbing';
}

// Keyboard shortcut handler for selection
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    // Cancel selection or dragging
    if (isSelecting || isResizing) {
      stopResizing();
      finishSelection();
      isSelecting = false;
      isResizing = false;
      selectionBox.style.display = 'none';
      selectionActive = false;
    } else if (selectionActive && selectionModeCheckbox.checked) {
      // Just clear the active selection but stay in selection mode
      selectionBox.style.display = 'none';
      selectionActive = false;
    } else if (selectionModeCheckbox.checked) {
      // Exit selection mode
      selectionModeCheckbox.checked = false;
      selectionBox.style.display = 'none';
      selectionActive = false;
      magnifiedImage.style.cursor = 'grab';
      magnifiedContainer.style.cursor = 'default';
    }
  } else if (e.key === 'Delete' || e.key === 'Backspace') {
    // Clear selection if active
    if (selectionActive && selectionModeCheckbox.checked) {
      selectionBox.style.display = 'none';
      selectionActive = false;
    }
  }
});
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
  isSelecting = false;
  magnifiedImage.style.cursor = 'grab';
}

// Cropped image dragging functions
function startCroppedDragging(e) {
  e.preventDefault();
  isDragging = true;

  startX = e.clientX;
  startY = e.clientY;

  startLeft = parseInt(croppedImage.style.left) || 0;
  startTop = parseInt(croppedImage.style.top) || 0;
  
  croppedImage.style.cursor = 'grabbing';
}

function startCroppedDraggingTouch(e) {
  if (e.touches.length !== 1) return;
  
  e.preventDefault();
  isDragging = true;
  
  const touch = e.touches[0];
  startX = touch.clientX;
  startY = touch.clientY;
  
  startLeft = parseInt(croppedImage.style.left) || 0;
  startTop = parseInt(croppedImage.style.top) || 0;
}

function dragCroppedImage(e) {
  if (!isDragging) return;
  
  e.preventDefault();
  const x = e.clientX;
  const y = e.clientY;
  
  const newLeft = startLeft + (x - startX);
  const newTop = startTop + (y - startY);
  
  croppedImage.style.left = newLeft + 'px';
  croppedImage.style.top = newTop + 'px';
}

function dragCroppedImageTouch(e) {
  if (!isDragging || e.touches.length !== 1) return;
  
  e.preventDefault();
  const touch = e.touches[0];
  const x = touch.clientX;
  const y = touch.clientY;
  
  const newLeft = startLeft + (x - startX);
  const newTop = startTop + (y - startY);
  
  croppedImage.style.left = newLeft + 'px';
  croppedImage.style.top = newTop + 'px';
}

function stopCroppedDragging() {
  isDragging = false;
  croppedImage.style.cursor = 'grab';
}

// Selection functions
// First, modify the stopDragging function to preserve the selection when in selection mode
function stopDragging() {
  isDragging = false;
  
  // Don't reset isSelecting if we're in selection mode AND we've created a valid selection
  if (!selectionModeCheckbox.checked || !selectionActive) {
    isSelecting = false;
  }
  
  magnifiedImage.style.cursor = 'grab';
  
  // If we're in selection mode, change cursor back to crosshair
  if (selectionModeCheckbox.checked) {
    magnifiedImage.style.cursor = 'crosshair';
  }
}

// Then, modify the handleSelection function to better handle selection completion
function handleSelection(e) {
  const containerRect = magnifiedContainer.getBoundingClientRect();
  const x = e.clientX - containerRect.left;
  const y = e.clientY - containerRect.top;
  
  if (!isSelecting) {
    // Start selection
    isSelecting = true;
    selectionStartX = x;
    selectionStartY = y;
    selectionBox.style.left = x + 'px';
    selectionBox.style.top = y + 'px';
    selectionBox.style.width = '0';
    selectionBox.style.height = '0';
    selectionBox.style.display = 'block';
  } else {
    // Update selection
    selectionCurrentX = x;
    selectionCurrentY = y;
    
    // Calculate top-left corner and dimensions
    const selLeft = Math.min(selectionStartX, selectionCurrentX);
    const selTop = Math.min(selectionStartY, selectionCurrentY);
    const selWidth = Math.abs(selectionCurrentX - selectionStartX);
    const selHeight = Math.abs(selectionCurrentY - selectionStartY);
    
    // Apply to selection box
    selectionBox.style.left = selLeft + 'px';
    selectionBox.style.top = selTop + 'px';
    selectionBox.style.width = selWidth + 'px';
    selectionBox.style.height = selHeight + 'px';
    
    // Only mark selection as active if it has a meaningful size
    if (selWidth > 5 && selHeight > 5) {
      selectionActive = true;
    }
  }
}

// Update the mouseup event listener to finalize the selection
magnifiedContainer.addEventListener('mouseup', function(e) {
  if (selectionModeCheckbox.checked && isSelecting) {
    // Finalize the selection but keep isSelecting true if we've made a valid selection
    if (selectionActive) {
      isSelecting = false;
    }
  }
});

// Also update the touchend event for touch devices
magnifiedContainer.addEventListener('touchend', function(e) {
  if (selectionModeCheckbox.checked && isSelecting) {
    // Finalize the selection but keep isSelecting true if we've made a valid selection
    if (selectionActive) {
      isSelecting = false;
    }
  }
});

// Update the selectionModeCheckbox event listener to properly initialize/reset selection state
selectionModeCheckbox.addEventListener('change', function() {
  if (this.checked) {
    // Enable selection mode
    selectionBox.style.display = 'none';
    selectionActive = false;
    magnifiedImage.style.cursor = 'crosshair';
    
    // These event listeners are already in your code, but make sure they're updated
    // with the new handleSelection function
  } else {
    // Disable selection mode
    isSelecting = false;
    selectionBox.style.display = 'none';
    selectionActive = false;
    magnifiedImage.style.cursor = 'grab';
  }
});
// Zoom functionality
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

// Grayscale functionality
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

// Process (crop) button functionality
processBtn.addEventListener('click', function() {
  if (!selectionActive) {
    alert('Please make a selection first');
    return;
  }
  
  loadingIndicator.style.display = 'block';
  
  setTimeout(() => {
    // Calculate the selection in terms of the original image
    const imgRect = magnifiedImage.getBoundingClientRect();
    const containerRect = magnifiedContainer.getBoundingClientRect();
    
    // Get selection box coordinates relative to container
    const selLeft = parseInt(selectionBox.style.left);
    const selTop = parseInt(selectionBox.style.top);
    const selWidth = parseInt(selectionBox.style.width);
    const selHeight = parseInt(selectionBox.style.height);
    
    // Calculate original image position and dimensions
    const imgLeft = parseInt(magnifiedImage.style.left);
    const imgTop = parseInt(magnifiedImage.style.top);
    const imgWidth = magnifiedImage.clientWidth / currentScale;
    const imgHeight = magnifiedImage.clientHeight / currentScale;
    
    // Calculate the selection in terms of the original image
    const cropX = (selLeft - imgLeft) / currentScale;
    const cropY = (selTop - imgTop) / currentScale;
    const cropWidth = selWidth / currentScale;
    const cropHeight = selHeight / currentScale;
    
    // Create a canvas to crop the image
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions to cropped size
    canvas.width = cropWidth;
    canvas.height = cropHeight;
    
    // Create an image to draw from
    const img = new Image();
    img.onload = function() {
      // Draw the cropped portion to the canvas
      ctx.drawImage(
        img,
        cropX, cropY, cropWidth, cropHeight,
        0, 0, cropWidth, cropHeight
      );
      
      // Convert canvas to data URL
      croppedImageData = canvas.toDataURL('image/png');
      
      // Setup cropped image view
      croppedImage.src = croppedImageData;
      croppedImage.style.width = 'auto';
      croppedImage.style.height = 'auto';
      croppedImage.style.maxWidth = '100%';
      croppedImage.style.maxHeight = '100%';
      
      // Center the cropped image after it loads
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
        
        // Update cropped image width and height variables
        croppedImageWidth = imgWidth;
        croppedImageHeight = imgHeight;
        
        // Reset cropped view controls
        croppedIntensitySlider.value = 1;
        croppedIntensityValue.textContent = '1';
        croppedCurrentScale = 1.0;
        croppedZoomInfo.textContent = 'Current zoom: 1.0x';
        croppedGrayscaleCheckbox.checked = grayscaleCheckbox.checked;
        applyGrayscaleCropped();
        
        // Show cropped tab
        croppedTab.style.display = 'block';
        croppedTab.click();
        
        loadingIndicator.style.display = 'none';
      };
    };
    img.onerror = function() {
      alert('Error cropping image. Please try again.');
      loadingIndicator.style.display = 'none';
    };
    img.src = imageData;
  }, 100);
});

// Download functions
downloadBtn.addEventListener('click', function() {
  // Create an anchor element
  const a = document.createElement('a');
  
  // Create a new canvas to capture the whole view including zoom and position
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Set canvas dimensions to container dimensions
  const containerWidth = magnifiedContainer.clientWidth;
  const containerHeight = magnifiedContainer.clientHeight;
  canvas.width = containerWidth;
  canvas.height = containerHeight;
  
  // Fill canvas with white background
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Calculate visible portion of the image
  const img = new Image();
  img.onload = function() {
    const scaledImgWidth = img.width * currentScale;
    const scaledImgHeight = img.height * currentScale;
    
    const imgLeft = parseInt(magnifiedImage.style.left) || 0;
    const imgTop = parseInt(magnifiedImage.style.top) || 0;
    
    // Draw image to canvas with current transform
    ctx.save();
    
    // Apply grayscale if needed
    if (grayscaleCheckbox.checked) {
      ctx.filter = 'grayscale(100%)';
    }
    
    ctx.drawImage(img, imgLeft, imgTop, scaledImgWidth, scaledImgHeight);
    ctx.restore();
    
    // Convert canvas to data URL
    const dataUrl = canvas.toDataURL('image/png');
    
    // Set download attributes
    a.href = dataUrl;
    a.download = 'magnified_image.png';
    
    // Trigger download
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  img.src = imageData;
});

croppedDownloadBtn.addEventListener('click', function() {
  if (!croppedImageData) return;
  
  // Create an anchor element
  const a = document.createElement('a');
  
  // Create a new canvas to capture the whole view including zoom and position
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Set canvas dimensions to container dimensions
  const containerWidth = document.querySelector('#cropped-tab-content #magnified-image-container').clientWidth;
  const containerHeight = document.querySelector('#cropped-tab-content #magnified-image-container').clientHeight;
  canvas.width = containerWidth;
  canvas.height = containerHeight;
  
  // Fill canvas with white background
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Calculate visible portion of the image
  const img = new Image();
  img.onload = function() {
    const scaledImgWidth = img.width * croppedCurrentScale;
    const scaledImgHeight = img.height * croppedCurrentScale;
    
    const imgLeft = parseInt(croppedImage.style.left) || 0;
    const imgTop = parseInt(croppedImage.style.top) || 0;
    
    // Draw image to canvas with current transform
    ctx.save();
    
    // Apply grayscale if needed
    if (croppedGrayscaleCheckbox.checked) {
      ctx.filter = 'grayscale(100%)';
    }
    
    ctx.drawImage(img, imgLeft, imgTop, scaledImgWidth, scaledImgHeight);
    ctx.restore();
    
    // Convert canvas to data URL
    const dataUrl = canvas.toDataURL('image/png');
    
    // Set download attributes
    a.href = dataUrl;
    a.download = 'cropped_image.png';
    
    // Trigger download
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

// Keyboard shortcuts for accessibility
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    // Cancel selection or dragging
    isDragging = false;
    isSelecting = false;
    isResizing = false;
    if (selectionModeCheckbox.checked) {
      selectionModeCheckbox.checked = false;
      selectionBox.style.display = 'none';
      selectionActive = false;
      magnifiedImage.style.cursor = 'grab';
    }
  }
});

// Initialize the app
window.addEventListener('DOMContentLoaded', function() {
  magnifiedSection.style.display = 'none';
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
        # Read image data and convert to base64
        img_data = file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        # Process image parameters
        intensity = float(request.form.get('intensity', 1.0))
        convert_to_grayscale = request.form.get('grayscale', 'false') == 'true'
        
        # Return the processed image data
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
    
    # In a real app, you would process the crop here
    # For this demo, we'll just return the original image
    return jsonify({'image': data['image']})

@app.route('/download', methods=['POST'])
def download_image():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    # Return the image data for download
    return jsonify({'downloadUrl': data['image']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
