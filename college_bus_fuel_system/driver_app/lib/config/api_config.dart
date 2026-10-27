import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiConfig {
  // Configurable base URL
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:5000/api';
    }
    try {
      if (Platform.isAndroid) {
        // Standard Android emulator loopback alias to host machine
        return 'http://10.0.2.2:5000/api';
      }
    } catch (_) {}
    return 'http://127.0.0.1:5000/api';
  }

  // Auth
  static String get login => '$baseUrl/auth/login';
  static String get me => '$baseUrl/auth/me';

  // Buses
  static String get myAssignedBus => '$baseUrl/buses/my-assigned';

  // Fuel entries
  static String get scanReceipt => '$baseUrl/fuel/scan-receipt';
  static String get submitFuel => '$baseUrl/fuel/submit';
  static String get myRecords => '$baseUrl/fuel/records';
  static String recordDetail(int id) => '$baseUrl/fuel/records/$id';
  static String correctRecord(int id) => '$baseUrl/fuel/records/$id/correct';

  // Secure receipt viewing
  static String billUrl(String filename, String token) =>
      '$baseUrl/bills/$filename?token=$token';
}
