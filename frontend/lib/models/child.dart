class Child {
  final int id;
  final int therapistId;
  final String name;
  final DateTime createdAt;

  Child({
    required this.id,
    required this.therapistId,
    required this.name,
    required this.createdAt,
  });

  factory Child.fromJson(Map<String, dynamic> json) {
    return Child(
      id: json['id'],
      therapistId: json['therapist_id'],
      name: json['name'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'therapist_id': therapistId,
      'name': name,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
