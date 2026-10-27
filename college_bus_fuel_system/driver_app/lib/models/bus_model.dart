class BusModel {
  final int id;
  final String busNumber;
  final String registrationNumber;
  final String? modelName;
  final double fuelTankCapacity;
  final String fuelType;
  final double currentOdometer;
  final String status;

  BusModel({
    required this.id,
    required this.busNumber,
    required this.registrationNumber,
    this.modelName,
    required this.fuelTankCapacity,
    required this.fuelType,
    required this.currentOdometer,
    required this.status,
  });

  factory BusModel.fromJson(Map<String, dynamic> json) {
    return BusModel(
      id: json['id'],
      busNumber: json['bus_number'] ?? '',
      registrationNumber: json['registration_number'] ?? '',
      modelName: json['model_name'],
      fuelTankCapacity: (json['fuel_tank_capacity'] as num?)?.toDouble() ?? 150.0,
      fuelType: json['fuel_type'] ?? 'DIESEL',
      currentOdometer: (json['current_odometer'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] ?? 'ACTIVE',
    );
  }
}
