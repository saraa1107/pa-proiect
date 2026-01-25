import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/category.dart';
import '../models/symbol.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  static const String backendUrl = 'http://localhost:8000';

  // ============ CATEGORII ============
  static Future<List<Category>> getCategories() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/categories'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Category.fromJson(json)).toList();
      } else {
        throw Exception('Eroare la încărcarea categoriilor');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Category> getCategory(int id) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/categories/$id'));
      if (response.statusCode == 200) {
        return Category.fromJson(json.decode(response.body));
      } else {
        throw Exception('Eroare la încărcarea categoriei');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  // ============ SIMBOLURI ============
  static Future<List<Symbol>> getSymbols({int? categoryId, String? search}) async {
    try {
      Uri uri = Uri.parse('$baseUrl/symbols');
      Map<String, String> queryParams = {};
      
      if (categoryId != null) {
        queryParams['category_id'] = categoryId.toString();
      }
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      
      if (queryParams.isNotEmpty) {
        uri = uri.replace(queryParameters: queryParams);
      }

      final response = await http.get(uri);
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Symbol.fromJson(json)).toList();
      } else {
        throw Exception('Eroare la încărcarea simbolurilor');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Symbol> getSymbol(int id) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/symbols/$id'));
      if (response.statusCode == 200) {
        return Symbol.fromJson(json.decode(response.body));
      } else {
        throw Exception('Eroare la încărcarea simbolului');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  // ============ TEXT-TO-SPEECH ============
  static Future<String> textToSpeech(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/tts/speak'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'text': text}),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final audioUrl = data['audio_url'] as String;
        // Returnează URL-ul complet
        if (audioUrl.startsWith('http')) {
          return audioUrl;
        }
        return 'http://localhost:8000$audioUrl';
      } else {
        throw Exception('Eroare la generarea vorbirii');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }
}

