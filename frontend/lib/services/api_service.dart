import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart' hide Category; // pentru kReleaseMode, dar exclude Category din Flutter
import 'package:http/http.dart' as http;
import '../models/category.dart';
import '../models/symbol.dart';
import '../models/child.dart';

class ApiService {
  // 🌐 AUTO-DETECT ENVIRONMENT (Production vs Development)
  // În production (deployed), folosește URL-ul live
  // În development (local), folosește localhost
  static String get baseUrl {
    if (kReleaseMode) {
      // PRODUCTION - Schimbă cu URL-ul tău de pe Render
      return 'https://aac-app-backend.onrender.com/api';
    } else {
      // DEVELOPMENT - Local
      return 'http://localhost:8000/api';
    }
  }
  
  static String get backendUrl {
    if (kReleaseMode) {
      // PRODUCTION
      return 'https://aac-app-backend.onrender.com';
    } else {
      // DEVELOPMENT
      return 'http://localhost:8000';
    }
  }
  
  // Debug helper
  static void printEnvironment() {
    print('🌐 API Environment:');
    print('   Mode: ${kReleaseMode ? "PRODUCTION" : "DEVELOPMENT"}');
    print('   Base URL: $baseUrl');
    print('   Backend: $backendUrl');
  }

  // ============ AUTENTIFICARE ============
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email, 'password': password}),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Autentificare eșuată');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Map<String, dynamic>> register(String name, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'name': name, 'email': email, 'password': password}),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Înregistrare eșuată');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  // ============ COPII (Children) ============
  static Future<List<Child>> getChildren(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/children'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Child.fromJson(json)).toList();
      } else {
        throw Exception('Eroare la încărcarea copiilor');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Child> createChild(String token, String name) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/children'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({'name': name}),
      );
      if (response.statusCode == 200) {
        return Child.fromJson(json.decode(response.body));
      } else {
        throw Exception('Eroare la crearea copilului');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<void> deleteChild(String token, int childId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/children/$childId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode != 200) {
        throw Exception('Eroare la ștergerea copilului');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<List<Category>> getChildCategories(String token, int childId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/children/$childId/categories'),
        headers: {'Authorization': 'Bearer $token'},
      );
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

  static Future<List<Symbol>> getChildSymbols(String token, int childId, {int? categoryId}) async {
    try {
      Uri uri = Uri.parse('$baseUrl/children/$childId/symbols');
      if (categoryId != null) {
        uri = uri.replace(queryParameters: {'category_id': categoryId.toString()});
      }
      final response = await http.get(
        uri,
        headers: {'Authorization': 'Bearer $token'},
      );
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

  static Future<List<Symbol>> getChildFavorites(String token, int childId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/children/$childId/favorites'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Symbol.fromJson(json)).toList();
      } else {
        throw Exception('Eroare la încărcarea favoritelor');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<void> addChildFavorite(String token, int childId, int symbolId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/children/$childId/favorites/$symbolId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode != 200) {
        throw Exception('Eroare la adăugarea în favorite');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<void> removeChildFavorite(String token, int childId, int symbolId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/children/$childId/favorites/$symbolId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode != 200) {
        throw Exception('Eroare la ștergerea din favorite');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Category> createChildCategory(String token, int childId, String name) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/children/$childId/categories'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({'name': name}),
      );
      if (response.statusCode == 200) {
        return Category.fromJson(json.decode(response.body));
      } else {
        throw Exception('Eroare la crearea categoriei');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<void> deleteChildCategory(String token, int childId, int categoryId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/children/$childId/categories/$categoryId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode != 200) {
        throw Exception('Eroare la ștergerea categoriei');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Symbol> createChildSymbol(String token, int childId, {
    required String name,
    required String text,
    required String imageUrl,
    required int categoryId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/children/$childId/symbols'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'name': name,
          'text': text,
          'image_url': imageUrl,
          'category_id': categoryId,
        }),
      );
      if (response.statusCode == 200) {
        return Symbol.fromJson(json.decode(response.body));
      } else {
        throw Exception('Eroare la crearea simbolului');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<Symbol> createChildSymbolWithImage(String token, int childId, {
    required String name,
    required String text,
    required int categoryId,
    required Uint8List imageBytes,
    required String fileName,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/children/$childId/symbols/upload'),
      );
      request.headers['Authorization'] = 'Bearer $token';
      request.fields['name'] = name;
      request.fields['text'] = text;
      request.fields['category_id'] = categoryId.toString();
      
      // Adaugă imaginea ca MultipartFile din bytes
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: fileName,
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        return Symbol.fromJson(json.decode(response.body));
      } else {
        final errorBody = json.decode(response.body);
        throw Exception(errorBody['detail'] ?? 'Eroare la crearea simbolului cu imagine');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<void> deleteChildSymbol(String token, int childId, int symbolId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/children/$childId/symbols/$symbolId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode != 200) {
        throw Exception('Eroare la ștergerea simbolului');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

  static Future<void> reorderChildSymbols(String token, int childId, List<Map<String, int>> items) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/children/$childId/symbols/reorder'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode(items),
      );
      if (response.statusCode != 200) {
        throw Exception('Eroare la reordonarea simbolurilor');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }

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
        return '$backendUrl$audioUrl';
      } else {
        throw Exception('Eroare la generarea vorbirii');
      }
    } catch (e) {
      throw Exception('Eroare de conexiune: $e');
    }
  }
}

