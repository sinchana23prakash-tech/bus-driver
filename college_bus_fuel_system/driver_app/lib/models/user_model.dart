class UserModel {
  final int id;
  final String username;
  final String email;
  final String fullName;
  final String? phoneNumber;
  final String role;

  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.fullName,
    this.phoneNumber,
    required this.role,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      phoneNumber: json['phone_number'],
      role: json['role'] ?? 'DRIVER',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'role': role,
    };
  }
}
