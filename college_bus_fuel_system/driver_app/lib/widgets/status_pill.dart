import 'package:flutter/material.dart';

class StatusPill extends StatelessWidget {
  final String status;

  const StatusPill({Key? key, required this.status}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    String label;
    IconData icon;

    switch (status) {
      case 'APPROVED':
        bg = Colors.green.shade50;
        fg = Colors.green.shade800;
        label = 'Approved';
        icon = Icons.check_circle_outline;
        break;
      case 'REJECTED':
        bg = Colors.red.shade50;
        fg = Colors.red.shade800;
        label = 'Rejected';
        icon = Icons.cancel_outlined;
        break;
      case 'CORRECTION_REQUIRED':
        bg = Colors.amber.shade50;
        fg = Colors.amber.shade900;
        label = 'Correction Needed';
        icon = Icons.error_outline;
        break;
      case 'PENDING':
      default:
        bg = Colors.blue.shade50;
        fg = Colors.blue.shade800;
        label = 'Pending Review';
        icon = Icons.access_time;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: fg.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: fg),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: fg,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
