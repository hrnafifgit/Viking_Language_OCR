import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../models/rune_detection.dart';

class InteractiveRuneCanvas extends StatelessWidget {
  final Uint8List? rawImageBytes;
  final String? base64AnnotatedImage;
  final int imageWidth;
  final int imageHeight;
  final List<RuneDetection> detections;
  final RuneDetection? selectedRune;
  final Function(RuneDetection) onRuneSelected;
  final bool showBoxes;

  const InteractiveRuneCanvas({
    Key? key,
    this.rawImageBytes,
    this.base64AnnotatedImage,
    required this.imageWidth,
    required this.imageHeight,
    required this.detections,
    required this.selectedRune,
    required this.onRuneSelected,
    this.showBoxes = true,
  }) : super(key: key);

  Color _getAngleColor(int angle) {
    switch (angle) {
      case 0:
        return const Color(0xFF00DC46); // Green
      case 180:
        return const Color(0xFF1EB4FF); // Sky Blue
      case 90:
        return const Color(0xFFFF8C00); // Orange
      case 270:
        return const Color(0xFFE600E6); // Magenta
      default:
        return const Color(0xFFD4AF37);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (rawImageBytes == null && (base64AnnotatedImage == null || base64AnnotatedImage!.isEmpty)) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.image_search, size: 70, color: Colors.white.withOpacity(0.2)),
            const SizedBox(height: 12),
            Text(
              'اختر صورة حجر أو التقط صورة بالكاميرا للبدء',
              style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 16),
            ),
          ],
        ),
      );
    }

    Uint8List? displayBytes;
    if (base64AnnotatedImage != null && base64AnnotatedImage!.isNotEmpty) {
      try {
        final pureBase64 = base64AnnotatedImage!.split(',').last;
        displayBytes = base64Decode(pureBase64);
      } catch (_) {
        displayBytes = rawImageBytes;
      }
    } else {
      displayBytes = rawImageBytes;
    }

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0B0E14),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white12),
      ),
      clipBehavior: Clip.antiAlias,
      child: InteractiveViewer(
        boundaryMargin: const EdgeInsets.all(40),
        minScale: 0.5,
        maxScale: 6.0,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final naturalW = imageWidth > 0 ? imageWidth.toDouble() : 800.0;
            final naturalH = imageHeight > 0 ? imageHeight.toDouble() : 600.0;

            return Center(
              child: AspectRatio(
                aspectRatio: naturalW / naturalH,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    // Base Image
                    Image.memory(
                      displayBytes!,
                      fit: BoxFit.fill,
                    ),

                    // Tappable Invisible/Highlighted Rune Hotspots
                    if (showBoxes && detections.isNotEmpty)
                      LayoutBuilder(
                        builder: (context, innerConstraints) {
                          final scaleX = innerConstraints.maxWidth / naturalW;
                          final scaleY = innerConstraints.maxHeight / naturalH;

                          final boxWidgets = <Widget>[];
                          final labelWidgets = <Widget>[];

                          for (final d in detections) {
                            final left = d.box[0] * scaleX;
                            final top = d.box[1] * scaleY;
                            final width = (d.box[2] - d.box[0]) * scaleX;
                            final height = (d.box[3] - d.box[1]) * scaleY;

                            final isSelected = selectedRune == d;
                            final color = _getAngleColor(d.angle);

                            // 1. Interactive Bounding Box
                            boxWidgets.add(
                              Positioned(
                                left: left,
                                top: top,
                                width: width,
                                height: height,
                                child: GestureDetector(
                                  onTap: () => onRuneSelected(d),
                                  behavior: HitTestBehavior.opaque,
                                  child: Container(
                                    decoration: BoxDecoration(
                                      border: Border.all(
                                        color: isSelected ? Colors.yellowAccent : color,
                                        width: isSelected ? 3.0 : 1.8,
                                      ),
                                      color: isSelected ? Colors.yellow.withOpacity(0.25) : null,
                                      boxShadow: isSelected
                                          ? [
                                              const BoxShadow(
                                                color: Colors.yellowAccent,
                                                blurRadius: 12,
                                                spreadRadius: 2,
                                              )
                                            ]
                                          : null,
                                    ),
                                  ),
                                ),
                              ),
                            );

                            // 2. Pure small Rune character floating directly above the box
                            labelWidgets.add(
                              Positioned(
                                left: left,
                                top: max(0.0, top - 11.0),
                                child: IgnorePointer(
                                  child: Text(
                                    d.rune,
                                    style: TextStyle(
                                      fontSize: 8.5,
                                      fontWeight: FontWeight.bold,
                                      color: isSelected ? Colors.yellowAccent : color,
                                      height: 1.0,
                                      shadows: const [
                                        Shadow(
                                          color: Colors.black,
                                          blurRadius: 2,
                                          offset: Offset(0, 1),
                                        ),
                                        Shadow(
                                          color: Colors.black,
                                          blurRadius: 2,
                                          offset: Offset(0, -1),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            );
                          }

                          return Stack(
                            clipBehavior: Clip.none,
                            children: [
                              ...boxWidgets,
                              ...labelWidgets,
                            ],
                          );
                        },
                      ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
