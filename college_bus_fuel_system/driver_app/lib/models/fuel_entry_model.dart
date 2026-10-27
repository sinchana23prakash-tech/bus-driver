class FuelEntryModel {
  final int id;
  final String referenceCode;
  final int busId;
  final String? busNumber;
  final double fuelLitres;
  final double ratePerLitre;
  final double totalCost;
  final double odometerReading;
  final String fuelStationName;
  final String billImageFilename;
  final DateTime? billDate;
  final String status;
  final bool isGpsVerified;
  final double? gpsDistanceMeters;
  final bool duplicateFlag;
  final String? duplicateWarningDetails;
  final String? adminRemarks;
  final String? correctionNotes;
  final double? ocrConfidenceScore;
  final String? ocrStatus;
  final double? mileageKmpl;
  final bool isMileageReliable;
  final DateTime? createdAt;

  FuelEntryModel({
    required this.id,
    required this.referenceCode,
    required this.busId,
    this.busNumber,
    required this.fuelLitres,
    required this.ratePerLitre,
    required this.totalCost,
    required this.odometerReading,
    required this.fuelStationName,
    required this.billImageFilename,
    this.billDate,
    required this.status,
    required this.isGpsVerified,
    this.gpsDistanceMeters,
    required this.duplicateFlag,
    this.duplicateWarningDetails,
    this.adminRemarks,
    this.correctionNotes,
    this.ocrConfidenceScore,
    this.ocrStatus,
    this.mileageKmpl,
    required this.isMileageReliable,
    this.createdAt,
  });

  factory FuelEntryModel.fromJson(Map<String, dynamic> json) {
    return FuelEntryModel(
      id: json['id'],
      referenceCode: json['reference_code'] ?? '',
      busId: json['bus_id'],
      busNumber: json['bus_number'],
      fuelLitres: (json['fuel_litres'] as num?)?.toDouble() ?? 0.0,
      ratePerLitre: (json['rate_per_litre'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
      odometerReading: (json['odometer_reading'] as num?)?.toDouble() ?? 0.0,
      fuelStationName: json['fuel_station_name'] ?? '',
      billImageFilename: json['bill_image_filename'] ?? '',
      billDate: json['bill_date'] != null ? DateTime.tryParse(json['bill_date']) : null,
      status: json['status'] ?? 'PENDING',
      isGpsVerified: json['is_gps_verified'] ?? false,
      gpsDistanceMeters: (json['gps_distance_meters'] as num?)?.toDouble(),
      duplicateFlag: json['duplicate_flag'] ?? false,
      duplicateWarningDetails: json['duplicate_warning_details'],
      adminRemarks: json['admin_remarks'],
      correctionNotes: json['correction_notes'],
      ocrConfidenceScore: (json['ocr_confidence_score'] as num?)?.toDouble(),
      ocrStatus: json['ocr_status'],
      mileageKmpl: (json['mileage_kmpl'] as num?)?.toDouble(),
      isMileageReliable: json['is_mileage_reliable'] ?? false,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
    );
  }
}
