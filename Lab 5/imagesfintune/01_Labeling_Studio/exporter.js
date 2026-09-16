/**
 * exporter.js - Dataset Exporters (YOLO, VOC XML, COCO, Cropped Patches, Full ZIP)
 */

export class DatasetExporter {
  /**
   * Convert bounding boxes to YOLO txt format
   * normalized: <class_id> <x_center> <y_center> <width> <height>
   */
  static toYOLO(annotations, imageWidth, imageHeight) {
    const lines = [];
    for (const ann of annotations) {
      if (ann.type !== 'rect' && ann.type !== 'box') continue;
      
      const x_center = (ann.x + ann.width / 2) / imageWidth;
      const y_center = (ann.y + ann.height / 2) / imageHeight;
      const w = ann.width / imageWidth;
      const h = ann.height / imageHeight;

      // Clamp 0 to 1
      const xc = Math.max(0, Math.min(1, x_center)).toFixed(6);
      const yc = Math.max(0, Math.min(1, y_center)).toFixed(6);
      const nw = Math.max(0, Math.min(1, w)).toFixed(6);
      const nh = Math.max(0, Math.min(1, h)).toFixed(6);

      lines.push(`${ann.classId} ${xc} ${yc} ${nw} ${nh}`);
    }
    return lines.join('\n');
  }

  /**
   * Parse YOLO txt format into annotations
   */
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

        const x = xc - w / 2;
        const y = yc - h / 2;

        const cls = classes.find(c => c.id === classId) || {
          id: classId,
          char: `${classId}`,
          name_ar: `فئة ${classId}`,
          name_en: `Class ${classId}`
        };

        annotations.push({
          id: `ann_${Date.now()}_${index}`,
          type: 'rect',
          x: Math.max(0, x),
          y: Math.max(0, y),
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

  /**
   * Generate YOLO data.yaml configuration string
   */
  static toYOLOyaml(classes, datasetName = 'inscriptions_dataset') {
    let yaml = `# Dataset configuration for YOLO\n`;
    yaml += `path: ./${datasetName}\n`;
    yaml += `train: images/train\n`;
    yaml += `val: images/val\n`;
    yaml += `test: images/test\n\n`;
    yaml += `nc: ${classes.length}\n`;
    yaml += `names:\n`;
    classes.forEach((cls) => {
      const name = cls.name_en || cls.name_ar || cls.char;
      yaml += `  ${cls.id}: '${name}'\n`;
    });
    return yaml;
  }

  /**
   * Generate Pascal VOC XML format
   */
  static toPascalVOC(annotations, filename, imageWidth, imageHeight, classes) {
    let xml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
    xml += `<annotation>\n`;
    xml += `  <folder>images</folder>\n`;
    xml += `  <filename>${filename}</filename>\n`;
    xml += `  <size>\n`;
    xml += `    <width>${imageWidth}</width>\n`;
    xml += `    <height>${imageHeight}</height>\n`;
    xml += `    <depth>3</depth>\n`;
    xml += `  </size>\n`;
    xml += `  <segmented>0</segmented>\n`;

    for (const ann of annotations) {
      if (ann.type !== 'rect' && ann.type !== 'box') continue;
      const cls = classes.find(c => c.id === ann.classId) || { name_en: `class_${ann.classId}` };
      const name = cls.name_en || cls.name_ar || cls.char;
      
      const xmin = Math.round(Math.max(0, ann.x));
      const ymin = Math.round(Math.max(0, ann.y));
      const xmax = Math.round(Math.min(imageWidth, ann.x + ann.width));
      const ymax = Math.round(Math.min(imageHeight, ann.y + ann.height));

      xml += `  <object>\n`;
      xml += `    <name>${name}</name>\n`;
      xml += `    <pose>Unspecified</pose>\n`;
      xml += `    <truncated>0</truncated>\n`;
      xml += `    <difficult>0</difficult>\n`;
      xml += `    <bndbox>\n`;
      xml += `      <xmin>${xmin}</xmin>\n`;
      xml += `      <ymin>${ymin}</ymin>\n`;
      xml += `      <xmax>${xmax}</xmax>\n`;
      xml += `      <ymax>${ymax}</ymax>\n`;
      xml += `    </bndbox>\n`;
      xml += `  </object>\n`;
    }

    xml += `</annotation>\n`;
    return xml;
  }

  /**
   * Generate COCO format JSON
   */
  static toCOCO(items, classes) {
    // items: array of { filename, width, height, annotations, id }
    const categories = classes.map(c => ({
      id: c.id,
      name: c.name_en || c.name_ar || c.char,
      supercategory: 'inscription_character'
    }));

    const images = [];
    const cocoAnnotations = [];
    let annIdCounter = 1;

    items.forEach((item, imgIdx) => {
      const imgId = imgIdx + 1;
      images.push({
        id: imgId,
        file_name: item.filename,
        width: item.width,
        height: item.height
      });

      item.annotations.forEach(ann => {
        if (ann.type !== 'rect' && ann.type !== 'box') return;
        const bbox = [Math.round(ann.x), Math.round(ann.y), Math.round(ann.width), Math.round(ann.height)];
        const area = Math.round(ann.width * ann.height);

        cocoAnnotations.push({
          id: annIdCounter++,
          image_id: imgId,
          category_id: ann.classId,
          bbox: bbox,
          area: area,
          segmentation: [],
          iscrowd: 0
        });
      });
    });

    return JSON.stringify({
      info: {
        description: 'Ancient Inscriptions and Character Dataset',
        date_created: new Date().toISOString()
      },
      licenses: [],
      images: images,
      annotations: cocoAnnotations,
      categories: categories
    }, null, 2);
  }

  /**
   * Crop individual annotated characters into separate canvas elements
   */
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

      ctx.drawImage(
        sourceCanvas,
        Math.round(x), Math.round(y), Math.round(w), Math.round(h),
        0, 0, Math.round(w), Math.round(h)
      );

      crops.push({
        index: idx,
        classId: ann.classId,
        char: ann.char || `${ann.classId}`,
        canvas: cropCanvas,
        width: Math.round(w),
        height: Math.round(h)
      });
    });

    return crops;
  }

  /**
   * Helper to trigger browser file download
   */
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

  /**
   * Helper to download string as text file
   */
  static downloadText(content, filename, mimeType = 'text/plain;charset=utf-8') {
    const blob = new Blob([content], { type: mimeType });
    this.downloadBlob(blob, filename);
  }
}
