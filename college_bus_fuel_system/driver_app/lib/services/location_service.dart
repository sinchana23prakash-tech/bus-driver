import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

class LocationResult {
  final double? latitude;
  final double? longitude;
  final bool isSuccess;
  final String message;

  LocationResult({
    this.latitude,
    this.longitude,
    required this.isSuccess,
    required this.message,
  });
}

class LocationService {
  static Future<LocationResult> getCurrentCoordinates() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return LocationResult(
          isSuccess: false,
          message: 'Location service is disabled on device.',
        );
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return LocationResult(
            isSuccess: false,
            message: 'Location permission was denied.',
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return LocationResult(
          isSuccess: false,
          message: 'Location permission permanently denied in device settings.',
        );
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 8),
      );

      return LocationResult(
        latitude: position.latitude,
        longitude: position.longitude,
        isSuccess: true,
        message: 'Location captured (${position.latitude.toStringAsFixed(4)}, ${position.longitude.toStringAsFixed(4)})',
      );
    } catch (e) {
      return LocationResult(
        isSuccess: false,
        message: 'Unable to acquire GPS fix: ${e.toString()}',
      );
    }
  }
}
