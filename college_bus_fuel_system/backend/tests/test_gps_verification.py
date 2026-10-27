def test_gps_geofence_verification(client, test_users, sample_bus, sample_bunk):
    driver_token = test_users['tokens']['driver1']

    # Case A: Inside bunk radius (Sample bunk is at 12.9716, 77.5946 with 500m radius)
    # Submission coordinate is roughly 15 meters away
    res_inside = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 40.0,
        'rate_per_litre': 98.0,
        'total_cost': 3920.0,
        'odometer_reading': 13000.0,
        'fuel_station_name': 'HPCL Campus Station',
        'bill_image_filename': 'bill_inside.jpg',
        'latitude': 12.9717,
        'longitude': 77.5947
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert res_inside.status_code == 201
    rec_inside = res_inside.get_json()['fuel_record']
    assert rec_inside['is_gps_verified'] is True
    assert rec_inside['gps_distance_meters'] < 50.0
    assert rec_inside['gps_nearest_bunk_id'] == sample_bunk.id

    # Case B: Far away from bunk (~10km away)
    res_outside = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 40.0,
        'rate_per_litre': 98.0,
        'total_cost': 3920.0,
        'odometer_reading': 13200.0,
        'fuel_station_name': 'Random Off-Campus Bunk',
        'bill_image_filename': 'bill_outside.jpg',
        'latitude': 13.0500,
        'longitude': 77.6500
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert res_outside.status_code == 201
    rec_outside = res_outside.get_json()['fuel_record']
    assert rec_outside['is_gps_verified'] is False
    assert rec_outside['gps_distance_meters'] > 5000.0
