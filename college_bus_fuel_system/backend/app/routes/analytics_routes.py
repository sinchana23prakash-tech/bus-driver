from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app.models.fuel_record import FuelRecord
from app.models.bus import Bus
from app.models.mileage import MileageComputation
from app.utils.auth_helpers import role_required

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def get_analytics_overview():
    """
    Provides high-level fleet KPIs, Diesel expenditure, status distributions,
    and bus-wise efficiency metrics calculated strictly dynamically from the database.
    """
    # 1. Approved Diesel Operational Totals (Strictly Approved DIESEL only)
    approved_diesel_spend = FuelRecord.query.filter_by(
        status='APPROVED',
        fuel_type='DIESEL'
    ).with_entities(func.sum(FuelRecord.total_cost)).scalar() or 0.0

    approved_diesel_litres = FuelRecord.query.filter_by(
        status='APPROVED',
        fuel_type='DIESEL'
    ).with_entities(func.sum(FuelRecord.fuel_litres)).scalar() or 0.0

    # 1b. Current Month Approved Diesel Totals (Across ALL 5 buses)
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    if now.month == 12:
        start_of_next_month = datetime(now.year + 1, 1, 1)
    else:
        start_of_next_month = datetime(now.year, now.month + 1, 1)

    current_month_diesel_spend = FuelRecord.query.filter(
        FuelRecord.status == 'APPROVED',
        FuelRecord.fuel_type == 'DIESEL',
        FuelRecord.bill_date >= start_of_month,
        FuelRecord.bill_date < start_of_next_month
    ).with_entities(func.sum(FuelRecord.total_cost)).scalar() or 0.0

    current_month_diesel_litres = FuelRecord.query.filter(
        FuelRecord.status == 'APPROVED',
        FuelRecord.fuel_type == 'DIESEL',
        FuelRecord.bill_date >= start_of_month,
        FuelRecord.bill_date < start_of_next_month
    ).with_entities(func.sum(FuelRecord.fuel_litres)).scalar() or 0.0

    current_month_label = now.strftime('%B %Y')

    # 2. Pending Review Queue (Strictly separated from operational expenditure)
    pending_count = FuelRecord.query.filter_by(status='PENDING').count()
    pending_spend = FuelRecord.query.filter_by(status='PENDING').with_entities(
        func.sum(FuelRecord.total_cost)
    ).scalar() or 0.0

    duplicate_count = FuelRecord.query.filter_by(duplicate_flag=True).count()
    total_buses = Bus.query.count()
    active_diesel_buses = Bus.query.filter_by(status='ACTIVE', fuel_type='DIESEL').count()

    # 3. Status Distribution Breakdown (Dynamic)
    status_counts = {}
    for st in ['APPROVED', 'PENDING', 'REJECTED', 'CORRECTION_REQUIRED']:
        cnt = FuelRecord.query.filter_by(status=st).count()
        sp = FuelRecord.query.filter_by(status=st).with_entities(func.sum(FuelRecord.total_cost)).scalar() or 0.0
        status_counts[st] = {
            'count': cnt,
            'total_cost': float(round(sp, 2))
        }

    # 4. Average Reliable Fleet Diesel Mileage (Sequence-verified heavy bus window: 2.0 - 9.0 km/L)
    avg_reliable_kmpl = MileageComputation.query.join(
        FuelRecord, MileageComputation.fuel_record_id == FuelRecord.id
    ).filter(
        FuelRecord.status == 'APPROVED',
        FuelRecord.fuel_type == 'DIESEL',
        MileageComputation.is_statistically_reliable == True
    ).with_entities(func.avg(MileageComputation.calculated_kmpl)).scalar()

    # 5. Bus-Wise Efficiency & Diesel Consumption (Dynamic)
    buses = Bus.query.order_by(Bus.id.asc()).all()
    bus_efficiency = []
    for bus in buses:
        # Sum only APPROVED DIESEL litres and cost
        bus_litres = FuelRecord.query.filter_by(
            bus_id=bus.id,
            status='APPROVED',
            fuel_type='DIESEL'
        ).with_entities(func.sum(FuelRecord.fuel_litres)).scalar() or 0.0

        bus_spend = FuelRecord.query.filter_by(
            bus_id=bus.id,
            status='APPROVED',
            fuel_type='DIESEL'
        ).with_entities(func.sum(FuelRecord.total_cost)).scalar() or 0.0

        reliable_logs = MileageComputation.query.join(
            FuelRecord, MileageComputation.fuel_record_id == FuelRecord.id
        ).filter(
            MileageComputation.bus_id == bus.id,
            FuelRecord.status == 'APPROVED',
            FuelRecord.fuel_type == 'DIESEL',
            MileageComputation.is_statistically_reliable == True
        ).all()

        if reliable_logs:
            avg_bus_kmpl = round(sum(float(l.calculated_kmpl) for l in reliable_logs) / len(reliable_logs), 2)
        else:
            avg_bus_kmpl = None

        bus_efficiency.append({
            'bus_id': bus.id,
            'bus_number': bus.bus_number,
            'registration_number': bus.registration_number,
            'model_name': bus.model_name,
            'fuel_type': bus.fuel_type or 'DIESEL',
            'current_odometer': float(bus.current_odometer),
            'total_diesel_litres': round(float(bus_litres), 2),
            'total_diesel_spend': round(float(bus_spend), 2),
            'reliable_avg_kmpl': avg_bus_kmpl
        })

    # 6. Recent Submissions Preview (Latest 5 records)
    recent_recs = FuelRecord.query.order_by(FuelRecord.bill_date.desc(), FuelRecord.id.desc()).limit(5).all()
    recent_submissions = [r.to_dict() for r in recent_recs]

    return jsonify({
        'total_spend': float(round(approved_diesel_spend, 2)),
        'total_diesel_spend': float(round(approved_diesel_spend, 2)),
        'total_litres': float(round(approved_diesel_litres, 2)),
        'total_diesel_litres': float(round(approved_diesel_litres, 2)),
        'current_month_diesel_spend': float(round(current_month_diesel_spend, 2)),
        'current_month_diesel_litres': float(round(current_month_diesel_litres, 2)),
        'current_month_label': current_month_label,
        'pending_approvals': pending_count,
        'pending_spend': float(round(pending_spend, 2)),
        'duplicate_warnings': duplicate_count,
        'active_buses': active_diesel_buses,
        'active_diesel_buses': active_diesel_buses,
        'total_buses': total_buses,
        'average_fleet_kmpl': float(round(avg_reliable_kmpl, 2)) if avg_reliable_kmpl else None,
        'average_diesel_kmpl': float(round(avg_reliable_kmpl, 2)) if avg_reliable_kmpl else None,
        'status_distribution': status_counts,
        'bus_efficiency': bus_efficiency,
        'recent_submissions': recent_submissions
    }), 200

@analytics_bp.route('/monthly-trends', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def get_monthly_trends():
    """
    Returns monthly aggregation of Diesel fuel litres and expenditure.
    Distinguishes approved Diesel from pending records to prevent double-counting.
    """
    all_records = FuelRecord.query.filter(
        FuelRecord.status.in_(['APPROVED', 'PENDING', 'REJECTED'])
    ).order_by(FuelRecord.bill_date.asc()).all()

    monthly_map = {}
    for r in all_records:
        month_key = r.bill_date.strftime('%Y-%m')
        if month_key not in monthly_map:
            dt = r.bill_date
            monthly_map[month_key] = {
                'month': month_key,
                'month_label': dt.strftime('%b %Y'),
                'approved_cost': 0.0,
                'approved_litres': 0.0,
                'approved_count': 0,
                'pending_cost': 0.0,
                'pending_litres': 0.0,
                'pending_count': 0,
                'rejected_count': 0,
                'diesel_litres': 0.0
            }

        rec_cost = float(r.total_cost)
        rec_litres = float(r.fuel_litres)
        ftype = (r.fuel_type or 'DIESEL').upper()

        if r.status == 'APPROVED':
            # Only count Diesel in institutional fuel spend & volume
            if ftype == 'DIESEL':
                monthly_map[month_key]['approved_cost'] += rec_cost
                monthly_map[month_key]['approved_litres'] += rec_litres
                monthly_map[month_key]['approved_count'] += 1
                monthly_map[month_key]['diesel_litres'] += rec_litres
        elif r.status == 'PENDING':
            monthly_map[month_key]['pending_cost'] += rec_cost
            monthly_map[month_key]['pending_litres'] += rec_litres
            monthly_map[month_key]['pending_count'] += 1
        elif r.status == 'REJECTED':
            monthly_map[month_key]['rejected_count'] += 1

    results = []
    for k in sorted(monthly_map.keys()):
        item = monthly_map[k]
        item['approved_cost'] = round(item['approved_cost'], 2)
        item['approved_litres'] = round(item['approved_litres'], 2)
        item['pending_cost'] = round(item['pending_cost'], 2)
        item['pending_litres'] = round(item['pending_litres'], 2)
        item['diesel_litres'] = round(item['diesel_litres'], 2)

        # Backwards compatible aliases
        item['total_cost'] = item['approved_cost']
        item['litres'] = item['approved_litres']
        item['avg_rate'] = round(item['approved_cost'] / item['approved_litres'], 2) if item['approved_litres'] > 0 else 0.0
        results.append(item)

    return jsonify({'monthly_trends': results}), 200

@analytics_bp.route('/bus-efficiency', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def get_bus_efficiency():
    """Returns per-bus fuel consumption, distance, and reliable mileage statistics for Diesel fleet."""
    buses = Bus.query.order_by(Bus.id.asc()).all()
    bus_stats = []

    for bus in buses:
        # Sum approved Diesel litres & spend strictly
        litres = FuelRecord.query.filter_by(
            bus_id=bus.id,
            status='APPROVED',
            fuel_type='DIESEL'
        ).with_entities(func.sum(FuelRecord.fuel_litres)).scalar() or 0.0

        spend = FuelRecord.query.filter_by(
            bus_id=bus.id,
            status='APPROVED',
            fuel_type='DIESEL'
        ).with_entities(func.sum(FuelRecord.total_cost)).scalar() or 0.0

        # Reliable mileage computations (Diesel only)
        reliable_logs = MileageComputation.query.join(
            FuelRecord, MileageComputation.fuel_record_id == FuelRecord.id
        ).filter(
            MileageComputation.bus_id == bus.id,
            FuelRecord.status == 'APPROVED',
            FuelRecord.fuel_type == 'DIESEL',
            MileageComputation.is_statistically_reliable == True
        ).all()

        if reliable_logs:
            avg_kmpl = round(sum(float(l.calculated_kmpl) for l in reliable_logs) / len(reliable_logs), 2)
            total_dist = round(sum(float(l.distance_travelled_km) for l in reliable_logs), 2)
        else:
            avg_kmpl = None
            total_dist = 0.0

        bus_stats.append({
            'bus_id': bus.id,
            'bus_number': bus.bus_number,
            'registration_number': bus.registration_number,
            'model_name': bus.model_name,
            'fuel_type': bus.fuel_type or 'DIESEL',
            'current_odometer': float(bus.current_odometer),
            'total_litres': round(float(litres), 2),
            'total_diesel_litres': round(float(litres), 2),
            'total_spend': round(float(spend), 2),
            'total_diesel_spend': round(float(spend), 2),
            'reliable_avg_kmpl': avg_kmpl,
            'reliable_distance_km': total_dist,
            'reliable_samples_count': len(reliable_logs)
        })

    return jsonify({'bus_efficiency': bus_stats}), 200
