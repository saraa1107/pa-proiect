import 'package:flutter/material.dart';

class Category {
  final int id;
  final String name;
  final String? description;
  final String? icon;
  final String? color;
  final DateTime createdAt;

  Category({
    required this.id,
    required this.name,
    this.description,
    this.icon,
    this.color,
    required this.createdAt,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      icon: json['icon'],
      color: json['color'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Color get colorValue {
    if (color != null && color!.startsWith('#')) {
      return Color(int.parse(color!.substring(1), radix: 16) + 0xFF000000);
    }
    return Colors.blue;
  }
}

