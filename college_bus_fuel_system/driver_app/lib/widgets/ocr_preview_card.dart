import 'package:flutter/material.dart';

class OcrPreviewCard extends StatelessWidget {
  final double confidenceScore;
  final String status;
  final String message;

  const OcrPreviewCard({
    Key? key,
    required this.confidenceScore,
    required this.status,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final bool isHighConfidence = confidenceScore >= 60.0;

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isHighConfidence ? Colors.green.shade50 : Colors.amber.shade50,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isHighConfidence ? Colors.green.shade200 : Colors.amber.shade300,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    isHighConfidence ? Icons.auto_awesome : Icons.help_outline,
                    size: 16,
                    color: isHighConfidence ? Colors.green.shade800 : Colors.amber.shade900,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'AI / OCR Receipt Scan',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      color: isHighConfidence ? Colors.green.shade900 : Colors.amber.shade900,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isHighConfidence ? Colors.green.shade100 : Colors.amber.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  confidenceScore > 0 ? '${confidenceScore.toStringAsFixed(0)}% Confidence' : 'Manual Entry',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: isHighConfidence ? Colors.green.shade900 : Colors.amber.shade900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            message.isNotEmpty
                ? message
                : 'Scanned fields have been pre-filled below. Please review and modify any incorrect values before submitting.',
            style: TextStyle(
              fontSize: 11,
              color: isHighConfidence ? Colors.green.shade800 : Colors.amber.shade900,
              height: 1.3,
            ),
          ),
        ],
      ),
    );
  }
}
