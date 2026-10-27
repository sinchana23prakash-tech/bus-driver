import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/fuel_entry_model.dart';
import '../widgets/status_pill.dart';
import 'correction_screen.dart';

class SubmissionDetailScreen extends StatelessWidget {
  final FuelEntryModel record;

  const SubmissionDetailScreen({Key? key, required this.record}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text(record.referenceCode),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Submission Status',
                        style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        record.status,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  StatusPill(status: record.status),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Correction Callout
            if (record.status == 'CORRECTION_REQUIRED') ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.amber.shade300),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.edit_note, color: Colors.amber.shade900),
                        const SizedBox(width: 8),
                        Text(
                          'Correction Requested by Administrator',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                            color: Colors.amber.shade900,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      record.correctionNotes ?? 'Please review and resubmit details.',
                      style: TextStyle(fontSize: 12, color: Colors.amber.shade900),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton.icon(
                      onPressed: () async {
                        final res = await Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => CorrectionScreen(record: record),
                          ),
                        );
                        if (res == true && context.mounted) {
                          Navigator.pop(context, true);
                        }
                      },
                      icon: const Icon(Icons.edit, size: 16),
                      label: const Text('Edit & Resubmit Entry'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.amber.shade700,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
            ],

            // Fuel Data Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Entry Specifications',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                  const Divider(height: 20),
                  _buildDataRow('Bus Number', record.busNumber ?? 'Assigned Bus'),
                  _buildDataRow('Station Name', record.fuelStationName),
                  _buildDataRow('Fuel Volume', '${record.fuelLitres} Litres'),
                  _buildDataRow('Rate / Litre', '₹ ${record.ratePerLitre.toStringAsFixed(2)}'),
                  _buildDataRow('Total Amount', '₹ ${record.totalCost.toStringAsFixed(2)}', isBold: true),
                  _buildDataRow('Odometer Reading', '${record.odometerReading.toStringAsFixed(0)} km'),
                  _buildDataRow('GPS Geofence', record.isGpsVerified ? 'Verified' : 'Unverified'),
                  if (record.billDate != null)
                    _buildDataRow('Receipt Date', record.billDate!.toLocal().toString().split('.')[0]),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Review Remarks if any
            if (record.adminRemarks != null && record.adminRemarks!.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Admin Remarks', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    const SizedBox(height: 4),
                    Text(record.adminRemarks!, style: const TextStyle(fontSize: 12, color: Color(0xFF475569))),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataRow(String label, String value, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
          Text(
            value,
            style: TextStyle(
              fontSize: 12,
              fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
              color: isBold ? const Color(0xFF2563EB) : const Color(0xFF0F172A),
            ),
          ),
        ],
      ),
    );
  }
}
