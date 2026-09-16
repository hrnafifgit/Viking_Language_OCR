import 'package:flutter/material.dart';
import '../models/rune_detection.dart';

class RuneDetailsSheet extends StatelessWidget {
  final RuneDetection rune;

  const RuneDetailsSheet({Key? key, required this.rune}) : super(key: key);

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
        return const Color(0xFFD4AF37); // Gold
    }
  }

  String _getAngleLabel(int angle) {
    switch (angle) {
      case 0:
        return '0° Normal (معتدل)';
      case 180:
        return '180° Inverted (مقلوب)';
      case 90:
        return '90° Vertical CW (رأسي)';
      case 270:
        return '270° Vertical CCW (رأسي معكوس)';
      default:
        return '$angle°';
    }
  }

  @override
  Widget build(BuildContext context) {
    final angleColor = _getAngleColor(rune.angle);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        border: Border.all(color: angleColor.withOpacity(0.4), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: angleColor.withOpacity(0.15),
            blurRadius: 30,
            spreadRadius: 2,
          )
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 44,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.white24,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Main Header Row: Glyph + Name & Sound
          Row(
            children: [
              Container(
                width: 72,
                height: 72,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: const Color(0xFF0D1117),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: angleColor, width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: angleColor.withOpacity(0.3),
                      blurRadius: 16,
                    )
                  ],
                ),
                child: Text(
                  rune.rune,
                  style: const TextStyle(
                    fontSize: 42,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(width: 18),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      rune.name.toUpperCase(),
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2,
                        color: Color(0xFFD4AF37), // Gold
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Latin Transliteration: /${rune.latin}/',
                      style: const TextStyle(
                        fontSize: 15,
                        color: Colors.white70,
                      ),
                    ),
                    if (rune.meaning.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Meaning: ${rune.meaning}',
                        style: const TextStyle(
                          fontSize: 13,
                          fontStyle: FontStyle.italic,
                          color: Colors.white54,
                        ),
                      ),
                    ]
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),
          const Divider(color: Colors.white12),
          const SizedBox(height: 12),

          // Metadata Grid: Confidence & Angle
          Row(
            children: [
              Expanded(
                child: _buildMetricCard(
                  title: 'Detection Confidence',
                  value: '${(rune.conf * 100).toStringAsFixed(1)}%',
                  icon: Icons.verified,
                  accentColor: const Color(0xFFD4AF37),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildMetricCard(
                  title: 'Orientation Angle',
                  value: _getAngleLabel(rune.angle),
                  icon: Icons.rotate_right,
                  accentColor: angleColor,
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),
          // Bounding Box Coordinates
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1117),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.white12),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Bounding Box (x1, y1, x2, y2):',
                  style: TextStyle(fontSize: 12, color: Colors.white54),
                ),
                Text(
                  '[${rune.box.map((v) => v.toStringAsFixed(0)).join(', ')}]',
                  style: const TextStyle(
                    fontSize: 12,
                    fontFamily: 'monospace',
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required IconData icon,
    required Color accentColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0D1117),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: accentColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: accentColor),
              const SizedBox(width: 6),
              Text(
                title,
                style: const TextStyle(fontSize: 11, color: Colors.white54),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: accentColor,
            ),
          ),
        ],
      ),
    );
  }
}
