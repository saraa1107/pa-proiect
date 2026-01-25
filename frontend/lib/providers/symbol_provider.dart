import 'package:flutter/foundation.dart';
import '../models/symbol.dart';
import '../services/api_service.dart';

class SymbolProvider with ChangeNotifier {
  List<Symbol> _symbols = [];
  List<Symbol> _filteredSymbols = [];
  bool _isLoading = false;
  String? _error;
  String _searchQuery = '';

  List<Symbol> get symbols => _filteredSymbols.isEmpty ? _symbols : _filteredSymbols;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get searchQuery => _searchQuery;

  Future<void> loadSymbols({int? categoryId}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _symbols = await ApiService.getSymbols(categoryId: categoryId);
      _filteredSymbols = [];
      _error = null;
    } catch (e) {
      _error = e.toString();
      _symbols = [];
      _filteredSymbols = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> searchSymbols(String query) async {
    _searchQuery = query;
    
    if (query.isEmpty) {
      _filteredSymbols = [];
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _filteredSymbols = await ApiService.getSymbols(search: query);
      _error = null;
    } catch (e) {
      _error = e.toString();
      _filteredSymbols = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearSearch() {
    _searchQuery = '';
    _filteredSymbols = [];
    notifyListeners();
  }
}


