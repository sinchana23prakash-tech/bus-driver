import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import StatusBadge from '../components/StatusBadge';
import DuplicateWarningAlert from '../components/DuplicateWarningAlert';
import SecureBillModal from '../components/SecureBillModal';
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  FileText, 
  MapPin, 
  Gauge, 
  Fuel, 
  User, 
  Bus as BusIcon,
  ShieldAlert,
  Info,
  AlertTriangle
} from 'lucide-react';

const FuelDetailReview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, policies } = useAuth();

  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form states for modals/actions
  const [adminRemarks, setAdminRemarks] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [correctionNotes, setCorrectionNotes] = useState('');
  const [activeActionModal, setActiveActionModal] = useState(null); // 'APPROVE', 'REJECT', 'CORRECTION'

  const fetchDetail = async () => {
    try {
      const res = await api.get(`/fuel/records/${id}`);
      setRecord(res.data.fuel_record);
    } catch (err) {
      setErrorMsg('Failed to load fuel submission detail.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const canPerformAction = user?.role === 'ADMIN' || (user?.role === 'VC' && policies?.vc_can_approve);

  const handleApprove = async () => {
    setActionLoading(true);
    setErrorMsg('');
    try {
      await api.post(`/approvals/${id}/approve`, { remarks: adminRemarks });
      setSuccessMsg('Record approved and bus odometer updated!');
      setActiveActionModal(null);
      fetchDetail();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to approve record.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      setErrorMsg('Rejection reason is required.');
      return;
    }
    setActionLoading(true);
    setErrorMsg('');
    try {
      await api.post(`/approvals/${id}/reject`, { rejection_reason: rejectionReason });
      setSuccessMsg('Record has been marked as rejected.');
      setActiveActionModal(null);
      fetchDetail();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to reject record.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRequestCorrection = async () => {
    if (!correctionNotes.trim()) {
      setErrorMsg('Correction notes explaining what needs adjustment are required.');
      return;
    }
    setActionLoading(true);
    setErrorMsg('');
    try {
      await api.post(`/approvals/${id}/request-correction`, { correction_notes: correctionNotes });
      setSuccessMsg('Correction requested. Driver has been prompted to resubmit.');
      setActiveActionModal(null);
      fetchDetail();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to request correction.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!record) {
    return (
      <div className="p-6 text-center text-slate-500">
        Record not found.{' '}
        <Link to="/requests" className="text-blue-600 font-semibold underline">
          Back to queue
        </Link>
      </div>
    );
  }

  const isCng = (record.fuel_type || record.bus_fuel_type) === 'CNG';
  const unitLabel = isCng ? 'kg' : 'Litres';
  const economyUnit = isCng ? 'km/kg' : 'km/L';

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Back button and Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-slate-900 font-mono">
                {record.reference_code}
              </h2>
              <StatusBadge status={record.status} />
              <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                isCng ? 'bg-amber-100 text-amber-900 border border-amber-200' : 'bg-blue-100 text-blue-800'
              }`}>
                {isCng ? 'LEGACY DEMO (CNG)' : 'DIESEL'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Submitted by Driver <strong className="text-slate-800">{record.driver_name}</strong> for{' '}
              <strong className="text-slate-800">{record.bus_number}</strong> on{' '}
              {record.bill_date ? new Date(record.bill_date).toLocaleString() : '—'}
            </p>
          </div>
        </div>

        {/* View Bill Button */}
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs shadow-sm transition"
        >
          <FileText className="w-4 h-4" />
          <span>Inspect Receipt Document</span>
        </button>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Fuel Type Mismatch Alert Banner */}
      {record.fuel_type_mismatch && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start gap-3 shadow-sm">
          <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-amber-950 text-sm">Fuel Type Discrepancy Flagged</h4>
            <p className="mt-0.5 leading-relaxed">
              This transaction was logged as <strong>{record.fuel_type}</strong>, but the vehicle ({record.bus_number}) is configured to operate on <strong>{record.bus_fuel_type}</strong>. Please verify the pump receipt carefully before approving.
            </p>
          </div>
        </div>
      )}

      {/* Duplicate / Odometer Warning Banner if flagged */}
      {record.duplicate_flag && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start gap-3 shadow-sm">
          <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-amber-950 text-sm">Reviewer Advisory Warning</h4>
            <p className="mt-0.5 leading-relaxed font-mono">
              {record.duplicate_warning_details || 'Duplicate submission criteria triggered. Please inspect receipt image.'}
            </p>
          </div>
        </div>
      )}

      {/* Main Grid Inspection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left 2 Cols: Financial, Odometer & Telemetry Details */}
        <div className="md:col-span-2 space-y-6">
          {/* Card: Fuel Transaction Metrics */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
              <Fuel className="w-4 h-4 text-blue-600" />
              <span>Fuel & Financial Specifications</span>
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-slate-500 block">Fuel Quantity</span>
                <span className="text-base font-bold text-slate-900 mt-1 block">
                  {record.fuel_litres} {unitLabel}
                </span>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-slate-500 block">Rate / Unit</span>
                <span className="text-base font-bold text-slate-900 mt-1 block">
                  ₹{record.rate_per_litre.toFixed(2)}
                </span>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-slate-500 block">Total Billed Cost</span>
                <span className="text-base font-bold text-blue-700 mt-1 block">
                  ₹{record.total_cost.toFixed(2)}
                </span>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-slate-500 block">Current Odometer</span>
                <span className="text-base font-bold text-slate-900 mt-1 block font-mono">
                  {record.odometer_reading ? `${record.odometer_reading.toLocaleString()} km` : '—'}
                </span>
              </div>
            </div>

            <div className="text-xs pt-2 space-y-1">
              <p className="text-slate-600">
                <strong className="text-slate-800">Fuel Station:</strong> {record.fuel_station_name}
              </p>
              <p className="text-slate-600">
                <strong className="text-slate-800">Bill Date:</strong>{' '}
                {record.bill_date ? new Date(record.bill_date).toLocaleString() : '—'}
              </p>
              <p className="text-slate-600">
                <strong className="text-slate-800">Dispensed Fuel Type:</strong>{' '}
                <span className="font-semibold text-slate-900">{record.fuel_type || 'DIESEL'}</span>
              </p>
            </div>
          </div>

          {/* Card: Sequential Odometer & Fuel Economy Analysis */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Gauge className="w-4 h-4 text-indigo-600" />
                <span>Odometer Progression & Fuel Economy</span>
              </span>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                record.is_mileage_reliable ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {record.is_mileage_reliable ? '✓ Statistically Sound' : 'Baseline / Incomplete History'}
              </span>
            </h3>

            {/* Odometer progression sequence */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 block text-[11px]">Previous Valid Odometer</span>
                <span className="text-sm font-mono font-bold text-slate-700 mt-1 block">
                  {record.previous_odometer ? `${record.previous_odometer.toLocaleString()} km` : 'None (First Entry)'}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 block text-[11px]">Current Odometer Reading</span>
                <span className="text-sm font-mono font-bold text-slate-900 mt-1 block">
                  {record.odometer_reading ? `${record.odometer_reading.toLocaleString()} km` : '—'}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-blue-50/70 border border-blue-200">
                <span className="text-blue-700 block text-[11px]">Distance Travelled (Δ)</span>
                <span className="text-sm font-mono font-bold text-blue-900 mt-1 block">
                  {record.distance_travelled_km !== null ? `+${record.distance_travelled_km.toLocaleString()} km` : '—'}
                </span>
              </div>
            </div>

            {/* Economy evaluation or Insufficient Data notification */}
            {record.mileage_kmpl ? (
              <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-emerald-950">Calculated Fuel Economy:</span>
                  <span className="text-lg font-bold font-mono text-emerald-900">
                    {record.mileage_kmpl} {economyUnit}
                  </span>
                </div>
                <p className="text-[11px] text-emerald-800">
                  Formula: {record.distance_travelled_km} km distance ÷ {record.fuel_litres} {unitLabel} fuel consumed = {record.mileage_kmpl} {economyUnit}.
                </p>
              </div>
            ) : (
              <div className="p-3.5 rounded-xl border border-amber-200 bg-amber-50/70 text-xs text-amber-900 space-y-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <Info className="w-4 h-4 text-amber-700 shrink-0" />
                  <span>Insufficient Historical Sequence Data</span>
                </div>
                <p className="text-[11px] leading-relaxed text-amber-800">
                  Fuel economy cannot be inferred from a single refuelling event without a verified chronological baseline. Furthermore, single-event calculations are subject to partial vs. full tank variations; reliable economy requires consecutive verified fill-up sequences.
                </p>
              </div>
            )}
          </div>

          {/* Card: GPS Geofence Verification */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-600" />
                <span>GPS Location Verification</span>
              </span>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                record.is_gps_verified ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'
              }`}>
                {record.is_gps_verified ? '✓ Geofence Verified' : 'Geofence Inactive (Coordinates Unverified)'}
              </span>
            </h3>

            <div className="text-xs space-y-2">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-slate-500 block">Submitted Coordinates:</span>
                  <span className="font-mono text-slate-800">
                    {record.submission_latitude && record.submission_longitude
                      ? `${record.submission_latitude.toFixed(6)}, ${record.submission_longitude.toFixed(6)}`
                      : 'Not recorded by device'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block">Nearest Approved Bunk:</span>
                  <span className="text-slate-800 font-medium">
                    {record.gps_nearest_bunk_name || 'None within registered locations'}
                  </span>
                </div>
              </div>

              {record.gps_distance_meters !== null && (
                <p className="text-slate-600 text-xs pt-1">
                  Distance to authorized station:{' '}
                  <strong className="text-slate-900 font-mono">
                    {record.gps_distance_meters > 1000
                      ? `${(record.gps_distance_meters / 1000).toFixed(2)} km`
                      : `${record.gps_distance_meters} meters`}
                  </strong>
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Right Col: Bus Profile & Review Actions */}
        <div className="space-y-6">
          {/* Assigned Bus Info */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3 text-xs">
            <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
              <BusIcon className="w-4 h-4 text-blue-600" />
              <span>Assigned Vehicle Details</span>
            </h3>
            <div className="space-y-2.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Bus Identifier:</span>
                <span className="font-bold text-slate-900">{record.bus_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Registration:</span>
                <span className="font-mono text-slate-800">{record.bus_registration}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Configured Fuel:</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  record.bus_fuel_type === 'CNG' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                }`}>
                  {record.bus_fuel_type || 'DIESEL'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Submitting Driver:</span>
                <span className="font-semibold text-slate-900">{record.driver_name}</span>
              </div>
            </div>
          </div>

          {/* Prior Review Remarks */}
          {record.reviewed_at && (
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-5 shadow-sm space-y-2 text-xs">
              <h3 className="font-bold text-slate-800 border-b border-slate-200 pb-2">
                Audit Review Trail
              </h3>
              <p className="text-slate-600">
                Reviewed by <strong className="text-slate-900">{record.reviewer_name}</strong> on{' '}
                {new Date(record.reviewed_at).toLocaleString()}
              </p>
              {record.admin_remarks && (
                <div className="bg-white p-2.5 rounded border border-slate-200 mt-2">
                  <span className="font-semibold text-slate-700 block mb-0.5">Admin Remarks:</span>
                  <span className="text-slate-600">{record.admin_remarks}</span>
                </div>
              )}
              {record.correction_notes && (
                <div className="bg-amber-50 p-2.5 rounded border border-amber-200 mt-2 text-amber-900">
                  <span className="font-semibold block mb-0.5">Correction Instructions:</span>
                  <span>{record.correction_notes}</span>
                </div>
              )}
            </div>
          )}

          {/* Action Center */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-900 text-sm border-b border-slate-100 pb-2 flex items-center justify-between">
              <span>Approval Action Center</span>
              <span className="text-[10px] uppercase font-bold text-slate-400">
                {user?.role} Access
              </span>
            </h3>

            {/* Check if VC is read-only */}
            {!canPerformAction ? (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900 space-y-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <ShieldAlert className="w-4 h-4 text-amber-700" />
                  <span>Executive Auditor Mode (Read-Only)</span>
                </div>
                <p className="text-[11px] text-amber-800">
                  College governance policy sets Vice Chancellor access to read-only audit. Action buttons are disabled.
                </p>
              </div>
            ) : record.status === 'APPROVED' ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>This fuel entry has already been verified and approved.</span>
              </div>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={() => setActiveActionModal('APPROVE')}
                  className="w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve & Update Odometer</span>
                </button>

                <button
                  onClick={() => setActiveActionModal('CORRECTION')}
                  className="w-full py-2.5 px-4 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs shadow-sm transition flex items-center justify-center gap-2"
                >
                  <AlertCircle className="w-4 h-4" />
                  <span>Request Driver Correction</span>
                </button>

                <button
                  onClick={() => setActiveActionModal('REJECT')}
                  className="w-full py-2.5 px-4 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Submission</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bill Preview Modal */}
      <SecureBillModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        filename={record.bill_image_filename}
        referenceCode={record.reference_code}
        ocrData={record.ocr_extracted_data}
        ocrConfidence={record.ocr_confidence_score}
        ocrStatus={record.ocr_status}
      />

      {/* Action Dialog Modals */}
      {activeActionModal === 'APPROVE' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <span>Confirm Fuel Approval</span>
            </h4>
            <p className="text-xs text-slate-600">
              Approving #{record.reference_code} will finalize ₹{record.total_cost} expenditure and update Bus #{record.bus_number} odometer to {record.odometer_reading} km.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Approval Remarks (Optional):
              </label>
              <textarea
                value={adminRemarks}
                onChange={(e) => setAdminRemarks(e.target.value)}
                placeholder="Verified against pump receipt..."
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setActiveActionModal(null)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={actionLoading}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition disabled:opacity-50"
              >
                {actionLoading ? 'Approving...' : 'Confirm Approval'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeActionModal === 'CORRECTION' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-600" />
              <span>Request Driver Correction</span>
            </h4>
            <p className="text-xs text-slate-600">
              Provide instructions explaining what the driver needs to correct in their mobile app.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Correction Instructions (Required):
              </label>
              <textarea
                required
                value={correctionNotes}
                onChange={(e) => setCorrectionNotes(e.target.value)}
                placeholder="e.g., Receipt amount blurry, please re-upload clear photo of printed amount line."
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:outline-none"
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setActiveActionModal(null)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={handleRequestCorrection}
                disabled={actionLoading}
                className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-bold transition disabled:opacity-50"
              >
                {actionLoading ? 'Sending...' : 'Send to Driver'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeActionModal === 'REJECT' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <XCircle className="w-5 h-5 text-rose-600" />
              <span>Reject Submission</span>
            </h4>
            <p className="text-xs text-slate-600">
              Rejection marks this claim invalid. Please explain the justification.
            </p>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Rejection Reason (Required):
              </label>
              <textarea
                required
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="e.g., Non-institutional private vehicle receipt uploaded."
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-rose-500 focus:outline-none"
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setActiveActionModal(null)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading}
                className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition disabled:opacity-50"
              >
                {actionLoading ? 'Rejecting...' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FuelDetailReview;
