/**
 * studio_bundle.js - Complete Self-Contained Inscription Image Processing & Labeling Studio
 * Works seamlessly in both HTTP and direct file:/// (double-click) modes with zero CORS restrictions.
 */

(function() {
  'use strict';

  // =========================================================================
  // 1. PALETTE & PRESETS
  // =========================================================================
  const PALETTE = [
    '#00f5d4', '#7b2cbf', '#fee440', '#f72585', '#4cc9f0',
    '#ff9e00', '#52b788', '#e63946', '#9d4edd', '#06d6a0',
    '#ff006e', '#8338ec', '#3a86ff', '#fb5607', '#ffbe0b',
    '#2a9d8f', '#e76f51', '#70e000', '#38b000', '#007200',
    '#d00000', '#9d0208', '#6a040f', '#03045e', '#023e8a',
    '#0077b6', '#0096c7', '#00b4d8', '#48cae4', '#90e0ef'
  ];

  function getClassColor(id) {
    return PALETTE[id % PALETTE.length];
  }

  // Nabataean Preset (40 items)
  const NABATAEAN_CLASSES = [
    { id: 0, char: '𐢀', name_ar: 'ألف نهائية (ـا)', name_en: 'FINAL_ALEPH', unicode: 'U+10880', type: 'letter' },
    { id: 1, char: '𐢁', name_ar: 'ألف مفردة (ا)', name_en: 'ALEPH', unicode: 'U+10881', type: 'letter' },
    { id: 2, char: '𐢂', name_ar: 'باء نهائية (ـب)', name_en: 'FINAL_BETH', unicode: 'U+10882', type: 'letter' },
    { id: 3, char: '𐢃', name_ar: 'باء مفردة (ب)', name_en: 'BETH', unicode: 'U+10883', type: 'letter' },
    { id: 4, char: '𐢄', name_ar: 'جيم (ج)', name_en: 'GIMEL', unicode: 'U+10884', type: 'letter' },
    { id: 5, char: '𐢅', name_ar: 'دال (د)', name_en: 'DALETH', unicode: 'U+10885', type: 'letter' },
    { id: 6, char: '𐢆', name_ar: 'هاء نهائية (ـه)', name_en: 'FINAL_HE', unicode: 'U+10886', type: 'letter' },
    { id: 7, char: '𐢇', name_ar: 'هاء مفردة (هـ)', name_en: 'HE', unicode: 'U+10887', type: 'letter' },
    { id: 8, char: '𐢈', name_ar: 'واو (و)', name_en: 'WAW', unicode: 'U+10888', type: 'letter' },
    { id: 9, char: '𐢉', name_ar: 'زاي (ز)', name_en: 'ZAYIN', unicode: 'U+10889', type: 'letter' },
    { id: 10, char: '𐢊', name_ar: 'حاء (ح)', name_en: 'HETH', unicode: 'U+1088A', type: 'letter' },
    { id: 11, char: '𐢋', name_ar: 'طاء (ط)', name_en: 'TETH', unicode: 'U+1088B', type: 'letter' },
    { id: 12, char: '𐢌', name_ar: 'ياء نهائية (ـي)', name_en: 'FINAL_YODH', unicode: 'U+1088C', type: 'letter' },
    { id: 13, char: '𐢍', name_ar: 'ياء مفردة (ي)', name_en: 'YODH', unicode: 'U+1088D', type: 'letter' },
    { id: 14, char: '𐢎', name_ar: 'كاف نهائية (ـك)', name_en: 'FINAL_KAPH', unicode: 'U+1088E', type: 'letter' },
    { id: 15, char: '𐢏', name_ar: 'كاف مفردة (ك)', name_en: 'KAPH', unicode: 'U+1088F', type: 'letter' },
    { id: 16, char: '𐢐', name_ar: 'لام نهائية (ـل)', name_en: 'FINAL_LAMEDH', unicode: 'U+10890', type: 'letter' },
    { id: 17, char: '𐢑', name_ar: 'لام مفردة (ل)', name_en: 'LAMEDH', unicode: 'U+10891', type: 'letter' },
    { id: 18, char: '𐢒', name_ar: 'ميم نهائية (ـم)', name_en: 'FINAL_MEM', unicode: 'U+10892', type: 'letter' },
    { id: 19, char: '𐢓', name_ar: 'ميم مفردة (م)', name_en: 'MEM', unicode: 'U+10893', type: 'letter' },
    { id: 20, char: '𐢔', name_ar: 'نون نهائية (ـن)', name_en: 'FINAL_NUN', unicode: 'U+10894', type: 'letter' },
    { id: 21, char: '𐢕', name_ar: 'نون مفردة (ن)', name_en: 'NUN', unicode: 'U+10895', type: 'letter' },
    { id: 22, char: '𐢖', name_ar: 'سمخ / سين (س)', name_en: 'SAMEKH', unicode: 'U+10896', type: 'letter' },
    { id: 23, char: '𐢗', name_ar: 'عين (ع)', name_en: 'AYIN', unicode: 'U+10897', type: 'letter' },
    { id: 24, char: '𐢘', name_ar: 'فاء (ف)', name_en: 'PE', unicode: 'U+10898', type: 'letter' },
    { id: 25, char: '𐢙', name_ar: 'صاد (ص)', name_en: 'SADHE', unicode: 'U+10899', type: 'letter' },
    { id: 26, char: '𐢚', name_ar: 'قاف (ق)', name_en: 'QOPH', unicode: 'U+1089A', type: 'letter' },
    { id: 27, char: '𐢛', name_ar: 'راء (ر)', name_en: 'RESH', unicode: 'U+1089B', type: 'letter' },
    { id: 28, char: '𐢜', name_ar: 'شين نهائية (ـش)', name_en: 'FINAL_SHIN', unicode: 'U+1089C', type: 'letter' },
    { id: 29, char: '𐢝', name_ar: 'شين مفردة (ش)', name_en: 'SHIN', unicode: 'U+1089D', type: 'letter' },
    { id: 30, char: '𐢞', name_ar: 'تاء (ت)', name_en: 'TAW', unicode: 'U+1089E', type: 'letter' },
    { id: 31, char: '𐢧', name_ar: 'رقم 1', name_en: 'NUMBER_ONE', unicode: 'U+108A7', type: 'number' },
    { id: 32, char: '𐢨', name_ar: 'رقم 2', name_en: 'NUMBER_TWO', unicode: 'U+108A8', type: 'number' },
    { id: 33, char: '𐢩', name_ar: 'رقم 3', name_en: 'NUMBER_THREE', unicode: 'U+108A9', type: 'number' },
    { id: 34, char: '𐢪', name_ar: 'رقم 4', name_en: 'NUMBER_FOUR', unicode: 'U+108AA', type: 'number' },
    { id: 35, char: '𐢫', name_ar: 'رقم 4 صليبي', name_en: 'CRUCIFORM_FOUR', unicode: 'U+108AB', type: 'number' },
    { id: 36, char: '𐢬', name_ar: 'رقم 5', name_en: 'NUMBER_FIVE', unicode: 'U+108AC', type: 'number' },
    { id: 37, char: '𐢭', name_ar: 'رقم 10', name_en: 'NUMBER_TEN', unicode: 'U+108AD', type: 'number' },
    { id: 38, char: '𐢮', name_ar: 'رقم 20', name_en: 'NUMBER_TWENTY', unicode: 'U+108AE', type: 'number' },
    { id: 39, char: '𐢯', name_ar: 'رقم 100', name_en: 'NUMBER_HUNDRED', unicode: 'U+108AF', type: 'number' }
  ];

  // Aramaic Preset
  const ARAMAIC_CLASSES = [
    { id: 0, char: '𐡀', name_ar: 'ألف (آرامية)', name_en: 'ARAMAIC_ALEPH', unicode: 'U+10840', type: 'letter' },
    { id: 1, char: '𐡁', name_ar: 'باء', name_en: 'ARAMAIC_BETH', unicode: 'U+10841', type: 'letter' },
    { id: 2, char: '𐡂', name_ar: 'جيم', name_en: 'ARAMAIC_GIMEL', unicode: 'U+10842', type: 'letter' },
    { id: 3, char: '𐡃', name_ar: 'دال', name_en: 'ARAMAIC_DALETH', unicode: 'U+10843', type: 'letter' },
    { id: 4, char: '𐡄', name_ar: 'هاء', name_en: 'ARAMAIC_HE', unicode: 'U+10844', type: 'letter' },
    { id: 5, char: '𐡅', name_ar: 'واو', name_en: 'ARAMAIC_WAW', unicode: 'U+10845', type: 'letter' },
    { id: 6, char: '𐡆', name_ar: 'زاي', name_en: 'ARAMAIC_ZAYIN', unicode: 'U+10846', type: 'letter' },
    { id: 7, char: '𐡇', name_ar: 'حاء', name_en: 'ARAMAIC_HETH', unicode: 'U+10847', type: 'letter' },
    { id: 8, char: '𐡈', name_ar: 'طاء', name_en: 'ARAMAIC_TETH', unicode: 'U+10848', type: 'letter' },
    { id: 9, char: '𐡉', name_ar: 'ياء', name_en: 'ARAMAIC_YODH', unicode: 'U+10849', type: 'letter' },
    { id: 10, char: '𐡊', name_ar: 'كاف', name_en: 'ARAMAIC_KAPH', unicode: 'U+1084A', type: 'letter' },
    { id: 11, char: '𐡋', name_ar: 'لام', name_en: 'ARAMAIC_LAMEDH', unicode: 'U+1084B', type: 'letter' },
    { id: 12, char: '𐡌', name_ar: 'ميم', name_en: 'ARAMAIC_MEM', unicode: 'U+1084C', type: 'letter' },
    { id: 13, char: '𐡍', name_ar: 'نون', name_en: 'ARAMAIC_NUN', unicode: 'U+1084D', type: 'letter' },
    { id: 14, char: '𐡎', name_ar: 'سمخ', name_en: 'ARAMAIC_SAMEKH', unicode: 'U+1084E', type: 'letter' },
    { id: 15, char: '𐡏', name_ar: 'عين', name_en: 'ARAMAIC_AYIN', unicode: 'U+1084F', type: 'letter' },
    { id: 16, char: '𐡐', name_ar: 'فاء / پي', name_en: 'ARAMAIC_PE', unicode: 'U+10850', type: 'letter' },
    { id: 17, char: '𐡑', name_ar: 'صاد', name_en: 'ARAMAIC_SADHE', unicode: 'U+10851', type: 'letter' },
    { id: 18, char: '𐡒', name_ar: 'قاف', name_en: 'ARAMAIC_QOPH', unicode: 'U+10852', type: 'letter' },
    { id: 19, char: '𐡓', name_ar: 'راء', name_en: 'ARAMAIC_RESH', unicode: 'U+10853', type: 'letter' },
    { id: 20, char: '𐡔', name_ar: 'شين', name_en: 'ARAMAIC_SHIN', unicode: 'U+10854', type: 'letter' },
    { id: 21, char: '𐡕', name_ar: 'تاء', name_en: 'ARAMAIC_TAW', unicode: 'U+10855', type: 'letter' }
  ];

  // Arabic Preset
  const ARABIC_CLASSES = [
    'أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص',
    'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'هـ', 'و', 'ي'
  ].map((char, index) => ({
    id: index,
    char: char,
    name_ar: `حرف ${char}`,
    name_en: `ARABIC_${char}`,
    unicode: `U+${char.charCodeAt(0).toString(16).toUpperCase()}`,
    type: 'letter'
  }));

  function parseClassesFile(rawContent, filename = '') {
    const content = rawContent.trim();
    if (!content) return [];

    if (filename.endsWith('.json') || (content.startsWith('[') && content.endsWith(']')) || (content.startsWith('{') && content.endsWith('}'))) {
      try {
        const parsed = JSON.parse(content);
        if (Array.isArray(parsed)) {
          return parsed.map((item, idx) => {
            if (typeof item === 'string') {
              return { id: idx, char: item, name_ar: item, name_en: item, type: 'custom' };
            }
            return {
              id: item.id !== undefined ? item.id : idx,
              char: item.char || item.symbol || item.name || `${idx}`,
              name_ar: item.name_ar || item.name || item.char || `فئة ${idx}`,
              name_en: item.name_en || item.name || item.char || `Class ${idx}`,
              unicode: item.unicode || '',
              type: item.type || 'custom'
            };
          });
        }
      } catch (e) {}
    }

    const lines = content.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith('#'));
    const parsedClasses = [];

    lines.forEach((line, idx) => {
      let cleanLine = line.replace(/^-\s*/, '').replace(/^\d+:\s*/, '').trim();
      const parenMatch = cleanLine.match(/^(\S+)\s*\((.+?)\)$/);
      const pipeMatch = cleanLine.split('|').map(s => s.trim());

      if (parenMatch) {
        const char = parenMatch[1];
        const desc = parenMatch[2];
        parsedClasses.push({
          id: idx,
          char: char,
          name_ar: desc,
          name_en: desc,
          unicode: char.length > 0 ? `U+${char.codePointAt(0).toString(16).toUpperCase()}` : '',
          type: 'custom'
        });
      } else if (pipeMatch.length >= 2) {
        const char = pipeMatch[0];
        const name_en = pipeMatch[1] || char;
        const name_ar = pipeMatch[2] || name_en;
        parsedClasses.push({
          id: idx,
          char: char,
          name_ar: name_ar,
          name_en: name_en,
          unicode: char.length > 0 ? `U+${char.codePointAt(0).toString(16).toUpperCase()}` : '',
          type: 'custom'
        });
      } else {
        parsedClasses.push({
          id: idx,
          char: cleanLine,
          name_ar: cleanLine,
          name_en: cleanLine,
          unicode: cleanLine.length <= 2 ? `U+${cleanLine.codePointAt(0).toString(16).toUpperCase()}` : '',
          type: 'custom'
        });
      }
    });

    return parsedClasses;
  }

  // =========================================================================
  // 2. IMAGE FILTER ENGINE
  // =========================================================================
  class FilterEngine {
    static applyPipeline(sourceCanvas, params) {
      const width = sourceCanvas.width;
      const height = sourceCanvas.height;

      const offscreen = document.createElement('canvas');
      offscreen.width = width;
      offscreen.height = height;
      const ctx = offscreen.getContext('2d', { willReadFrequently: true });

      ctx.drawImage(sourceCanvas, 0, 0);
      let imgData = ctx.getImageData(0, 0, width, height);
      let data = imgData.data;

      // 1. Basic adjustments
      const hasBasicAdj = params.brightness !== 0 || params.contrast !== 0 || 
                           params.exposure !== 0 || params.gamma !== 1 || 
                           params.saturation !== 0 || params.invert;

      if (hasBasicAdj) {
        const bFactor = params.brightness * 255;
        const cFactor = (259 * (params.contrast * 255 + 255)) / (255 * (259 - params.contrast * 255));
        const expFactor = Math.pow(2, params.exposure);
        const invGamma = 1 / Math.max(0.01, params.gamma);
        const sat = 1 + params.saturation;

        for (let i = 0; i < data.length; i += 4) {
          let r = data[i];
          let g = data[i + 1];
          let b = data[i + 2];

          if (params.invert) {
            r = 255 - r;
            g = 255 - g;
            b = 255 - b;
          }

          r = r * expFactor + bFactor;
          g = g * expFactor + bFactor;
          b = b * expFactor + bFactor;

          r = cFactor * (r - 128) + 128;
          g = cFactor * (g - 128) + 128;
          b = cFactor * (b - 128) + 128;

          if (params.gamma !== 1) {
            r = 255 * Math.pow(Math.max(0, Math.min(255, r)) / 255, invGamma);
            g = 255 * Math.pow(Math.max(0, Math.min(255, g)) / 255, invGamma);
            b = 255 * Math.pow(Math.max(0, Math.min(255, b)) / 255, invGamma);
          }

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

      // 2. Grayscale
      if (params.grayscale) {
        for (let i = 0; i < data.length; i += 4) {
          const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
          data[i] = gray;
          data[i + 1] = gray;
          data[i + 2] = gray;
        }
      }

      // 3. Histogram Equalization
      if (params.equalizeHist) {
        imgData = this.histogramEqualization(imgData, width, height);
        data = imgData.data;
      }

      // 4. Median Denoise
      if (params.medianDenoise > 0) {
        imgData = this.medianFilter(imgData, width, height, params.medianDenoise);
        data = imgData.data;
      }

      // 5. Sharpen
      if (params.sharpen > 0) {
        imgData = this.sharpenFilter(imgData, width, height, params.sharpen);
        data = imgData.data;
      }

      // 6. Edge Detection
      if (params.edgeDetection && params.edgeDetection !== 'none') {
        imgData = this.detectEdges(imgData, width, height, params.edgeDetection, params.edgeStrength || 1);
        data = imgData.data;
      }

      // 7. Emboss
      if (params.emboss) {
        imgData = this.embossFilter(imgData, width, height, params.embossAngle || 45, params.embossStrength || 1.5);
        data = imgData.data;
      }

      // 8. Binarization
      if (params.binarize && params.binarize !== 'none') {
        imgData = this.applyThreshold(imgData, width, height, params.binarize, params.thresholdVal, params.adaptiveWindow || 15);
        data = imgData.data;
      }

      // 9. Color Map
      if (params.colorMap && params.colorMap !== 'none') {
        imgData = this.applyColorMap(imgData, width, height, params.colorMap);
        data = imgData.data;
      }

      ctx.putImageData(imgData, 0, 0);
      return offscreen;
    }

    static histogramEqualization(imgData, width, height) {
      const data = imgData.data;
      const numPixels = width * height;
      const hist = new Int32Array(256);

      for (let i = 0; i < data.length; i += 4) {
        const v = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
        hist[v]++;
      }

      let cum = 0, cdfMin = -1;
      const cdf = new Float32Array(256);
      for (let i = 0; i < 256; i++) {
        cum += hist[i];
        cdf[i] = cum;
        if (cum > 0 && cdfMin === -1) cdfMin = cum;
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
          rBuf.sort(); gBuf.sort(); bBuf.sort();
          const dstIdx = (y * width + x) * 4;
          dst[dstIdx] = rBuf[mid];
          dst[dstIdx + 1] = gBuf[mid];
          dst[dstIdx + 2] = bBuf[mid];
        }
      }
      return imgData;
    }

    static sharpenFilter(imgData, width, height, strength = 1) {
      const src = new Uint8ClampedArray(imgData.data);
      const dst = imgData.data;
      const s = strength;
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

    static detectEdges(imgData, width, height, mode, strength = 1) {
      const src = new Uint8ClampedArray(imgData.data);
      const dst = imgData.data;
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
        const dilated = new Float32Array(width * height);
        const eroded = new Float32Array(width * height);
        for (let y = 1; y < height - 1; y++) {
          for (let x = 1; x < width - 1; x++) {
            let maxV = -Infinity, minV = Infinity;
            for (let dy = -1; dy <= 1; dy++) {
              for (let dx = -1; dx <= 1; dx++) {
                const v = gray[(y + dy) * width + (x + dx)];
                if (v > maxV) maxV = v;
                if (v < minV) minV = v;
              }
            }
            const idx = y * width + x;
            dilated[idx] = maxV;
            eroded[idx] = minV;
          }
        }
        for (let i = 0; i < gray.length; i++) {
          const grad = Math.min(255, (dilated[i] - eroded[i]) * strength * 1.5);
          const dstIdx = i * 4;
          dst[dstIdx] = grad; dst[dstIdx + 1] = grad; dst[dstIdx + 2] = grad;
        }
      }
      return imgData;
    }

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

    static applyThreshold(imgData, width, height, mode, thresholdVal = 128, windowSize = 15) {
      const data = imgData.data;
      const gray = new Uint8Array(width * height);

      for (let i = 0; i < gray.length; i++) {
        const idx = i * 4;
        gray[i] = Math.round(0.299 * data[idx] + 0.587 * data[idx + 1] + 0.114 * data[idx + 2]);
      }

      if (mode === 'otsu') {
        const hist = new Int32Array(256);
        for (let i = 0; i < gray.length; i++) hist[gray[i]]++;
        let sum = 0;
        for (let i = 0; i < 256; i++) sum += i * hist[i];
        let sumB = 0, wB = 0, wF = 0, maxVar = 0;
        thresholdVal = 128;
        for (let t = 0; t < 256; t++) {
          wB += hist[t];
          if (wB === 0) continue;
          wF = gray.length - wB;
          if (wF === 0) break;
          sumB += t * hist[t];
          const mB = sumB / wB;
          const mF = (sum - sumB) / wF;
          const v = wB * wF * (mB - mF) * (mB - mF);
          if (v > maxVar) {
            maxVar = v;
            thresholdVal = t;
          }
        }
      }

      if (mode === 'adaptive') {
        const S = Math.max(3, Math.round(windowSize));
        const s2 = Math.floor(S / 2);
        const T = 0.15;
        const integral = new Float64Array(width * height);

        for (let x = 0; x < width; x++) {
          let sum = 0;
          for (let y = 0; y < height; y++) {
            const idx = y * width + x;
            sum += gray[idx];
            integral[idx] = x === 0 ? sum : integral[idx - 1] + sum;
          }
        }

        for (let y = 0; y < height; y++) {
          for (let x = 0; x < width; x++) {
            const x1 = Math.max(0, x - s2), x2 = Math.min(width - 1, x + s2);
            const y1 = Math.max(0, y - s2), y2 = Math.min(height - 1, y + s2);
            const count = (x2 - x1 + 1) * (y2 - y1 + 1);
            let sum = integral[y2 * width + x2];
            if (x1 > 0) sum -= integral[y2 * width + (x1 - 1)];
            if (y1 > 0) sum -= integral[(y1 - 1) * width + x2];
            if (x1 > 0 && y1 > 0) sum += integral[(y1 - 1) * width + (x1 - 1)];

            const idx = y * width + x;
            const val = (gray[idx] * count) < (sum * (1.0 - T)) ? 0 : 255;
            data[idx * 4] = val; data[idx * 4 + 1] = val; data[idx * 4 + 2] = val;
          }
        }
        return imgData;
      }

      for (let i = 0; i < gray.length; i++) {
        const val = gray[i] >= thresholdVal ? 255 : 0;
        data[i * 4] = val; data[i * 4 + 1] = val; data[i * 4 + 2] = val;
      }
      return imgData;
    }

    static applyColorMap(imgData, width, height, mapName) {
      const data = imgData.data;
      for (let i = 0; i < data.length; i += 4) {
        const g = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
        const norm = g / 255;
        let r = 0, gr = 0, b = 0;

        switch (mapName) {
          case 'heatmap':
            r = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(norm * 4 - 3))));
            gr = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(norm * 4 - 2))));
            b = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(norm * 4 - 1))));
            break;
          case 'sandstone':
            r = Math.min(255, norm * 260 + 20);
            gr = Math.min(255, norm * 180 + 10);
            b = Math.min(255, norm * 100);
            break;
          case 'obsidian':
            r = Math.min(255, Math.pow(norm, 2) * 50);
            gr = Math.min(255, Math.pow(norm, 1.5) * 255);
            b = Math.min(255, norm * 255 + 50);
            break;
          case 'ironbow':
            r = Math.min(255, Math.sin(norm * Math.PI) * 255 + (norm > 0.5 ? (norm - 0.5) * 510 : 0));
            gr = Math.min(255, Math.pow(norm, 2) * 255);
            b = Math.min(255, Math.cos(norm * Math.PI / 2) * 255);
            break;
          case 'nightvision':
            r = 0; gr = Math.min(255, norm * 280); b = Math.min(255, norm * 60);
            break;
          default:
            r = data[i]; gr = data[i + 1]; b = data[i + 2];
        }
        data[i] = r; data[i + 1] = gr; data[i + 2] = b;
      }
      return imgData;
    }

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

  // =========================================================================
  // 3. DATASET EXPORTER
  // =========================================================================
  class DatasetExporter {
    static toYOLO(annotations, imageWidth, imageHeight) {
      const lines = [];
      for (const ann of annotations) {
        if (ann.type !== 'rect' && ann.type !== 'box') continue;
        const xc = Math.max(0, Math.min(1, (ann.x + ann.width / 2) / imageWidth)).toFixed(6);
        const yc = Math.max(0, Math.min(1, (ann.y + ann.height / 2) / imageHeight)).toFixed(6);
        const nw = Math.max(0, Math.min(1, ann.width / imageWidth)).toFixed(6);
        const nh = Math.max(0, Math.min(1, ann.height / imageHeight)).toFixed(6);
        lines.push(`${ann.classId} ${xc} ${yc} ${nw} ${nh}`);
      }
      return lines.join('\n');
    }

    static fromYOLO(yoloText, imageWidth, imageHeight, classes) {
      const lines = yoloText.trim().split(/\r?\n/);
      const annotations = [];
      lines.forEach((line, index) => {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 5) {
          const classId = parseInt(parts[0], 10);
          const xc = parseFloat(parts[1]) * imageWidth;
          const yc = parseFloat(parts[2]) * imageHeight;
          const w = parseFloat(parts[3]) * imageWidth;
          const h = parseFloat(parts[4]) * imageHeight;

          const cls = classes.find(c => c.id === classId) || {
            id: classId,
            char: `${classId}`,
            name_ar: `فئة ${classId}`,
            name_en: `Class ${classId}`
          };

          annotations.push({
            id: `ann_${Date.now()}_${index}`,
            type: 'rect',
            x: Math.max(0, xc - w / 2),
            y: Math.max(0, yc - h / 2),
            width: Math.min(imageWidth, w),
            height: Math.min(imageHeight, h),
            classId: classId,
            className: cls.name_ar || cls.name_en || cls.char,
            char: cls.char,
            locked: false,
            visible: true
          });
        }
      });
      return annotations;
    }

    static toYOLOyaml(classes) {
      let yaml = `# Dataset configuration for YOLO\npath: ./inscriptions_dataset\ntrain: images/train\nval: images/val\n\nnc: ${classes.length}\nnames:\n`;
      classes.forEach((cls) => {
        yaml += `  ${cls.id}: '${cls.name_en || cls.name_ar || cls.char}'\n`;
      });
      return yaml;
    }

    static cropAnnotations(sourceCanvas, annotations, padding = 4) {
      const crops = [];
      const srcW = sourceCanvas.width;
      const srcH = sourceCanvas.height;

      annotations.forEach((ann, idx) => {
        if (ann.type !== 'rect' && ann.type !== 'box') return;
        const x = Math.max(0, ann.x - padding);
        const y = Math.max(0, ann.y - padding);
        const w = Math.min(srcW - x, ann.width + padding * 2);
        const h = Math.min(srcH - y, ann.height + padding * 2);
        if (w <= 0 || h <= 0) return;

        const cropCanvas = document.createElement('canvas');
        cropCanvas.width = Math.round(w);
        cropCanvas.height = Math.round(h);
        const ctx = cropCanvas.getContext('2d');
        ctx.drawImage(sourceCanvas, Math.round(x), Math.round(y), Math.round(w), Math.round(h), 0, 0, Math.round(w), Math.round(h));

        crops.push({
          index: idx,
          classId: ann.classId,
          char: ann.char || `${ann.classId}`,
          canvas: cropCanvas
        });
      });
      return crops;
    }

    static downloadBlob(blob, filename) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    static downloadText(content, filename, mimeType = 'text/plain;charset=utf-8') {
      const blob = new Blob([content], { type: mimeType });
      this.downloadBlob(blob, filename);
    }
  }

  // =========================================================================
  // 4. INTERACTIVE CANVAS LABELER
  // =========================================================================
  class LabelingCanvas {
    constructor(canvasElement, options = {}) {
      this.canvas = canvasElement;
      this.ctx = canvasElement.getContext('2d');
      this.originalImage = null;
      this.processedCanvas = null;

      this.scale = 1;
      this.panX = 0;
      this.panY = 0;
      this.minScale = 0.05;
      this.maxScale = 30;

      this.activeTool = 'rect';
      this.activeClassId = 0;
      this.classes = [];

      this.annotations = [];
      this.selectedAnnotation = null;
      this.hoveredAnnotation = null;
      this.hoveredHandle = null;

      this.isMouseDown = false;
      this.isPanning = false;
      this.isDrawingRect = false;
      this.isDraggingAnnotation = false;
      this.isResizingHandle = false;

      this.dragStartX = 0;
      this.dragStartY = 0;
      this.initialAnnState = null;
      this.currentRect = null;
      this.currentPolygonPoints = [];

      this.splitView = false;
      this.splitPos = 0.5;
      this.isDraggingSplit = false;

      this.cursorX = 0;
      this.cursorY = 0;
      this.showCrosshair = true;

      this.history = [];
      this.historyIndex = -1;

      this.onSelectionChange = options.onSelectionChange || (() => {});
      this.onAnnotationsChange = options.onAnnotationsChange || (() => {});
      this.onZoomChange = options.onZoomChange || (() => {});

      this.initEvents();
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
      let newScale = Math.max(this.minScale, Math.min(this.maxScale, this.scale * factor));
      const cx = clientCenterX !== null ? clientCenterX : this.canvas.width / 2;
      const cy = clientCenterY !== null ? clientCenterY : this.canvas.height / 2;

      const imgX = (cx - this.panX) / prevScale;
      const imgY = (cy - this.panY) / prevScale;

      this.scale = newScale;
      this.panX = cx - imgX * this.scale;
      this.panY = cy - imgY * this.scale;

      this.onZoomChange(this.scale);
      this.render();
    }

    screenToImage(sx, sy) {
      return { x: (sx - this.panX) / this.scale, y: (sy - this.panY) / this.scale };
    }

    imageToScreen(ix, iy) {
      return { x: ix * this.scale + this.panX, y: iy * this.scale + this.panY };
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

    initEvents() {
      const c = this.canvas;
      c.addEventListener('wheel', (e) => {
        e.preventDefault();
        const { sx: mx, sy: my } = this.getCanvasCoords(e);
        this.zoom(e.deltaY < 0 ? 1.15 : 0.87, mx, my);
      }, { passive: false });

      c.addEventListener('mousedown', (e) => this.handleMouseDown(e));
      window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
      window.addEventListener('mouseup', (e) => this.handleMouseUp(e));
      c.addEventListener('dblclick', () => {
        if (this.activeTool === 'polygon' && this.currentPolygonPoints.length >= 3) {
          this.finishPolygon();
        }
      });
      c.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    handleMouseDown(e) {
      const { sx, sy } = this.getCanvasCoords(e);
      const imgPt = this.screenToImage(sx, sy);

      this.cursorX = sx;
      this.cursorY = sy;
      this.isMouseDown = true;

      if (e.button === 1 || e.button === 2 || this.activeTool === 'pan' || e.spaceKey) {
        this.isPanning = true;
        this.dragStartX = sx;
        this.dragStartY = sy;
        this.canvas.style.cursor = 'grabbing';
        return;
      }

      if (e.button !== 0) return;

      if (this.splitView) {
        const splitScreenX = this.splitPos * this.canvas.width;
        if (Math.abs(sx - splitScreenX) < 12) {
          this.isDraggingSplit = true;
          return;
        }
      }

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

      if (this.activeTool === 'rect') {
        this.isDrawingRect = true;
        this.dragStartX = imgPt.x;
        this.dragStartY = imgPt.y;
        this.currentRect = { x: imgPt.x, y: imgPt.y, width: 0, height: 0 };
        this.selectAnnotation(null);
        this.render();
        return;
      }

      if (this.activeTool === 'polygon') {
        if (this.currentPolygonPoints.length > 2) {
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

      if (this.isPanning) {
        this.panX += (sx - this.dragStartX);
        this.panY += (sy - this.dragStartY);
        this.dragStartX = sx;
        this.dragStartY = sy;
        this.render();
        return;
      }

      if (this.isDraggingSplit) {
        this.splitPos = Math.max(0.02, Math.min(0.98, sx / this.canvas.width));
        this.render();
        return;
      }

      if (this.isDrawingRect && this.currentRect) {
        this.currentRect = {
          x: Math.min(this.dragStartX, imgPt.x),
          y: Math.min(this.dragStartY, imgPt.y),
          width: Math.abs(imgPt.x - this.dragStartX),
          height: Math.abs(imgPt.y - this.dragStartY)
        };
        this.render();
        return;
      }

      if (this.isResizingHandle && this.selectedAnnotation && this.initialAnnState) {
        const dx = imgPt.x - this.dragStartX;
        const dy = imgPt.y - this.dragStartY;
        this.resizeHandle(this.selectedAnnotation, this.initialAnnState, this.hoveredHandle, dx, dy);
        this.render();
        return;
      }

      if (this.isDraggingAnnotation && this.selectedAnnotation && this.initialAnnState) {
        this.selectedAnnotation.x = this.initialAnnState.x + (imgPt.x - this.dragStartX);
        this.selectedAnnotation.y = this.initialAnnState.y + (imgPt.y - this.dragStartY);
        this.render();
        return;
      }

      if (this.selectedAnnotation && !this.selectedAnnotation.locked) {
        const handle = this.getHandleAt(sx, sy, this.selectedAnnotation);
        if (handle) {
          this.hoveredHandle = handle;
          this.canvas.style.cursor = handle.includes('nw') || handle.includes('se') ? 'nwse-resize' :
                                    handle.includes('ne') || handle.includes('sw') ? 'nesw-resize' :
                                    handle.includes('n') || handle.includes('s') ? 'ns-resize' : 'ew-resize';
          this.render();
          return;
        }
      }
      this.hoveredHandle = null;

      const hit = this.getAnnotationAt(imgPt.x, imgPt.y);
      this.hoveredAnnotation = hit;
      this.canvas.style.cursor = this.activeTool === 'select' ? (hit ? 'move' : 'default') :
                                this.activeTool === 'pan' ? 'grab' : 'crosshair';
      this.render();
    }

    handleMouseUp() {
      if (this.isPanning) this.isPanning = false;
      if (this.isDraggingSplit) this.isDraggingSplit = false;

      if (this.isDrawingRect && this.currentRect) {
        if (this.currentRect.width > 6 && this.currentRect.height > 6) {
          const cls = this.classes.find(c => c.id === this.activeClassId) || {
            id: this.activeClassId, char: `${this.activeClassId}`, name_ar: `فئة ${this.activeClassId}`, name_en: `Class ${this.activeClassId}`
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

    finishPolygon() {
      if (this.currentPolygonPoints.length < 3) return;
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      this.currentPolygonPoints.forEach(p => {
        minX = Math.min(minX, p.x); minY = Math.min(minY, p.y);
        maxX = Math.max(maxX, p.x); maxY = Math.max(maxY, p.y);
      });

      const cls = this.classes.find(c => c.id === this.activeClassId) || {
        id: this.activeClassId, char: `${this.activeClassId}`, name_ar: `فئة ${this.activeClassId}`, name_en: `Class ${this.activeClassId}`
      };

      const newAnn = {
        id: `ann_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
        type: 'polygon',
        points: [...this.currentPolygonPoints],
        x: Math.round(minX), y: Math.round(minY),
        width: Math.round(maxX - minX), height: Math.round(maxY - minY),
        classId: this.activeClassId,
        className: cls.name_ar || cls.name_en || cls.char,
        char: cls.char,
        locked: false, visible: true
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
      dup.x += 15; dup.y += 15;
      if (dup.points) dup.points = dup.points.map(p => ({ x: p.x + 15, y: p.y + 15 }));
      this.annotations.push(dup);
      this.selectAnnotation(dup);
      this.saveHistory('Duplicate Annotation');
      this.onAnnotationsChange(this.annotations);
      this.render();
    }

    clearAnnotations() {
      this.annotations = [];
      this.selectAnnotation(null);
      this.saveHistory('Clear All');
      this.onAnnotationsChange(this.annotations);
      this.render();
    }

    setAnnotations(anns) {
      this.annotations = anns || [];
      this.selectAnnotation(null);
      this.saveHistory('Load Annotations');
      this.onAnnotationsChange(this.annotations);
      this.render();
    }

    saveHistory() {
      if (this.historyIndex < this.history.length - 1) {
        this.history = this.history.slice(0, this.historyIndex + 1);
      }
      this.history.push(JSON.stringify(this.annotations));
      if (this.history.length > 40) this.history.shift();
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
      this.saveHistory();
    }

    getHandles(ann) {
      const { x, y, width: w, height: h } = ann;
      return [
        { name: 'nw', x: x, y: y }, { name: 'n', x: x + w / 2, y: y },
        { name: 'ne', x: x + w, y: y }, { name: 'e', x: x + w, y: y + h / 2 },
        { name: 'se', x: x + w, y: y + h }, { name: 's', x: x + w / 2, y: y + h },
        { name: 'sw', x: x, y: y + h }, { name: 'w', x: x, y: y + h / 2 }
      ];
    }

    getHandleAt(sx, sy, ann) {
      if (ann.type !== 'rect') return null;
      const handles = this.getHandles(ann);
      for (const h of handles) {
        const scr = this.imageToScreen(h.x, h.y);
        if (Math.hypot(sx - scr.x, sy - scr.y) <= 8) return h.name;
      }
      return null;
    }

    resizeHandle(ann, initial, handle, dx, dy) {
      let { x, y, width: w, height: h } = initial;
      if (handle.includes('e')) w += dx;
      if (handle.includes('s')) h += dy;
      if (handle.includes('w')) { x += dx; w -= dx; }
      if (handle.includes('n')) { y += dy; h -= dy; }
      ann.x = Math.round(x); ann.y = Math.round(y);
      ann.width = Math.max(4, Math.round(w)); ann.height = Math.max(4, Math.round(h));
    }

    getAnnotationAt(ix, iy) {
      for (let i = this.annotations.length - 1; i >= 0; i--) {
        const ann = this.annotations[i];
        if (!ann.visible) continue;
        if (ann.type === 'rect') {
          if (ix >= ann.x && ix <= ann.x + ann.width && iy >= ann.y && iy <= ann.y + ann.height) return ann;
        }
      }
      return null;
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      ctx.clearRect(0, 0, w, h);

      // Dark grid background
      ctx.fillStyle = '#0a0e17';
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = '#141c2b';
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 32) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
      for (let y = 0; y < h; y += 32) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

      if (!this.processedCanvas) return;

      ctx.save();
      ctx.translate(this.panX, this.panY);
      ctx.scale(this.scale, this.scale);
      ctx.imageSmoothingEnabled = this.scale < 4;

      if (this.splitView && this.originalImage) {
        const splitImgX = (this.splitPos * w - this.panX) / this.scale;
        ctx.save();
        ctx.beginPath();
        ctx.rect(0, 0, splitImgX, this.processedCanvas.height);
        ctx.clip();
        ctx.drawImage(this.processedCanvas, 0, 0);
        ctx.restore();

        ctx.save();
        ctx.beginPath();
        ctx.rect(splitImgX, 0, this.processedCanvas.width - splitImgX, this.processedCanvas.height);
        ctx.clip();
        ctx.drawImage(this.originalImage, 0, 0);
        ctx.restore();
      } else {
        ctx.drawImage(this.processedCanvas, 0, 0);
      }

      // Draw annotations
      for (const ann of this.annotations) {
        if (!ann.visible) continue;
        const isSel = this.selectedAnnotation && this.selectedAnnotation.id === ann.id;
        const color = getClassColor(ann.classId);

        ctx.save();
        ctx.lineWidth = (isSel ? 3 : 1.5) / this.scale;
        ctx.strokeStyle = isSel ? '#00f5d4' : color;
        ctx.fillStyle = isSel ? `${color}40` : `${color}20`;

        if (ann.type === 'rect') {
          ctx.fillRect(ann.x, ann.y, ann.width, ann.height);
          ctx.strokeRect(ann.x, ann.y, ann.width, ann.height);

          // Badge
          const labelText = ann.char ? `${ann.char} ${ann.className || ''}` : (ann.className || `Class ${ann.classId}`);
          const fontSize = Math.max(11 / this.scale, 13 / this.scale);
          ctx.font = `bold ${fontSize}px 'Cairo', sans-serif`;
          const textMetrics = ctx.measureText(labelText);
          const badgeW = textMetrics.width + 12 / this.scale;
          const badgeH = fontSize + 8 / this.scale;

          ctx.fillStyle = isSel ? '#00f5d4' : color;
          ctx.fillRect(ann.x, ann.y - badgeH, badgeW, badgeH);
          ctx.fillStyle = '#05070a';
          ctx.fillText(labelText, ann.x + 6 / this.scale, ann.y - 4 / this.scale);

          if (isSel && !ann.locked) {
            const handles = this.getHandles(ann);
            const hs = 7 / this.scale;
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#00f5d4';
            ctx.lineWidth = 1.5 / this.scale;
            handles.forEach(hd => {
              ctx.fillRect(hd.x - hs / 2, hd.y - hs / 2, hs, hs);
              ctx.strokeRect(hd.x - hs / 2, hd.y - hs / 2, hs, hs);
            });
          }
        }
        ctx.restore();
      }

      if (this.isDrawingRect && this.currentRect) {
        const color = getClassColor(this.activeClassId);
        ctx.strokeStyle = color;
        ctx.lineWidth = 2 / this.scale;
        ctx.fillStyle = `${color}33`;
        ctx.fillRect(this.currentRect.x, this.currentRect.y, this.currentRect.width, this.currentRect.height);
        ctx.strokeRect(this.currentRect.x, this.currentRect.y, this.currentRect.width, this.currentRect.height);
      }

      ctx.restore();

      // Split slider
      if (this.splitView) {
        const splitX = this.splitPos * w;
        ctx.strokeStyle = '#00f5d4';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(splitX, 0); ctx.lineTo(splitX, h); ctx.stroke();
        ctx.fillStyle = '#00f5d4';
        ctx.beginPath(); ctx.arc(splitX, h / 2, 14, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#000'; ctx.font = 'bold 12px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText('⬌', splitX, h / 2);
        ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      }

      // Crosshairs
      if (this.showCrosshair && (this.activeTool === 'rect' || this.activeTool === 'polygon')) {
        ctx.strokeStyle = 'rgba(0, 245, 212, 0.4)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(this.cursorX, 0); ctx.lineTo(this.cursorX, h);
        ctx.moveTo(0, this.cursorY); ctx.lineTo(w, this.cursorY);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }
  }

  // =========================================================================
  // 5. MASTER CONTROLLER & UI BINDING
  // =========================================================================
  const state = {
    lang: 'ar',
    theme: 'dark',
    activePreset: 'nabataean',
    classes: [...NABATAEAN_CLASSES],
    customClasses: null,
    activeClassId: 0,
    searchQuery: '',
    images: [],
    currentImageIndex: -1,
    filters: {
      brightness: 0, contrast: 0, exposure: 0, gamma: 1.0, saturation: 0,
      invert: false, grayscale: false, equalizeHist: false, sharpen: 0,
      medianDenoise: 0, blur: 0, emboss: false, embossAngle: 45, embossStrength: 1.5,
      edgeDetection: 'none', edgeStrength: 1.0, binarize: 'none', thresholdVal: 128,
      adaptiveWindow: 15, colorMap: 'none'
    },
    rotation: 0,
    flipH: false,
    flipV: false,
    processedCanvas: null,
    splitView: false
  };

  let labeler = null;

  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : 'ℹ️');
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  function applyImageProcessing(immediate = false) {
    if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) return;
    const cur = state.images[state.currentImageIndex];
    if (!cur.originalCanvas) return;

    const transformed = FilterEngine.transformCanvas(cur.originalCanvas, state.rotation, state.flipH, state.flipV);
    const filtered = FilterEngine.applyPipeline(transformed, state.filters);

    state.processedCanvas = filtered;
    labeler.setImage(cur.originalCanvas, false);
    labeler.setProcessedCanvas(filtered);

    cur.filters = { ...state.filters };
    cur.rotation = state.rotation;
    cur.flipH = state.flipH;
    cur.flipV = state.flipV;
  }

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
            if (state.currentImageIndex === -1) selectImage(0);
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

    const empty = document.getElementById('emptyState');
    if (empty) empty.style.display = 'none';

    if (cur.filters) state.filters = { ...cur.filters };
    state.rotation = cur.rotation || 0;
    state.flipH = cur.flipH || false;
    state.flipV = cur.flipV || false;

    syncFilterControls();

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
    const counter = document.getElementById('imageCounter');
    if (counter) counter.textContent = `${current} / ${total} ${state.lang === 'ar' ? 'صور' : 'images'}`;
  }

  function updateThumbnailsUI() {
    const strip = document.getElementById('thumbStrip');
    const addBtn = document.getElementById('stripAddBtn');
    if (!strip || !addBtn) return;

    strip.innerHTML = '';
    strip.appendChild(addBtn);

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

      strip.insertBefore(card, addBtn);
    });
  }

  function setAlphabetPreset(presetKey) {
    state.activePreset = presetKey;
    if (presetKey === 'nabataean') state.classes = [...NABATAEAN_CLASSES];
    else if (presetKey === 'aramaic') state.classes = [...ARAMAIC_CLASSES];
    else if (presetKey === 'arabic') state.classes = [...ARABIC_CLASSES];
    else if (presetKey === 'custom' && state.customClasses) state.classes = [...state.customClasses];

    state.activeClassId = state.classes.length > 0 ? state.classes[0].id : 0;
    labeler.setClasses(state.classes);
    labeler.setActiveClass(state.activeClassId);

    renderCharacterGrid();
    updateClassDropdowns();
  }

  function renderCharacterGrid() {
    const grid = document.getElementById('characterGrid');
    if (!grid) return;
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

    const badge = document.getElementById('classesCountBadge');
    if (badge) badge.textContent = `${state.classes.length} ${state.lang === 'ar' ? 'فئة' : 'classes'}`;

    filtered.forEach(cls => {
      const card = document.createElement('div');
      card.className = `char-card ${cls.id === state.activeClassId ? 'active' : ''}`;

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
        const indicator = document.getElementById('activeClassIndicator');
        if (indicator) indicator.textContent = `${cls.char} (${cls.id}) - ${title.textContent}`;
      });

      grid.appendChild(card);
    });
  }

  function updateClassDropdowns() {
    const select = document.getElementById('inspectorClassSelect');
    if (!select) return;
    select.innerHTML = '';
    state.classes.forEach(cls => {
      const opt = document.createElement('option');
      opt.value = cls.id;
      const name = state.lang === 'ar' ? (cls.name_ar || cls.char) : (cls.name_en || cls.char);
      opt.textContent = `${cls.char} [${cls.id}] - ${name}`;
      select.appendChild(opt);
    });
  }

  function handleImportClassesFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const parsed = parseClassesFile(e.target.result, file.name);
      if (parsed.length === 0) {
        showToast('تعذر استخراج فئات من الملف المختار', 'error');
        return;
      }
      state.customClasses = parsed;
      const opt = document.getElementById('optCustomAlphabet');
      if (opt) opt.style.display = 'block';
      const select = document.getElementById('selectAlphabetPreset');
      if (select) select.value = 'custom';
      setAlphabetPreset('custom');
      showToast(`تم استيراد ${parsed.length} فئة بنجاح من ${file.name}`, 'success');
    };
    reader.readAsText(file);
  }

  function syncFilterControls() {
    const f = state.filters;
    const setVal = (id, val, textId = null, suffix = '') => {
      const el = document.getElementById(id);
      if (el) el.value = val;
      if (textId) {
        const tel = document.getElementById(textId);
        if (tel) tel.textContent = `${val}${suffix}`;
      }
    };
    setVal('sliderBrightness', f.brightness, 'valBrightness');
    setVal('sliderContrast', f.contrast, 'valContrast');
    setVal('sliderExposure', f.exposure, 'valExposure');
    setVal('sliderGamma', f.gamma, 'valGamma');
    setVal('sliderSaturation', f.saturation, 'valSaturation');
    setVal('sliderSharpen', f.sharpen, 'valSharpen');
    setVal('sliderMedian', f.medianDenoise, 'valMedian');
    setVal('sliderRotation', state.rotation, 'valRotation', '°');

    const inv = document.getElementById('toggleInvert'); if (inv) inv.checked = f.invert;
    const gr = document.getElementById('toggleGrayscale'); if (gr) gr.checked = f.grayscale;
    const eq = document.getElementById('toggleEqualize'); if (eq) eq.checked = f.equalizeHist;
    const emb = document.getElementById('toggleEmboss'); if (emb) emb.checked = f.emboss;

    const edge = document.getElementById('selectEdgeDetection'); if (edge) edge.value = f.edgeDetection;
    const bin = document.getElementById('selectBinarize'); if (bin) bin.value = f.binarize;
    const col = document.getElementById('selectColorMap'); if (col) col.value = f.colorMap;
  }

  function applyPreset(presetName) {
    state.filters = {
      brightness: 0, contrast: 0, exposure: 0, gamma: 1.0, saturation: 0,
      invert: false, grayscale: false, equalizeHist: false, sharpen: 0,
      medianDenoise: 0, blur: 0, emboss: false, embossAngle: 45, embossStrength: 1.5,
      edgeDetection: 'none', edgeStrength: 1.0, binarize: 'none', thresholdVal: 128,
      adaptiveWindow: 15, colorMap: 'none'
    };

    if (presetName === 'stone_boost') {
      state.filters.equalizeHist = true;
      state.filters.sharpen = 1.6;
      state.filters.contrast = 0.35;
    } else if (presetName === 'dark_invert') {
      state.filters.invert = true;
      state.filters.grayscale = true;
      state.filters.contrast = 0.45;
      state.filters.sharpen = 1.2;
    } else if (presetName === 'deep_contrast') {
      state.filters.contrast = 0.65;
      state.filters.sharpen = 1.8;
      state.filters.equalizeHist = true;
    } else if (presetName === 'otsu_clean') {
      state.filters.binarize = 'otsu';
    } else if (presetName === 'sobel_edges') {
      state.filters.edgeDetection = 'sobel';
      state.filters.edgeStrength = 1.5;
      state.filters.invert = true;
    } else if (presetName === 'sandstone_map') {
      state.filters.colorMap = 'sandstone';
      state.filters.contrast = 0.3;
    }

    syncFilterControls();
    applyImageProcessing(true);
    showToast(`تم تطبيق قالب "${presetName}"`, 'success');
  }

  function initStudio() {
    const canvasEl = document.getElementById('mainCanvas');
    if (!canvasEl) return;

    labeler = new LabelingCanvas(canvasEl, {
      onSelectionChange: (selected) => {
        const card = document.getElementById('selectedAnnCard');
        if (!card) return;
        if (!selected) { card.style.display = 'none'; return; }
        card.style.display = 'flex';
        const sel = document.getElementById('inspectorClassSelect');
        if (sel) sel.value = selected.classId;
        const coords = document.getElementById('inspectorCoords');
        if (coords) coords.textContent = `X: ${selected.x}, Y: ${selected.y}`;
        const sz = document.getElementById('inspectorSize');
        if (sz) sz.textContent = `W: ${selected.width}, H: ${selected.height}`;
      },
      onAnnotationsChange: (annotations) => {
        if (state.currentImageIndex >= 0 && state.images[state.currentImageIndex]) {
          state.images[state.currentImageIndex].annotations = annotations;
        }
        updateAnnotationsList();
      },
      onZoomChange: (scale) => {
        const z = document.getElementById('zoomLevelDisplay');
        if (z) z.textContent = `${Math.round(scale * 100)}%`;
      }
    });

    const resize = () => {
      const ws = document.getElementById('canvasWorkspace');
      if (ws) {
        canvasEl.width = ws.clientWidth;
        canvasEl.height = ws.clientHeight;
        labeler.render();
      }
    };
    resize();
    window.addEventListener('resize', resize);

    setAlphabetPreset('nabataean');
    bindAllControls();

    // Try preloading sample image
    fetch('Untitled.jpg').then(r => r.blob()).then(blob => {
      const file = new File([blob], 'nabataean_sample.jpg', { type: 'image/jpeg' });
      addImageFiles([file]);
    }).catch(() => {});

    // Expose helpers globally
    window.addImageFiles = addImageFiles;
    window.handleImportClassesFile = handleImportClassesFile;
    window.applyPreset = applyPreset;
    window.labeler = labeler;
    window.studioState = state;

    console.log('Studio bundle ready!');
  }

  function updateAnnotationsList() {
    const list = document.getElementById('annotationsList');
    if (!list) return;
    list.innerHTML = '';
    const badge = document.getElementById('annCountBadge');
    if (badge) badge.textContent = `${labeler.annotations.length} ${state.lang === 'ar' ? 'عناصر' : 'items'}`;

    labeler.annotations.forEach((ann, idx) => {
      const item = document.createElement('div');
      item.className = `ann-item ${labeler.selectedAnnotation && labeler.selectedAnnotation.id === ann.id ? 'active' : ''}`;
      item.innerHTML = `
        <div class="ann-info">
          <div class="ann-color-bar" style="background-color: ${getClassColor(ann.classId)};"></div>
          <span>${ann.char || ''} ${ann.className || `Class ${ann.classId}`} (#${idx + 1})</span>
        </div>
      `;
      item.addEventListener('click', () => labeler.selectAnnotation(ann));
      list.appendChild(item);
    });
  }

  function bindAllControls() {
    const on = (id, evt, fn) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener(evt, fn);
    };

    on('prevImageBtn', 'click', () => { if (state.currentImageIndex > 0) selectImage(state.currentImageIndex - 1); });
    on('nextImageBtn', 'click', () => { if (state.currentImageIndex < state.images.length - 1) selectImage(state.currentImageIndex + 1); });

    on('sliderRotation', 'input', (e) => {
      state.rotation = parseInt(e.target.value, 10);
      const val = document.getElementById('valRotation');
      if (val) val.textContent = `${state.rotation}°`;
      applyImageProcessing();
    });

    on('btnRotateCW', 'click', () => {
      state.rotation = (state.rotation + 90) % 360;
      if (state.rotation > 180) state.rotation -= 360;
      syncFilterControls();
      applyImageProcessing(true);
    });

    on('btnRotateCCW', 'click', () => {
      state.rotation = (state.rotation - 90) % 360;
      if (state.rotation < -180) state.rotation += 360;
      syncFilterControls();
      applyImageProcessing(true);
    });

    on('btnFlipH', 'click', () => { state.flipH = !state.flipH; applyImageProcessing(true); });
    on('btnFlipV', 'click', () => { state.flipV = !state.flipV; applyImageProcessing(true); });
    on('resetRotationBtn', 'click', () => { state.rotation = 0; state.flipH = false; state.flipV = false; syncFilterControls(); applyImageProcessing(true); });

    // Filter Sliders
    const bindSl = (id, valId, key, isInt = false) => {
      on(id, 'input', (e) => {
        state.filters[key] = isInt ? parseInt(e.target.value, 10) : parseFloat(e.target.value);
        const t = document.getElementById(valId);
        if (t) t.textContent = e.target.value;
        applyImageProcessing();
      });
    };

    bindSl('sliderBrightness', 'valBrightness', 'brightness');
    bindSl('sliderContrast', 'valContrast', 'contrast');
    bindSl('sliderExposure', 'valExposure', 'exposure');
    bindSl('sliderGamma', 'valGamma', 'gamma');
    bindSl('sliderSaturation', 'valSaturation', 'saturation');
    bindSl('sliderSharpen', 'valSharpen', 'sharpen');
    bindSl('sliderMedian', 'valMedian', 'medianDenoise', true);

    on('toggleInvert', 'change', (e) => { state.filters.invert = e.target.checked; applyImageProcessing(true); });
    on('toggleGrayscale', 'change', (e) => { state.filters.grayscale = e.target.checked; applyImageProcessing(true); });
    on('toggleEqualize', 'change', (e) => { state.filters.equalizeHist = e.target.checked; applyImageProcessing(true); });
    on('toggleEmboss', 'change', (e) => { state.filters.emboss = e.target.checked; applyImageProcessing(true); });

    on('selectEdgeDetection', 'change', (e) => { state.filters.edgeDetection = e.target.value; applyImageProcessing(true); });
    on('selectBinarize', 'change', (e) => { state.filters.binarize = e.target.value; applyImageProcessing(true); });
    on('selectColorMap', 'change', (e) => { state.filters.colorMap = e.target.value; applyImageProcessing(true); });

    document.querySelectorAll('.chip-btn[data-preset]').forEach(btn => {
      btn.addEventListener('click', () => applyPreset(btn.dataset.preset));
    });

    on('resetFiltersBtn', 'click', () => {
      state.filters = {
        brightness: 0, contrast: 0, exposure: 0, gamma: 1.0, saturation: 0,
        invert: false, grayscale: false, equalizeHist: false, sharpen: 0,
        medianDenoise: 0, blur: 0, emboss: false, embossAngle: 45, embossStrength: 1.5,
        edgeDetection: 'none', edgeStrength: 1.0, binarize: 'none', thresholdVal: 128,
        adaptiveWindow: 15, colorMap: 'none'
      };
      syncFilterControls();
      applyImageProcessing(true);
      showToast('تمت إعادة ضبط الفلاتر', 'info');
    });

    // Tools
    const tools = [
      { id: 'toolSelect', name: 'select' },
      { id: 'toolRect', name: 'rect' },
      { id: 'toolPolygon', name: 'polygon' },
      { id: 'toolPan', name: 'pan' }
    ];
    tools.forEach(t => {
      on(t.id, 'click', () => {
        tools.forEach(o => {
          const el = document.getElementById(o.id);
          if (el) el.classList.toggle('active', o.id === t.id);
        });
        labeler.setTool(t.name);
      });
    });

    on('btnUndo', 'click', () => labeler.undo());
    on('btnRedo', 'click', () => labeler.redo());
    on('btnDuplicate', 'click', () => labeler.duplicateSelected());
    on('btnDelete', 'click', () => labeler.deleteSelected());
    on('btnDeleteSelectedAnn', 'click', () => labeler.deleteSelected());
    on('btnClearAllAnn', 'click', () => labeler.clearAnnotations());

    on('btnZoomIn', 'click', () => labeler.zoom(1.25));
    on('btnZoomOut', 'click', () => labeler.zoom(0.8));
    on('btnFitScreen', 'click', () => labeler.fitToScreen());

    on('toggleSplitBtn', 'click', () => {
      state.splitView = !state.splitView;
      const b = document.getElementById('toggleSplitBtn');
      if (b) b.classList.toggle('active', state.splitView);
      labeler.setSplitView(state.splitView);
    });

    on('toggleCrosshairBtn', 'click', () => {
      labeler.showCrosshair = !labeler.showCrosshair;
      const b = document.getElementById('toggleCrosshairBtn');
      if (b) b.classList.toggle('active', labeler.showCrosshair);
      labeler.render();
    });

    on('selectAlphabetPreset', 'change', (e) => setAlphabetPreset(e.target.value));
    on('classSearchInput', 'input', (e) => { state.searchQuery = e.target.value; renderCharacterGrid(); });

    // Modals
    const expModal = document.getElementById('exportModal');
    on('openExportModalBtn', 'click', () => { if (expModal) expModal.classList.add('show'); });
    on('closeExportModalBtn', 'click', () => { if (expModal) expModal.classList.remove('show'); });
    on('closeExportModalBtn2', 'click', () => { if (expModal) expModal.classList.remove('show'); });

    const scModal = document.getElementById('shortcutsModal');
    on('shortcutsModalBtn', 'click', () => { if (scModal) scModal.classList.add('show'); });
    on('closeShortcutsModalBtn', 'click', () => { if (scModal) scModal.classList.remove('show'); });
    on('closeShortcutsModalBtn2', 'click', () => { if (scModal) scModal.classList.remove('show'); });

    // Exports
    on('btnExportYOLO', 'click', () => {
      if (state.currentImageIndex < 0) { showToast('لا توجد صورة محددة', 'error'); return; }
      const cur = state.images[state.currentImageIndex];
      const yolo = DatasetExporter.toYOLO(cur.annotations, labeler.processedCanvas.width, labeler.processedCanvas.height);
      const baseName = cur.name.replace(/\.[^/.]+$/, '');
      DatasetExporter.downloadText(yolo, `${baseName}.txt`);
      DatasetExporter.downloadText(state.classes.map(c => c.name_en || c.name_ar || c.char).join('\n'), 'classes.txt');
      DatasetExporter.downloadText(DatasetExporter.toYOLOyaml(state.classes), 'data.yaml');
      showToast('تم تصدير ملفات YOLO بنجاح', 'success');
    });

    on('btnExportImage', 'click', () => {
      if (!labeler.processedCanvas) return;
      labeler.processedCanvas.toBlob(blob => {
        DatasetExporter.downloadBlob(blob, 'enhanced_image.png');
        showToast('تم حفظ الصورة المعالجة', 'success');
      });
    });

    // Language & Theme
    on('langToggleBtn', 'click', () => {
      state.lang = state.lang === 'ar' ? 'en' : 'ar';
      document.documentElement.lang = state.lang;
      document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
      renderCharacterGrid();
      updateImageCounter();
    });

    on('themeToggleBtn', 'click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', state.theme);
      labeler.render();
    });
  }

  // Self-start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStudio);
  } else {
    initStudio();
  }
})();
