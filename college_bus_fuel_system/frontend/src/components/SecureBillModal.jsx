import React, { useState } from 'react';
import { X, ZoomIn, ZoomOut, CheckCircle, AlertTriangle, Info, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SecureBillModal = ({ isOpen, onClose, filename, referenceCode, ocrData, ocrConfidence, ocrStatus }) => {
  const { token } = useAuth();
  const [zoom, setZoom] = useState(1);

  if (!isOpen || !filename) return null;

  const billUrl = `/api/bills/${encodeURIComponent(filename)}?token=${encodeURIComponent(token)}`;
  const isPdf = filename.toLowerCase().endsWith('.pdf');
  const conf = Number(ocrConfidence || 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/75 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl max-w-5xl w-full max-h-[94vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              <span>Bill Receipt Document Inspection: {referenceCode}</span>
            </h3>
            <p className="text-xs text-slate-500 font-mono mt-0.5">{filename}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setZoom(prev => Math.min(prev + 0.25, 2.5))}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoom(prev => Math.max(prev - 0.25, 0.5))}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-100">
          {/* Document Viewer */}
          <div className="md:col-span-2 bg-slate-200/50 rounded-xl border border-slate-300 p-2 flex items-center justify-center min-h-[440px] overflow-auto">
            {isPdf ? (
              <iframe src={billUrl} className="w-full h-full min-h-[500px] rounded-lg" title="Receipt PDF" />
            ) : (
              <img
                src={billUrl}
                alt="Fuel Receipt Document"
                style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}
                className="max-h-[640px] rounded shadow-md transition-transform duration-150 object-contain"
              />
            )}
          </div>

          {/* OCR / AI Side-by-side verification panel */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4 h-fit shadow-sm text-xs">
            {/* Confidence & Engine Status */}
            <div className="border-b border-slate-100 pb-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">
                  AI / OCR Extraction
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                  conf >= 60 ? 'bg-emerald-100 text-emerald-800' : conf > 0 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                }`}>
                  {conf > 0 ? `${conf}% Confidence` : 'Manual Fallback'}
                </span>
              </div>
              
              {/* Visual confidence bar */}
              <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${
                    conf >= 60 ? 'bg-emerald-500' : conf > 0 ? 'bg-amber-500' : 'bg-slate-300'
                  }`}
                  style={{ width: `${conf}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">Engine Status: {ocrStatus}</p>
            </div>

            {/* Arithmetic discrepancy alert */}
            {ocrData?.arithmetic_warning && (
              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-[11px] flex items-start gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold block">Arithmetic Warning</span>
                  <span>{ocrData.arithmetic_note || 'Quantity × Rate differs from Total.'}</span>
                </div>
              </div>
            )}

            {/* Extracted Fields */}
            <div className="space-y-2.5">
              <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                <span className="text-slate-500">Fuel Station:</span>
                <span className="font-semibold text-slate-900 text-right">
                  {ocrData?.fuel_station_name || '—'}
                </span>
              </div>

              {ocrData?.station_address && (
                <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                  <span className="text-slate-500">Address / City:</span>
                  <span className="font-medium text-slate-800 text-right">
                    {ocrData.station_address}
                  </span>
                </div>
              )}

              {ocrData?.receipt_number && (
                <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                  <span className="text-slate-500">Receipt / Txn #:</span>
                  <span className="font-mono font-bold text-blue-700 text-right">
                    {ocrData.receipt_number}
                  </span>
                </div>
              )}

              <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                <span className="text-slate-500">Receipt Date:</span>
                <span className="font-mono text-slate-800 text-right">
                  {ocrData?.bill_date_str || '—'}
                </span>
              </div>

              {ocrData?.fuel_type && (
                <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                  <span className="text-slate-500">Fuel Type:</span>
                  <span className="font-bold text-slate-900 text-right">
                    {ocrData.fuel_type}
                  </span>
                </div>
              )}

              <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                <span className="text-slate-500">Quantity Volume:</span>
                <span className="font-bold text-slate-900 text-right">
                  {ocrData?.fuel_litres ? `${ocrData.fuel_litres} L/kg` : '—'}
                </span>
              </div>

              <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                <span className="text-slate-500">Rate / Unit:</span>
                <span className="font-semibold text-slate-800 text-right">
                  {ocrData?.rate_per_litre ? `₹${ocrData.rate_per_litre}` : '—'}
                </span>
              </div>

              <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                <span className="text-slate-500">Final Total Billed:</span>
                <span className="font-bold text-blue-700 text-right">
                  {ocrData?.total_cost ? `₹${ocrData.total_cost}` : '—'}
                </span>
              </div>

              {ocrData?.payment_method && (
                <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                  <span className="text-slate-500">Payment Mode:</span>
                  <span className="font-semibold text-slate-700 text-right">
                    {ocrData.payment_method}
                  </span>
                </div>
              )}

              {ocrData?.vehicle_registration && (
                <div className="flex justify-between items-start gap-2 border-b border-slate-50 pb-1.5">
                  <span className="text-slate-500">Vehicle Reg #:</span>
                  <span className="font-mono font-bold text-slate-900 text-right">
                    {ocrData.vehicle_registration}
                  </span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 leading-normal flex items-start gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
              <span>Verify that all OCR extracted figures reconcile against printed values before approval.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecureBillModal;
