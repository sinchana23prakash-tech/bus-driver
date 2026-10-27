import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../models/fuel_entry_model.dart';
import '../services/auth_service.dart';
import '../services/fuel_service.dart';

class CorrectionScreen extends StatefulWidget {
  final FuelEntryModel record;

  const CorrectionScreen({Key? key, required this.record}) : super(key: key);

  @override
  State<CorrectionScreen> createState() => _CorrectionScreenState();
}

class _CorrectionScreenState extends State<CorrectionScreen> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _litresController;
  late TextEditingController _rateController;
  late TextEditingController _totalController;
  late TextEditingController _odometerController;
  late TextEditingController _stationController;

  File? _newReceiptFile;
  String? _newFilename;
  String? _newHash;
  bool _isUploadingPhoto = false;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _litresController = TextEditingController(text: widget.record.fuelLitres.toString());
    _rateController = TextEditingController(text: widget.record.ratePerLitre.toString());
    _totalController = TextEditingController(text: widget.record.totalCost.toString());
    _odometerController = TextEditingController(text: widget.record.odometerReading.toStringAsFixed(0));
    _stationController = TextEditingController(text: widget.record.fuelStationName);
  }

  void _calculateTotal() {
    final litres = double.tryParse(_litresController.text);
    final rate = double.tryParse(_rateController.text);
    if (litres != null && rate != null && litres > 0 && rate > 0) {
      _totalController.text = (litres * rate).toStringAsFixed(2);
    }
  }

  Future<void> _pickNewPhoto() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.camera, imageQuality: 85);
    if (picked == null) return;

    final file = File(picked.path);
    setState(() {
      _newReceiptFile = file;
      _isUploadingPhoto = true;
    });

    final auth = Provider.of<AuthService>(context, listen: false);
    try {
      final res = await FuelService.scanReceiptFile(file, auth.token!);
      setState(() {
        _newFilename = res['bill_image_filename'];
        _newHash = res['bill_image_hash'];
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Photo upload notice: $e')),
      );
    } finally {
      if (mounted) setState(() => _isUploadingPhoto = false);
    }
  }

  Future<void> _handleResubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);
    final auth = Provider.of<AuthService>(context, listen: false);

    try {
      final payload = {
        'fuel_litres': double.parse(_litresController.text),
        'rate_per_litre': double.parse(_rateController.text),
        'total_cost': double.parse(_totalController.text),
        'odometer_reading': double.parse(_odometerController.text),
        'fuel_station_name': _stationController.text.trim(),
        if (_newFilename != null) 'bill_image_filename': _newFilename,
        if (_newHash != null) 'bill_image_hash': _newHash,
      };

      await FuelService.resubmitCorrection(widget.record.id, payload, auth.token!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Correction resubmitted successfully!'),
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
        title: Text('Correct Entry: ${widget.record.referenceCode}'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Instructions from admin
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.amber.shade300),
                ),
                child: Text(
                  'Administrator Note: ${widget.record.correctionNotes ?? 'Adjust incorrect fields and resubmit.'}',
                  style: TextStyle(fontSize: 12, color: Colors.amber.shade900, height: 1.3),
                ),
              ),
              const SizedBox(height: 14),

              // Re-take photo option
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    const Text('Optional: Replace Receipt Photo', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: _isUploadingPhoto ? null : _pickNewPhoto,
                      icon: const Icon(Icons.camera_alt, size: 16),
                      label: Text(_isUploadingPhoto ? 'Uploading...' : 'Take New Photo', style: const TextStyle(fontSize: 12)),
                    ),
                    if (_newReceiptFile != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text('New photo attached: ${_newReceiptFile!.path.split(Platform.pathSeparator).last}', style: const TextStyle(fontSize: 11, color: Colors.green)),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              // Form fields
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    TextFormField(
                      controller: _stationController,
                      decoration: const InputDecoration(labelText: 'Station Name', border: OutlineInputBorder()),
                      validator: (val) => val == null || val.trim().isEmpty ? 'Required' : null,
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _litresController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(labelText: 'Litres', border: OutlineInputBorder()),
                            onChanged: (_) => _calculateTotal(),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: TextFormField(
                            controller: _rateController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(labelText: 'Rate/Ltr', border: OutlineInputBorder()),
                            onChanged: (_) => _calculateTotal(),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _totalController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(labelText: 'Total (₹)', border: OutlineInputBorder()),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: TextFormField(
                            controller: _odometerController,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: const InputDecoration(labelText: 'Odometer (km)', border: OutlineInputBorder()),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),

              ElevatedButton(
                onPressed: _isSubmitting ? null : _handleResubmit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: _isSubmitting
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Resubmit Entry for Review', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
