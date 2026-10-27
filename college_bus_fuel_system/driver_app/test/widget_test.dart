import 'package:flutter_test/flutter_test.dart';
import 'package:college_bus_driver_app/models/fuel_entry_model.dart';
import 'package:college_bus_driver_app/models/bus_model.dart';
import 'package:college_bus_driver_app/models/user_model.dart';

void main() {
  test('UserModel deserialization test', () {
    final json = {
      'id': 10,
      'username': 'driver_ramesh',
      'email': 'ramesh@college.edu',
      'full_name': 'Ramesh Kumar',
      'phone_number': '9876543210',
      'role': 'DRIVER'
    };

    final user = UserModel.fromJson(json);
    expect(user.id, 10);
    expect(user.username, 'driver_ramesh');
    expect(user.role, 'DRIVER');
    expect(user.fullName, 'Ramesh Kumar');
  });

  test('BusModel deserialization test', () {
    final json = {
      'id': 3,
      'bus_number': 'Bus #03',
      'registration_number': 'KA-01-AB-1234',
      'model_name': 'Tata Starbus',
      'fuel_tank_capacity': 150.0,
      'fuel_type': 'DIESEL',
      'current_odometer': 14200.0,
      'status': 'ACTIVE'
    };

    final bus = BusModel.fromJson(json);
    expect(bus.id, 3);
    expect(bus.busNumber, 'Bus #03');
    expect(bus.registrationNumber, 'KA-01-AB-1234');
    expect(bus.currentOdometer, 14200.0);
  });

  test('FuelEntryModel deserialization test', () {
    final json = {
      'id': 101,
      'reference_code': 'FL-2026-AB12CD',
      'bus_id': 3,
      'bus_number': 'Bus #03',
      'fuel_litres': 45.5,
      'rate_per_litre': 101.2,
      'total_cost': 4604.6,
      'odometer_reading': 14450.0,
      'fuel_station_name': 'IOCL Campus Station',
      'bill_image_filename': 'bill_sample.jpg',
      'status': 'PENDING',
      'is_gps_verified': true,
      'duplicate_flag': false,
      'is_mileage_reliable': true
    };

    final entry = FuelEntryModel.fromJson(json);
    expect(entry.id, 101);
    expect(entry.referenceCode, 'FL-2026-AB12CD');
    expect(entry.fuelLitres, 45.5);
    expect(entry.totalCost, 4604.6);
    expect(entry.isGpsVerified, true);
    expect(entry.status, 'PENDING');
  });
}
