class RuneDetection {
  final int clsId;
  final String name;
  final String rune;
  final String latin;
  final String meaning;
  final double conf;
  final int angle;
  final List<double> box; // [x1, y1, x2, y2]
  final double cx;
  final double cy;

  RuneDetection({
    required this.clsId,
    required this.name,
    required this.rune,
    required this.latin,
    required this.meaning,
    required this.conf,
    required this.angle,
    required this.box,
    required this.cx,
    required this.cy,
  });

  factory RuneDetection.fromJson(Map<String, dynamic> json) {
    return RuneDetection(
      clsId: json['cls_id'] as int? ?? 0,
      name: json['name'] as String? ?? 'unknown',
      rune: json['rune'] as String? ?? '?',
      latin: json['latin'] as String? ?? '?',
      meaning: json['meaning'] as String? ?? '',
      conf: (json['conf'] as num?)?.toDouble() ?? 0.0,
      angle: json['angle'] as int? ?? 0,
      box: (json['box'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          [0, 0, 0, 0],
      cx: (json['cx'] as num?)?.toDouble() ?? 0.0,
      cy: (json['cy'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ScanStats {
  final int angle0;
  final int angle90;
  final int angle180;
  final int angle270;
  final int total;

  ScanStats({
    required this.angle0,
    required this.angle90,
    required this.angle180,
    required this.angle270,
    required this.total,
  });

  factory ScanStats.fromJson(Map<String, dynamic> json) {
    return ScanStats(
      angle0: json['angle_0'] as int? ?? 0,
      angle90: json['angle_90'] as int? ?? 0,
      angle180: json['angle_180'] as int? ?? 0,
      angle270: json['angle_270'] as int? ?? 0,
      total: json['total'] as int? ?? 0,
    );
  }
}

class PredictionResponse {
  final bool success;
  final int width;
  final int height;
  final int totalRunes;
  final ScanStats stats;
  final String runicText;
  final String transliteration;
  final List<RuneDetection> detections;
  final String annotatedImage; // base64 data uri

  PredictionResponse({
    required this.success,
    required this.width,
    required this.height,
    required this.totalRunes,
    required this.stats,
    required this.runicText,
    required this.transliteration,
    required this.detections,
    required this.annotatedImage,
  });

  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    return PredictionResponse(
      success: json['success'] as bool? ?? false,
      width: json['width'] as int? ?? 0,
      height: json['height'] as int? ?? 0,
      totalRunes: json['total_runes'] as int? ?? 0,
      stats: ScanStats.fromJson(json['stats'] as Map<String, dynamic>? ?? {}),
      runicText: json['runic_text'] as String? ?? '',
      transliteration: json['transliteration'] as String? ?? '',
      detections: (json['detections'] as List<dynamic>?)
              ?.map((e) => RuneDetection.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      annotatedImage: json['annotated_image'] as String? ?? '',
    );
  }
}

class SampleStone {
  final String id;
  final String name;
  final String file;

  SampleStone({required this.id, required this.name, required this.file});

  factory SampleStone.fromJson(Map<String, dynamic> json) {
    return SampleStone(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      file: json['file'] as String? ?? '',
    );
  }
}
