/**
 * labeler.js - Interactive Annotation Canvas Engine
 */

import { getClassColor } from './presets.js';

export class LabelingCanvas {
  constructor(canvasElement, options = {}) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');

    // Images
    this.originalImage = null;   // Original HTMLImageElement or Canvas
    this.processedCanvas = null; // Filtered & Rotated Offscreen Canvas

    // Transform State
    this.scale = 1;
    this.panX = 0;
    this.panY = 0;
    this.minScale = 0.05;
    this.maxScale = 30;

    // Tool State: 'select', 'rect', 'polygon', 'pan', 'magic'
    this.activeTool = 'rect';
    this.activeClassId = 0;
    this.classes = [];

    // Annotations Array
    this.annotations = [];
    this.selectedAnnotation = null;
    this.hoveredAnnotation = null;
    this.hoveredHandle = null;

    // Drawing / Interaction State
    this.isMouseDown = false;
    this.isPanning = false;
    this.isDrawingRect = false;
    this.isDraggingAnnotation = false;
    this.isResizingHandle = false;

    this.dragStartX = 0;
    this.dragStartY = 0;
    this.initialAnnState = null;
    this.currentRect = null;

    // Polygon in-progress
    this.currentPolygonPoints = [];

    // Split-view comparison state
    this.splitView = false;
    this.splitPos = 0.5; // 0 to 1
    this.isDraggingSplit = false;

    // Crosshair & cursor
    this.cursorX = 0;
    this.cursorY = 0;
    this.showCrosshair = true;

    // History for Undo/Redo
    this.history = [];
    this.historyIndex = -1;

    // Callbacks
    this.onSelectionChange = options.onSelectionChange || (() => {});
    this.onAnnotationsChange = options.onAnnotationsChange || (() => {});
    this.onZoomChange = options.onZoomChange || (() => {});

    this.initEventListeners();
  }

  setClasses(classes) {
    this.classes = classes;
    this.render();
  }

  setImage(imageOrCanvas, resetView = true) {
    this.originalImage = imageOrCanvas;
    this.processedCanvas = imageOrCanvas;
    if (resetView) {
      this.fitToScreen();
      this.clearHistory();
    }
    this.render();
  }

  setProcessedCanvas(canvas) {
    this.processedCanvas = canvas;
    this.render();
  }

  setTool(toolName) {
    this.activeTool = toolName;
    if (this.currentPolygonPoints.length > 0 && toolName !== 'polygon') {
      this.currentPolygonPoints = [];
    }
    this.render();
  }

  setActiveClass(classId) {
    this.activeClassId = classId;
    if (this.selectedAnnotation && !this.selectedAnnotation.locked) {
      this.selectedAnnotation.classId = classId;
      const cls = this.classes.find(c => c.id === classId);
      if (cls) {
        this.selectedAnnotation.className = cls.name_ar || cls.name_en || cls.char;
        this.selectedAnnotation.char = cls.char;
      }
      this.saveHistory('Change Class');
      this.onAnnotationsChange(this.annotations);
      this.render();
    }
  }

  setSplitView(enabled) {
    this.splitView = enabled;
    this.render();
  }

  fitToScreen() {
    if (!this.processedCanvas) return;
    const cw = this.canvas.width;
    const ch = this.canvas.height;
    const iw = this.processedCanvas.width;
    const ih = this.processedCanvas.height;

    const scaleX = (cw * 0.88) / iw;
    const scaleY = (ch * 0.88) / ih;
    this.scale = Math.min(scaleX, scaleY, 1.5);

    this.panX = (cw - iw * this.scale) / 2;
    this.panY = (ch - ih * this.scale) / 2;

    this.onZoomChange(this.scale);
    this.render();
  }

  zoom(factor, clientCenterX = null, clientCenterY = null) {
    const prevScale = this.scale;
    let newScale = this.scale * factor;
    newScale = Math.max(this.minScale, Math.min(this.maxScale, newScale));

    const cx = clientCenterX !== null ? clientCenterX : this.canvas.width / 2;
    const cy = clientCenterY !== null ? clientCenterY : this.canvas.height / 2;

    // Zoom towards center point
    const imgX = (cx - this.panX) / prevScale;
    const imgY = (cy - this.panY) / prevScale;

    this.scale = newScale;
    this.panX = cx - imgX * this.scale;
    this.panY = cy - imgY * this.scale;

    this.onZoomChange(this.scale);
    this.render();
  }

  // Coordinate transforms
  screenToImage(sx, sy) {
    return {
      x: (sx - this.panX) / this.scale,
      y: (sy - this.panY) / this.scale
    };
  }

  imageToScreen(ix, iy) {
    return {
      x: ix * this.scale + this.panX,
      y: iy * this.scale + this.panY
    };
  }

  getCanvasCoords(e) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = rect.width > 0 ? (this.canvas.width / rect.width) : 1;
    const scaleY = rect.height > 0 ? (this.canvas.height / rect.height) : 1;
    return {
      sx: (e.clientX - rect.left) * scaleX,
      sy: (e.clientY - rect.top) * scaleY
    };
  }

  initEventListeners() {
    const c = this.canvas;

    c.addEventListener('wheel', (e) => {
      e.preventDefault();
      const { sx: mx, sy: my } = this.getCanvasCoords(e);
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      this.zoom(factor, mx, my);
    }, { passive: false });

    c.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    window.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    c.addEventListener('dblclick', (e) => this.handleDoubleClick(e));
    c.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  handleMouseDown(e) {
    const { sx, sy } = this.getCanvasCoords(e);
    const imgPt = this.screenToImage(sx, sy);

    this.cursorX = sx;
    this.cursorY = sy;
    this.isMouseDown = true;

    // Middle click or Space + Click or Pan tool = Pan
    if (e.button === 1 || e.button === 2 || this.activeTool === 'pan' || e.spaceKey) {
      this.isPanning = true;
      this.dragStartX = sx;
      this.dragStartY = sy;
      this.canvas.style.cursor = 'grabbing';
      return;
    }

    if (e.button !== 0) return;

    // Split-view slider drag check
    if (this.splitView) {
      const splitScreenX = this.splitPos * this.canvas.width;
      if (Math.abs(sx - splitScreenX) < 12) {
        this.isDraggingSplit = true;
        return;
      }
    }

    // Check handle click on selected annotation
    if (this.selectedAnnotation && !this.selectedAnnotation.locked) {
      const handle = this.getHandleAt(sx, sy, this.selectedAnnotation);
      if (handle) {
        this.isResizingHandle = true;
        this.hoveredHandle = handle;
        this.dragStartX = imgPt.x;
        this.dragStartY = imgPt.y;
        this.initialAnnState = { ...this.selectedAnnotation };
        return;
      }
    }

    // Check hit on existing annotations (top to bottom)
    const hitAnn = this.getAnnotationAt(imgPt.x, imgPt.y);

    if (this.activeTool === 'select' || (hitAnn && this.activeTool === 'rect' && e.altKey)) {
      if (hitAnn) {
        this.selectAnnotation(hitAnn);
        if (!hitAnn.locked) {
          this.isDraggingAnnotation = true;
          this.dragStartX = imgPt.x;
          this.dragStartY = imgPt.y;
          this.initialAnnState = { ...hitAnn };
        }
      } else {
        this.selectAnnotation(null);
      }
      this.render();
      return;
    }

    // Draw Rectangle Tool
    if (this.activeTool === 'rect') {
      this.isDrawingRect = true;
      this.dragStartX = imgPt.x;
      this.dragStartY = imgPt.y;
      this.currentRect = {
        x: imgPt.x,
        y: imgPt.y,
        width: 0,
        height: 0
      };
      this.selectAnnotation(null);
      this.render();
      return;
    }

    // Polygon Tool Point Add
    if (this.activeTool === 'polygon') {
      if (this.currentPolygonPoints.length > 2) {
        // Check if clicking close to first point to close
        const first = this.imageToScreen(this.currentPolygonPoints[0].x, this.currentPolygonPoints[0].y);
        if (Math.hypot(sx - first.x, sy - first.y) < 14) {
          this.finishPolygon();
          return;
        }
      }
      this.currentPolygonPoints.push({ x: imgPt.x, y: imgPt.y });
      this.render();
    }
  }

  handleMouseMove(e) {
    const { sx, sy } = this.getCanvasCoords(e);
    const imgPt = this.screenToImage(sx, sy);

    this.cursorX = sx;
    this.cursorY = sy;

    // Pan
    if (this.isPanning) {
      this.panX += (sx - this.dragStartX);
      this.panY += (sy - this.dragStartY);
      this.dragStartX = sx;
      this.dragStartY = sy;
      this.render();
      return;
    }

    // Split drag
    if (this.isDraggingSplit) {
      this.splitPos = Math.max(0.02, Math.min(0.98, sx / this.canvas.width));
      this.render();
      return;
    }

    // Draw Rect
    if (this.isDrawingRect && this.currentRect) {
      const x = Math.min(this.dragStartX, imgPt.x);
      const y = Math.min(this.dragStartY, imgPt.y);
      const w = Math.abs(imgPt.x - this.dragStartX);
      const h = Math.abs(imgPt.y - this.dragStartY);

      this.currentRect = { x, y, width: w, height: h };
      this.render();
      return;
    }

    // Resize Handle
    if (this.isResizingHandle && this.selectedAnnotation && this.initialAnnState) {
      const dx = imgPt.x - this.dragStartX;
      const dy = imgPt.y - this.dragStartY;
      this.resizeAnnotationWithHandle(this.selectedAnnotation, this.initialAnnState, this.hoveredHandle, dx, dy);
      this.render();
      return;
    }

    // Drag Annotation
    if (this.isDraggingAnnotation && this.selectedAnnotation && this.initialAnnState) {
      const dx = imgPt.x - this.dragStartX;
      const dy = imgPt.y - this.dragStartY;
      this.selectedAnnotation.x = this.initialAnnState.x + dx;
      this.selectedAnnotation.y = this.initialAnnState.y + dy;
      this.render();
      return;
    }

    // Hover detection & cursor updates
    if (this.selectedAnnotation && !this.selectedAnnotation.locked) {
      const handle = this.getHandleAt(sx, sy, this.selectedAnnotation);
      if (handle) {
        this.hoveredHandle = handle;
        this.updateHandleCursor(handle);
        this.render();
        return;
      }
    }
    this.hoveredHandle = null;

    const hit = this.getAnnotationAt(imgPt.x, imgPt.y);
    this.hoveredAnnotation = hit;

    if (this.activeTool === 'select') {
      this.canvas.style.cursor = hit ? 'move' : 'default';
    } else if (this.activeTool === 'rect') {
      this.canvas.style.cursor = 'crosshair';
    } else if (this.activeTool === 'polygon') {
      this.canvas.style.cursor = 'crosshair';
    } else if (this.activeTool === 'pan') {
      this.canvas.style.cursor = 'grab';
    }

    this.render();
  }

  handleMouseUp(e) {
    if (this.isPanning) {
      this.isPanning = false;
      this.canvas.style.cursor = this.activeTool === 'pan' ? 'grab' : 'crosshair';
    }

    if (this.isDraggingSplit) {
      this.isDraggingSplit = false;
    }

    if (this.isDrawingRect && this.currentRect) {
      if (this.currentRect.width > 6 && this.currentRect.height > 6) {
        const cls = this.classes.find(c => c.id === this.activeClassId) || {
          id: this.activeClassId,
          char: `${this.activeClassId}`,
          name_ar: `فئة ${this.activeClassId}`,
          name_en: `Class ${this.activeClassId}`
        };

        const newAnn = {
          id: `ann_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
          type: 'rect',
          x: Math.round(this.currentRect.x),
          y: Math.round(this.currentRect.y),
          width: Math.round(this.currentRect.width),
          height: Math.round(this.currentRect.height),
          classId: this.activeClassId,
          className: cls.name_ar || cls.name_en || cls.char,
          char: cls.char,
          locked: false,
          visible: true
        };

        this.annotations.push(newAnn);
        this.selectAnnotation(newAnn);
        this.saveHistory('Create Box');
        this.onAnnotationsChange(this.annotations);
      }
      this.isDrawingRect = false;
      this.currentRect = null;
      this.render();
    }

    if (this.isResizingHandle || this.isDraggingAnnotation) {
      this.isResizingHandle = false;
      this.isDraggingAnnotation = false;
      this.initialAnnState = null;
      this.saveHistory('Transform Box');
      this.onAnnotationsChange(this.annotations);
      this.render();
    }

    this.isMouseDown = false;
  }

  handleDoubleClick(e) {
    if (this.activeTool === 'polygon' && this.currentPolygonPoints.length >= 3) {
      this.finishPolygon();
    }
  }

  finishPolygon() {
    if (this.currentPolygonPoints.length < 3) return;

    // Calculate bounding box around polygon
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    this.currentPolygonPoints.forEach(p => {
      minX = Math.min(minX, p.x);
      minY = Math.min(minY, p.y);
      maxX = Math.max(maxX, p.x);
      maxY = Math.max(maxY, p.y);
    });

    const cls = this.classes.find(c => c.id === this.activeClassId) || {
      id: this.activeClassId,
      char: `${this.activeClassId}`,
      name_ar: `فئة ${this.activeClassId}`,
      name_en: `Class ${this.activeClassId}`
    };

    const newAnn = {
      id: `ann_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      type: 'polygon',
      points: [...this.currentPolygonPoints],
      x: Math.round(minX),
      y: Math.round(minY),
      width: Math.round(maxX - minX),
      height: Math.round(maxY - minY),
      classId: this.activeClassId,
      className: cls.name_ar || cls.name_en || cls.char,
      char: cls.char,
      locked: false,
      visible: true
    };

    this.annotations.push(newAnn);
    this.currentPolygonPoints = [];
    this.selectAnnotation(newAnn);
    this.saveHistory('Create Polygon');
    this.onAnnotationsChange(this.annotations);
    this.render();
  }

  selectAnnotation(ann) {
    this.selectedAnnotation = ann;
    this.onSelectionChange(ann);
    this.render();
  }

  deleteSelected() {
    if (!this.selectedAnnotation) return;
    this.annotations = this.annotations.filter(a => a.id !== this.selectedAnnotation.id);
    this.selectAnnotation(null);
    this.saveHistory('Delete Annotation');
    this.onAnnotationsChange(this.annotations);
    this.render();
  }

  duplicateSelected() {
    if (!this.selectedAnnotation) return;
    const dup = JSON.parse(JSON.stringify(this.selectedAnnotation));
    dup.id = `ann_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    dup.x += 15;
    dup.y += 15;
    if (dup.points) {
      dup.points = dup.points.map(p => ({ x: p.x + 15, y: p.y + 15 }));
    }
    this.annotations.push(dup);
    this.selectAnnotation(dup);
    this.saveHistory('Duplicate Annotation');
    this.onAnnotationsChange(this.annotations);
    this.render();
  }

  clearAnnotations() {
    if (this.annotations.length === 0) return;
    this.annotations = [];
    this.selectAnnotation(null);
    this.saveHistory('Clear All');
    this.onAnnotationsChange(this.annotations);
    this.render();
  }

  setAnnotations(anns) {
    this.annotations = anns;
    this.selectAnnotation(null);
    this.saveHistory('Load Annotations');
    this.onAnnotationsChange(this.annotations);
    this.render();
  }

  // History Undo/Redo
  saveHistory(actionName = '') {
    if (this.historyIndex < this.history.length - 1) {
      this.history = this.history.slice(0, this.historyIndex + 1);
    }
    const state = JSON.stringify(this.annotations);
    this.history.push(state);
    if (this.history.length > 50) this.history.shift();
    this.historyIndex = this.history.length - 1;
  }

  undo() {
    if (this.historyIndex > 0) {
      this.historyIndex--;
      this.annotations = JSON.parse(this.history[this.historyIndex]);
      this.selectedAnnotation = null;
      this.onAnnotationsChange(this.annotations);
      this.render();
    }
  }

  redo() {
    if (this.historyIndex < this.history.length - 1) {
      this.historyIndex++;
      this.annotations = JSON.parse(this.history[this.historyIndex]);
      this.selectedAnnotation = null;
      this.onAnnotationsChange(this.annotations);
      this.render();
    }
  }

  clearHistory() {
    this.history = [];
    this.historyIndex = -1;
    this.saveHistory('Initial');
  }

  // Handle detection & resizing
  getHandles(ann) {
    const { x, y, width: w, height: h } = ann;
    return [
      { name: 'nw', x: x, y: y },
      { name: 'n',  x: x + w / 2, y: y },
      { name: 'ne', x: x + w, y: y },
      { name: 'e',  x: x + w, y: y + h / 2 },
      { name: 'se', x: x + w, y: y + h },
      { name: 's',  x: x + w / 2, y: y + h },
      { name: 'sw', x: x, y: y + h },
      { name: 'w',  x: x, y: y + h / 2 }
    ];
  }

  getHandleAt(sx, sy, ann) {
    if (ann.type !== 'rect') return null;
    const handles = this.getHandles(ann);
    const radius = 8; // Screen px tolerance

    for (const h of handles) {
      const scr = this.imageToScreen(h.x, h.y);
      if (Math.hypot(sx - scr.x, sy - scr.y) <= radius) {
        return h.name;
      }
    }
    return null;
  }

  updateHandleCursor(handle) {
    switch (handle) {
      case 'nw': case 'se': this.canvas.style.cursor = 'nwse-resize'; break;
      case 'ne': case 'sw': this.canvas.style.cursor = 'nesw-resize'; break;
      case 'n':  case 's':  this.canvas.style.cursor = 'ns-resize'; break;
      case 'e':  case 'w':  this.canvas.style.cursor = 'ew-resize'; break;
      default: this.canvas.style.cursor = 'default';
    }
  }

  resizeAnnotationWithHandle(ann, initial, handle, dx, dy) {
    let { x, y, width: w, height: h } = initial;

    if (handle.includes('e')) w += dx;
    if (handle.includes('s')) h += dy;
    if (handle.includes('w')) {
      x += dx;
      w -= dx;
    }
    if (handle.includes('n')) {
      y += dy;
      h -= dy;
    }

    if (w < 4) {
      if (handle.includes('w')) x += w - 4;
      w = 4;
    }
    if (h < 4) {
      if (handle.includes('n')) y += h - 4;
      h = 4;
    }

    ann.x = Math.round(x);
    ann.y = Math.round(y);
    ann.width = Math.round(w);
    ann.height = Math.round(h);
  }

  getAnnotationAt(ix, iy) {
    for (let i = this.annotations.length - 1; i >= 0; i--) {
      const ann = this.annotations[i];
      if (!ann.visible) continue;

      if (ann.type === 'rect') {
        if (ix >= ann.x && ix <= ann.x + ann.width &&
            iy >= ann.y && iy <= ann.y + ann.height) {
          return ann;
        }
      } else if (ann.type === 'polygon' && ann.points) {
        if (this.isPointInPolygon(ix, iy, ann.points)) {
          return ann;
        }
      }
    }
    return null;
  }

  isPointInPolygon(x, y, points) {
    let inside = false;
    for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
      const xi = points[i].x, yi = points[i].y;
      const xj = points[j].x, yj = points[j].y;
      const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }
    return inside;
  }

  // Main Render Loop
  render() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Draw dark workspace grid pattern
    this.drawGrid(ctx, w, h);

    if (!this.processedCanvas) return;

    ctx.save();
    ctx.translate(this.panX, this.panY);
    ctx.scale(this.scale, this.scale);

    // Disable image smoothing at high zoom for pixel-perfect inspection
    ctx.imageSmoothingEnabled = this.scale < 4;

    if (this.splitView && this.originalImage) {
      // Split view: Left = Processed, Right = Original
      const splitImgX = (this.splitPos * w - this.panX) / this.scale;

      // Draw Processed
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, splitImgX, this.processedCanvas.height);
      ctx.clip();
      ctx.drawImage(this.processedCanvas, 0, 0);
      ctx.restore();

      // Draw Original
      ctx.save();
      ctx.beginPath();
      ctx.rect(splitImgX, 0, this.processedCanvas.width - splitImgX, this.processedCanvas.height);
      ctx.clip();
      ctx.drawImage(this.originalImage, 0, 0);
      ctx.restore();
    } else {
      // Normal draw
      ctx.drawImage(this.processedCanvas, 0, 0);
    }

    // Draw Annotations
    this.drawAnnotations(ctx);

    // Draw active drawing rect
    if (this.isDrawingRect && this.currentRect) {
      const color = getClassColor(this.activeClassId);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2 / this.scale;
      ctx.fillStyle = `${color}33`;
      ctx.fillRect(this.currentRect.x, this.currentRect.y, this.currentRect.width, this.currentRect.height);
      ctx.strokeRect(this.currentRect.x, this.currentRect.y, this.currentRect.width, this.currentRect.height);
    }

    // Draw active polygon points
    if (this.activeTool === 'polygon' && this.currentPolygonPoints.length > 0) {
      const color = getClassColor(this.activeClassId);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2 / this.scale;
      ctx.fillStyle = `${color}44`;

      ctx.beginPath();
      this.currentPolygonPoints.forEach((p, idx) => {
        if (idx === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      const imgPt = this.screenToImage(this.cursorX, this.cursorY);
      ctx.lineTo(imgPt.x, imgPt.y);
      ctx.stroke();

      // Draw points
      this.currentPolygonPoints.forEach((p, idx) => {
        ctx.fillStyle = idx === 0 ? '#ff0055' : '#ffffff';
        ctx.beginPath();
        ctx.arc(p.x, p.y, 4 / this.scale, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      });
    }

    ctx.restore();

    // Draw Split-view vertical line & handle
    if (this.splitView) {
      this.drawSplitSlider(ctx, w, h);
    }

    // Draw Crosshair lines
    if (this.showCrosshair && (this.activeTool === 'rect' || this.activeTool === 'polygon')) {
      this.drawCrosshair(ctx, w, h);
    }
  }

  drawGrid(ctx, w, h) {
    ctx.fillStyle = '#0f141c';
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = '#18202d';
    ctx.lineWidth = 1;
    const gridSize = 32;

    ctx.beginPath();
    for (let x = 0; x < w; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
    }
    ctx.stroke();
  }

  drawAnnotations(ctx) {
    const isSelectedOrHovered = (ann) => 
      this.selectedAnnotation && this.selectedAnnotation.id === ann.id;

    for (const ann of this.annotations) {
      if (!ann.visible) continue;

      const isSel = isSelectedOrHovered(ann);
      const isHov = this.hoveredAnnotation && this.hoveredAnnotation.id === ann.id;
      const color = getClassColor(ann.classId);

      ctx.save();
      ctx.lineWidth = (isSel ? 3 : (isHov ? 2.5 : 1.5)) / this.scale;
      ctx.strokeStyle = isSel ? '#00f5d4' : color;
      ctx.fillStyle = isSel ? `${color}40` : `${color}20`;

      if (ann.type === 'rect') {
        ctx.fillRect(ann.x, ann.y, ann.width, ann.height);
        ctx.strokeRect(ann.x, ann.y, ann.width, ann.height);
        this.drawClassBadge(ctx, ann, color, isSel);

        // Draw resize handles if selected
        if (isSel && !ann.locked) {
          this.drawHandles(ctx, ann);
        }
      } else if (ann.type === 'polygon' && ann.points) {
        ctx.beginPath();
        ann.points.forEach((p, idx) => {
          if (idx === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        this.drawClassBadge(ctx, ann, color, isSel);
      }

      ctx.restore();
    }
  }

  drawClassBadge(ctx, ann, color, isSel) {
    const labelText = ann.char ? `${ann.char} ${ann.className || ''}` : (ann.className || `Class ${ann.classId}`);
    const fontSize = Math.max(11 / this.scale, 13 / this.scale);
    ctx.font = `bold ${fontSize}px 'Cairo', 'Outfit', sans-serif`;

    const textMetrics = ctx.measureText(labelText);
    const badgeW = textMetrics.width + 12 / this.scale;
    const badgeH = fontSize + 8 / this.scale;
    const badgeX = ann.x;
    const badgeY = ann.y - badgeH;

    // Background pill
    ctx.fillStyle = isSel ? '#00f5d4' : color;
    ctx.beginPath();
    ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 4 / this.scale);
    ctx.fill();

    // Text
    ctx.fillStyle = '#05070a';
    ctx.fillText(labelText, badgeX + 6 / this.scale, badgeY + badgeH - 4 / this.scale);
  }

  drawHandles(ctx, ann) {
    const handles = this.getHandles(ann);
    const handleSize = 7 / this.scale;

    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#00f5d4';
    ctx.lineWidth = 1.5 / this.scale;

    handles.forEach(h => {
      ctx.fillRect(h.x - handleSize / 2, h.y - handleSize / 2, handleSize, handleSize);
      ctx.strokeRect(h.x - handleSize / 2, h.y - handleSize / 2, handleSize, handleSize);
    });
  }

  drawSplitSlider(ctx, w, h) {
    const splitX = this.splitPos * w;

    ctx.strokeStyle = '#00f5d4';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(splitX, 0);
    ctx.lineTo(splitX, h);
    ctx.stroke();

    // Slider circular button
    ctx.fillStyle = '#00f5d4';
    ctx.beginPath();
    ctx.arc(splitX, h / 2, 14, 0, Math.PI * 2);
    ctx.fill();

    // Split arrows icon
    ctx.fillStyle = '#000000';
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('⬌', splitX, h / 2);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
  }

  drawCrosshair(ctx, w, h) {
    ctx.strokeStyle = 'rgba(0, 245, 212, 0.4)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);

    ctx.beginPath();
    ctx.moveTo(this.cursorX, 0);
    ctx.lineTo(this.cursorX, h);
    ctx.moveTo(0, this.cursorY);
    ctx.lineTo(w, this.cursorY);
    ctx.stroke();
    ctx.setLineDash([]);
  }
}
