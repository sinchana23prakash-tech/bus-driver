import React from 'react';
import { Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

const StatusBadge = ({ status }) => {
  switch (status) {
    case 'APPROVED':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Approved
        </span>
      );
    case 'REJECTED':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          <XCircle className="w-3.5 h-3.5" />
          Rejected
        </span>
      );
    case 'CORRECTION_REQUIRED':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
          <AlertCircle className="w-3.5 h-3.5" />
          Correction Needed
        </span>
      );
    case 'PENDING':
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <Clock className="w-3.5 h-3.5" />
          Pending Review
        </span>
      );
  }
};

export default StatusBadge;
