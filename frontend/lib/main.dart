import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/mode_selection_screen.dart';
import 'providers/auth_provider.dart';
import 'providers/symbol_provider.dart';
import 'providers/category_provider.dart';
import 'providers/sentence_provider.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => CategoryProvider()),
        ChangeNotifierProvider(create: (_) => SymbolProvider()),
        ChangeNotifierProvider(create: (_) => SentenceProvider()),
      ],
      child: MaterialApp(
        title: 'AAC Communication System',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const ModeSelectionScreen(),
      ),
    );
  }
}


