def test_mileage_calculation_and_reliability_filter(client, test_users, sample_bus):
    driver_token = test_users['tokens']['driver1']

    # Entry 1: Baseline entry (Odo: 13500 km)
    res1 = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 50.0,
        'rate_per_litre': 100.0,
        'total_cost': 5000.0,
        'odometer_reading': 13500.0,
        'fuel_station_name': 'Campus Pump',
        'bill_image_filename': 'bill_entry1.jpg'
    }, headers={'Authorization': f'Bearer {driver_token}'})
    assert res1.status_code == 201
    rec1 = res1.get_json()['fuel_record']
    # First entry has insufficient sequential data
    assert rec1['mileage_kmpl'] is None
    assert rec1['is_mileage_reliable'] is False

    # Entry 2: Sequential valid progression (Odo: 13700 km, distance: 200 km, fuel: 50L -> 4.0 km/L)
    res2 = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 50.0,
        'rate_per_litre': 100.0,
        'total_cost': 5000.0,
        'odometer_reading': 13700.0,
        'fuel_station_name': 'Campus Pump',
        'bill_image_filename': 'bill_entry2.jpg'
    }, headers={'Authorization': f'Bearer {driver_token}'})
    assert res2.status_code == 201
    rec2 = res2.get_json()['fuel_record']
    assert rec2['mileage_kmpl'] == 4.0
    assert rec2['is_mileage_reliable'] is True

    # Entry 3: Odometer rollback anomaly (Odo: 13600 km, less than previous 13700)
    res3 = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 50.0,
        'rate_per_litre': 100.0,
        'total_cost': 5000.0,
        'odometer_reading': 13600.0,
        'fuel_station_name': 'Campus Pump',
        'bill_image_filename': 'bill_entry3.jpg'
    }, headers={'Authorization': f'Bearer {driver_token}'})
    assert res3.status_code == 201
    rec3 = res3.get_json()['fuel_record']
    # Anomaly flagged: cannot claim reliable positive mileage
    assert rec3['is_mileage_reliable'] is False
