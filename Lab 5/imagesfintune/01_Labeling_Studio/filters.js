/**
 * filters.js - High-Performance Image Processing & Inscription Enhancement Engine
 */

export class FilterEngine {
  /**
   * Apply all active filter parameters to an ImageData buffer or offscreen canvas.
   */
  static applyPipeline(sourceCanvas, params) {
    const width = sourceCanvas.width;
    const height = sourceCanvas.height;

    // Create a working canvas
    const offscreen = document.createElement('canvas');
    offscreen.width = width;
    offscreen.height = height;
    const ctx = offscreen.getContext('2d', { willReadFrequently: true });

    // Draw source
    ctx.drawImage(sourceCanvas, 0, 0);
    let imgData = ctx.getImageData(0, 0, width, height);
    let data = imgData.data;

    // 1. Brightness, Contrast, Exposure, Gamma, Saturation, Invert
    const hasBasicAdj = params.brightness !== 0 || params.contrast !== 0 || 
                         params.exposure !== 0 || params.gamma !== 1 || 
                         params.saturation !== 0 || params.invert;

    if (hasBasicAdj) {
      const bFactor = params.brightness * 255; // -255 to 255
      const cFactor = (259 * (params.contrast * 255 + 255)) / (255 * (259 - params.contrast * 255));
      const expFactor = Math.pow(2, params.exposure);
      const invGamma = 1 / Math.max(0.01, params.gamma);
      const sat = 1 + params.saturation; // 0 (desat) to 2+

      for (let i = 0; i < data.length; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        // Invert
        if (params.invert) {
          r = 255 - r;
          g = 255 - g;
          b = 255 - b;
        }

        // Exposure & Brightness
        r = r * expFactor + bFactor;
        g = g * expFactor + bFactor;
        b = b * expFactor + bFactor;

        // Contrast
        r = cFactor * (r - 128) + 128;
        g = cFactor * (g - 128) + 128;
        b = cFactor * (b - 128) + 128;

        // Gamma
        if (params.gamma !== 1) {
          r = 255 * Math.pow(Math.max(0, Math.min(255, r)) / 255, invGamma);
          g = 255 * Math.pow(Math.max(0, Math.min(255, g)) / 255, invGamma);
          b = 255 * Math.pow(Math.max(0, Math.min(255, b)) / 255, invGamma);
        }

        // Saturation
        if (params.saturation !== 0) {
          const gray = 0.299 * r + 0.587 * g + 0.114 * b;
          r = gray + sat * (r - gray);
          g = gray + sat * (g - gray);
          b = gray + sat * (b - gray);
        }

        data[i] = Math.max(0, Math.min(255, r));
        data[i + 1] = Math.max(0, Math.min(255, g));
        data[i + 2] = Math.max(0, Math.min(255, b));
      }
    }

    // 2. Grayscale conversion
    if (params.grayscale) {
      for (let i = 0; i < data.length; i += 4) {
        const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
        data[i] = gray;
        data[i + 1] = gray;
        data[i + 2] = gray;
      }
    }

    // 3. Histogram Equalization (Local contrast enhancement for stone textures)
    if (params.equalizeHist) {
      imgData = this.histogramEqualization(imgData, width, height);
      data = imgData.data;
    }

    // 4. Median Denoise Filter (removes rock grain while keeping edges sharp)
    if (params.medianDenoise > 0) {
      imgData = this.medianFilter(imgData, width, height, params.medianDenoise);
      data = imgData.data;
    }

    // 5. Gaussian / Box Blur
    if (params.blur > 0) {
      imgData = this.boxBlur(imgData, width, height, params.blur);
      data = imgData.data;
    }

    // 6. Sharpen & Unsharp Mask
    if (params.sharpen > 0) {
      imgData = this.sharpenFilter(imgData, width, height, params.sharpen);
      data = imgData.data;
    }

    // 7. Edge Detection
    if (params.edgeDetection && params.edgeDetection !== 'none') {
      imgData = this.detectEdges(imgData, width, height, params.edgeDetection, params.edgeStrength || 1);
      data = imgData.data;
    }

    // 8. 3D Emboss / Relief
    if (params.emboss) {
      imgData = this.embossFilter(imgData, width, height, params.embossAngle || 45, params.embossStrength || 1.5);
      data = imgData.data;
    }

    // 9. Binarization & Adaptive Thresholding
    if (params.binarize && params.binarize !== 'none') {
      imgData = this.applyThreshold(imgData, width, height, params.binarize, params.thresholdVal, params.adaptiveWindow || 15);
      data = imgData.data;
    }

    // 10. False Color Maps (Heatmap, Sandstone, Obsidian, Ironbow)
    if (params.colorMap && params.colorMap !== 'none') {
      imgData = this.applyColorMap(imgData, width, height, params.colorMap);
      data = imgData.data;
    }

    ctx.putImageData(imgData, 0, 0);
    return offscreen;
  }

  /**
   * Fast Histogram Equalization
   */
  static histogramEqualization(imgData, width, height) {
    const data = imgData.data;
    const numPixels = width * height;
    const hist = new Int32Array(256);

    for (let i = 0; i < data.length; i += 4) {
      const v = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
      hist[v]++;
    }

    // Cumulative distribution function (CDF)
    const cdf = new Float32Array(256);
    let cum = 0;
    let cdfMin = -1;

    for (let i = 0; i < 256; i++) {
      cum += hist[i];
      cdf[i] = cum;
      if (cum > 0 && cdfMin === -1) {
        cdfMin = cum;
      }
    }

    const cdfScale = 255 / (numPixels - cdfMin || 1);
    const lut = new Uint8Array(256);
    for (let i = 0; i < 256; i++) {
      lut[i] = Math.max(0, Math.min(255, Math.round((cdf[i] - cdfMin) * cdfScale)));
    }

    for (let i = 0; i < data.length; i += 4) {
      const v = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
      const newV = lut[v];
      const ratio = v > 0 ? newV / v : 1;
      data[i] = Math.min(255, data[i] * ratio);
      data[i + 1] = Math.min(255, data[i + 1] * ratio);
      data[i + 2] = Math.min(255, data[i + 2] * ratio);
    }

    return imgData;
  }

  /**
   * 3x3 Median filter
   */
  static medianFilter(imgData, width, height, radius = 1) {
    const src = new Uint8ClampedArray(imgData.data);
    const dst = imgData.data;
    const windowSize = (2 * radius + 1) * (2 * radius + 1);
    const rBuf = new Uint8Array(windowSize);
    const gBuf = new Uint8Array(windowSize);
    const bBuf = new Uint8Array(windowSize);
    const mid = Math.floor(windowSize / 2);

    for (let y = radius; y < height - radius; y++) {
      for (let x = radius; x < width - radius; x++) {
        let count = 0;
        for (let dy = -radius; dy <= radius; dy++) {
          for (let dx = -radius; dx <= radius; dx++) {
            const idx = ((y + dy) * width + (x + dx)) * 4;
            rBuf[count] = src[idx];
            gBuf[count] = src[idx + 1];
            bBuf[count] = src[idx + 2];
            count++;
          }
        }
        rBuf.sort();
        gBuf.sort();
        bBuf.sort();

        const dstIdx = (y * width + x) * 4;
        dst[dstIdx] = rBuf[mid];
        dst[dstIdx + 1] = gBuf[mid];
        dst[dstIdx + 2] = bBuf[mid];
      }
    }
    return imgData;
  }

  /**
   * Box Blur / Fast Approximation
   */
  static boxBlur(imgData, width, height, radius) {
    const src = new Uint8ClampedArray(imgData.data);
    const dst = imgData.data;
    const r = Math.max(1, Math.round(radius));

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let rSum = 0, gSum = 0, bSum = 0, count = 0;
        for (let dy = -r; dy <= r; dy++) {
          const ny = y + dy;
          if (ny < 0 || ny >= height) continue;
          for (let dx = -r; dx <= r; dx++) {
            const nx = x + dx;
            if (nx < 0 || nx >= width) continue;
            const idx = (ny * width + nx) * 4;
            rSum += src[idx];
            gSum += src[idx + 1];
            bSum += src[idx + 2];
            count++;
          }
        }
        const dstIdx = (y * width + x) * 4;
        dst[dstIdx] = rSum / count;
        dst[dstIdx + 1] = gSum / count;
        dst[dstIdx + 2] = bSum / count;
      }
    }
    return imgData;
  }

  /**
   * Sharpen Filter using 3x3 convolution
   */
  static sharpenFilter(imgData, width, height, strength = 1) {
    const src = new Uint8ClampedArray(imgData.data);
    const dst = imgData.data;
    const s = strength;
    // Kernel: [0, -s, 0, -s, 1 + 4s, -s, 0, -s, 0]
    const center = 1 + 4 * s;

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        const dstIdx = (y * width + x) * 4;
        for (let c = 0; c < 3; c++) {
          const val = center * src[dstIdx + c]
            - s * src[((y - 1) * width + x) * 4 + c]
            - s * src[((y + 1) * width + x) * 4 + c]
            - s * src[(y * width + (x - 1)) * 4 + c]
            - s * src[(y * width + (x + 1)) * 4 + c];
          dst[dstIdx + c] = Math.max(0, Math.min(255, val));
        }
      }
    }
    return imgData;
  }

  /**
   * Edge Detection (Sobel, Laplacian, Morphological)
   */
  static detectEdges(imgData, width, height, mode, strength = 1) {
    const src = new Uint8ClampedArray(imgData.data);
    const dst = imgData.data;

    // Convert src to grayscale array first
    const gray = new Float32Array(width * height);
    for (let i = 0; i < gray.length; i++) {
      const idx = i * 4;
      gray[i] = 0.299 * src[idx] + 0.587 * src[idx + 1] + 0.114 * src[idx + 2];
    }

    if (mode === 'sobel') {
      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          const gx = (-1 * gray[(y - 1) * width + (x - 1)] + 1 * gray[(y - 1) * width + (x + 1)]) +
                     (-2 * gray[y * width + (x - 1)]       + 2 * gray[y * width + (x + 1)]) +
                     (-1 * gray[(y + 1) * width + (x - 1)] + 1 * gray[(y + 1) * width + (x + 1)]);

          const gy = (-1 * gray[(y - 1) * width + (x - 1)] - 2 * gray[(y - 1) * width + x] - 1 * gray[(y - 1) * width + (x + 1)]) +
                     ( 1 * gray[(y + 1) * width + (x - 1)] + 2 * gray[(y + 1) * width + x] + 1 * gray[(y + 1) * width + (x + 1)]);

          const mag = Math.min(255, Math.hypot(gx, gy) * strength);
          const dstIdx = (y * width + x) * 4;
          dst[dstIdx] = mag;
          dst[dstIdx + 1] = mag;
          dst[dstIdx + 2] = mag;
        }
      }
    } else if (mode === 'laplacian') {
      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          const val = (
            4 * gray[y * width + x] -
            gray[(y - 1) * width + x] -
            gray[(y + 1) * width + x] -
            gray[y * width + (x - 1)] -
            gray[y * width + (x + 1)]
          ) * strength;

          const mag = Math.max(0, Math.min(255, Math.abs(val)));
          const dstIdx = (y * width + x) * 4;
          dst[dstIdx] = mag;
          dst[dstIdx + 1] = mag;
          dst[dstIdx + 2] = mag;
        }
      }
    } else if (mode === 'morphology') {
      // Morphological Gradient: Dilation - Erosion (great for carved lines)
      const dilated = new Float32Array(width * height);
      const eroded = new Float32Array(width * height);

      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          let maxVal = -Infinity;
          let minVal = Infinity;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              const v = gray[(y + dy) * width + (x + dx)];
              if (v > maxVal) maxVal = v;
              if (v < minVal) minVal = v;
            }
          }
          const idx = y * width + x;
          dilated[idx] = maxVal;
          eroded[idx] = minVal;
        }
      }

      for (let i = 0; i < gray.length; i++) {
        const grad = Math.min(255, (dilated[i] - eroded[i]) * strength * 1.5);
        const dstIdx = i * 4;
        dst[dstIdx] = grad;
        dst[dstIdx + 1] = grad;
        dst[dstIdx + 2] = grad;
      }
    }

    return imgData;
  }

  /**
   * 3D Emboss / Relief Filter for stone carvings
   */
  static embossFilter(imgData, width, height, angle = 45, strength = 1.5) {
    const src = new Uint8ClampedArray(imgData.data);
    const dst = imgData.data;

    const rad = (angle * Math.PI) / 180;
    const dx = Math.round(Math.cos(rad));
    const dy = Math.round(Math.sin(rad));

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        const pCurrent = (y * width + x) * 4;
        const pOffset = ((y + dy) * width + (x + dx)) * 4;

        for (let c = 0; c < 3; c++) {
          const diff = (src[pCurrent + c] - src[pOffset + c]) * strength;
          dst[pCurrent + c] = Math.max(0, Math.min(255, 128 + diff));
        }
      }
    }
    return imgData;
  }

  /**
   * Binarization & Adaptive Thresholding
   */
  static applyThreshold(imgData, width, height, mode, thresholdVal = 128, windowSize = 15) {
    const data = imgData.data;
    const gray = new Uint8Array(width * height);

    for (let i = 0; i < gray.length; i++) {
      const idx = i * 4;
      gray[i] = Math.round(0.299 * data[idx] + 0.587 * data[idx + 1] + 0.114 * data[idx + 2]);
    }

    if (mode === 'otsu') {
      thresholdVal = this.computeOtsuThreshold(gray);
    }

    if (mode === 'adaptive') {
      // Bradley-Roth Local Adaptive Thresholding using Integral Image
      const S = Math.max(3, Math.round(windowSize));
      const s2 = Math.floor(S / 2);
      const T = 0.15; // 15% below local mean

      // Compute Integral Image
      const integral = new Float64Array(width * height);
      for (let x = 0; x < width; x++) {
        let sum = 0;
        for (let y = 0; y < height; y++) {
          const idx = y * width + x;
          sum += gray[idx];
          if (x === 0) {
            integral[idx] = sum;
          } else {
            integral[idx] = integral[idx - 1] + sum;
          }
        }
      }

      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const x1 = Math.max(0, x - s2);
          const x2 = Math.min(width - 1, x + s2);
          const y1 = Math.max(0, y - s2);
          const y2 = Math.min(height - 1, y + s2);

          const count = (x2 - x1 + 1) * (y2 - y1 + 1);

          let sum = integral[y2 * width + x2];
          if (x1 > 0) sum -= integral[y2 * width + (x1 - 1)];
          if (y1 > 0) sum -= integral[(y1 - 1) * width + x2];
          if (x1 > 0 && y1 > 0) sum += integral[(y1 - 1) * width + (x1 - 1)];

          const idx = y * width + x;
          const dstIdx = idx * 4;
          const val = (gray[idx] * count) < (sum * (1.0 - T)) ? 0 : 255;
          data[dstIdx] = val;
          data[dstIdx + 1] = val;
          data[dstIdx + 2] = val;
        }
      }
      return imgData;
    }

    // Global / Otsu thresholding
    for (let i = 0; i < gray.length; i++) {
      const val = gray[i] >= thresholdVal ? 255 : 0;
      const idx = i * 4;
      data[idx] = val;
      data[idx + 1] = val;
      data[idx + 2] = val;
    }

    return imgData;
  }

  /**
   * Otsu Threshold Algorithm
   */
  static computeOtsuThreshold(gray) {
    const hist = new Int32Array(256);
    const total = gray.length;

    for (let i = 0; i < total; i++) {
      hist[gray[i]]++;
    }

    let sum = 0;
    for (let i = 0; i < 256; i++) sum += i * hist[i];

    let sumB = 0;
    let wB = 0;
    let wF = 0;
    let maxVariance = 0;
    let threshold = 128;

    for (let t = 0; t < 256; t++) {
      wB += hist[t];
      if (wB === 0) continue;
      wF = total - wB;
      if (wF === 0) break;

      sumB += t * hist[t];
      const mB = sumB / wB;
      const mF = (sum - sumB) / wF;

      const variance = wB * wF * (mB - mF) * (mB - mF);
      if (variance > maxVariance) {
        maxVariance = variance;
        threshold = t;
      }
    }

    return threshold;
  }

  /**
   * Color Maps (Heatmap, Sandstone, Obsidian, Ironbow)
   */
  static applyColorMap(imgData, width, height, mapName) {
    const data = imgData.data;

    for (let i = 0; i < data.length; i += 4) {
      const g = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      const norm = g / 255;
      let r = 0, gr = 0, b = 0;

      switch (mapName) {
        case 'heatmap': // Jet / Inferno
          r = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(norm * 4 - 3))));
          gr = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(norm * 4 - 2))));
          b = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(norm * 4 - 1))));
          break;

        case 'sandstone': // Desert Rock Carvings palette
          r = Math.min(255, norm * 260 + 20);
          gr = Math.min(255, norm * 180 + 10);
          b = Math.min(255, norm * 100);
          break;

        case 'obsidian': // High-contrast neon on dark slate
          r = Math.min(255, Math.pow(norm, 2) * 50);
          gr = Math.min(255, Math.pow(norm, 1.5) * 255);
          b = Math.min(255, norm * 255 + 50);
          break;

        case 'ironbow': // FLIR thermal camera style
          r = Math.min(255, Math.sin(norm * Math.PI) * 255 + (norm > 0.5 ? (norm - 0.5) * 510 : 0));
          gr = Math.min(255, Math.pow(norm, 2) * 255);
          b = Math.min(255, Math.cos(norm * Math.PI / 2) * 255);
          break;

        case 'nightvision':
          r = 0;
          gr = Math.min(255, norm * 280);
          b = Math.min(255, norm * 60);
          break;

        default:
          r = data[i];
          gr = data[i + 1];
          b = data[i + 2];
      }

      data[i] = r;
      data[i + 1] = gr;
      data[i + 2] = b;
    }

    return imgData;
  }

  /**
   * Geometric transformation: Rotate canvas by angle (degrees) and/or flip
   */
  static transformCanvas(sourceCanvas, rotationDeg = 0, flipH = false, flipV = false) {
    const rad = (rotationDeg * Math.PI) / 180;
    const sin = Math.abs(Math.sin(rad));
    const cos = Math.abs(Math.cos(rad));

    const w = sourceCanvas.width;
    const h = sourceCanvas.height;

    const newWidth = Math.round(w * cos + h * sin);
    const newHeight = Math.round(w * sin + h * cos);

    const outCanvas = document.createElement('canvas');
    outCanvas.width = newWidth;
    outCanvas.height = newHeight;
    const ctx = outCanvas.getContext('2d');

    ctx.translate(newWidth / 2, newHeight / 2);
    ctx.rotate(rad);
    ctx.scale(flipH ? -1 : 1, flipV ? -1 : 1);
    ctx.drawImage(sourceCanvas, -w / 2, -h / 2);

    return outCanvas;
  }
}
