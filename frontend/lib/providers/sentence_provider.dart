import 'package:flutter/foundation.dart';
import '../models/symbol.dart';

class SentenceProvider extends ChangeNotifier {
  final List<Symbol> _sentence = [];

  List<Symbol> get sentence => _sentence;
  String get sentenceText => _sentence.map((s) => s.text).join(' ');

  void addSymbol(Symbol symbol) {
    _sentence.add(symbol);
    notifyListeners();
  }

  void removeSymbolAt(int index) {
    if (index >= 0 && index < _sentence.length) {
      _sentence.removeAt(index);
      notifyListeners();
    }
  }

  void clear() {
    _sentence.clear();
    notifyListeners();
  }
}
