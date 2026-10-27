import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';
import '../models/user_model.dart';

class AuthService extends ChangeNotifier {
  UserModel? _currentUser;
  String? _token;
  bool _isLoading = true;

  UserModel? get currentUser => _currentUser;
  String? get token => _token;
  bool get isAuthenticated => _token != null && _currentUser != null;
  bool get isLoading => _isLoading;

  AuthService() {
    loadSavedSession();
  }

  Future<void> loadSavedSession() async {
    _isLoading = true;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedToken = prefs.getString('driver_token');
      final savedUser = prefs.getString('driver_user');

      if (savedToken != null && savedUser != null) {
        _token = savedToken;
        _currentUser = UserModel.fromJson(jsonDecode(savedUser));
      }
    } catch (e) {
      debugPrint('Session restore error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String identifier, String password) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.login),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'identifier': identifier.trim(),
          'password': password,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['access_token'] != null) {
        _token = data['access_token'];
        _currentUser = UserModel.fromJson(data['user']);

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('driver_token', _token!);
        await prefs.setString('driver_user', jsonEncode(data['user']));

        notifyListeners();
        return true;
      } else {
        throw Exception(data['error'] ?? 'Authentication failed');
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> logout() async {
    _token = null;
    _currentUser = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('driver_token');
    await prefs.remove('driver_user');
    notifyListeners();
  }
}
