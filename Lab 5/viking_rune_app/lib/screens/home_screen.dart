import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';

import '../models/rune_detection.dart';
import '../services/api_service.dart';
import '../services/offline_rune_service.dart';
import '../widgets/interactive_rune_canvas.dart';
import '../widgets/rune_details_sheet.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _serverOnline = false;
  bool _isOfflineMode = true; // Default: 100% On-Device / Offline without server
  bool _isModelReady = false;
  bool _isLoading = false;
  String _statusMessage = 'جاهز للفحص (محلياً داخل الجوال)';

  // Detection Settings
  bool _enable4Way = false; // Default: Fast single scan (0°). User can toggle 4-Way for multi-angle scanning.
  double _confThreshold = 0.18;
  int _imgSize = 1024;

  // Current State
  Uint8List? _rawImageBytes;
  String? _currentFilename;
  PredictionResponse? _prediction;
  RuneDetection? _selectedRune;
  List<SampleStone> _samples = [];

  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _initOfflineModel();
    _checkServer();
  }

  Future<void> _initOfflineModel() async {
    final ready = await OfflineRuneService.initModel();
    if (mounted) {
      setState(() {
        _isModelReady = ready;
        if (ready && _isOfflineMode) {
          _statusMessage = 'الموديل الداخلي جاهز للفحص الدائم (بدون سيرفر)';
        } else if (!ready && _isOfflineMode) {
          _statusMessage = 'تنبيه: يجب إعادة تشغيل flutter run بالكامل (Full Restart) لتحميل الموديل والمكتبات الجديدة.';
        }
      });
    }
  }

  Future<void> _checkServer() async {
    final online = await ApiService.checkHealth();
    if (mounted) {
      setState(() {
        _serverOnline = online;
      });
    }
    if (online) {
      _loadSamples();
    }
  }

  Future<void> _loadSamples() async {
    final samples = await ApiService.getSamples();
    if (mounted) {
      setState(() {
        _samples = samples;
      });
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 90,
      );
      if (photo != null) {
        final bytes = await photo.readAsBytes();
        _processNewImage(bytes, photo.name);
      }
    } catch (e) {
      _showSnackbar('خطأ في اختيار الصورة: $e');
    }
  }

  Future<void> _pickFileDesktop() async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 90,
      );
      if (photo != null) {
        final bytes = await photo.readAsBytes();
        _processNewImage(bytes, photo.name);
      }
    } catch (e) {
      _showSnackbar('خطأ في اختيار الصورة: $e');
    }
  }

  Future<void> _selectSample(SampleStone sample) async {
    setState(() {
      _isLoading = true;
      _statusMessage = 'جاري تحميل عينة ${sample.name}...';
    });

    final bytes = await ApiService.getSampleImageBytes(sample.id);
    if (bytes != null) {
      _processNewImage(bytes, sample.file);
    } else {
      setState(() => _isLoading = false);
      _showSnackbar('تعذر تحميل العينة من الخادم');
    }
  }

  Future<void> _processNewImage(Uint8List bytes, String filename) async {
    setState(() {
      _rawImageBytes = bytes;
      _currentFilename = filename;
      _prediction = null;
      _selectedRune = null;
      _isLoading = true;
      _statusMessage = _isOfflineMode
          ? (_enable4Way
              ? 'جاري الفحص متعدد الخيوط (Multi-threading ⚡) عبر 4 زوايا...'
              : 'جاري الفحص المسرّع داخل الجوال بالذكاء الاصطناعي ⚡...')
          : (_enable4Way
              ? 'جاري إرسال الصورة للمسح الرباعي بالخادم (0° + 90° + 180° + 270°)...'
              : 'جاري الكشف بالخادم بالوضع العادي 0°...');
    });

    try {
      PredictionResponse pred;
      if (_isOfflineMode) {
        pred = await OfflineRuneService.detectRunes(
          imageBytes: bytes,
          confThreshold: _confThreshold,
          enable4Way: _enable4Way,
        );
      } else {
        pred = await ApiService.predictImage(
          imageBytes: bytes,
          filename: filename,
          conf: _confThreshold,
          imgsz: _imgSize,
          enable4Way: _enable4Way,
        );
      }

      setState(() {
        _prediction = pred;
        _isLoading = false;
        _statusMessage = 'تم الكشف عن ${pred.totalRunes} رمزاً من لغة الفايكنج (${_isOfflineMode ? "محلياً داخل الهاتف ⚡" : "عبر الخادم 🌐"})!';
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _statusMessage = _isOfflineMode ? 'فشل الفحص المحلي: $e' : 'فشل الاتصال بالخادم';
      });
      _showSnackbar('خطأ أثناء الفحص: $e');
    }
  }

  void _showRuneDetails(RuneDetection rune) {
    setState(() {
      _selectedRune = rune;
    });

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => RuneDetailsSheet(rune: rune),
    );
  }

  void _showSettingsDialog() {
    final controller = TextEditingController(text: ApiService.baseUrl);
    bool tempOffline = _isOfflineMode;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          backgroundColor: const Color(0xFF161B22),
          title: const Row(
            children: [
              Icon(Icons.memory, color: Color(0xFFD4AF37)),
              SizedBox(width: 8),
              Text('إعدادات محرك الذكاء الاصطناعي', style: TextStyle(color: Color(0xFFD4AF37), fontSize: 16)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF21262D),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: tempOffline ? const Color(0xFFD4AF37) : Colors.transparent,
                  ),
                ),
                child: SwitchListTile(
                  title: const Text(
                    'الموديل الداخلي المثبت بالجوال ⚡',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  subtitle: const Text(
                    'تشغيل ذاتي دائم بدون سيرفر وبدون إنترنت (Offline)',
                    style: TextStyle(fontSize: 11, color: Colors.white70),
                  ),
                  value: tempOffline,
                  activeColor: const Color(0xFFD4AF37),
                  onChanged: (val) {
                    setDialogState(() {
                      tempOffline = val;
                    });
                  },
                ),
              ),
              const SizedBox(height: 16),
              if (!tempOffline) ...[
                const Text(
                  'عنوان الخادم الخارجي (Backend URL):\n(للكمبيوتر: http://127.0.0.1:5000)\n(للهاتف عبر الواي فاي: http://192.168.8.159:5000)',
                  style: TextStyle(fontSize: 11, color: Colors.white60),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: controller,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: 'Server URL',
                    labelStyle: TextStyle(color: Colors.white60),
                  ),
                ),
              ] else ...[
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.3)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.check_circle, color: Colors.greenAccent, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'الموديل مثبت بشكل دائم داخل ملفات التطبيق (ONNX Runtime) بدقة 100%.',
                          style: TextStyle(fontSize: 11, color: Colors.greenAccent),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء', style: TextStyle(color: Colors.white54)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFD4AF37)),
              onPressed: () {
                setState(() {
                  _isOfflineMode = tempOffline;
                  if (!tempOffline) {
                    ApiService.baseUrl = controller.text.trim();
                  }
                  _statusMessage = _isOfflineMode
                      ? 'تم تفعيل الفحص الداخلي بالجوال (Offline)'
                      : 'تم تفعيل وضع الخادم الخارجي';
                });
                Navigator.pop(context);
                if (!_isOfflineMode) {
                  _checkServer();
                }
              },
              child: const Text('حفظ الإعدادات', style: TextStyle(color: Colors.black)),
            ),
          ],
        ),
      ),
    );
  }

  void _showSnackbar(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: const Color(0xFF21262D)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isWideScreen = MediaQuery.of(context).size.width > 900;

    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 2,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFFD4AF37).withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFD4AF37)),
              ),
              child: const Text(
                'ᚱ',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
              ),
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Viking Epigraphy AI',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    'قارئ ومترجم النقوش بالذكاء الاصطناعي',
                    style: TextStyle(fontSize: 10, color: Colors.white54),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          // Engine Mode & Status Pill
          InkWell(
            onTap: _showSettingsDialog,
            borderRadius: BorderRadius.circular(20),
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: _isOfflineMode
                    ? const Color(0xFFD4AF37).withValues(alpha: 0.18)
                    : (_serverOnline
                        ? Colors.green.withValues(alpha: 0.15)
                        : Colors.red.withValues(alpha: 0.15)),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: _isOfflineMode
                      ? const Color(0xFFD4AF37)
                      : (_serverOnline ? Colors.greenAccent : Colors.redAccent),
                  width: 1.2,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _isOfflineMode
                        ? (_isModelReady ? Icons.bolt : Icons.hourglass_top)
                        : Icons.circle,
                    size: _isOfflineMode ? 14 : 10,
                    color: _isOfflineMode
                        ? (_isModelReady ? const Color(0xFFD4AF37) : Colors.amberAccent)
                        : (_serverOnline ? Colors.greenAccent : Colors.redAccent),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    _isOfflineMode
                        ? (_isModelReady ? 'موديل الجوال ⚡ (مدمج دائم)' : 'جاري تجهيز الموديل...')
                        : (_serverOnline ? 'خادم متصل' : 'خادم غير متصل'),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: _isOfflineMode
                          ? (_isModelReady ? const Color(0xFFD4AF37) : Colors.amberAccent)
                          : (_serverOnline ? Colors.greenAccent : Colors.redAccent),
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Icon(Icons.settings, size: 14, color: Colors.white54),
                ],
              ),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Top Controls & Options Bar
            _buildControlsBar(),

            // Main Content Area
            Expanded(
              child: isWideScreen
                  ? Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Expanded(flex: 3, child: _buildCanvasArea()),
                        Expanded(flex: 2, child: _buildResultsPanel()),
                      ],
                    )
                  : Column(
                      children: [
                        Expanded(flex: 3, child: _buildCanvasArea()),
                        if (_prediction != null)
                          Expanded(flex: 2, child: _buildResultsPanel()),
                      ],
                    ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _prediction == null ? _buildSampleCarousel() : null,
    );
  }

  Widget _buildControlsBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: const BoxDecoration(
        color: Color(0xFF161B22),
        border: Border(bottom: BorderSide(color: Colors.white12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Row 1: Action Buttons & 4-Way Switch
          Wrap(
            alignment: WrapAlignment.spaceBetween,
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 10,
            runSpacing: 8,
            children: [
              // Action Buttons: Pick / Camera
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFD4AF37),
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _isLoading ? null : _pickFileDesktop,
                    icon: const Icon(Icons.photo_library, size: 18),
                    label: const Text('اختيار صورة', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Colors.white24),
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt, size: 18),
                    label: const Text('الكاميرا'),
                  ),
                ],
              ),

              // 4-Way Rotational TTA Toggle Switch
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
                decoration: BoxDecoration(
                  color: _enable4Way ? const Color(0xFF1F6FEB).withOpacity(0.18) : Colors.white.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: _enable4Way ? const Color(0xFF1F6FEB) : Colors.white12,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.rotate_right,
                      size: 18,
                      color: _enable4Way ? const Color(0xFF58A6FF) : Colors.white54,
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'المسح الرباعي (4-Way TTA)',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(width: 4),
                    Switch(
                      value: _enable4Way,
                      activeColor: const Color(0xFF58A6FF),
                      onChanged: (val) {
                        setState(() => _enable4Way = val);
                        if (_rawImageBytes != null && _currentFilename != null) {
                          _processNewImage(_rawImageBytes!, _currentFilename!);
                        }
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          // Row 2: Confidence Threshold (العتبة) Slider & Presets
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1117),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.white12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Wrap(
                  alignment: WrapAlignment.spaceBetween,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  spacing: 8,
                  runSpacing: 4,
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.tune, size: 15, color: Color(0xFFD4AF37)),
                        const SizedBox(width: 6),
                        Text(
                          'عتبة الثقة (Threshold): ${(_confThreshold * 100).toInt()}%',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
                        ),
                      ],
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _buildThresholdChip('0.10', 0.10),
                        const SizedBox(width: 4),
                        _buildThresholdChip('0.18', 0.18),
                        const SizedBox(width: 4),
                        _buildThresholdChip('0.30', 0.30),
                        const SizedBox(width: 4),
                        _buildThresholdChip('0.50', 0.50),
                      ],
                    ),
                  ],
                ),
                SliderTheme(
                  data: SliderTheme.of(context).copyWith(
                    activeTrackColor: const Color(0xFFD4AF37),
                    inactiveTrackColor: Colors.white12,
                    thumbColor: const Color(0xFFD4AF37),
                    overlayColor: const Color(0xFFD4AF37).withOpacity(0.2),
                    thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
                    trackHeight: 3,
                  ),
                  child: Slider(
                    value: _confThreshold,
                    min: 0.05,
                    max: 0.70,
                    divisions: 65,
                    label: '${(_confThreshold * 100).toInt()}%',
                    onChanged: (val) {
                      setState(() => _confThreshold = val);
                    },
                    onChangeEnd: (val) {
                      if (_rawImageBytes != null && _currentFilename != null) {
                        _processNewImage(_rawImageBytes!, _currentFilename!);
                      }
                    },
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 6),

          // Row 3: Status text & Loading indicator
          Row(
            children: [
              if (_isLoading)
                const Padding(
                  padding: EdgeInsets.only(left: 6),
                  child: SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFD4AF37)),
                  ),
                ),
              Expanded(
                child: Text(
                  _statusMessage,
                  style: TextStyle(
                    fontSize: 11,
                    color: _isLoading ? const Color(0xFFD4AF37) : Colors.white70,
                    fontStyle: _isLoading ? FontStyle.italic : FontStyle.normal,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildThresholdChip(String label, double value) {
    final isSelected = (_confThreshold - value).abs() < 0.02;
    return InkWell(
      onTap: () {
        setState(() => _confThreshold = value);
        if (_rawImageBytes != null && _currentFilename != null) {
          _processNewImage(_rawImageBytes!, _currentFilename!);
        }
      },
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFD4AF37).withOpacity(0.2) : Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isSelected ? const Color(0xFFD4AF37) : Colors.white12,
            width: 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? const Color(0xFFD4AF37) : Colors.white60,
          ),
        ),
      ),
    );
  }

  Widget _buildCanvasArea() {
    return Container(
      margin: const EdgeInsets.all(12),
      child: Stack(
        children: [
          InteractiveRuneCanvas(
            rawImageBytes: _rawImageBytes,
            base64AnnotatedImage: _prediction?.annotatedImage,
            imageWidth: _prediction?.width ?? 0,
            imageHeight: _prediction?.height ?? 0,
            detections: _prediction?.detections ?? [],
            selectedRune: _selectedRune,
            onRuneSelected: _showRuneDetails,
          ),
          if (_isLoading)
            Container(
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.6),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const CircularProgressIndicator(color: Color(0xFFD4AF37)),
                    const SizedBox(height: 16),
                    Text(
                      _statusMessage,
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildResultsPanel() {
    if (_prediction == null) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.only(right: 12, top: 12, bottom: 12, left: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white12),
      ),
      child: ListView(
        children: [
          // Header Stats
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome, color: Color(0xFFD4AF37), size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'تم اكتشاف ${_prediction!.totalRunes} رمزاً',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF21262D),
                  foregroundColor: Colors.white70,
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                ),
                onPressed: () {
                  Clipboard.setData(ClipboardData(
                    text: 'نص الفايكنج:\n${_prediction!.runicText}\n\nالنقحرة الصوتية:\n${_prediction!.transliteration}',
                  ));
                  _showSnackbar('تم نسخ نص الفايكنج والنقحرة بنجاح!');
                },
                icon: const Icon(Icons.copy, size: 14),
                label: const Text('نسخ الكل', style: TextStyle(fontSize: 12)),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Angle Breakdown Chips
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: [
              _buildAngleChip('0° معتدل', _prediction!.stats.angle0, const Color(0xFF00DC46)),
              _buildAngleChip('180° مقلوب', _prediction!.stats.angle180, const Color(0xFF1EB4FF)),
              _buildAngleChip('90° رأسي', _prediction!.stats.angle90, const Color(0xFFFF8C00)),
              _buildAngleChip('270° رأسي', _prediction!.stats.angle270, const Color(0xFFE600E6)),
            ],
          ),

          const SizedBox(height: 16),
          const Divider(color: Colors.white12),

          // Runic Text Card
          const Text(
            'نص الفايكنج المستخرج (Viking Inscriptions):',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFFD4AF37)),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1117),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            child: SelectableText(
              _prediction!.runicText.isEmpty ? 'لا توجد نصوص' : _prediction!.runicText,
              style: const TextStyle(
                fontSize: 24,
                letterSpacing: 2.0,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),

          const SizedBox(height: 14),

          // Transliteration Card
          const Text(
            'النقحرة اللاتينية الصوتية (Transliteration):',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white70),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1117),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            child: SelectableText(
              _prediction!.transliteration.isEmpty ? 'N/A' : _prediction!.transliteration,
              style: const TextStyle(
                fontSize: 18,
                letterSpacing: 1.5,
                color: Color(0xFF58A6FF),
                fontFamily: 'monospace',
                fontWeight: FontWeight.w600,
              ),
            ),
          ),

          const SizedBox(height: 16),
          const Divider(color: Colors.white12),

          // Runes Grid / Clickable Chips
          const Text(
            'انقر على أي رمز لعرض تفاصيله ومعناه:',
            style: TextStyle(fontSize: 12, color: Colors.white54),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: _prediction!.detections.map((d) {
              final isSelected = _selectedRune == d;
              return ActionChip(
                backgroundColor: isSelected ? const Color(0xFFD4AF37) : const Color(0xFF0D1117),
                side: BorderSide(
                  color: isSelected ? Colors.white : Colors.white24,
                  width: isSelected ? 1.5 : 1.0,
                ),
                label: Text(
                  '${d.rune} ${d.latin}',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: isSelected ? Colors.black : Colors.white,
                  ),
                ),
                onPressed: () => _showRuneDetails(d),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildAngleChip(String label, int count, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Text(
        '$label: $count',
        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color),
      ),
    );
  }

  Widget _buildSampleCarousel() {
    if (_samples.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: const BoxDecoration(
        color: Color(0xFF161B22),
        border: Border(top: BorderSide(color: Colors.white12)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.history_edu, size: 16, color: Color(0xFFD4AF37)),
              SizedBox(width: 8),
              Text(
                'عينات أحجار تاريخية جاهزة للاختبار الفوري بنقرة واحدة:',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white70),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _samples.map((sample) {
                return Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFFD4AF37),
                      side: const BorderSide(color: Color(0xFFD4AF37), width: 1),
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    onPressed: _isLoading ? null : () => _selectSample(sample),
                    icon: const Icon(Icons.image, size: 16),
                    label: Text(sample.name, style: const TextStyle(fontSize: 12)),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
