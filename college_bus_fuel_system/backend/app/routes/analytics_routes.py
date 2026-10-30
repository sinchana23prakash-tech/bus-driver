import calendar
from datetime import datetime, timedelta, date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app.models.fuel_record import FuelRecord
from app.models.bus import Bus
from app.models.user import User
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

@analytics_bp.route('/periodic-report', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def get_periodic_report():
    """
    Returns comprehensive analytics, trends, breakdown statistics, and records
    filtered by weekly, monthly, yearly, or custom date period.
    """
    period = request.args.get('period', 'monthly').lower()
    offset = int(request.args.get('offset', 0))
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Determine reference date based on latest records or current date
    latest_rec = FuelRecord.query.order_by(FuelRecord.bill_date.desc()).first()
    anchor_date = latest_rec.bill_date if latest_rec else datetime.utcnow()

    # Calculate date bounds
    if start_date_str and end_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            range_label = f"{start_dt.strftime('%b %d, %Y')} – {end_dt.strftime('%b %d, %Y')}"
            period = 'custom'
        except ValueError:
            period = 'monthly'

    if period == 'weekly':
        target_date = anchor_date + timedelta(weeks=offset)
        # Week starts Monday
        start_of_week = target_date - timedelta(days=target_date.weekday())
        start_dt = datetime(start_of_week.year, start_of_week.month, start_of_week.day, 0, 0, 0)
        end_dt = start_dt + timedelta(days=6, hours=23, minutes=59, seconds=59)
        range_label = f"Week of {start_dt.strftime('%b %d, %Y')} - {end_dt.strftime('%b %d, %Y')}"

        time_series = []
        for d in range(7):
            day_start = start_dt + timedelta(days=d)
            day_end = day_start + timedelta(days=1)
            day_recs = FuelRecord.query.filter(
                FuelRecord.bill_date >= day_start,
                FuelRecord.bill_date < day_end
            ).all()
            appr = [r for r in day_recs if r.status == 'APPROVED']
            time_series.append({
                'label': day_start.strftime('%a, %b %d'),
                'short_label': day_start.strftime('%a %d'),
                'date': day_start.strftime('%Y-%m-%d'),
                'total_cost': round(sum(float(r.total_cost) for r in day_recs), 2),
                'approved_cost': round(sum(float(r.total_cost) for r in appr), 2),
                'fuel_litres': round(sum(float(r.fuel_litres) for r in day_recs), 2),
                'approved_litres': round(sum(float(r.fuel_litres) for r in appr), 2),
                'requests_count': len(day_recs)
            })

    elif period == 'monthly':
        y = anchor_date.year
        m = anchor_date.month + offset
        while m > 12:
            m -= 12
            y += 1
        while m < 1:
            m += 12
            y -= 1

        _, last_day = calendar.monthrange(y, m)
        start_dt = datetime(y, m, 1, 0, 0, 0)
        end_dt = datetime(y, m, last_day, 23, 59, 59)
        range_label = start_dt.strftime('%B %Y')

        # Weekly buckets within the month
        time_series = []
        slices = [
            (1, min(7, last_day), 'Week 1'),
            (8, min(14, last_day), 'Week 2'),
            (15, min(21, last_day), 'Week 3'),
            (22, min(28, last_day), 'Week 4')
        ]
        if last_day > 28:
            slices.append((29, last_day, 'Week 5'))

        for s_day, e_day, w_title in slices:
            w_start = datetime(y, m, s_day, 0, 0, 0)
            w_end = datetime(y, m, e_day, 23, 59, 59)
            w_recs = FuelRecord.query.filter(
                FuelRecord.bill_date >= w_start,
                FuelRecord.bill_date <= w_end
            ).all()
            appr = [r for r in w_recs if r.status == 'APPROVED']
            time_series.append({
                'label': f"{w_title} ({m}/{s_day} - {m}/{e_day})",
                'short_label': f"{w_title} ({s_day} - {e_day})",
                'date': f"{y}-{m:02d}-{s_day:02d}",
                'total_cost': round(sum(float(r.total_cost) for r in w_recs), 2),
                'approved_cost': round(sum(float(r.total_cost) for r in appr), 2),
                'fuel_litres': round(sum(float(r.fuel_litres) for r in w_recs), 2),
                'approved_litres': round(sum(float(r.fuel_litres) for r in appr), 2),
                'requests_count': len(w_recs)
            })

    elif period == 'yearly':
        y = anchor_date.year + offset
        start_dt = datetime(y, 1, 1, 0, 0, 0)
        end_dt = datetime(y, 12, 31, 23, 59, 59)
        range_label = f"Calendar Year {y}"

        time_series = []
        for m in range(1, 13):
            _, last_day = calendar.monthrange(y, m)
            m_start = datetime(y, m, 1, 0, 0, 0)
            m_end = datetime(y, m, last_day, 23, 59, 59)
            m_recs = FuelRecord.query.filter(
                FuelRecord.bill_date >= m_start,
                FuelRecord.bill_date <= m_end
            ).all()
            appr = [r for r in m_recs if r.status == 'APPROVED']
            time_series.append({
                'label': calendar.month_name[m],
                'short_label': calendar.month_abbr[m],
                'date': f"{y}-{m:02d}",
                'total_cost': round(sum(float(r.total_cost) for r in m_recs), 2),
                'approved_cost': round(sum(float(r.total_cost) for r in appr), 2),
                'fuel_litres': round(sum(float(r.fuel_litres) for r in m_recs), 2),
                'approved_litres': round(sum(float(r.fuel_litres) for r in appr), 2),
                'requests_count': len(m_recs)
            })

    else:
        # All time
        earliest = FuelRecord.query.order_by(FuelRecord.bill_date.asc()).first()
        start_dt = earliest.bill_date if earliest else datetime(2025, 1, 1)
        end_dt = datetime.utcnow() + timedelta(days=1)
        range_label = "All Time Fleet Records"

        # Monthly series
        all_recs = FuelRecord.query.order_by(FuelRecord.bill_date.asc()).all()
        month_buckets = {}
        for r in all_recs:
            mk = r.bill_date.strftime('%Y-%m')
            if mk not in month_buckets:
                month_buckets[mk] = []
            month_buckets[mk].append(r)

        time_series = []
        for mk in sorted(month_buckets.keys()):
            m_recs = month_buckets[mk]
            appr = [r for r in m_recs if r.status == 'APPROVED']
            dt_obj = datetime.strptime(mk, '%Y-%m')
            time_series.append({
                'label': dt_obj.strftime('%b %Y'),
                'short_label': dt_obj.strftime('%b \'%y'),
                'date': mk,
                'total_cost': round(sum(float(r.total_cost) for r in m_recs), 2),
                'approved_cost': round(sum(float(r.total_cost) for r in appr), 2),
                'fuel_litres': round(sum(float(r.fuel_litres) for r in m_recs), 2),
                'approved_litres': round(sum(float(r.fuel_litres) for r in appr), 2),
                'requests_count': len(m_recs)
            })

    # Fetch records within this period
    period_records = FuelRecord.query.filter(
        FuelRecord.bill_date >= start_dt,
        FuelRecord.bill_date <= end_dt
    ).order_by(FuelRecord.bill_date.desc(), FuelRecord.id.desc()).all()

    # Totals
    total_requests = len(period_records)
    total_fuel_issued = round(sum(float(r.fuel_litres) for r in period_records), 2)
    approved_records = [r for r in period_records if r.status == 'APPROVED']
    pending_records = [r for r in period_records if r.status == 'PENDING']
    rejected_records = [r for r in period_records if r.status == 'REJECTED']
    correction_records = [r for r in period_records if r.status == 'CORRECTION_REQUIRED']

    total_fuel_consumption = round(sum(float(r.fuel_litres) for r in approved_records), 2)
    total_expenditure = round(sum(float(r.total_cost) for r in approved_records), 2)
    total_spend_all = round(sum(float(r.total_cost) for r in period_records), 2)
    pending_expenditure = round(sum(float(r.total_cost) for r in pending_records), 2)

    distinct_buses = set(r.bus_id for r in period_records if r.bus_id)
    distinct_drivers = set(r.driver_id for r in period_records if r.driver_id)
    avg_rate = round(total_spend_all / total_fuel_issued, 2) if total_fuel_issued > 0 else 0.0

    # Status Breakdown
    status_distribution = [
        {
            'status': 'APPROVED',
            'label': 'Approved',
            'count': len(approved_records),
            'total_cost': total_expenditure,
            'litres': total_fuel_consumption,
            'color': '#15803d'  # Green
        },
        {
            'status': 'PENDING',
            'label': 'Pending Review',
            'count': len(pending_records),
            'total_cost': pending_expenditure,
            'litres': round(sum(float(r.fuel_litres) for r in pending_records), 2),
            'color': '#b45309'  # Amber
        },
        {
            'status': 'REJECTED',
            'label': 'Rejected',
            'count': len(rejected_records),
            'total_cost': round(sum(float(r.total_cost) for r in rejected_records), 2),
            'litres': round(sum(float(r.fuel_litres) for r in rejected_records), 2),
            'color': '#b91c1c'  # Red
        },
        {
            'status': 'CORRECTION_REQUIRED',
            'label': 'Correction Needed',
            'count': len(correction_records),
            'total_cost': round(sum(float(r.total_cost) for r in correction_records), 2),
            'litres': round(sum(float(r.fuel_litres) for r in correction_records), 2),
            'color': '#6366f1'  # Indigo
        }
    ]

    # Driver-wise Aggregation
    driver_map = {}
    for r in period_records:
        d_id = r.driver_id or 0
        if d_id not in driver_map:
            driver_name = r.driver.full_name if r.driver else f"Driver #{d_id}"
            username = r.driver.username if r.driver else f"driver_{d_id}"
            driver_map[d_id] = {
                'driver_id': d_id,
                'driver_name': driver_name,
                'username': username,
                'total_litres': 0.0,
                'approved_litres': 0.0,
                'total_cost': 0.0,
                'approved_cost': 0.0,
                'requests_count': 0,
                'approved_count': 0,
                'buses': set()
            }
        driver_map[d_id]['total_litres'] += float(r.fuel_litres)
        driver_map[d_id]['total_cost'] += float(r.total_cost)
        driver_map[d_id]['requests_count'] += 1
        if r.bus and r.bus.bus_number:
            driver_map[d_id]['buses'].add(r.bus.bus_number)
        if r.status == 'APPROVED':
            driver_map[d_id]['approved_litres'] += float(r.fuel_litres)
            driver_map[d_id]['approved_cost'] += float(r.total_cost)
            driver_map[d_id]['approved_count'] += 1

    driver_wise = []
    for d_id, d_data in driver_map.items():
        driver_wise.append({
            'driver_id': d_id,
            'driver_name': d_data['driver_name'],
            'username': d_data['username'],
            'total_litres': round(d_data['total_litres'], 2),
            'approved_litres': round(d_data['approved_litres'], 2),
            'total_cost': round(d_data['total_cost'], 2),
            'approved_cost': round(d_data['approved_cost'], 2),
            'requests_count': d_data['requests_count'],
            'approved_count': d_data['approved_count'],
            'buses': list(d_data['buses'])
        })
    driver_wise.sort(key=lambda x: x['total_cost'], reverse=True)

    # Bus-wise Aggregation
    bus_map = {}
    for r in period_records:
        b_id = r.bus_id or 0
        if b_id not in bus_map:
            bus_num = r.bus.bus_number if r.bus else f"Bus #{b_id}"
            reg_num = r.bus.registration_number if r.bus else ''
            model = r.bus.model_name if r.bus else ''
            ftype = r.fuel_type or (r.bus.fuel_type if r.bus else 'DIESEL')
            bus_map[b_id] = {
                'bus_id': b_id,
                'bus_number': bus_num,
                'registration_number': reg_num,
                'model_name': model,
                'fuel_type': ftype,
                'total_litres': 0.0,
                'approved_litres': 0.0,
                'total_cost': 0.0,
                'approved_cost': 0.0,
                'requests_count': 0,
                'approved_count': 0,
                'odometer_min': float(r.odometer_reading),
                'odometer_max': float(r.odometer_reading)
            }
        bus_map[b_id]['total_litres'] += float(r.fuel_litres)
        bus_map[b_id]['total_cost'] += float(r.total_cost)
        bus_map[b_id]['requests_count'] += 1
        if float(r.odometer_reading) < bus_map[b_id]['odometer_min']:
            bus_map[b_id]['odometer_min'] = float(r.odometer_reading)
        if float(r.odometer_reading) > bus_map[b_id]['odometer_max']:
            bus_map[b_id]['odometer_max'] = float(r.odometer_reading)
        if r.status == 'APPROVED':
            bus_map[b_id]['approved_litres'] += float(r.fuel_litres)
            bus_map[b_id]['approved_cost'] += float(r.total_cost)
            bus_map[b_id]['approved_count'] += 1

    bus_wise = []
    for b_id, b_data in bus_map.items():
        dist_km = max(0.0, round(b_data['odometer_max'] - b_data['odometer_min'], 2))
        avg_kmpl = round(dist_km / b_data['approved_litres'], 2) if b_data['approved_litres'] > 0 and dist_km > 0 else None
        bus_wise.append({
            'bus_id': b_id,
            'bus_number': b_data['bus_number'],
            'registration_number': b_data['registration_number'],
            'model_name': b_data['model_name'],
            'fuel_type': b_data['fuel_type'],
            'total_litres': round(b_data['total_litres'], 2),
            'approved_litres': round(b_data['approved_litres'], 2),
            'total_cost': round(b_data['total_cost'], 2),
            'approved_cost': round(b_data['approved_cost'], 2),
            'requests_count': b_data['requests_count'],
            'approved_count': b_data['approved_count'],
            'distance_km': dist_km,
            'average_kmpl': avg_kmpl
        })
    bus_wise.sort(key=lambda x: x['total_cost'], reverse=True)

    # Detailed Records Table
    serialized_records = []
    for r in period_records:
        serialized_records.append({
            'id': r.id,
            'reference_code': r.reference_code,
            'bill_date': r.bill_date.isoformat(),
            'formatted_date': r.bill_date.strftime('%Y-%m-%d %H:%M'),
            'bus_number': r.bus.bus_number if r.bus else 'Unassigned',
            'registration_number': r.bus.registration_number if r.bus else '',
            'driver_name': r.driver.full_name if r.driver else 'Unassigned',
            'driver_username': r.driver.username if r.driver else '',
            'fuel_type': r.fuel_type or 'DIESEL',
            'fuel_litres': float(r.fuel_litres),
            'rate_per_litre': float(r.rate_per_litre),
            'total_cost': float(r.total_cost),
            'odometer_reading': float(r.odometer_reading),
            'fuel_station_name': r.fuel_station_name or 'N/A',
            'is_gps_verified': bool(r.is_gps_verified),
            'gps_distance_meters': float(r.gps_distance_meters) if r.gps_distance_meters else None,
            'duplicate_flag': bool(r.duplicate_flag),
            'status': r.status
        })

    return jsonify({
        'period': period,
        'offset': offset,
        'range_label': range_label,
        'start_date': start_dt.strftime('%Y-%m-%d'),
        'end_date': end_dt.strftime('%Y-%m-%d'),
        'summary': {
            'total_requests': total_requests,
            'total_fuel_issued': total_fuel_issued,
            'total_fuel_consumption': total_fuel_consumption,
            'total_expenditure': total_expenditure,
            'total_spend_all': total_spend_all,
            'pending_expenditure': pending_expenditure,
            'buses_served': len(distinct_buses),
            'drivers_active': len(distinct_drivers),
            'average_rate': avg_rate,
            'approved_count': len(approved_records),
            'pending_count': len(pending_records),
            'rejected_count': len(rejected_records),
            'correction_count': len(correction_records)
        },
        'status_distribution': status_distribution,
        'time_series': time_series,
        'driver_wise': driver_wise,
        'bus_wise': bus_wise,
        'records': serialized_records
    }), 200
