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



/* Root styles */
:root {
  --primary-color: #4285f4;
  --primary-hover: #2a75f3;
  --secondary-color: #34a853;
  --secondary-hover: #2d9249;
  --text-color: #333;
  --light-bg: #f9f9f9;
  --border-color: #ddd;
  --shadow-color: rgba(0, 0, 0, 0.1);
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  padding: 0;
  color: var(--text-color);
  background-color: var(--light-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  color: var(--primary-color);
  margin-bottom: 30px;
}

/* Upload section */
#upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.upload-area {
  border: 3px dashed #ccc;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  width: 100%;
  max-width: 600px;
  transition: all 0.3s ease;
}

.upload-area:hover, .upload-area:focus {
  border-color: var(--primary-color);
  background-color: rgba(66, 133, 244, 0.05);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

#file-input {
  display: none;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.tab {
  padding: 12px 20px;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  font-weight: 500;
  transition: background-color 0.2s;
  border: 1px solid transparent;
  border-bottom: none;
}

.tab:hover {
  background-color: rgba(66, 133, 244, 0.1);
}

.tab.active {
  background-color: white;
  border-color: var(--border-color);
  border-bottom: 2px solid white;
  margin-bottom: -1px;
  color: var(--primary-color);
}

.tab-content {
  display: none;
  background: white;
  border-radius: 0 8px 8px 8px;
  padding: 20px;
  box-shadow: 0 4px 6px var(--shadow-color);
}

.tab-content.active {
  display: block;
}

/* Controls */
.control-panel {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.slider-container {
  margin-bottom: 15px;
}

.slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #d3d3d3;
  outline: none;
  transition: opacity 0.2s;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  background: var(--primary-hover);
  transform: scale(1.1);
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.slider::-moz-range-thumb:hover {
  background: var(--primary-hover);
  transform: scale(1.1);
}

.checkbox-container {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.checkbox-container input[type="checkbox"] {
  margin-right: 10px;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.instructions {
  margin-top: 15px;
  padding: 10px;
  background-color: #fff;
  border-left: 4px solid var(--primary-color);
  border-radius: 0 4px 4px 0;
}

/* Image container */
#magnified-image-container {
  position: relative;
  width: 100%;
  height: 500px;
  margin: 20px 0;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: #f0f0f0;
  background-image: linear-gradient(45deg, #e0e0e0 25%, transparent 25%), 
                    linear-gradient(-45deg, #e0e0e0 25%, transparent 25%), 
                    linear-gradient(45deg, transparent 75%, #e0e0e0 75%), 
                    linear-gradient(-45deg, transparent 75%, #e0e0e0 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

#magnified-image, #cropped-image {
  position: absolute;
  cursor: grab;
  user-select: none;
  transform-origin: top left;
}

#magnified-image:active, #cropped-image:active {
  cursor: grabbing;
}

#selection-box {
  position: absolute;
  border: 2px dashed rgba(65, 105, 225, 0.8);
  background-color: rgba(65, 105, 225, 0.2);
  pointer-events: none;
  display: none;
}

.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: white;
  border: 1px solid rgba(65, 105, 225, 0.8);
  border-radius: 50%;
  pointer-events: all;
  cursor: pointer;
}

.handle-nw { top: -5px; left: -5px; cursor: nw-resize; }
.handle-n { top: -5px; left: calc(50% - 5px); cursor: n-resize; }
.handle-ne { top: -5px; right: -5px; cursor: ne-resize; }
.handle-e { top: calc(50% - 5px); right: -5px; cursor: e-resize; }
.handle-se { bottom: -5px; right: -5px; cursor: se-resize; }
.handle-s { bottom: -5px; left: calc(50% - 5px); cursor: s-resize; }
.handle-sw { bottom: -5px; left: -5px; cursor: sw-resize; }
.handle-w { top: calc(50% - 5px); left: -5px; cursor: w-resize; }

/* Buttons */
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: var(--primary-color);
  color: white;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.button:hover {
  background-color: var(--primary-hover);
}

.button.process {
  background-color: var(--secondary-color);
}

.button.process:hover {
  background-color: var(--secondary-hover);
}

.button.download {
  background-color: #ea4335;
}

.button.download:hover {
  background-color: #d33426;
}

#zoom-info, #cropped-zoom-info {
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

/* Loading indicator */
.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 15px 30px;
  border-radius: 5px;
  font-weight: 500;
  display: none;
  z-index: 10;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .control-panel {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .button {
    width: 100%;
  }
  
  #magnified-image-container {
    height: 350px;
  }
}

"""

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Image Magnifier & Cropper</title>

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
  if (!isDragging) return;
  if (e.touches.length === 1) {
    e.preventDefault();

    const touch = e.touches[0];
    const dx = touch.clientX - startX;
    const dy = touch.clientY - startY;

    const newLeft = startLeft + dx;
    const newTop = startTop + dy;

    magnifiedImage.style.left = newLeft + 'px';
    magnifiedImage.style.top = newTop + 'px';
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

  const dx = e.clientX - startX;
  const dy = e.clientY - startY;

  const newLeft = startLeft + dx;
  const newTop = startTop + dy;

  croppedImage.style.left = newLeft + 'px';
  croppedImage.style.top = newTop + 'px';
}

function dragCroppedImageTouch(e) {
  if (!isDragging) return;
  if (e.touches.length === 1) {
    e.preventDefault();

    const touch = e.touches[0];
    const dx = touch.clientX - startX;
    const dy = touch.clientY - startY;

    const newLeft = startLeft + dx;
    const newTop = startTop + dy;

    croppedImage.style.left = newLeft + 'px';
    croppedImage.style.top = newTop + 'px';
  }
}

function stopCroppedDragging() {
  isDragging = false;
}

intensitySlider.addEventListener('input', () => {
  const value = parseFloat(intensitySlider.value);
  intensityValue.textContent = value.toFixed(1);
  currentScale = value;
  zoomInfo.textContent = `Current zoom: ${value.toFixed(1)}x`;
  magnifiedImage.style.transform = `scale(${value})`;
});

croppedIntensitySlider.addEventListener('input', () => {
  const value = parseFloat(croppedIntensitySlider.value);
  croppedIntensityValue.textContent = value.toFixed(1);
  croppedCurrentScale = value;
  croppedZoomInfo.textContent = `Current zoom: ${value.toFixed(1)}x`;
  croppedImage.style.transform = `scale(${value})`;
});

grayscaleCheckbox.addEventListener('change', applyGrayscale);
croppedGrayscaleCheckbox.addEventListener('change', applyCroppedGrayscale);

selectionModeCheckbox.addEventListener('change', () => {
  if (selectionModeCheckbox.checked) {
    magnifiedContainer.addEventListener('mousedown', startSelection);
    document.addEventListener('mousemove', updateSelection);
    document.addEventListener('mouseup', endSelection);
    
    magnifiedContainer.addEventListener('touchstart', startSelectionTouch);
    document.addEventListener('touchmove', updateSelectionTouch);
    document.addEventListener('touchend', endSelection);
  } else {
    magnifiedContainer.removeEventListener('mousedown', startSelection);
    document.removeEventListener('mousemove', updateSelection);
    document.removeEventListener('mouseup', endSelection);
    
    magnifiedContainer.removeEventListener('touchstart', startSelectionTouch);
    document.removeEventListener('touchmove', updateSelectionTouch);
    document.removeEventListener('touchend', endSelection);
    
    selectionBox.style.display = 'none';
    selectionActive = false;
  }
});

function startSelection(e) {
  if (!selectionModeCheckbox.checked || isResizing) return;
  e.preventDefault();
  
  isSelecting = true;
  selectionActive = true;
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionStartX = e.clientX - containerRect.left;
  selectionStartY = e.clientY - containerRect.top;
  
  selectionBox.style.left = selectionStartX + 'px';
  selectionBox.style.top = selectionStartY + 'px';
  selectionBox.style.width = '0';
  selectionBox.style.height = '0';
  selectionBox.style.display = 'block';
}

function startSelectionTouch(e) {
  if (!selectionModeCheckbox.checked || isResizing || e.touches.length !== 1) return;
  e.preventDefault();
  
  isSelecting = true;
  selectionActive = true;
  
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionStartX = touch.clientX - containerRect.left;
  selectionStartY = touch.clientY - containerRect.top;
  
  selectionBox.style.left = selectionStartX + 'px';
  selectionBox.style.top = selectionStartY + 'px';
  selectionBox.style.width = '0';
  selectionBox.style.height = '0';
  selectionBox.style.display = 'block';
}

function updateSelection(e) {
  if (!isSelecting) return;
  e.preventDefault();
  
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionCurrentX = e.clientX - containerRect.left;
  selectionCurrentY = e.clientY - containerRect.top;

  // Calculate the selection box dimensions
  const left = Math.min(selectionStartX, selectionCurrentX);
  const top = Math.min(selectionStartY, selectionCurrentY);
  const width = Math.abs(selectionCurrentX - selectionStartX);
  const height = Math.abs(selectionCurrentY - selectionStartY);
  
  // Apply constraints to keep selection within container
  const constrainedLeft = Math.max(0, Math.min(left, containerRect.width));
  const constrainedTop = Math.max(0, Math.min(top, containerRect.height));
  const constrainedWidth = Math.min(width, containerRect.width - constrainedLeft);
  const constrainedHeight = Math.min(height, containerRect.height - constrainedTop);
  
  // Set selection box properties
  selectionBox.style.left = constrainedLeft + 'px';
  selectionBox.style.top = constrainedTop + 'px';
  selectionBox.style.width = constrainedWidth + 'px';
  selectionBox.style.height = constrainedHeight + 'px';
}

function updateSelectionTouch(e) {
  if (!isSelecting || e.touches.length !== 1) return;
  e.preventDefault();
  
  const touch = e.touches[0];
  const containerRect = magnifiedContainer.getBoundingClientRect();
  selectionCurrentX = touch.clientX - containerRect.left;
  selectionCurrentY = touch.clientY - containerRect.top;

  // Calculate the selection box dimensions
  const left = Math.min(selectionStartX, selectionCurrentX);
  const top = Math.min(selectionStartY, selectionCurrentY);
  const width = Math.abs(selectionCurrentX - selectionStartX);
  const height = Math.abs(selectionCurrentY - selectionStartY);
  
  // Apply constraints to keep selection within container
  const constrainedLeft = Math.max(0, Math.min(left, containerRect.width));
  const constrainedTop = Math.max(0, Math.min(top, containerRect.height));
  const constrainedWidth = Math.min(width, containerRect.width - constrainedLeft);
  const constrainedHeight = Math.min(height, containerRect.height - constrainedTop);
  
  // Set selection box properties
  selectionBox.style.left = constrainedLeft + 'px';
  selectionBox.style.top = constrainedTop + 'px';
  selectionBox.style.width = constrainedWidth + 'px';
  selectionBox.style.height = constrainedHeight + 'px';
}

function endSelection() {
  isSelecting = false;
}

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

processBtn.addEventListener('click', () => {
  if (!selectionActive) {
    alert('Please select an area to crop first.');
    return;
  }
  
  loadingIndicator.style.display = 'block';
  setTimeout(() => processImage(), 50);
});

function processImage() {
  // Get the selection coordinates
  const boxLeft = parseInt(selectionBox.style.left);
  const boxTop = parseInt(selectionBox.style.top);
  const boxWidth = parseInt(selectionBox.style.width);
  const boxHeight = parseInt(selectionBox.style.height);
  
  if (boxWidth < 10 || boxHeight < 10) {
    alert('Selection too small. Please select a larger area.');
    loadingIndicator.style.display = 'none';
    return;
  }
  
  // Create a temporary canvas to crop the image
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Create a temporary image to get the scaled image data
  const tempImg = new Image();
  tempImg.onload = function() {
    // Calculate the scale factor between original image and displayed image
    const displayedImgWidth = magnifiedImage.getBoundingClientRect().width / currentScale;
    const displayedImgHeight = magnifiedImage.getBoundingClientRect().height / currentScale;
    
    const scaleFactorX = originalImageWidth / displayedImgWidth;
    const scaleFactorY = originalImageHeight / displayedImgHeight;
    
    // Calculate the offset considering current position and scale
    const offsetX = parseInt(magnifiedImage.style.left || '0') / currentScale;
    const offsetY = parseInt(magnifiedImage.style.top || '0') / currentScale;
    
    // Calculate the source coordinates in the original image
    const sourceX = (boxLeft / currentScale - offsetX) * scaleFactorX;
    const sourceY = (boxTop / currentScale - offsetY) * scaleFactorY;
    const sourceWidth = (boxWidth / currentScale) * scaleFactorX;
    const sourceHeight = (boxHeight / currentScale) * scaleFactorY;
    
    // Set canvas dimensions to the cropped size
    canvas.width = sourceWidth;
    canvas.height = sourceHeight;
    
    // Draw the cropped portion to the canvas
    ctx.drawImage(
      tempImg,
      sourceX, sourceY, sourceWidth, sourceHeight,
      0, 0, sourceWidth, sourceHeight
    );
    
    // Apply grayscale if needed
    if (grayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
        data[i] = avg;     // red
        data[i + 1] = avg; // green
        data[i + 2] = avg; // blue
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    // Get the cropped image data
    croppedImageData = canvas.toDataURL('image/jpeg', 0.9);
    
    // Update the cropped image tab
    setupCroppedImage(croppedImageData);
    
    // Hide loading indicator
    loadingIndicator.style.display = 'none';
  };
  tempImg.src = imageData;
}

function setupCroppedImage(croppedDataUrl) {
  croppedTab.style.display = '';
  croppedTab.click();
  
  croppedCurrentScale = 1.0;
  croppedIntensitySlider.value = 1;
  croppedIntensityValue.textContent = '1';
  croppedZoomInfo.textContent = 'Current zoom: 1.0x';
  
  croppedGrayscaleCheckbox.checked = grayscaleCheckbox.checked;
  
  const img = new Image();
  img.onload = function() {
    croppedImageWidth = this.width;
    croppedImageHeight = this.height;
    
    // Center the image initially
    croppedImage.src = croppedDataUrl;
    croppedImage.style.width = 'auto';
    croppedImage.style.height = 'auto';
    croppedImage.style.maxWidth = '100%';
    croppedImage.style.maxHeight = '100%';
    
    // Center the image after it loads
    croppedImage.onload = function() {
      const container = document.querySelector('#cropped-tab-content #magnified-image-container');
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;
      const imgWidth = croppedImage.clientWidth;
      const imgHeight = croppedImage.clientHeight;
      
      // Calculate the position to center the image
      const leftPos = (containerWidth - imgWidth) / 2;
      const topPos = (containerHeight - imgHeight) / 2;
      
      croppedImage.style.left = leftPos + 'px';
      croppedImage.style.top = topPos + 'px';
      croppedImage.style.transform = 'scale(1)';
    };
    
    applyCroppedGrayscale();
  };
  img.src = croppedDataUrl;
}

downloadBtn.addEventListener('click', () => {
  const a = document.createElement('a');
  
  // Create a temporary canvas to apply magnification
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  const tempImg = new Image();
  tempImg.onload = function() {
    // Apply the current magnification
    canvas.width = tempImg.width * currentScale;
    canvas.height = tempImg.height * currentScale;
    
    // Draw the image with magnification
    ctx.scale(currentScale, currentScale);
    ctx.drawImage(tempImg, 0, 0);
    
    // Apply grayscale if needed
    if (grayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
        data[i] = avg;     // red
        data[i + 1] = avg; // green
        data[i + 2] = avg; // blue
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    // Create download link
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
    a.href = dataUrl;
    a.download = 'magnified-image.jpg';
    a.click();
  };
  tempImg.src = imageData;
});

croppedDownloadBtn.addEventListener('click', () => {
  if (!croppedImageData) return;
  
  const a = document.createElement('a');
  
  // Create a temporary canvas to apply magnification
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  const tempImg = new Image();
  tempImg.onload = function() {
    // Apply the current magnification
    canvas.width = tempImg.width * croppedCurrentScale;
    canvas.height = tempImg.height * croppedCurrentScale;
    
    // Draw the image with magnification
    ctx.scale(croppedCurrentScale, croppedCurrentScale);
    ctx.drawImage(tempImg, 0, 0);
    
    // Apply grayscale if needed
    if (croppedGrayscaleCheckbox.checked) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
        data[i] = avg;     // red
        data[i + 1] = avg; // green
        data[i + 2] = avg; // blue
      }
      ctx.putImageData(imageData, 0, 0);
    }
    
    // Create download link
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
    a.href = dataUrl;
    a.download = 'cropped-image.jpg';
    a.click();
  };
  tempImg.src = croppedImageData;
});

newImageBtn.addEventListener('click', () => {
  uploadSection.style.display = 'block';
  magnifierSection.style.display = 'none';
  fileInput.value = '';
});

backToOriginalBtn.addEventListener('click', () => {
  tabs[0].click();
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
