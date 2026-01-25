import 'category.dart';

class Symbol {
  final int id;
  final String name;
  final String text;
  final String imageUrl;
  final int categoryId;
  final int usageCount;
  final DateTime createdAt;
  final Category category;

  Symbol({
    required this.id,
    required this.name,
    required this.text,
    required this.imageUrl,
    required this.categoryId,
    required this.usageCount,
    required this.createdAt,
    required this.category,
  });

  factory Symbol.fromJson(Map<String, dynamic> json) {
    // Construiește URL-ul complet pentru imagine
    String imageUrl = json['image_url'] as String;
    if (imageUrl.startsWith('/')) {
      // Dacă este un path relativ, adaugă base URL-ul backend-ului
      imageUrl = 'http://localhost:8000$imageUrl';
    }
    
    return Symbol(
      id: json['id'],
      name: json['name'],
      text: json['text'],
      imageUrl: imageUrl,
      categoryId: json['category_id'],
      usageCount: json['usage_count'],
      createdAt: DateTime.parse(json['created_at']),
      category: Category.fromJson(json['category']),
    );
  }
}


