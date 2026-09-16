import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../models/rune_detection.dart';

class ApiService {
  static String baseUrl = 'http://192.168.8.159:5000';

  static Future<bool> checkHealth() async {
    final candidates = [
      baseUrl,
      'http://192.168.8.159:5000',
      'http://127.0.0.1:5000',
      'http://10.0.2.2:5000',
    ];
    for (final candidate in candidates) {
      try {
        final uri = Uri.parse('$candidate/health');
        final response = await http.get(uri).timeout(const Duration(seconds: 3));
        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          if (data['status'] == 'ok') {
            baseUrl = candidate;
            return true;
          }
        }
      } catch (_) {}
    }
    return false;
  }

  static Future<List<SampleStone>> getSamples() async {
    try {
      final uri = Uri.parse('$baseUrl/samples');
      final response = await http.get(uri).timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((e) => SampleStone.fromJson(e)).toList();
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  static Future<Uint8List?> getSampleImageBytes(String sampleId) async {
    try {
      final uri = Uri.parse('$baseUrl/samples/$sampleId');
      final response = await http.get(uri).timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        return response.bodyBytes;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  static Future<PredictionResponse> predictImage({
    required Uint8List imageBytes,
    required String filename,
    double conf = 0.18,
    int imgsz = 1024,
    bool enable4Way = true,
  }) async {
    final uri = Uri.parse('$baseUrl/predict');
    final request = http.MultipartRequest('POST', uri);

    request.fields['conf'] = conf.toString();
    request.fields['imgsz'] = imgsz.toString();
    request.fields['enable_4way'] = enable4Way ? 'true' : 'false';

    request.files.add(
      http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: filename.isEmpty ? 'upload.jpg' : filename,
      ),
    );

    final streamedResponse = await request.send().timeout(const Duration(seconds: 60));
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return PredictionResponse.fromJson(data);
    } else {
      throw Exception('Server error (${response.statusCode}): ${response.body}');
    }
  }
}
