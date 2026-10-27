import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/bus_model.dart';
import '../models/fuel_entry_model.dart';

class FuelService {
  static Future<BusModel?> getMyAssignedBus(String token) async {
    final response = await http.get(
      Uri.parse(ApiConfig.myAssignedBus),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['bus'] != null) {
        return BusModel.fromJson(data['bus']);
      }
    }
    return null;
  }

  static Future<Map<String, dynamic>> scanReceiptFile(File imageFile, String token) async {
    final request = http.MultipartRequest('POST', Uri.parse(ApiConfig.scanReceipt));
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('bill_image', imageFile.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data;
    } else {
      throw Exception(data['error'] ?? 'Receipt scanning failed');
    }
  }

  static Future<FuelEntryModel> submitFuelEntry(Map<String, dynamic> payload, String token) async {
    final response = await http.post(
      Uri.parse(ApiConfig.submitFuel),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(payload),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 201 && data['fuel_record'] != null) {
      return FuelEntryModel.fromJson(data['fuel_record']);
    } else {
      throw Exception(data['error'] ?? 'Fuel submission failed');
    }
  }

  static Future<List<FuelEntryModel>> getMyRecords(String token, {String? status}) async {
    String url = ApiConfig.myRecords;
    if (status != null && status.isNotEmpty) {
      url += '?status=$status';
    }

    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List list = data['records'] ?? [];
      return list.map((item) => FuelEntryModel.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load submissions');
    }
  }

  static Future<FuelEntryModel> resubmitCorrection(int recordId, Map<String, dynamic> payload, String token) async {
    final response = await http.put(
      Uri.parse(ApiConfig.correctRecord(recordId)),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(payload),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200 && data['fuel_record'] != null) {
      return FuelEntryModel.fromJson(data['fuel_record']);
    } else {
      throw Exception(data['error'] ?? 'Correction resubmission failed');
    }
  }
}
