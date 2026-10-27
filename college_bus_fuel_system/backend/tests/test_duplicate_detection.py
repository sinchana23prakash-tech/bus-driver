def test_duplicate_bill_detection_generates_human_review_warning(client, test_users, sample_bus):
    driver_token = test_users['tokens']['driver1']

    test_image_hash = "ff00aa55331100aa"

    # Submission 1: Original
    res1 = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 50.0,
        'rate_per_litre': 100.0,
        'total_cost': 5000.0,
        'odometer_reading': 12800.0,
        'fuel_station_name': 'IOCL Campus Station',
        'bill_image_filename': 'bill_original.jpg',
        'bill_image_hash': test_image_hash
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert res1.status_code == 201
    rec1 = res1.get_json()['fuel_record']
    assert rec1['duplicate_flag'] is False

    # Submission 2: Re-using the same receipt image hash
    res2 = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 50.0,
        'rate_per_litre': 100.0,
        'total_cost': 5000.0,
        'odometer_reading': 12950.0,
        'fuel_station_name': 'IOCL Campus Station',
        'bill_image_filename': 'bill_reused.jpg',
        'bill_image_hash': test_image_hash  # Same hash
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert res2.status_code == 201
    rec2 = res2.get_json()['fuel_record']
    # Must flag warning for reviewer, without crashing or making fraud accusations
    assert rec2['duplicate_flag'] is True
    assert 'Perceptual receipt match' in rec2['duplicate_warning_details']
    assert rec2['status'] == 'PENDING'  # Stays queued for human reviewer discretion
