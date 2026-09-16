import 'dart:ui';
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const VikingRuneApp());
}

class VikingRuneApp extends StatelessWidget {
  const VikingRuneApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Viking Epigraphy AI',
      debugShowCheckedModeBanner: false,
      scrollBehavior: const MaterialScrollBehavior().copyWith(
        dragDevices: {
          PointerDeviceKind.mouse,
          PointerDeviceKind.touch,
          PointerDeviceKind.stylus,
          PointerDeviceKind.unknown,
        },
      ),
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        primaryColor: const Color(0xFFD4AF37),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFD4AF37),
          secondary: Color(0xFF1F6FEB),
          surface: Color(0xFF161B22),
          background: Color(0xFF0D1117),
        ),
        cardColor: const Color(0xFF161B22),
        dividerColor: Colors.white12,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
