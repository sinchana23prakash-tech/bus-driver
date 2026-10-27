import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/fuel_service.dart';
import '../models/bus_model.dart';
import '../models/fuel_entry_model.dart';
import 'fuel_entry_screen.dart';
import 'submission_history_screen.dart';
import '../widgets/status_pill.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  BusModel? _assignedBus;
  List<FuelEntryModel> _recentSubmissions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    final auth = Provider.of<AuthService>(context, listen: false);
    if (auth.token == null) return;

    setState(() => _isLoading = true);
    try {
      final bus = await FuelService.getMyAssignedBus(auth.token!);
      final records = await FuelService.getMyRecords(auth.token!);
      setState(() {
        _assignedBus = bus;
        _recentSubmissions = records.take(3).toList();
      });
    } catch (e) {
      debugPrint('Error loading driver dashboard: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthService>(context);
    final driver = auth.currentUser;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Driver Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _loadDashboardData,
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            onPressed: () => auth.logout(),
            tooltip: 'Sign Out',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Driver Info Header
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF1E3A8A), Color(0xFF2563EB)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Row(
                        children: [
                          CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.white.withOpacity(0.2),
                            child: const Icon(Icons.person, color: Colors.white, size: 28),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  driver?.fullName ?? 'Driver',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Employee ID: ${driver?.username ?? '—'}',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.8),
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Assigned Bus Details Card
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.02),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.directions_bus, size: 18, color: Color(0xFF2563EB)),
                                  const SizedBox(width: 6),
                                  const Text(
                                    'Assigned Vehicle',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                      color: Color(0xFF334155),
                                    ),
                                  ),
                                ],
                              ),
                              if (_assignedBus != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.green.shade50,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    _assignedBus!.status,
                                    style: TextStyle(
                                      color: Colors.green.shade800,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 10,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                          const Divider(height: 20),
                          if (_assignedBus == null)
                            const Padding(
                              padding: EdgeInsets.symmetric(vertical: 8),
                              child: Text(
                                'No bus is currently assigned to your driver account. Please contact Fleet Administrator.',
                                style: TextStyle(color: Colors.orange, fontSize: 12),
                              ),
                            )
                          else
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _assignedBus!.busNumber,
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF0F172A),
                                      ),
                                    ),
                                    Text(
                                      _assignedBus!.registrationNumber,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Color(0xFF64748B),
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: [
                                    const Text(
                                      'Current Odometer',
                                      style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                                    ),
                                    Text(
                                      '${_assignedBus!.currentOdometer.toStringAsFixed(0)} km',
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF1E3A8A),
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Quick Actions
                    Row(
                      children: [
                        Expanded(
                          child: InkWell(
                            onTap: () async {
                              if (_assignedBus == null) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                      'No bus is currently assigned. Please contact the Fleet Administrator to assign a bus to your account before submitting fuel entries.',
                                    ),
                                    backgroundColor: Color(0xFFDC2626),
                                    duration: Duration(seconds: 4),
                                  ),
                                );
                                return;
                              }
                              final res = await Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => FuelEntryScreen(bus: _assignedBus!),
                                ),
                              );
                              if (res == true) _loadDashboardData();
                            },
                            borderRadius: BorderRadius.circular(14),
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 14),
                              decoration: BoxDecoration(
                                color: _assignedBus == null
                                    ? const Color(0xFF94A3B8)
                                    : const Color(0xFF2563EB),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: Column(
                                children: [
                                  const Icon(Icons.local_gas_station_rounded, color: Colors.white, size: 28),
                                  const SizedBox(height: 8),
                                  const Text(
                                    'Submit Fuel Entry',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                    ),
                                  ),
                                  if (_assignedBus == null) ...[
                                    const SizedBox(height: 4),
                                    const Text(
                                      '(Bus Assignment Required)',
                                      style: TextStyle(
                                        color: Color(0xFFF1F5F9),
                                        fontSize: 10,
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: InkWell(
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const SubmissionHistoryScreen(),
                                ),
                              );
                            },
                            borderRadius: BorderRadius.circular(14),
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 14),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(color: const Color(0xFFCBD5E1)),
                              ),
                              child: Column(
                                children: const [
                                  Icon(Icons.history_rounded, color: Color(0xFF1E3A8A), size: 28),
                                  SizedBox(height: 8),
                                  Text(
                                    'My Submissions',
                                    style: TextStyle(
                                      color: Color(0xFF0F172A),
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Recent Submissions Section
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Recent Submissions',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        TextButton(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const SubmissionHistoryScreen(),
                              ),
                            );
                          },
                          child: const Text('View All', style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),

                    if (_recentSubmissions.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(24),
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: const Text(
                          'No fuel entries submitted yet.',
                          style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                        ),
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _recentSubmissions.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, index) {
                          final rec = _recentSubmissions[index];
                          return Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: Row(
                              children: [
                                CircleAvatar(
                                  radius: 18,
                                  backgroundColor: const Color(0xFFEFF6FF),
                                  child: const Icon(
                                    Icons.receipt_long_rounded,
                                    color: Color(0xFF2563EB),
                                    size: 18,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        rec.referenceCode,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13,
                                          fontFamily: 'monospace',
                                        ),
                                      ),
                                      Text(
                                        '${rec.fuelLitres} L • ₹${rec.totalCost.toStringAsFixed(2)}',
                                        style: const TextStyle(
                                          fontSize: 12,
                                          color: Color(0xFF64748B),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                StatusPill(status: rec.status),
                              ],
                            ),
                          );
                        },
                      ),
                  ],
                ),
              ),
            ),
    );
  }
}
