import 'dart:io' show Platform;
import 'dart:isolate';
import 'dart:math';
import 'dart:typed_data';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_onnxruntime/flutter_onnxruntime.dart';
import 'package:image/image.dart' as img;

import '../models/rune_detection.dart';

class _PreprocessResult {
  final Float32List floatBytes;
  final int angle;
  final int origW;
  final int origH;
  final int scanW;
  final int scanH;
  final int left;
  final int top;
  final double ratio;

  _PreprocessResult({
    required this.floatBytes,
    required this.angle,
    required this.origW,
    required this.origH,
    required this.scanW,
    required this.scanH,
    required this.left,
    required this.top,
    required this.ratio,
  });
}

class OfflineRuneService {
  // Turbo 640x640 INT8 mobile model (26MB, optimized for ARM NEON)
  static const String modelAssetPath = 'assets/models/viking_rune_model_640.onnx';
  static const int modelInputSize = 640;
  static const int numClasses = 17;
  static const int numAnchors = 8400;

  static OrtSession? _session;
  static bool _isModelLoaded = false;

  static const Map<int, Map<String, String>> runesInfo = {
    0:  {"rune": "ᚠ", "latin": "f",   "name": "fehu",      "meaning": "Wealth / Cattle"},
    1:  {"rune": "ᚢ", "latin": "u",   "name": "uruz",      "meaning": "Aurochs / Strength"},
    2:  {"rune": "ᚦ", "latin": "th",  "name": "thurisaz",  "meaning": "Giant / Thorn"},
    3:  {"rune": "ᚬ", "latin": "a",   "name": "ansuz",     "meaning": "God / Odin"},
    4:  {"rune": "ᚱ", "latin": "r",   "name": "raidho",    "meaning": "Ride / Journey"},
    5:  {"rune": "ᚴ", "latin": "k",   "name": "kaunan",    "meaning": "Ulcer / Torch"},
    6:  {"rune": "ᚼ", "latin": "h",   "name": "hagalaz",   "meaning": "Hail / Disruption"},
    7:  {"rune": "ᚾ", "latin": "n",   "name": "naudiz",    "meaning": "Need / Distress"},
    8:  {"rune": "ᛁ", "latin": "i",   "name": "isaz",      "meaning": "Ice / Stillness"},
    9:  {"rune": "ᛅ", "latin": "a",   "name": "ar_jera",   "meaning": "Year / Harvest"},
    10: {"rune": "ᛋ", "latin": "s",   "name": "sowilo",    "meaning": "Sun / Victory"},
    11: {"rune": "ᛏ", "latin": "t",   "name": "tiwaz",     "meaning": "Tyr / Justice"},
    12: {"rune": "ᛒ", "latin": "b",   "name": "berkanan",  "meaning": "Birch / Rebirth"},
    13: {"rune": "ᛉ", "latin": "m",   "name": "mannaz",    "meaning": "Human / Man"},
    14: {"rune": "ᛚ", "latin": "l",   "name": "laguz",     "meaning": "Water / Flow"},
    15: {"rune": "ᛦ", "latin": "R",   "name": "yr",        "meaning": "Yew bow / Tree"},
    16: {"rune": ":", "latin": ":",   "name": "separator", "meaning": "Word Divider"},
  };

  static String? _lastInitError;

  /// Initialize ONNX Runtime with multi-threaded CPU execution
  static Future<bool> initModel() async {
    if (_isModelLoaded && _session != null) return true;
    try {
      final ort = OnnxRuntime();

      final int cpuCores = kIsWeb ? 2 : Platform.numberOfProcessors;
      final int intraThreads = cpuCores >= 4 ? 4 : max(1, cpuCores);

      final sessionOptions = OrtSessionOptions(
        intraOpNumThreads: intraThreads,
        interOpNumThreads: 1,
        providers: [
          OrtProvider.CPU,
        ],
        useArena: true,
      );

      _session = await ort.createSessionFromAsset(
        modelAssetPath,
        options: sessionOptions,
      );
      _isModelLoaded = true;
      _lastInitError = null;
      // ignore: avoid_print
      print('⚡ [OfflineRuneService] Model initialized successfully with $intraThreads threads.');
      return true;
    } catch (e, stack) {
      _isModelLoaded = false;
      _lastInitError = '$e';
      // ignore: avoid_print
      print('DEBUG: initModel error: $e\n$stack');
      return false;
    }
  }

  static bool get isReady => _isModelLoaded;
  static String? get lastError => _lastInitError;

  /// Full detection pipeline with true parallel multi-threaded worker Isolates
  static Future<PredictionResponse> detectRunes({
    required Uint8List imageBytes,
    double confThreshold = 0.18,
    bool enable4Way = false,
  }) async {
    final totalSw = Stopwatch()..start();

    final ready = await initModel();
    if (!ready || _session == null) {
      throw Exception('تعذر تحميل موديل الفايكنج: $_lastInitError');
    }

    final rotations = <int>[0];
    if (enable4Way) {
      rotations.addAll([180, 90, 270]);
    }

    // 1. True Parallel Multi-Threading: Process all angles concurrently across worker Isolates
    final prepSw = Stopwatch()..start();
    final preprocessedTasks = await Future.wait(
      rotations.map((angle) => _preprocessAngleWorker(
        imageBytes: imageBytes,
        angle: angle,
      )),
    );
    prepSw.stop();

    final origW = preprocessedTasks.first.origW;
    final origH = preprocessedTasks.first.origH;

    // ignore: avoid_print
    print('⚡ [TIMING] Parallel Worker Isolates (${rotations.length} threads): ${prepSw.elapsedMilliseconds}ms (${origW}x$origH)');

    final allAccepted = <Map<String, dynamic>>[];
    final stats = {0: 0, 90: 0, 180: 0, 270: 0};

    // 2. High-speed ONNX inference pass for each angle
    final infSw = Stopwatch()..start();
    for (final prep in preprocessedTasks) {
      final inputTensor = await OrtValue.fromList(
        prep.floatBytes,
        [1, 3, modelInputSize, modelInputSize],
      );

      final outputs = await _session!.run({'images': inputTensor});
      inputTensor.dispose();

      final outputTensor = outputs['output0'];
      if (outputTensor == null) {
        throw Exception('لم يتم العثور على مخرجات الموديل (output0).');
      }

      final rawFlat = await outputTensor.asFlattenedList();
      outputTensor.dispose();

      // 3. Direct parsing and NMS
      final detections = _parseAndNmsDirect(
        flat: rawFlat,
        confThreshold: confThreshold,
        scanW: prep.scanW,
        scanH: prep.scanH,
        left: prep.left,
        top: prep.top,
        ratio: prep.ratio,
        numAnchors: numAnchors,
      );

      for (final det in detections) {
        final rBox = det['box'] as List<double>;
        final origBox = _transformBoxToOriginal(
          box: rBox,
          angle: prep.angle,
          scanW: prep.scanW,
          scanH: prep.scanH,
          origW: origW,
          origH: origH,
        );

        final cx = (origBox[0] + origBox[2]) * 0.5;
        final cy = (origBox[1] + origBox[3]) * 0.5;

        // Smart Geometric Suppression: Discard duplicate detections across angles
        bool overlap = false;
        for (final accepted in allAccepted) {
          final acceptedBox = accepted['box'] as List<double>;
          final iou = _calculateIoU(origBox, acceptedBox);
          if (iou > 0.18 || _isPointInside(cx, cy, acceptedBox)) {
            overlap = true;
            break;
          }
        }

        if (overlap) continue;

        final clsId = det['clsId'] as int;
        final conf = det['conf'] as double;
        final info = runesInfo[clsId] ?? {
          "rune": "?",
          "latin": "?",
          "name": "unknown",
          "meaning": ""
        };

        allAccepted.add({
          "cls_id": clsId,
          "name": info["name"],
          "rune": info["rune"],
          "latin": info["latin"],
          "meaning": info["meaning"] ?? "",
          "conf": double.parse(conf.toStringAsFixed(4)),
          "angle": prep.angle,
          "box": [
            double.parse(origBox[0].toStringAsFixed(1)),
            double.parse(origBox[1].toStringAsFixed(1)),
            double.parse(origBox[2].toStringAsFixed(1)),
            double.parse(origBox[3].toStringAsFixed(1)),
          ],
          "cx": double.parse(cx.toStringAsFixed(1)),
          "cy": double.parse(cy.toStringAsFixed(1)),
        });

        stats[prep.angle] = (stats[prep.angle] ?? 0) + 1;
      }
    }
    infSw.stop();

    // Sort detections in natural reading order: primary by Y ribbon, then by X
    allAccepted.sort((a, b) {
      final ay = ((a['cy'] as double) / 60.0).round();
      final by = ((b['cy'] as double) / 60.0).round();
      if (ay != by) return ay.compareTo(by);
      return (a['cx'] as double).compareTo(b['cx'] as double);
    });

    final runicText = allAccepted.map((d) => d['rune'] as String).join();
    final latinTranslit = allAccepted.map((d) => d['latin'] as String).join();

    totalSw.stop();
    // ignore: avoid_print
    print('⚡ [TIMING] Inference & NMS: ${infSw.elapsedMilliseconds}ms | 🏁 TOTAL PIPELINE: ${totalSw.elapsedMilliseconds}ms (${(totalSw.elapsedMilliseconds / 1000).toStringAsFixed(2)}s)');

    final runeDetections = allAccepted.map((d) => RuneDetection.fromJson(d)).toList();

    return PredictionResponse(
      success: true,
      width: origW,
      height: origH,
      totalRunes: runeDetections.length,
      stats: ScanStats(
        angle0: stats[0] ?? 0,
        angle90: stats[90] ?? 0,
        angle180: stats[180] ?? 0,
        angle270: stats[270] ?? 0,
        total: runeDetections.length,
      ),
      runicText: runicText,
      transliteration: latinTranslit,
      detections: runeDetections,
      annotatedImage: "", // Interactive canvas renders vector bounding boxes with 60fps GPU acceleration
    );
  }

  // ==========================================
  // Direct High-Speed Parsing (Single-Pass 1D)
  // ==========================================

  static List<Map<String, dynamic>> _parseAndNmsDirect({
    required List<dynamic> flat,
    required double confThreshold,
    required int scanW,
    required int scanH,
    required int left,
    required int top,
    required double ratio,
    required int numAnchors,
  }) {
    final candidates = <Map<String, dynamic>>[];

    final int cxOffset = 0 * numAnchors;
    final int cyOffset = 1 * numAnchors;
    final int wOffset  = 2 * numAnchors;
    final int hOffset  = 3 * numAnchors;
    final int clsOffset = 4 * numAnchors;

    final double invRatio = 1.0 / ratio;

    for (int col = 0; col < numAnchors; col++) {
      double maxConf = 0.0;
      int maxClass = -1;

      for (int c = 0; c < numClasses; c++) {
        final double score = (flat[clsOffset + c * numAnchors + col] as num).toDouble();
        if (score > maxConf) {
          maxConf = score;
          maxClass = c;
        }
      }

      if (maxConf >= confThreshold) {
        final double cx = (flat[cxOffset + col] as num).toDouble();
        final double cy = (flat[cyOffset + col] as num).toDouble();
        final double w  = (flat[wOffset + col] as num).toDouble();
        final double h  = (flat[hOffset + col] as num).toDouble();

        final double halfW = w * 0.5;
        final double halfH = h * 0.5;

        final double canvasX1 = cx - halfW;
        final double canvasY1 = cy - halfH;
        final double canvasX2 = cx + halfW;
        final double canvasY2 = cy + halfH;

        final double sX1 = ((canvasX1 - left) * invRatio).clamp(0.0, scanW.toDouble());
        final double sY1 = ((canvasY1 - top) * invRatio).clamp(0.0, scanH.toDouble());
        final double sX2 = ((canvasX2 - left) * invRatio).clamp(0.0, scanW.toDouble());
        final double sY2 = ((canvasY2 - top) * invRatio).clamp(0.0, scanH.toDouble());

        candidates.add({
          'box': [sX1, sY1, sX2, sY2],
          'conf': maxConf,
          'clsId': maxClass,
        });
      }
    }

    if (candidates.isEmpty) return [];

    // Sort by confidence descending
    candidates.sort((a, b) => (b['conf'] as double).compareTo(a['conf'] as double));

    // NMS suppression
    final nmsDetections = <Map<String, dynamic>>[];
    for (final cand in candidates) {
      final candBox = cand['box'] as List<double>;
      bool suppress = false;
      for (final selected in nmsDetections) {
        final iou = _calculateIoU(candBox, selected['box'] as List<double>);
        if (cand['clsId'] == selected['clsId']) {
          if (iou > 0.45) {
            suppress = true;
            break;
          }
        } else {
          if (iou > 0.70) {
            suppress = true;
            break;
          }
        }
      }
      if (!suppress) {
        nmsDetections.add(cand);
        if (nmsDetections.length >= 80) break;
      }
    }

    return nmsDetections;
  }

  // ==========================================
  // Background Worker Isolates (Parallel Preprocessing)
  // ==========================================

  /// High-speed worker isolate: decodes, rotates, letterboxes to 640x640,
  /// and converts RGB to normalized Float32 in a single pass without memory copying.
  static Future<_PreprocessResult> _preprocessAngleWorker({
    required Uint8List imageBytes,
    required int angle,
  }) async {
    return await Isolate.run(() {
      final decoded = img.decodeImage(imageBytes);
      if (decoded == null) {
        throw Exception('فشل في فك تشفير صورة الإدخال.');
      }

      final int origW = decoded.width;
      final int origH = decoded.height;

      // 1. Rotate if needed for 4-Way TTA
      img.Image scanImg;
      if (angle == 90) {
        scanImg = img.copyRotate(decoded, angle: 90);
      } else if (angle == 180) {
        scanImg = img.copyRotate(decoded, angle: 180);
      } else if (angle == 270) {
        scanImg = img.copyRotate(decoded, angle: 270);
      } else {
        scanImg = decoded;
      }

      final int scanW = scanImg.width;
      final int scanH = scanImg.height;

      // 2. Compute aspect-preserving letterbox parameters to fit modelInputSize (640)
      final double r = min(
        modelInputSize / scanW.toDouble(),
        modelInputSize / scanH.toDouble(),
      );
      final int newUnpadW = (scanW * r).round();
      final int newUnpadH = (scanH * r).round();

      final double padX = (modelInputSize - newUnpadW) * 0.5;
      final double padY = (modelInputSize - newUnpadH) * 0.5;
      final int left = (padX - 0.1).round();
      final int top = (padY - 0.1).round();

      // Fast linear resize
      final img.Image resized = (scanW == newUnpadW && scanH == newUnpadH)
          ? scanImg
          : img.copyResize(
              scanImg,
              width: newUnpadW,
              height: newUnpadH,
              interpolation: img.Interpolation.linear,
            );

      // Create model input canvas padded with 114 gray
      final letterboxImg = img.Image(
        width: modelInputSize,
        height: modelInputSize,
        numChannels: 3,
      );
      img.fill(letterboxImg, color: img.ColorRgb8(114, 114, 114));
      img.compositeImage(letterboxImg, resized, dstX: left, dstY: top);

      // 3. Fast normalized Float32 planar array (1 x 3 x 640 x 640)
      final floatBytes = Float32List(1 * 3 * modelInputSize * modelInputSize);
      final planeSize = modelInputSize * modelInputSize;
      final rgbBytes = letterboxImg.getBytes(order: img.ChannelOrder.rgb);
      const double inv255 = 1.0 / 255.0;

      for (int i = 0; i < planeSize; i++) {
        final pi = i * 3;
        floatBytes[i] = rgbBytes[pi] * inv255;
        floatBytes[planeSize + i] = rgbBytes[pi + 1] * inv255;
        floatBytes[2 * planeSize + i] = rgbBytes[pi + 2] * inv255;
      }

      return _PreprocessResult(
        floatBytes: floatBytes,
        angle: angle,
        origW: origW,
        origH: origH,
        scanW: scanW,
        scanH: scanH,
        left: left,
        top: top,
        ratio: r,
      );
    });
  }

  // ==========================================
  // Helper Math Functions
  // ==========================================

  static List<double> _transformBoxToOriginal({
    required List<double> box,
    required int angle,
    required int scanW,
    required int scanH,
    required int origW,
    required int origH,
  }) {
    final rx1 = box[0];
    final ry1 = box[1];
    final rx2 = box[2];
    final ry2 = box[3];

    if (angle == 0) {
      return [rx1, ry1, rx2, ry2];
    } else if (angle == 180) {
      final ox1 = origW - 1 - rx2;
      final ox2 = origW - 1 - rx1;
      final oy1 = origH - 1 - ry2;
      final oy2 = origH - 1 - ry1;
      return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)];
    } else if (angle == 90) {
      final ox1 = ry1;
      final ox2 = ry2;
      final oy1 = origH - 1 - rx2;
      final oy2 = origH - 1 - rx1;
      return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)];
    } else if (angle == 270) {
      final ox1 = origW - 1 - ry2;
      final ox2 = origW - 1 - ry1;
      final oy1 = rx1;
      final oy2 = rx2;
      return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)];
    }
    return box;
  }

  static double _calculateIoU(List<double> boxA, List<double> boxB) {
    final xA = max(boxA[0], boxB[0]);
    final yA = max(boxA[1], boxB[1]);
    final xB = min(boxA[2], boxB[2]);
    final yB = min(boxA[3], boxB[3]);

    final interW = max(0.0, xB - xA);
    final interH = max(0.0, yB - yA);
    final interArea = interW * interH;
    if (interArea <= 0.0) return 0.0;

    final boxAArea = max(1e-5, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]));
    final boxBArea = max(1e-5, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]));

    return interArea / (boxAArea + boxBArea - interArea);
  }

  static bool _isPointInside(double px, double py, List<double> box) {
    return px >= box[0] && px <= box[2] && py >= box[1] && py <= box[3];
  }
}
