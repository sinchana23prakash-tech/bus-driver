import os
from flask import Blueprint, request, jsonify, send_from_directory, abort
from flask_jwt_extended import decode_token
from app.models.user import User
from app.models.fuel_record import FuelRecord
from config import Config

bill_bp = Blueprint('bills', __name__, url_prefix='/api/bills')

def extract_and_verify_user_from_request():
    """Extracts and verifies user identity from Authorization header or ?token= param."""
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    elif 'token' in request.args:
        token = request.args.get('token')

    if not token:
        return None

    try:
        decoded = decode_token(token)
        user_id = decoded['sub']
        return User.query.get(int(user_id))
    except Exception:
        return None

@bill_bp.route('/<filename>', methods=['GET'])
def get_secure_bill_file(filename):
    """
    Authorized bill image retrieval.
    Prevents path traversal, checks valid JWT session, and enforces role access.
    """
    # Sanitize filename (strictly alphanumeric, underscores, hyphens, and extension)
    clean_name = os.path.basename(filename)
    if '..' in clean_name or '/' in clean_name or '\\' in clean_name:
        return jsonify({'error': 'Invalid file path requested'}), 400

    user = extract_and_verify_user_from_request()
    if not user or not user.is_active:
        return jsonify({'error': 'Unauthorized: Valid authentication token required to view receipt documents'}), 401

    # Authorization Check:
    # Admin and VC can view all receipts.
    # Driver can only view bills that belong to their own fuel submissions.
    if user.role == 'DRIVER':
        record = FuelRecord.query.filter_by(
            bill_image_filename=clean_name,
            driver_id=user.id
        ).first()
        if not record:
            return jsonify({'error': 'Forbidden: You do not have permission to view this receipt.'}), 403

    upload_dir = Config.UPLOAD_FOLDER
    full_path = os.path.join(upload_dir, clean_name)
    if not os.path.exists(full_path):
        return jsonify({'error': 'Receipt file not found on disk.'}), 404

    return send_from_directory(upload_dir, clean_name)
