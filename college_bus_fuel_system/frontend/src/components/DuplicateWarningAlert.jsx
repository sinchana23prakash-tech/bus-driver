import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

const DuplicateWarningAlert = ({ warningDetails, matchedId }) => {
  if (!warningDetails) return null;

  return (
    <div className="bg-amber-50 border border-amber-300 rounded-lg p-4 my-3 text-sm text-amber-900 shadow-sm">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-amber-950 flex items-center gap-1.5">
            Verification Notice: Potential Duplicate / Repeated Receipt
          </p>
          <p className="text-xs text-amber-800 leading-relaxed">
            {warningDetails}
          </p>
          <div className="flex items-center gap-1 text-[11px] text-amber-700 mt-2">
            <Info className="w-3.5 h-3.5" />
            <span>This is an automated advisory flag for reviewer inspection, not an accusation of discrepancy.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DuplicateWarningAlert;
