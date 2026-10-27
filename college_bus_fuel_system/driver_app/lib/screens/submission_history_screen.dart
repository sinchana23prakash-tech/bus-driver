import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/fuel_service.dart';
import '../models/fuel_entry_model.dart';
import '../widgets/status_pill.dart';
import 'submission_detail_screen.dart';

class SubmissionHistoryScreen extends StatefulWidget {
  const SubmissionHistoryScreen({Key? key}) : super(key: key);

  @override
  State<SubmissionHistoryScreen> createState() => _SubmissionHistoryScreenState();
}

class _SubmissionHistoryScreenState extends State<SubmissionHistoryScreen> {
  List<FuelEntryModel> _records = [];
  bool _isLoading = true;
  String? _selectedFilter;

  final List<Map<String, String?>> _filterTabs = [
    {'label': 'All', 'value': null},
    {'label': 'Pending', 'value': 'PENDING'},
    {'label': 'Correction', 'value': 'CORRECTION_REQUIRED'},
    {'label': 'Approved', 'value': 'APPROVED'},
    {'label': 'Rejected', 'value': 'REJECTED'},
  ];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final auth = Provider.of<AuthService>(context, listen: false);
    if (auth.token == null) return;

    setState(() => _isLoading = true);
    try {
      final list = await FuelService.getMyRecords(auth.token!, status: _selectedFilter);
      setState(() => _records = list);
    } catch (e) {
      debugPrint('Error loading submissions history: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('My Fuel Submissions'),
      ),
      body: Column(
        children: [
          // Filter Tabs
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: _filterTabs.map((tab) {
                final isSelected = _selectedFilter == tab['value'];
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(tab['label']!, style: const TextStyle(fontSize: 12)),
                    selected: isSelected,
                    onSelected: (_) {
                      setState(() => _selectedFilter = tab['value']);
                      _loadHistory();
                    },
                    selectedColor: const Color(0xFFEFF6FF),
                    checkmarkColor: const Color(0xFF2563EB),
                    labelStyle: TextStyle(
                      color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF64748B),
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          // List View
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _records.isEmpty
                    ? Center(
                        child: Text(
                          'No submissions found for selected filter.',
                          style: TextStyle(color: Colors.grey.shade500, fontSize: 13),
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadHistory,
                        child: ListView.separated(
                          padding: const EdgeInsets.all(16),
                          itemCount: _records.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 10),
                          itemBuilder: (context, index) {
                            final item = _records[index];
                            return InkWell(
                              onTap: () async {
                                final res = await Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => SubmissionDetailScreen(record: item),
                                  ),
                                );
                                if (res == true) _loadHistory();
                              },
                              borderRadius: BorderRadius.circular(12),
                              child: Container(
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: item.status == 'CORRECTION_REQUIRED'
                                        ? Colors.amber.shade300
                                        : const Color(0xFFE2E8F0),
                                  ),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          item.referenceCode,
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 13,
                                            fontFamily: 'monospace',
                                          ),
                                        ),
                                        StatusPill(status: item.status),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          '${item.fuelLitres} L @ ₹${item.ratePerLitre}',
                                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                                        ),
                                        Text(
                                          '₹${item.totalCost.toStringAsFixed(2)}',
                                          style: const TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.bold,
                                            color: Color(0xFF0F172A),
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          item.fuelStationName,
                                          style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                                        ),
                                        Text(
                                          '${item.odometerReading.toStringAsFixed(0)} km',
                                          style: const TextStyle(
                                            fontSize: 11,
                                            fontFamily: 'monospace',
                                            color: Color(0xFF64748B),
                                          ),
                                        ),
                                      ],
                                    ),
                                    if (item.status == 'CORRECTION_REQUIRED')
                                      Padding(
                                        padding: const EdgeInsets.only(top: 8),
                                        child: Row(
                                          children: [
                                            Icon(Icons.touch_app, size: 14, color: Colors.amber.shade900),
                                            const SizedBox(width: 4),
                                            Text(
                                              'Action Required: Tap to edit and resubmit',
                                              style: TextStyle(
                                                fontSize: 11,
                                                fontWeight: FontWeight.bold,
                                                color: Colors.amber.shade900,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
