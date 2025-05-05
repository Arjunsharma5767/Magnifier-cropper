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
  position: relative;
  left: 0;
  top: 0;
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
  border: 2px dashed #ea4335;
  background-color: rgba(234, 67, 53, 0.2);
  pointer-events: none;
  display: none;
  z-index: 10;
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
  align-items: centre;
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
          <p>Drag to pan around the image. Use the slider to zoom in. Enable selection mode and drag to select an area for cropping.</p>
        </div>
      </div>
      <div id="magnified-image-container">
        <div class="loading" id="loading-indicator">Processing...</div>
        <img id="magnified-image" src="" alt="Original Image" />
        <div id="selection-box"></div>
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
    magnifiedImage.src = imageUrl;
    magnifiedImage.style.width = '100%';
    magnifiedImage.style.height = 'auto';
    magnifiedImage.style.top = '0px';
    magnifiedImage.style.left = '0px';
    magnifiedImage.style.transform = 'scale(1)';
    applyGrayscale();
    setupDragging();
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

function startDragging(e) {
  if (selectionModeCheckbox.checked) return;
  e.preventDefault();
  isDragging = true;

  startX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  startY = e.clientY || (e.touches ? e.touches[0].clientY : 0);

  startLeft = parseInt(magnifiedImage.style.left) || 0;
  startTop = parseInt(magnifiedImage.style.top) || 0;
}

function startDraggingTouch(e) {
  if (selectionModeCheckbox.checked) return;
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

  let newLeft = startLeft + dx;
  let newTop = startTop + dy;

  const containerWidth = magnifiedContainer.clientWidth;
  const containerHeight = magnifiedContainer.clientHeight;
  const imageWidth = originalImageWidth * currentScale;
  const imageHeight = originalImageHeight * currentScale;

  const minLeft = Math.min(0, containerWidth - imageWidth);
  const maxLeft = 0;
  const minTop = Math.min(0, containerHeight - imageHeight);
  const maxTop = 0;

  newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
  newTop = Math.max(minTop, Math.min(maxTop, newTop));

  magnifiedImage.style.left = newLeft + 'px';
  magnifiedImage.style.top = newTop + 'px';
}

function dragImageTouch(e) {
  if (e.touches.length === 1) {
    dragImage(e);
  }
}

function stopDragging() {
  isDragging = false;
}

// Cropped image drag vars
let isCroppedDragging = false;
let croppedStartX, croppedStartY, croppedStartLeft, croppedStartTop;

function startCroppedDragging(e) {
  e.preventDefault();
  isCroppedDragging = true;
  croppedStartX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  croppedStartY = e.clientY || (e.touches ? e.touches[0].clientY : 0);

  croppedStartLeft = parseInt(croppedImage.style.left) || 0;
  croppedStartTop = parseInt(croppedImage.style.top) || 0;
}

function startCroppedDraggingTouch(e) {
  if (e.touches.length === 1) {
    e.preventDefault();
    isCroppedDragging = true;
    const touch = e.touches[0];
    croppedStartX = touch.clientX;
    croppedStartY = touch.clientY;
    croppedStartLeft = parseInt(croppedImage.style.left) || 0;
    croppedStartTop = parseInt(croppedImage.style.top) || 0;
  }
}

function dragCroppedImage(e) {
  if (!isCroppedDragging) return;
  e.preventDefault();
  const clientX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
  const clientY = e.clientY || (e.touches ? e.touches[0].clientY : 0);
  const dx = clientX - croppedStartX;
  const dy = clientY - croppedStartY;

  let newLeft = croppedStartLeft + dx;
  let newTop = croppedStartTop + dy;

  const croppedContainer = document.querySelector('#cropped-tab-content #magnified-image-container');
  const containerWidth = croppedContainer.clientWidth;
  const containerHeight = croppedContainer.clientHeight;
  const imageWidth = croppedImageWidth * croppedCurrentScale;
  const imageHeight = croppedImageHeight * croppedCurrentScale;

  const minLeft = Math.min(0, containerWidth - imageWidth);
  const maxLeft = 0;
  const minTop = Math.min(0, containerHeight - imageHeight);
  const maxTop = 0;

  newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
  newTop = Math.max(minTop, Math.min(maxTop, newTop));

  croppedImage.style.left = newLeft + 'px';
  croppedImage.style.top = newTop + 'px';
}

function dragCroppedImageTouch(e) {
  if (e.touches.length === 1) {
    dragCroppedImage(e);
  }
}

function stopCroppedDragging() {
  isCroppedDragging = false;
}

function setupCroppedImage(imageUrl) {
  croppedTab.style.display = 'block';

  croppedCurrentScale = 1.0;
  croppedIntensitySlider.value = 1;
  croppedIntensityValue.textContent = '1';
  croppedZoomInfo.textContent = 'Current zoom: 1.0x';

  croppedImage.style.left = '0px';
  croppedImage.style.top = '0px';
  croppedImage.style.transform = 'scale(1)';
  
  croppedImage.style.filter = croppedGrayscaleCheckbox.checked ? 'grayscale(100%)' : 'none';
  croppedImage.src = imageUrl;

  croppedImage.onload = () => {
    croppedImageWidth = croppedImage.naturalWidth;
    croppedImageHeight = croppedImage.naturalHeight;
    croppedImage.style.width = '100%';
    croppedImage.style.height = 'auto';
  };

  tabs[1].click();
}

function getCroppedArea() {
  if (!selectionBox.style.width || parseInt(selectionBox.style.width) === 0) return null;

  const selBoxRect = selectionBox.getBoundingClientRect();
  const containerRect = magnifiedContainer.getBoundingClientRect();

  const selectionRelativeX = selBoxRect.left - containerRect.left;
  const selectionRelativeY = selBoxRect.top - containerRect.top;

  const imgLeft = parseInt(magnifiedImage.style.left) || 0;
  const imgTop = parseInt(magnifiedImage.style.top) || 0;
  const scale = currentScale;
  const x = (selectionRelativeX - imgLeft) / scale;
  const y = (selectionRelativeY - imgTop) / scale;
  const width = selBoxRect.width / scale;
  const height = selBoxRect.height / scale;

  const adjustedX = Math.max(0, Math.min(originalImageWidth, x));
  const adjustedY = Math.max(0, Math.min(originalImageHeight, y));
  const adjustedWidth = Math.min(originalImageWidth - adjustedX, width);
  const adjustedHeight = Math.min(originalImageHeight - adjustedY, height);

  if (adjustedWidth <= 0 || adjustedHeight <= 0) return null;

  return {
    x: adjustedX,
    y: adjustedY,
    width: adjustedWidth,
    height: adjustedHeight
  };
}

function cropImage(imageDataUrl, croppedArea) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = function() {
      const canvas = document.createElement('canvas');
      canvas.width = croppedArea.width;
      canvas.height = croppedArea.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(
        img,
        croppedArea.x,
        croppedArea.y,
        croppedArea.width,
        croppedArea.height,
        0,
        0,
        croppedArea.width,
        croppedArea.height
      );
      resolve(canvas.toDataURL('image/png'));
    };
    img.onerror = () => reject(new Error('Failed to load image for cropping'));
    img.src = imageDataUrl;
  });
}

processBtn.addEventListener('click', async () => {
  if (!selectionBox.style.width || parseInt(selectionBox.style.width) === 0) {
    alert('Please enable selection mode and select an area to crop.');
    return;
  }
  const area = getCroppedArea();
  if (!area || area.width <= 0 || area.height <= 0) {
    alert('Invalid crop selection. Please select a valid area.');
    return;
  }
  loadingIndicator.style.display = 'block';
  try {
    const croppedUrl = await cropImage(imageData, area);
    croppedImageData = croppedUrl;
    setupCroppedImage(croppedImageData);
  } catch (error) {
    alert('Error cropping image: ' + error.message);
    console.error('Cropping error:', error);
  } finally {
    loadingIndicator.style.display = 'none';
  }
});

downloadBtn.addEventListener('click', () => {
  if (!imageData) return;
  const link = document.createElement('a');
  link.href = imageData;
  link.download = 'magnified-image.png';
  link.click();
});

croppedDownloadBtn.addEventListener('click', () => {
  if (!croppedImageData) return;
  const link = document.createElement('a');
  link.href = croppedImageData;
  link.download = 'cropped-image.png';
  link.click();
});

newImageBtn.addEventListener('click', () => {
  uploadSection.style.display = 'block';
  magnifierSection.style.display = 'none';
});

backToOriginalBtn.addEventListener('click', () => {
  tabs[0].click();
});

intensitySlider.addEventListener('input', () => {
  currentScale = parseFloat(intensitySlider.value);
  intensityValue.textContent = currentScale.toFixed(1);
  magnifiedImage.style.transform = `scale(${currentScale})`;
  zoomInfo.textContent = `Current zoom: ${currentScale.toFixed(1)}x`;
  applyGrayscale();
});

croppedIntensitySlider.addEventListener('input', () => {
  croppedCurrentScale = parseFloat(croppedIntensitySlider.value);
  croppedIntensityValue.textContent = croppedCurrentScale.toFixed(1);
  croppedImage.style.transform = `scale(${croppedCurrentScale})`;
  croppedZoomInfo.textContent = `Current zoom: ${croppedCurrentScale.toFixed(1)}x`;
  croppedImage.style.filter = croppedGrayscaleCheckbox.checked ? 'grayscale(100%)' : 'none';
});

grayscaleCheckbox.addEventListener('change', applyGrayscale);
croppedGrayscaleCheckbox.addEventListener('change', () => {
  croppedImage.style.filter = croppedGrayscaleCheckbox.checked ? 'grayscale(100%)' : 'none';
});

function applyGrayscale() {
  magnifiedImage.style.filter = grayscaleCheckbox.checked ? 'grayscale(100%)' : 'none';
}

// Selection mode functionality
selectionModeCheckbox.addEventListener('change', () => {
  if (selectionModeCheckbox.checked) {
    selectionBox.style.display = 'block';
    selectionActive = true;
  } else {
    selectionBox.style.display = 'none';
    selectionActive = false;
    selectionBox.style.width = '0px';
    selectionBox.style.height = '0px';
  }
});

magnifiedContainer.addEventListener('mousedown', (e) => {
  if (!selectionModeCheckbox.checked) return;
  e.preventDefault();
  selectionActive = true;
  selectionStartX = e.pageX - magnifiedContainer.getBoundingClientRect().left;
  selectionStartY = e.pageY - magnifiedContainer.getBoundingClientRect().top;
  selectionBox.style.left = `${selectionStartX}px`;
  selectionBox.style.top = `${selectionStartY}px`;
  selectionBox.style.width = '0px';
  selectionBox.style.height = '0px';
  selectionBox.style.display = 'block';
});

magnifiedContainer.addEventListener('mousemove', (e) => {
  if (!selectionActive) return;
  e.preventDefault();
  const currentX = e.pageX - magnifiedContainer.getBoundingClientRect().left;
  const currentY = e.pageY - magnifiedContainer.getBoundingClientRect().top;
  const x = Math.min(currentX, selectionStartX);
  const y = Math.min(currentY, selectionStartY);
  const width = Math.abs(currentX - selectionStartX);
  const height = Math.abs(currentY - selectionStartY);
  selectionBox.style.left = `${x}px`;
  selectionBox.style.top = `${y}px`;
  selectionBox.style.width = `${width}px`;
  selectionBox.style.height = `${height}px`;
});

document.addEventListener('mouseup', () => {
  if (selectionActive) {
    selectionActive = false;
  }
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, css=CSS_STYLE)

if __name__ == '__main__':
    app.run(debug=True)
