/**
 * app.js - Master Application Controller
 */

import { NABATAEAN_CLASSES, ARAMAIC_CLASSES, ARABIC_CLASSES, parseClassesFile, getClassColor } from './presets.js';
import { FilterEngine } from './filters.js';
import { LabelingCanvas } from './labeler.js';
import { DatasetExporter } from './exporter.js';

// Application State
const state = {
  lang: 'ar',
  theme: 'dark',
  
  // Classes
  activePreset: 'nabataean',
  classes: [...NABATAEAN_CLASSES],
  customClasses: null,
  activeClassId: 0,
  searchQuery: '',

  // Multi-image dataset
  images: [], // array of { id, file, name, originalCanvas, width, height, annotations, filters, rotation, flipH, flipV }
  currentImageIndex: -1,

  // Current active filter params
  filters: {
    brightness: 0,
    contrast: 0,
    exposure: 0,
    gamma: 1.0,
    saturation: 0,
    invert: false,
    grayscale: false,
    equalizeHist: false,
    sharpen: 0,
    medianDenoise: 0,
    blur: 0,
    emboss: false,
    embossAngle: 45,
    embossStrength: 1.5,
    edgeDetection: 'none',
    edgeStrength: 1.0,
    binarize: 'none',
    thresholdVal: 128,
    adaptiveWindow: 15,
    colorMap: 'none'
  },

  // Geometric transforms
  rotation: 0,
  flipH: false,
  flipV: false,

  // Processed canvas cache
  processedCanvas: null,

  // Split-view
  splitView: false
};

// DOM Elements Cache
const DOM = {};

function initDOM() {
  const ids = [
    'appTitle', 'appSubtitle', 'prevImageBtn', 'nextImageBtn', 'imageCounter',
    'importClassesBtn', 'classesFileInput', 'uploadImageBtn', 'imageFileInput',
    'importYoloBtn', 'yoloFileInput', 'openExportModalBtn', 'langToggleBtn',
    'themeToggleBtn', 'shortcutsModalBtn', 'resetFiltersBtn', 'resetRotationBtn',
    'sliderRotation', 'valRotation', 'btnRotateCCW', 'btnRotateCW', 'btnFlipH', 'btnFlipV',
    'sliderBrightness', 'valBrightness', 'sliderContrast', 'valContrast',
    'sliderExposure', 'valExposure', 'sliderGamma', 'valGamma',
    'sliderSaturation', 'valSaturation', 'toggleInvert', 'toggleGrayscale',
    'toggleEqualize', 'sliderSharpen', 'valSharpen', 'sliderMedian', 'valMedian',
    'toggleEmboss', 'sliderEmbossAngle', 'valEmbossAngle', 'embossAngleGroup',
    'selectEdgeDetection', 'sliderEdgeStrength', 'valEdgeStrength', 'edgeStrengthGroup',
    'selectBinarize', 'sliderThreshold', 'valThreshold', 'manualThresholdGroup',
    'selectColorMap', 'mainCanvas', 'canvasWorkspace', 'emptyState', 'emptyUploadBtn',
    'toolSelect', 'toolRect', 'toolPolygon', 'toolPan', 'btnUndo', 'btnRedo',
    'btnDuplicate', 'btnDelete', 'toggleSplitBtn', 'toggleCrosshairBtn',
    'btnZoomOut', 'btnZoomIn', 'btnFitScreen', 'zoomLevelDisplay',
    'classesCountBadge', 'selectAlphabetPreset', 'optCustomAlphabet',
    'classSearchInput', 'characterGrid', 'activeClassIndicator',
    'selectedAnnCard', 'inspectorClassSelect', 'inspectorCoords', 'inspectorSize',
    'toggleLockSelected', 'btnDeleteSelectedAnn', 'annotationsList', 'annCountBadge',
    'btnClearAllAnn', 'thumbStrip', 'stripAddBtn', 'exportModal', 'closeExportModalBtn',
    'closeExportModalBtn2', 'shortcutsModal', 'closeShortcutsModalBtn', 'closeShortcutsModalBtn2',
    'btnExportYOLO', 'btnExportCrops', 'btnExportFullZip', 'btnExportImage',
    'btnExportVOC', 'btnExportCOCO', 'toastContainer'
  ];

  ids.forEach(id => {
    DOM[id] = document.getElementById(id);
  });
}

// Instantiate Labeling Engine
let labeler = null;

function initLabeler() {
  labeler = new LabelingCanvas(DOM.mainCanvas, {
    onSelectionChange: (selected) => updateSelectionUI(selected),
    onAnnotationsChange: (annotations) => {
      if (state.currentImageIndex >= 0 && state.images[state.currentImageIndex]) {
        state.images[state.currentImageIndex].annotations = annotations;
      }
      updateAnnotationsListUI();
      updateThumbnailsBadge();
    },
    onZoomChange: (scale) => {
      DOM.zoomLevelDisplay.textContent = `${Math.round(scale * 100)}%`;
    }
  });

  labeler.setClasses(state.classes);
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
}

function resizeCanvas() {
  const container = DOM.canvasWorkspace;
  DOM.mainCanvas.width = container.clientWidth;
  DOM.mainCanvas.height = container.clientHeight;
  if (labeler) labeler.render();
}

// Toast Notifications Helper
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = 'toast';
  const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : 'ℹ️');
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  DOM.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// =========================================================================
// Image Pipeline & Processing
// =========================================================================

let filterDebounceTimer = null;

function applyImageProcessing(immediate = false) {
  if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) return;

  const run = () => {
    const cur = state.images[state.currentImageIndex];
    if (!cur.originalCanvas) return;

    // 1. Geometric transforms (Rotation & Flips)
    const transformed = FilterEngine.transformCanvas(
      cur.originalCanvas,
      state.rotation,
      state.flipH,
      state.flipV
    );

    // 2. Filter pipeline
    const filtered = FilterEngine.applyPipeline(transformed, state.filters);

    state.processedCanvas = filtered;
    labeler.setImage(cur.originalCanvas, false);
    labeler.setProcessedCanvas(filtered);

    // Save to current image cache
    cur.filters = { ...state.filters };
    cur.rotation = state.rotation;
    cur.flipH = state.flipH;
    cur.flipV = state.flipV;
  };

  if (immediate) {
    run();
  } else {
    clearTimeout(filterDebounceTimer);
    filterDebounceTimer = setTimeout(run, 25);
  }
}

// =========================================================================
// Multi-Image Dataset Queue Management
// =========================================================================

function addImageFiles(files) {
  if (!files || files.length === 0) return;

  const validFiles = Array.from(files).filter(f => f.type.startsWith('image/'));
  if (validFiles.length === 0) {
    showToast('يرجى اختيار ملفات صور صالحة (PNG, JPG, WebP)', 'error');
    return;
  }

  let loadedCount = 0;
  validFiles.forEach((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const offCanvas = document.createElement('canvas');
        offCanvas.width = img.naturalWidth;
        offCanvas.height = img.naturalHeight;
        const ctx = offCanvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        const imgObj = {
          id: `img_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
          file: file,
          name: file.name,
          originalCanvas: offCanvas,
          width: img.naturalWidth,
          height: img.naturalHeight,
          annotations: [],
          filters: { ...state.filters },
          rotation: 0,
          flipH: false,
          flipV: false
        };

        state.images.push(imgObj);
        loadedCount++;

        if (loadedCount === validFiles.length) {
          updateThumbnailsUI();
          if (state.currentImageIndex === -1) {
            selectImage(0);
          }
          showToast(`تم تحميل ${loadedCount} صورة بنجاح`, 'success');
        }
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function selectImage(index) {
  if (index < 0 || index >= state.images.length) return;
  state.currentImageIndex = index;
  const cur = state.images[index];

  DOM.emptyState.style.display = 'none';

  // Restore cached filters & rotation for this image
  if (cur.filters) state.filters = { ...cur.filters };
  state.rotation = cur.rotation || 0;
  state.flipH = cur.flipH || false;
  state.flipV = cur.flipV || false;

  syncFilterControlsToState();

  // Apply processing & reset view to fit
  const transformed = FilterEngine.transformCanvas(cur.originalCanvas, state.rotation, state.flipH, state.flipV);
  const filtered = FilterEngine.applyPipeline(transformed, state.filters);

  state.processedCanvas = filtered;
  labeler.setImage(cur.originalCanvas, true);
  labeler.setProcessedCanvas(filtered);
  labeler.setAnnotations(cur.annotations || []);

  updateThumbnailsUI();
  updateImageCounter();
}

function updateImageCounter() {
  const total = state.images.length;
  const current = total === 0 ? 0 : state.currentImageIndex + 1;
  DOM.imageCounter.textContent = `${current} / ${total} ${state.lang === 'ar' ? 'صور' : 'images'}`;
}

function updateThumbnailsUI() {
  // Clear thumb items except add button
  const addBtn = DOM.stripAddBtn;
  DOM.thumbStrip.innerHTML = '';
  DOM.thumbStrip.appendChild(addBtn);

  state.images.forEach((img, idx) => {
    const card = document.createElement('div');
    card.className = `thumb-card ${idx === state.currentImageIndex ? 'active' : ''}`;
    card.title = img.name;

    const thumbCanvas = document.createElement('canvas');
    thumbCanvas.className = 'thumb-img';
    thumbCanvas.width = 85;
    thumbCanvas.height = 60;
    const ctx = thumbCanvas.getContext('2d');
    ctx.drawImage(img.originalCanvas, 0, 0, 85, 60);

    const badge = document.createElement('span');
    badge.className = 'thumb-badge';
    badge.textContent = `${img.annotations ? img.annotations.length : 0}`;

    card.appendChild(thumbCanvas);
    card.appendChild(badge);

    card.addEventListener('click', () => selectImage(idx));
    DOM.thumbStrip.insertBefore(card, addBtn);
  });
}

function updateThumbnailsBadge() {
  const cards = DOM.thumbStrip.querySelectorAll('.thumb-card');
  if (cards[state.currentImageIndex]) {
    const badge = cards[state.currentImageIndex].querySelector('.thumb-badge');
    if (badge && state.images[state.currentImageIndex]) {
      badge.textContent = `${state.images[state.currentImageIndex].annotations.length}`;
    }
  }
}

// =========================================================================
// Classes & Virtual Character Grid Management
// =========================================================================

function setAlphabetPreset(presetKey) {
  state.activePreset = presetKey;
  if (presetKey === 'nabataean') {
    state.classes = [...NABATAEAN_CLASSES];
  } else if (presetKey === 'aramaic') {
    state.classes = [...ARAMAIC_CLASSES];
  } else if (presetKey === 'arabic') {
    state.classes = [...ARABIC_CLASSES];
  } else if (presetKey === 'custom' && state.customClasses) {
    state.classes = [...state.customClasses];
  }

  state.activeClassId = state.classes.length > 0 ? state.classes[0].id : 0;
  labeler.setClasses(state.classes);
  labeler.setActiveClass(state.activeClassId);

  renderCharacterGrid();
  updateClassDropdowns();
  updateActiveClassIndicator();
}

function renderCharacterGrid() {
  const grid = DOM.characterGrid;
  grid.innerHTML = '';

  const query = state.searchQuery.toLowerCase().trim();
  const filtered = state.classes.filter(c => {
    if (!query) return true;
    return (
      (c.char && c.char.toLowerCase().includes(query)) ||
      (c.name_ar && c.name_ar.toLowerCase().includes(query)) ||
      (c.name_en && c.name_en.toLowerCase().includes(query)) ||
      `${c.id}` === query
    );
  });

  DOM.classesCountBadge.textContent = `${state.classes.length} ${state.lang === 'ar' ? 'فئة' : 'classes'}`;

  filtered.forEach(cls => {
    const card = document.createElement('div');
    card.className = `char-card ${cls.id === state.activeClassId ? 'active' : ''}`;
    card.dataset.id = cls.id;

    const idSpan = document.createElement('span');
    idSpan.className = 'char-badge-id';
    idSpan.textContent = cls.id;

    const colorDot = document.createElement('span');
    colorDot.className = 'char-color-dot';
    colorDot.style.backgroundColor = getClassColor(cls.id);

    const glyph = document.createElement('div');
    glyph.className = 'char-glyph';
    glyph.textContent = cls.char || `${cls.id}`;

    const title = document.createElement('div');
    title.className = 'char-title';
    title.textContent = state.lang === 'ar' ? (cls.name_ar || cls.char) : (cls.name_en || cls.char);

    card.appendChild(idSpan);
    card.appendChild(colorDot);
    card.appendChild(glyph);
    card.appendChild(title);

    card.addEventListener('click', () => {
      state.activeClassId = cls.id;
      labeler.setActiveClass(cls.id);
      renderCharacterGrid();
      updateActiveClassIndicator();
    });

    grid.appendChild(card);
  });
}

function updateActiveClassIndicator() {
  const cls = state.classes.find(c => c.id === state.activeClassId);
  if (cls) {
    const name = state.lang === 'ar' ? (cls.name_ar || cls.char) : (cls.name_en || cls.char);
    DOM.activeClassIndicator.textContent = `${cls.char} (${cls.id}) - ${name}`;
  }
}

function updateClassDropdowns() {
  const select = DOM.inspectorClassSelect;
  select.innerHTML = '';
  state.classes.forEach(cls => {
    const opt = document.createElement('option');
    opt.value = cls.id;
    const name = state.lang === 'ar' ? (cls.name_ar || cls.char) : (cls.name_en || cls.char);
    opt.textContent = `${cls.char} [${cls.id}] - ${name}`;
    select.appendChild(opt);
  });
}

// Handle Custom Classes File Import (.txt, .json, .yaml)
function handleImportClassesFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    const parsed = parseClassesFile(content, file.name);

    if (parsed.length === 0) {
      showToast('تعذر استخراج فئات من الملف المختار', 'error');
      return;
    }

    state.customClasses = parsed;
    DOM.optCustomAlphabet.style.display = 'block';
    DOM.selectAlphabetPreset.value = 'custom';
    setAlphabetPreset('custom');

    showToast(`تم استيراد ${parsed.length} فئة وحرف بنجاح من ${file.name}`, 'success');
  };
  reader.readAsText(file);
}

// =========================================================================
// Annotations & Selection Inspector UI
// =========================================================================

function updateSelectionUI(selected) {
  if (!selected) {
    DOM.selectedAnnCard.style.display = 'none';
    return;
  }

  DOM.selectedAnnCard.style.display = 'flex';
  DOM.inspectorClassSelect.value = selected.classId;
  DOM.inspectorCoords.textContent = `X: ${selected.x}, Y: ${selected.y}`;
  DOM.inspectorSize.textContent = `W: ${selected.width}, H: ${selected.height}`;
  DOM.toggleLockSelected.checked = !!selected.locked;

  // Highlight active in characters grid
  state.activeClassId = selected.classId;
  renderCharacterGrid();
  updateActiveClassIndicator();
}

function updateAnnotationsListUI() {
  const list = DOM.annotationsList;
  list.innerHTML = '';

  const count = labeler.annotations.length;
  DOM.annCountBadge.textContent = `${count} ${state.lang === 'ar' ? 'عناصر' : 'items'}`;

  labeler.annotations.forEach((ann, idx) => {
    const item = document.createElement('div');
    item.className = `ann-item ${labeler.selectedAnnotation && labeler.selectedAnnotation.id === ann.id ? 'active' : ''}`;

    const info = document.createElement('div');
    info.className = 'ann-info';

    const colorBar = document.createElement('div');
    colorBar.className = 'ann-color-bar';
    colorBar.style.backgroundColor = getClassColor(ann.classId);

    const title = document.createElement('span');
    title.textContent = `${ann.char || ''} ${ann.className || `Class ${ann.classId}`} (#${idx + 1})`;

    info.appendChild(colorBar);
    info.appendChild(title);

    const actions = document.createElement('div');
    actions.className = 'ann-item-actions';

    // Visibility toggle
    const visBtn = document.createElement('button');
    visBtn.className = 'btn btn-icon-only btn-sm';
    visBtn.textContent = ann.visible !== false ? '👁️' : '🕶️';
    visBtn.title = 'إخفاء / إظهار';
    visBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      ann.visible = !ann.visible;
      labeler.render();
      updateAnnotationsListUI();
    });

    // Delete btn
    const delBtn = document.createElement('button');
    delBtn.className = 'btn btn-icon-only btn-sm';
    delBtn.textContent = '🗑️';
    delBtn.title = 'حذف';
    delBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      labeler.annotations = labeler.annotations.filter(a => a.id !== ann.id);
      if (labeler.selectedAnnotation && labeler.selectedAnnotation.id === ann.id) {
        labeler.selectAnnotation(null);
      }
      labeler.saveHistory('Delete');
      labeler.onAnnotationsChange(labeler.annotations);
      labeler.render();
    });

    actions.appendChild(visBtn);
    actions.appendChild(delBtn);

    item.appendChild(info);
    item.appendChild(actions);

    item.addEventListener('click', () => {
      labeler.selectAnnotation(ann);
      updateAnnotationsListUI();
    });

    list.appendChild(item);
  });
}

// =========================================================================
// Controls & Filter Sliders Binding
// =========================================================================

function syncFilterControlsToState() {
  const f = state.filters;
  DOM.sliderBrightness.value = f.brightness;
  DOM.valBrightness.textContent = f.brightness;

  DOM.sliderContrast.value = f.contrast;
  DOM.valContrast.textContent = f.contrast;

  DOM.sliderExposure.value = f.exposure;
  DOM.valExposure.textContent = f.exposure;

  DOM.sliderGamma.value = f.gamma;
  DOM.valGamma.textContent = f.gamma;

  DOM.sliderSaturation.value = f.saturation;
  DOM.valSaturation.textContent = f.saturation;

  DOM.toggleInvert.checked = f.invert;
  DOM.toggleGrayscale.checked = f.grayscale;
  DOM.toggleEqualize.checked = f.equalizeHist;

  DOM.sliderSharpen.value = f.sharpen;
  DOM.valSharpen.textContent = f.sharpen;

  DOM.sliderMedian.value = f.medianDenoise;
  DOM.valMedian.textContent = f.medianDenoise;

  DOM.toggleEmboss.checked = f.emboss;
  DOM.embossAngleGroup.style.display = f.emboss ? 'flex' : 'none';
  DOM.sliderEmbossAngle.value = f.embossAngle;
  DOM.valEmbossAngle.textContent = `${f.embossAngle}°`;

  DOM.selectEdgeDetection.value = f.edgeDetection;
  DOM.edgeStrengthGroup.style.display = f.edgeDetection !== 'none' ? 'flex' : 'none';
  DOM.sliderEdgeStrength.value = f.edgeStrength;
  DOM.valEdgeStrength.textContent = f.edgeStrength;

  DOM.selectBinarize.value = f.binarize;
  DOM.manualThresholdGroup.style.display = f.binarize === 'global' ? 'flex' : 'none';
  DOM.sliderThreshold.value = f.thresholdVal;
  DOM.valThreshold.textContent = f.thresholdVal;

  DOM.selectColorMap.value = f.colorMap;

  // Rotation
  DOM.sliderRotation.value = state.rotation;
  DOM.valRotation.textContent = `${state.rotation}°`;
}

function resetAllFilters() {
  state.filters = {
    brightness: 0,
    contrast: 0,
    exposure: 0,
    gamma: 1.0,
    saturation: 0,
    invert: false,
    grayscale: false,
    equalizeHist: false,
    sharpen: 0,
    medianDenoise: 0,
    blur: 0,
    emboss: false,
    embossAngle: 45,
    embossStrength: 1.5,
    edgeDetection: 'none',
    edgeStrength: 1.0,
    binarize: 'none',
    thresholdVal: 128,
    adaptiveWindow: 15,
    colorMap: 'none'
  };
  syncFilterControlsToState();
  applyImageProcessing(true);
  showToast('تمت إعادة ضبط جميع الفلاتر', 'info');
}

function applyPreset(presetName) {
  resetAllFilters();
  switch (presetName) {
    case 'stone_boost': // Boost relief & contrast of carved lines
      state.filters.equalizeHist = true;
      state.filters.sharpen = 1.6;
      state.filters.contrast = 0.35;
      state.filters.medianDenoise = 1;
      break;

    case 'dark_invert': // Invert dark basalt/granite stones
      state.filters.invert = true;
      state.filters.grayscale = true;
      state.filters.contrast = 0.45;
      state.filters.gamma = 0.85;
      state.filters.sharpen = 1.2;
      break;

    case 'deep_contrast': // High-contrast shadows in grooves
      state.filters.contrast = 0.65;
      state.filters.brightness = 0.05;
      state.filters.sharpen = 1.8;
      state.filters.equalizeHist = true;
      break;

    case 'otsu_clean': // Automatic clean binarization
      state.filters.binarize = 'otsu';
      state.filters.medianDenoise = 1;
      break;

    case 'sobel_edges': // Edge detection for carved incisions
      state.filters.edgeDetection = 'sobel';
      state.filters.edgeStrength = 1.5;
      state.filters.invert = true;
      break;

    case 'sandstone_map': // Thermal / sandstone false color map
      state.filters.colorMap = 'sandstone';
      state.filters.contrast = 0.3;
      state.filters.sharpen = 1.2;
      break;
  }

  syncFilterControlsToState();
  applyImageProcessing(true);
  showToast(`تم تطبيق قالب "${presetName}"`, 'success');
}

// =========================================================================
// Event Listeners Setup
// =========================================================================

function setupEventListeners() {
  // Navigation & Uploads
  DOM.prevImageBtn.addEventListener('click', () => {
    if (state.currentImageIndex > 0) selectImage(state.currentImageIndex - 1);
  });
  DOM.nextImageBtn.addEventListener('click', () => {
    if (state.currentImageIndex < state.images.length - 1) selectImage(state.currentImageIndex + 1);
  });

  DOM.uploadImageBtn.addEventListener('click', () => DOM.imageFileInput.click());
  DOM.emptyUploadBtn.addEventListener('click', () => DOM.imageFileInput.click());
  DOM.stripAddBtn.addEventListener('click', () => DOM.imageFileInput.click());

  DOM.imageFileInput.addEventListener('change', (e) => {
    addImageFiles(e.target.files);
    e.target.value = '';
  });

  // Drag and Drop Images onto Canvas
  const dropArea = DOM.canvasWorkspace;
  dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.style.border = '2px dashed var(--accent-cyan)';
  });
  dropArea.addEventListener('dragleave', () => {
    dropArea.style.border = 'none';
  });
  dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.style.border = 'none';
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addImageFiles(e.dataTransfer.files);
    }
  });

  // Import Classes File
  DOM.importClassesBtn.addEventListener('click', () => DOM.classesFileInput.click());
  DOM.classesFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleImportClassesFile(e.target.files[0]);
    }
    e.target.value = '';
  });

  // Import YOLO txt
  DOM.importYoloBtn.addEventListener('click', () => DOM.yoloFileInput.click());
  DOM.yoloFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) {
          showToast('يرجى تحميل صورة أولاً لإسقاط توسيمات YOLO عليها', 'error');
          return;
        }
        const img = state.images[state.currentImageIndex];
        const annotations = DatasetExporter.fromYOLO(
          evt.target.result,
          labeler.processedCanvas.width,
          labeler.processedCanvas.height,
          state.classes
        );
        labeler.setAnnotations(annotations);
        showToast(`تم استيراد ${annotations.length} صندوق توسيم من ${file.name}`, 'success');
      };
      reader.readAsText(file);
    }
    e.target.value = '';
  });

  // Alphabet Preset Switcher
  DOM.selectAlphabetPreset.addEventListener('change', (e) => {
    setAlphabetPreset(e.target.value);
  });

  // Search Filter
  DOM.classSearchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    renderCharacterGrid();
  });

  // Filter Presets Chips
  document.querySelectorAll('.chip-btn[data-preset]').forEach(btn => {
    btn.addEventListener('click', () => applyPreset(btn.dataset.preset));
  });

  // Reset Filters
  DOM.resetFiltersBtn.addEventListener('click', resetAllFilters);

  // Rotation Controls
  DOM.sliderRotation.addEventListener('input', (e) => {
    state.rotation = parseInt(e.target.value, 10);
    DOM.valRotation.textContent = `${state.rotation}°`;
    applyImageProcessing();
  });

  DOM.resetRotationBtn.addEventListener('click', () => {
    state.rotation = 0;
    state.flipH = false;
    state.flipV = false;
    DOM.sliderRotation.value = 0;
    DOM.valRotation.textContent = '0°';
    applyImageProcessing(true);
  });

  DOM.btnRotateCW.addEventListener('click', () => {
    state.rotation = (state.rotation + 90) % 360;
    if (state.rotation > 180) state.rotation -= 360;
    DOM.sliderRotation.value = state.rotation;
    DOM.valRotation.textContent = `${state.rotation}°`;
    applyImageProcessing(true);
  });

  DOM.btnRotateCCW.addEventListener('click', () => {
    state.rotation = (state.rotation - 90) % 360;
    if (state.rotation < -180) state.rotation += 360;
    DOM.sliderRotation.value = state.rotation;
    DOM.valRotation.textContent = `${state.rotation}°`;
    applyImageProcessing(true);
  });

  DOM.btnFlipH.addEventListener('click', () => {
    state.flipH = !state.flipH;
    applyImageProcessing(true);
  });

  DOM.btnFlipV.addEventListener('click', () => {
    state.flipV = !state.flipV;
    applyImageProcessing(true);
  });

  // Filter Sliders Bindings
  const bindSlider = (sliderEl, valEl, propKey, isInt = false) => {
    sliderEl.addEventListener('input', (e) => {
      const val = isInt ? parseInt(e.target.value, 10) : parseFloat(e.target.value);
      state.filters[propKey] = val;
      valEl.textContent = val;
      applyImageProcessing();
    });
  };

  bindSlider(DOM.sliderBrightness, DOM.valBrightness, 'brightness');
  bindSlider(DOM.sliderContrast, DOM.valContrast, 'contrast');
  bindSlider(DOM.sliderExposure, DOM.valExposure, 'exposure');
  bindSlider(DOM.sliderGamma, DOM.valGamma, 'gamma');
  bindSlider(DOM.sliderSaturation, DOM.valSaturation, 'saturation');
  bindSlider(DOM.sliderSharpen, DOM.valSharpen, 'sharpen');
  bindSlider(DOM.sliderMedian, DOM.valMedian, 'medianDenoise', true);
  bindSlider(DOM.sliderEmbossAngle, DOM.valEmbossAngle, 'embossAngle', true);
  bindSlider(DOM.sliderEdgeStrength, DOM.valEdgeStrength, 'edgeStrength');
  bindSlider(DOM.sliderThreshold, DOM.valThreshold, 'thresholdVal', true);

  // Toggles
  DOM.toggleInvert.addEventListener('change', (e) => {
    state.filters.invert = e.target.checked;
    applyImageProcessing(true);
  });

  DOM.toggleGrayscale.addEventListener('change', (e) => {
    state.filters.grayscale = e.target.checked;
    applyImageProcessing(true);
  });

  DOM.toggleEqualize.addEventListener('change', (e) => {
    state.filters.equalizeHist = e.target.checked;
    applyImageProcessing(true);
  });

  DOM.toggleEmboss.addEventListener('change', (e) => {
    state.filters.emboss = e.target.checked;
    DOM.embossAngleGroup.style.display = e.target.checked ? 'flex' : 'none';
    applyImageProcessing(true);
  });

  DOM.selectEdgeDetection.addEventListener('change', (e) => {
    state.filters.edgeDetection = e.target.value;
    DOM.edgeStrengthGroup.style.display = e.target.value !== 'none' ? 'flex' : 'none';
    applyImageProcessing(true);
  });

  DOM.selectBinarize.addEventListener('change', (e) => {
    state.filters.binarize = e.target.value;
    DOM.manualThresholdGroup.style.display = e.target.value === 'global' ? 'flex' : 'none';
    applyImageProcessing(true);
  });

  DOM.selectColorMap.addEventListener('change', (e) => {
    state.filters.colorMap = e.target.value;
    applyImageProcessing(true);
  });

  // Tools Selection
  const selectTool = (toolName, activeBtn) => {
    [DOM.toolSelect, DOM.toolRect, DOM.toolPolygon, DOM.toolPan].forEach(b => b.classList.remove('active'));
    activeBtn.classList.add('active');
    labeler.setTool(toolName);
  };

  DOM.toolSelect.addEventListener('click', () => selectTool('select', DOM.toolSelect));
  DOM.toolRect.addEventListener('click', () => selectTool('rect', DOM.toolRect));
  DOM.toolPolygon.addEventListener('click', () => selectTool('polygon', DOM.toolPolygon));
  DOM.toolPan.addEventListener('click', () => selectTool('pan', DOM.toolPan));

  // Undo / Redo / Duplicate / Delete
  DOM.btnUndo.addEventListener('click', () => labeler.undo());
  DOM.btnRedo.addEventListener('click', () => labeler.redo());
  DOM.btnDuplicate.addEventListener('click', () => labeler.duplicateSelected());
  DOM.btnDelete.addEventListener('click', () => labeler.deleteSelected());
  DOM.btnDeleteSelectedAnn.addEventListener('click', () => labeler.deleteSelected());
  DOM.btnClearAllAnn.addEventListener('click', () => {
    if (confirm(state.lang === 'ar' ? 'هل أنت متأكد من مسح جميع التوسيمات الحالية؟' : 'Clear all annotations?')) {
      labeler.clearAnnotations();
    }
  });

  // Inspector bindings
  DOM.inspectorClassSelect.addEventListener('change', (e) => {
    const classId = parseInt(e.target.value, 10);
    labeler.setActiveClass(classId);
  });

  DOM.toggleLockSelected.addEventListener('change', (e) => {
    if (labeler.selectedAnnotation) {
      labeler.selectedAnnotation.locked = e.target.checked;
    }
  });

  // Split View & Crosshair
  DOM.toggleSplitBtn.addEventListener('click', () => {
    state.splitView = !state.splitView;
    DOM.toggleSplitBtn.classList.toggle('active', state.splitView);
    labeler.setSplitView(state.splitView);
  });

  DOM.toggleCrosshairBtn.addEventListener('click', () => {
    labeler.showCrosshair = !labeler.showCrosshair;
    DOM.toggleCrosshairBtn.classList.toggle('active', labeler.showCrosshair);
    labeler.render();
  });

  // Zoom controls
  DOM.btnZoomIn.addEventListener('click', () => labeler.zoom(1.25));
  DOM.btnZoomOut.addEventListener('click', () => labeler.zoom(0.8));
  DOM.btnFitScreen.addEventListener('click', () => labeler.fitToScreen());

  // Modals & Popups
  DOM.openExportModalBtn.addEventListener('click', () => DOM.exportModal.classList.add('show'));
  DOM.closeExportModalBtn.addEventListener('click', () => DOM.exportModal.classList.remove('show'));
  DOM.closeExportModalBtn2.addEventListener('click', () => DOM.exportModal.classList.remove('show'));

  DOM.shortcutsModalBtn.addEventListener('click', () => DOM.shortcutsModal.classList.add('show'));
  DOM.closeShortcutsModalBtn.addEventListener('click', () => DOM.shortcutsModal.classList.remove('show'));
  DOM.closeShortcutsModalBtn2.addEventListener('click', () => DOM.shortcutsModal.classList.remove('show'));

  // Global Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

    if (e.ctrlKey || e.metaKey) {
      if (e.key.toLowerCase() === 'z') {
        e.preventDefault();
        labeler.undo();
      } else if (e.key.toLowerCase() === 'y') {
        e.preventDefault();
        labeler.redo();
      } else if (e.key.toLowerCase() === 'd') {
        e.preventDefault();
        labeler.duplicateSelected();
      }
      return;
    }

    switch (e.key.toLowerCase()) {
      case 'r': selectTool('rect', DOM.toolRect); break;
      case 'v': selectTool('select', DOM.toolSelect); break;
      case 'p': selectTool('polygon', DOM.toolPolygon); break;
      case 'h': selectTool('pan', DOM.toolPan); break;
      case 'f': labeler.fitToScreen(); break;
      case 's': DOM.toggleSplitBtn.click(); break;
      case 'c': DOM.toggleCrosshairBtn.click(); break;
      case 'delete':
      case 'backspace':
        labeler.deleteSelected();
        break;
      case 'a':
      case 'arrowleft':
        if (state.lang === 'ar') {
          if (state.currentImageIndex < state.images.length - 1) selectImage(state.currentImageIndex + 1);
        } else {
          if (state.currentImageIndex > 0) selectImage(state.currentImageIndex - 1);
        }
        break;
      case 'd':
      case 'arrowright':
        if (state.lang === 'ar') {
          if (state.currentImageIndex > 0) selectImage(state.currentImageIndex - 1);
        } else {
          if (state.currentImageIndex < state.images.length - 1) selectImage(state.currentImageIndex + 1);
        }
        break;
    }
  });

  // Language & Theme Switchers
  DOM.langToggleBtn.addEventListener('click', toggleLanguage);
  DOM.themeToggleBtn.addEventListener('click', toggleTheme);

  // Setup Exporters
  setupExportActions();
}

// =========================================================================
// Exporters Handler
// =========================================================================

function setupExportActions() {
  // 1. YOLO Single/Batch Export
  DOM.btnExportYOLO.addEventListener('click', () => {
    if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) {
      showToast('لا توجد صورة محددة للتصدير', 'error');
      return;
    }
    const cur = state.images[state.currentImageIndex];
    const yoloText = DatasetExporter.toYOLO(cur.annotations, labeler.processedCanvas.width, labeler.processedCanvas.height);
    const baseName = cur.name.replace(/\.[^/.]+$/, '');
    DatasetExporter.downloadText(yoloText, `${baseName}.txt`);

    // Also download classes.txt and data.yaml
    const classesText = state.classes.map(c => c.name_en || c.name_ar || c.char).join('\n');
    DatasetExporter.downloadText(classesText, 'classes.txt');

    const yaml = DatasetExporter.toYOLOyaml(state.classes);
    DatasetExporter.downloadText(yaml, 'data.yaml');

    showToast('تم تصدير ملفات YOLO بنجاح', 'success');
  });

  // 2. Cropped Character Patches ZIP Export
  DOM.btnExportCrops.addEventListener('click', async () => {
    if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) {
      showToast('لا توجد صورة محددة لقص التوسيمات منها', 'error');
      return;
    }
    const cur = state.images[state.currentImageIndex];
    if (cur.annotations.length === 0) {
      showToast('لا توجد صناديق توسيم في هذه الصورة لقصها', 'error');
      return;
    }

    if (typeof JSZip === 'undefined') {
      showToast('جاري تحميل مكتبة ZIP، يرجى الانتظار ثانية...', 'info');
      return;
    }

    const zip = new JSZip();
    const crops = DatasetExporter.cropAnnotations(labeler.processedCanvas, cur.annotations, 4);

    crops.forEach((crop) => {
      const cls = state.classes.find(c => c.id === crop.classId) || { name_en: `class_${crop.classId}` };
      const folderName = `${crop.classId}_${cls.name_en || cls.name_ar || crop.char}`;
      const imgDataUrl = crop.canvas.toDataURL('image/png').split(',')[1];
      zip.folder(folderName).file(`crop_${crop.index}_${crop.classId}.png`, imgDataUrl, { base64: true });
    });

    const content = await zip.generateAsync({ type: 'blob' });
    DatasetExporter.downloadBlob(content, `cropped_characters_${Date.now()}.zip`);
    showToast(`تم تصدير ${crops.length} مقتطف حرف في ملف ZIP`, 'success');
  });

  // 3. Full Dataset ZIP Export (Images + Labels + Crops + Configs)
  DOM.btnExportFullZip.addEventListener('click', async () => {
    if (state.images.length === 0) {
      showToast('لا توجد صور في مجموعة البيانات لتصديرها', 'error');
      return;
    }

    if (typeof JSZip === 'undefined') {
      showToast('مكتبة JSZip غير متوفرة حالياً', 'error');
      return;
    }

    showToast('جاري تجهيز حزمة Dataset الكاملة...', 'info');
    const zip = new JSZip();
    const imgFolder = zip.folder('images/train');
    const labelFolder = zip.folder('labels/train');

    for (let i = 0; i < state.images.length; i++) {
      const imgObj = state.images[i];
      const baseName = imgObj.name.replace(/\.[^/.]+$/, '');

      // Render transformed and filtered canvas for this image
      const transformed = FilterEngine.transformCanvas(imgObj.originalCanvas, imgObj.rotation || 0, imgObj.flipH, imgObj.flipV);
      const filtered = FilterEngine.applyPipeline(transformed, imgObj.filters || state.filters);

      const imgDataUrl = filtered.toDataURL('image/jpeg', 0.95).split(',')[1];
      imgFolder.file(`${baseName}.jpg`, imgDataUrl, { base64: true });

      // YOLO label
      const yoloText = DatasetExporter.toYOLO(imgObj.annotations || [], filtered.width, filtered.height);
      labelFolder.file(`${baseName}.txt`, yoloText);
    }

    // Config files
    const classesText = state.classes.map(c => c.name_en || c.name_ar || c.char).join('\n');
    zip.file('classes.txt', classesText);

    const yaml = DatasetExporter.toYOLOyaml(state.classes);
    zip.file('data.yaml', yaml);

    const blob = await zip.generateAsync({ type: 'blob' });
    DatasetExporter.downloadBlob(blob, `yolo_dataset_${Date.now()}.zip`);
    showToast('تم تصدير حزمة Dataset الكاملة بنجاح!', 'success');
  });

  // 4. Export Processed Image (Full Resolution)
  DOM.btnExportImage.addEventListener('click', () => {
    if (!labeler.processedCanvas) {
      showToast('لا توجد صورة معالجة لحفظها', 'error');
      return;
    }
    const cur = state.images[state.currentImageIndex];
    const baseName = cur ? cur.name.replace(/\.[^/.]+$/, '') : 'enhanced_image';
    labeler.processedCanvas.toBlob((blob) => {
      DatasetExporter.downloadBlob(blob, `${baseName}_enhanced.png`);
      showToast('تم حفظ الصورة المعالجة بدقة عالية', 'success');
    }, 'image/png');
  });

  // 5. Pascal VOC XML Export
  DOM.btnExportVOC.addEventListener('click', () => {
    if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) return;
    const cur = state.images[state.currentImageIndex];
    const xml = DatasetExporter.toPascalVOC(
      cur.annotations,
      cur.name,
      labeler.processedCanvas.width,
      labeler.processedCanvas.height,
      state.classes
    );
    const baseName = cur.name.replace(/\.[^/.]+$/, '');
    DatasetExporter.downloadText(xml, `${baseName}.xml`, 'application/xml');
    showToast('تم تصدير Pascal VOC XML', 'success');
  });

  // 6. COCO JSON Export
  DOM.btnExportCOCO.addEventListener('click', () => {
    if (state.images.length === 0) return;
    const items = state.images.map(img => ({
      filename: img.name,
      width: img.width,
      height: img.height,
      annotations: img.annotations || []
    }));
    const json = DatasetExporter.toCOCO(items, state.classes);
    DatasetExporter.downloadText(json, `coco_annotations_${Date.now()}.json`, 'application/json');
    showToast('تم تصدير COCO JSON بنجاح', 'success');
  });
}

// =========================================================================
// Localization & Themes
// =========================================================================

function toggleLanguage() {
  state.lang = state.lang === 'ar' ? 'en' : 'ar';
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';

  // Update UI texts
  DOM.appTitle.textContent = state.lang === 'ar' ? 'استوديو معالجة الصور والتوسيم' : 'Inscription Image & Labeling Studio';
  DOM.txtImportClasses.textContent = state.lang === 'ar' ? 'استيراد ملف الحروف' : 'Import Classes File';
  DOM.txtUploadImage.textContent = state.lang === 'ar' ? 'رفع صور' : 'Upload Images';
  DOM.txtImportYolo.textContent = state.lang === 'ar' ? 'استيراد YOLO' : 'Import YOLO';
  DOM.txtExportBtn.textContent = state.lang === 'ar' ? 'تصدير البيانات' : 'Export Data';

  updateImageCounter();
  renderCharacterGrid();
  updateClassDropdowns();
  updateActiveClassIndicator();
  updateAnnotationsListUI();
}

function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  labeler.render();
}

// Load default sample if available or initialize studio
async function loadDefaultPresetData() {
  setAlphabetPreset('nabataean');

  // Try to preload Untitled.jpg if it exists in the root folder as a nice starter sample
  try {
    const resp = await fetch('Untitled.jpg');
    if (resp.ok) {
      const blob = await resp.blob();
      const file = new File([blob], 'nabataean_sample.jpg', { type: 'image/jpeg' });
      addImageFiles([file]);
    }
  } catch (e) {
    console.log('No default image preload');
  }
}

// Bootstrap Application
function startStudio() {
  try {
    initDOM();
    initLabeler();
    setupEventListeners();
    loadDefaultPresetData();

    // Global hooks for direct trigger safety
    window.studioState = state;
    window.labelerInstance = labeler;
    window.addImageFiles = addImageFiles;
    window.handleImportClassesFile = handleImportClassesFile;
    window.handleImportYolo = (file) => {
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
        if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) {
          showToast('يرجى تحميل صورة أولاً لإسقاط توسيمات YOLO عليها', 'error');
          return;
        }
        const annotations = DatasetExporter.fromYOLO(
          evt.target.result,
          labeler.processedCanvas.width,
          labeler.processedCanvas.height,
          state.classes
        );
        labeler.setAnnotations(annotations);
        showToast(`تم استيراد ${annotations.length} صندوق توسيم من ${file.name}`, 'success');
      };
      reader.readAsText(file);
    };
    window.applyPreset = applyPreset;
    window.selectAlphabetPreset = setAlphabetPreset;

    console.log('Inscription & Image Studio initialized successfully');
  } catch (err) {
    console.error('Error starting studio:', err);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startStudio);
} else {
  startStudio();
}

