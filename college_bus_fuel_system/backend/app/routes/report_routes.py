import io
import csv
from datetime import datetime
from flask import Blueprint, Response, request, send_file
from flask_jwt_extended import jwt_required
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.fuel_record import FuelRecord
from app.utils.auth_helpers import role_required

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/fuel-csv', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def export_fuel_csv():
    """Generates and streams a CSV of fuel records."""
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = FuelRecord.query
    if start_date_str:
        try:
            s_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(FuelRecord.bill_date >= s_dt)
        except ValueError:
            pass
    if end_date_str:
        try:
            e_dt = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(FuelRecord.bill_date <= e_dt)
        except ValueError:
            pass

    records = query.order_by(FuelRecord.bill_date.desc(), FuelRecord.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Reference Code', 'Bus Number', 'Registration', 'Driver Name', 'Bill Date',
        'Fuel Litres', 'Rate / Litre', 'Total Cost (INR)', 'Odometer Reading (KM)',
        'Fuel Station', 'GPS Verified', 'Nearest Bunk Dist (m)', 'Duplicate Warning',
        'Status', 'Reviewed By', 'Admin Remarks'
    ])

    for r in records:
        writer.writerow([
            r.reference_code,
            r.bus.bus_number if r.bus else '',
            r.bus.registration_number if r.bus else '',
            r.driver.full_name if r.driver else '',
            r.bill_date.strftime('%Y-%m-%d %H:%M') if r.bill_date else '',
            float(r.fuel_litres),
            float(r.rate_per_litre),
            float(r.total_cost),
            float(r.odometer_reading),
            r.fuel_station_name,
            'YES' if r.is_gps_verified else 'NO',
            float(r.gps_distance_meters) if r.gps_distance_meters else 'N/A',
            'YES' if r.duplicate_flag else 'NO',
            r.status,
            r.reviewer.full_name if r.reviewer else '',
            r.admin_remarks or ''
        ])

    output.seek(0)
    filename = f"college_bus_fuel_report_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@report_bp.route('/fuel-pdf', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def export_fuel_pdf():
    """Generates a formal PDF audit summary report using ReportLab."""
    records = FuelRecord.query.order_by(FuelRecord.created_at.desc()).limit(100).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1  # Center
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        alignment=1
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )

    elements = []

    # Header
    elements.append(Paragraph("COLLEGE TRANSPORTATION DEPARTMENT", title_style))
    elements.append(Paragraph(f"Official Fleet Fuel & Mileage Audit Report — Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", subtitle_style))
    elements.append(Spacer(1, 15))

    # Table Header
    table_data = [[
        Paragraph('<b>Ref Code</b>', cell_style),
        Paragraph('<b>Bus</b>', cell_style),
        Paragraph('<b>Driver</b>', cell_style),
        Paragraph('<b>Date</b>', cell_style),
        Paragraph('<b>Litres</b>', cell_style),
        Paragraph('<b>Cost (₹)</b>', cell_style),
        Paragraph('<b>Odo (km)</b>', cell_style),
        Paragraph('<b>Station</b>', cell_style),
        Paragraph('<b>GPS</b>', cell_style),
        Paragraph('<b>Status</b>', cell_style)
    ]]

    for r in records:
        table_data.append([
            Paragraph(r.reference_code, cell_style),
            Paragraph(r.bus.bus_number if r.bus else '', cell_style),
            Paragraph(r.driver.full_name if r.driver else '', cell_style),
            Paragraph(r.bill_date.strftime('%Y-%m-%d') if r.bill_date else '', cell_style),
            Paragraph(f"{float(r.fuel_litres):.1f} L", cell_style),
            Paragraph(f"₹{float(r.total_cost):.2f}", cell_style),
            Paragraph(f"{float(r.odometer_reading):.0f}", cell_style),
            Paragraph(r.fuel_station_name[:20], cell_style),
            Paragraph('Verified' if r.is_gps_verified else 'Warning', cell_style),
            Paragraph(r.status, cell_style)
        ])

    col_widths = [85, 55, 90, 65, 55, 65, 55, 110, 60, 80]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
    ]))

    elements.append(t)
    doc.build(elements)

    buffer.seek(0)
    filename = f"college_fuel_audit_report_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
