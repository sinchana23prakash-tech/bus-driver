import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/fuel_service.dart';
import '../services/location_service.dart';
import '../models/bus_model.dart';
import '../widgets/ocr_preview_card.dart';

class FuelEntryScreen extends StatefulWidget {
  final BusModel bus;

  const FuelEntryScreen({Key? key, required this.bus}) : super(key: key);

  @override
  State<FuelEntryScreen> createState() => _FuelEntryScreenState();
}

class _FuelEntryScreenState extends State<FuelEntryScreen> {
  final _formKey = GlobalKey<FormState>();

  File? _receiptImage;
  String? _uploadedFilename;
  String? _uploadedHash;
  Map<String, dynamic>? _ocrData;
  double _ocrConfidence = 0.0;
  String _ocrStatus = 'MANUAL_FALLBACK';
  String _ocrMessage = '';

  double? _latitude;
  double? _longitude;
  String? _locationStatusText;

  final _litresController = TextEditingController();
  final _rateController = TextEditingController();
  final _totalController = TextEditingController();
  final _odometerController = TextEditingController();
  final _stationController = TextEditingController();

  bool _isScanningOcr = false;
  bool _isGettingLocation = false;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _odometerController.text = widget.bus.currentOdometer.toStringAsFixed(0);
    _captureCurrentGps();
  }

  Future<void> _captureCurrentGps() async {
    setState(() => _isGettingLocation = true);
    final result = await LocationService.getCurrentCoordinates();
    setState(() {
      _isGettingLocation = false;
      if (result.isSuccess) {
        _latitude = result.latitude;
        _longitude = result.longitude;
        _locationStatusText = result.message;
      } else {
        _locationStatusText = result.message;
      }
    });
  }

  Future<void> _pickReceipt(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(
      source: source,
      maxWidth: 1600,
      maxHeight: 1600,
      imageQuality: 85,
    );

    if (pickedFile == null) return;

    final file = File(pickedFile.path);
    setState(() {
      _receiptImage = file;
      _isScanningOcr = true;
    });

    final auth = Provider.of<AuthService>(context, listen: false);
    try {
      final res = await FuelService.scanReceiptFile(file, auth.token!);
      setState(() {
        _uploadedFilename = res['bill_image_filename'];
        _uploadedHash = res['bill_image_hash'];
        _ocrConfidence = (res['ocr_confidence_score'] as num?)?.toDouble() ?? 0.0;
        _ocrStatus = res['ocr_status'] ?? 'MANUAL_FALLBACK';
        _ocrMessage = res['ocr_message'] ?? '';
        _ocrData = res['ocr_extracted_data'];

        // Auto-fill form fields from OCR if detected
        if (_ocrData != null) {
          if (_ocrData!['fuel_litres'] != null) {
            _litresController.text = _ocrData!['fuel_litres'].toString();
          }
          if (_ocrData!['rate_per_litre'] != null) {
            _rateController.text = _ocrData!['rate_per_litre'].toString();
          }
          if (_ocrData!['total_cost'] != null) {
            _totalController.text = _ocrData!['total_cost'].toString();
          }
          if (_ocrData!['fuel_station_name'] != null) {
            _stationController.text = _ocrData!['fuel_station_name'].toString();
          }
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Receipt scan notice: $e. You can fill details manually.')),
      );
    } finally {
      if (mounted) setState(() => _isScanningOcr = false);
    }
  }

  void _calculateTotal() {
    final litres = double.tryParse(_litresController.text);
    final rate = double.tryParse(_rateController.text);
    if (litres != null && rate != null && litres > 0 && rate > 0) {
      _totalController.text = (litres * rate).toStringAsFixed(2);
    }
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    if (_uploadedFilename == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture or select the fuel bill receipt.')),
      );
      return;
    }

    setState(() => _isSubmitting = true);
    final auth = Provider.of<AuthService>(context, listen: false);

    try {
      final payload = {
        'bus_id': widget.bus.id,
        'fuel_litres': double.parse(_litresController.text),
        'rate_per_litre': double.parse(_rateController.text),
        'total_cost': double.parse(_totalController.text),
        'odometer_reading': double.parse(_odometerController.text),
        'fuel_station_name': _stationController.text.trim(),
        'bill_image_filename': _uploadedFilename,
        'bill_image_hash': _uploadedHash,
        'ocr_extracted_data': _ocrData,
        'ocr_confidence_score': _ocrConfidence,
        'ocr_status': _ocrStatus,
        'latitude': _latitude,
        'longitude': _longitude,
      };

      await FuelService.submitFuelEntry(payload, auth.token!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Fuel record submitted successfully and queued for verification!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  void dispose() {
    _litresController.dispose();
    _rateController.dispose();
    _totalController.dispose();
    _odometerController.dispose();
    _stationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text('New Fuel Entry: ${widget.bus.busNumber}'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Receipt Capture Area
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    if (_receiptImage != null)
                      ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.file(
                          _receiptImage!,
                          height: 180,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                      )
                    else
                      Container(
                        height: 120,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFFCBD5E1), style: BorderStyle.solid),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            Icon(Icons.camera_alt_outlined, size: 36, color: Color(0xFF64748B)),
                            SizedBox(height: 6),
                            Text(
                              'Attach Official Petrol Bunk Bill Receipt',
                              style: TextStyle(color: Color(0xFF64748B), fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _isScanningOcr ? null : () => _pickReceipt(ImageSource.camera),
                            icon: const Icon(Icons.camera_alt, size: 16),
                            label: const Text('Camera', style: TextStyle(fontSize: 12)),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _isScanningOcr ? null : () => _pickReceipt(ImageSource.gallery),
                            icon: const Icon(Icons.photo_library, size: 16),
                            label: const Text('Gallery', style: TextStyle(fontSize: 12)),
                          ),
                        ),
                      ],
                    ),
                    if (_isScanningOcr)
                      Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                            SizedBox(width: 8),
                            Text('Scanning receipt with AI/OCR...', style: TextStyle(fontSize: 12, color: Colors.blue)),
                          ],
                        ),
                      ),
                    if (_receiptImage != null && !_isScanningOcr)
                      OcrPreviewCard(
                        confidenceScore: _ocrConfidence,
                        status: _ocrStatus,
                        message: _ocrMessage,
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              // Form fields card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),

                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      'Bill & Consumption Values',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 12),

                    // Fuel Station Name
                    TextFormField(
                      controller: _stationController,
                      decoration: const InputDecoration(
                        labelText: 'Fuel Station Name',
                        prefixIcon: Icon(Icons.local_gas_station, size: 18),
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                      validator: (val) => val == null || val.trim().isEmpty ? 'Station name is required' : null,
                    ),
                    const SizedBox(height: 12),

                    // Litres & Rate
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _litresController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(
                              labelText: 'Litres',
                              suffixText: 'L',
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            ),
                            onChanged: (_) => _calculateTotal(),
                            validator: (val) {
                              final n = double.tryParse(val ?? '');
                              return n == null || n <= 0 ? 'Enter litres' : null;
                            },
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: TextFormField(
                            controller: _rateController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(
                              labelText: 'Rate / Ltr',
                              prefixText: '₹ ',
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            ),
                            onChanged: (_) => _calculateTotal(),
                            validator: (val) {
                              final n = double.tryParse(val ?? '');
                              return n == null || n <= 0 ? 'Enter rate' : null;
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Total Cost & Odometer
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _totalController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(
                              labelText: 'Total Cost',
                              prefixText: '₹ ',
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            ),
                            validator: (val) {
                              final n = double.tryParse(val ?? '');
                              return n == null || n <= 0 ? 'Enter total' : null;
                            },
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: TextFormField(
                            controller: _odometerController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(
                              labelText: 'Odometer (km)',
                              suffixText: 'km',
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            ),
                            validator: (val) {
                              final n = double.tryParse(val ?? '');
                              return n == null || n < 0 ? 'Enter km' : null;
                            },
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              // GPS Snapshot Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    Icon(
                      _latitude != null ? Icons.location_on : Icons.location_off,
                      color: _latitude != null ? Colors.green : Colors.orange,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'GPS Verification Snapshot',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                          ),
                          Text(
                            _locationStatusText ?? 'Acquiring GPS...',
                            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: _isGettingLocation
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.my_location, size: 20),
                      onPressed: _isGettingLocation ? null : _captureCurrentGps,
                      tooltip: 'Re-acquire GPS',
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Submit Button
              ElevatedButton(
                onPressed: _isSubmitting ? null : _handleSubmit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text(
                        'Submit Fuel Entry for Approval',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
