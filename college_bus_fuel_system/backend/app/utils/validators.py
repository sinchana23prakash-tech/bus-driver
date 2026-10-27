import re

def validate_email_format(email: str) -> bool:
    if not email or len(email) > 120:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def validate_fuel_submission_data(data: dict) -> list:
    """Validates raw fuel submission inputs and returns list of error messages."""
    errors = []

    bus_id = data.get('bus_id')
    if not bus_id:
        errors.append("bus_id is required.")

    try:
        fuel_litres = float(data.get('fuel_litres', 0))
        if fuel_litres <= 0 or fuel_litres > 600:
            errors.append("fuel_litres must be between 0.1 and 600.0 litres.")
    except (ValueError, TypeError):
        errors.append("Invalid numerical value for fuel_litres.")

    try:
        rate = float(data.get('rate_per_litre', 0))
        if rate <= 0 or rate > 300:
            errors.append("rate_per_litre must be a valid positive rate.")
    except (ValueError, TypeError):
        errors.append("Invalid numerical value for rate_per_litre.")

    try:
        total_cost = float(data.get('total_cost', 0))
        if total_cost <= 0:
            errors.append("total_cost must be greater than 0.")
    except (ValueError, TypeError):
        errors.append("Invalid numerical value for total_cost.")

    try:
        odometer = float(data.get('odometer_reading', 0))
        if odometer <= 0:
            errors.append("odometer_reading must be a positive number greater than 0.")
    except (ValueError, TypeError):
        errors.append("Invalid numerical value for odometer_reading.")

    station_name = data.get('fuel_station_name', '').strip()
    if not station_name or len(station_name) < 2:
        errors.append("fuel_station_name is required.")

    fuel_type = data.get('fuel_type')
    if fuel_type:
        fuel_type_str = str(fuel_type).strip().upper()
        if fuel_type_str != 'DIESEL':
            errors.append(f"Invalid fuel type '{fuel_type}'. Institutional college bus fleet operates strictly on DIESEL.")

    return errors

def check_odometer_warnings(bus, odometer_reading: float) -> list:
    """
    Checks for non-blocking odometer regression or anomalies.
    Returns list of warning messages for reviewer inspection.
    """
    warnings = []
    if bus and bus.current_odometer is not None:
        current_bus_odo = float(bus.current_odometer)
        if current_bus_odo > 0 and odometer_reading < current_bus_odo:
            diff = current_bus_odo - odometer_reading
            warnings.append(
                f"Odometer regression detected: Submitted {odometer_reading:,.0f} km is {diff:,.0f} km lower than the bus's last recorded odometer ({current_bus_odo:,.0f} km)."
            )
    return warnings
