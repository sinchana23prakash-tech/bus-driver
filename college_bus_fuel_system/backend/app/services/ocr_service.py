import os
import re
import json
import shutil
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
from config import Config

# Attempt importing pytesseract
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# Attempt importing google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def find_tesseract_binary() -> str:
    """Finds working tesseract binary path on Windows or PATH."""
    configured_cmd = Config.TESSERACT_CMD
    if configured_cmd and os.path.exists(configured_cmd):
        return configured_cmd
    
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe")
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p

    which_path = shutil.which("tesseract")
    if which_path:
        return which_path

    return None


def preprocess_image_for_ocr(img: Image.Image) -> Image.Image:
    """Preprocesses receipt image: grayscale, resize, and contrast enhancement."""
    try:
        gray = img.convert('L')
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.8)
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        return sharpened
    except Exception:
        return img


def validate_receipt_arithmetic(data: dict) -> dict:
    """
    Validates arithmetic consistency between litres, rate, and total_cost.
    Flags discrepancies without inventing or altering extracted numbers.
    """
    litres = data.get('fuel_litres')
    rate = data.get('rate_per_litre')
    total = data.get('total_cost')

    if litres is not None and rate is not None and total is not None:
        try:
            expected_total = round(float(litres) * float(rate), 2)
            actual_total = round(float(total), 2)
            diff = abs(expected_total - actual_total)
            if diff > 3.0: # Allow small rounding tolerance
                data['arithmetic_warning'] = True
                data['arithmetic_note'] = f"Expected ₹{expected_total:.2f} ({litres}L × ₹{rate}), but receipt displays ₹{actual_total:.2f} (diff: ₹{diff:.2f})."
            else:
                data['arithmetic_warning'] = False
        except (ValueError, TypeError):
            pass
    return data


def parse_fuel_receipt_text(raw_text: str) -> dict:
    """
    Enhanced regex parser for Indian petrol/CNG bunk receipts.
    Extracts fuel litres, total cost, rate, station name, address, receipt no, date,
    payment method, vehicle reg, and fuel type.
    """
    data = {}
    tokens_matched = 0
    total_tokens_tested = 6

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # 1. Fuel Station Name heuristic
    for idx, line in enumerate(lines[:5]):
        upper_line = line.upper()
        if any(term in upper_line for term in ['FUELS', 'PETROLEUM', 'IOCL', 'HPCL', 'BPCL', 'INDIANOIL', 'BHARAT', 'SHELL', 'STATION', 'FILLING', 'ENTERPRISES', 'SERVICES']):
            data['fuel_station_name'] = line
            tokens_matched += 1
            # Check next line for address/city
            if idx + 1 < len(lines):
                next_line = lines[idx + 1]
                if not re.search(r'\d{2}[/-]\d{2}', next_line) and len(next_line) > 3:
                    data['station_address'] = next_line
            break

    # 2. Receipt / Invoice / Txn number
    receipt_patterns = [
        r'(?:INVOICE|INV|BILL|RECEIPT|TXN|ROC|R\s*NO)\s*(?:NO|NUM|#)?\s*[:=\-]?\s*([A-Za-z0-9\-_/]{4,20})',
        r'(?:SL\s*NO)\s*[:=\-]?\s*([0-9]{3,10})'
    ]
    for pattern in receipt_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            cand = match.group(1).strip()
            if not any(k in cand.upper() for k in ['DATE', 'TIME', 'TOTAL', 'RATE']):
                data['receipt_number'] = cand
                break

    # 3. Fuel Type detection (Institutional college bus fleet operates strictly on DIESEL)
    fuel_type_patterns = [
        (r'\b(?:DIESEL|HSD|SPEED\s*DIESEL)\b', 'DIESEL')
    ]
    for pattern, ftype in fuel_type_patterns:
        if re.search(pattern, raw_text, re.IGNORECASE):
            data['fuel_type'] = ftype
            break
    if 'fuel_type' not in data:
        data['fuel_type'] = 'DIESEL'

    # 4. Fuel Litres / Volume
    litres_patterns = [
        r'(?:VOLUME|VOL|QTY|QUANTITY|LITRES|LITRE|LTRS|LTR)\s*[:=\-]?\s*([0-9]+(?:\.[0-9]{1,3})?)',
        r'([0-9]+(?:\.[0-9]{2,3}))\s*(?:L|LTR|LITRES)\b'
    ]
    for pattern in litres_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                litres = float(match.group(1))
                if 1.0 <= litres <= 600.0:
                    data['fuel_litres'] = litres
                    tokens_matched += 1
                    break
            except ValueError:
                pass

    # 5. Rate / Price per Litre
    rate_patterns = [
        r'(?:RATE|PRICE|PRC)\s*(?:/|PER)?\s*(?:LTR|LITRE|KG)?\s*[:=\-]?\s*(?:RS|INR|₹)?\s*([0-9]+(?:\.[0-9]{1,2})?)',
        r'(?:RS|INR|₹)\s*([0-9]{2,3}\.[0-9]{2})\s*/\s*(?:L|LTR|KG)'
    ]
    for pattern in rate_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                rate = float(match.group(1))
                if 50.0 <= rate <= 250.0:
                    data['rate_per_litre'] = rate
                    tokens_matched += 1
                    break
            except ValueError:
                pass

    # 6. Total Amount / Cost
    amount_patterns = [
        r'(?:TOTAL|TOT|NET\s*AMT|AMOUNT|NET\s*AMOUNT|SALE)\s*[:=\-]?\s*(?:RS|INR|₹)?\s*([0-9]+(?:\.[0-9]{1,2})?)',
        r'(?:RS|INR|₹)\.?\s*([0-9]+(?:\.[0-9]{2}))'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                amt = float(match.group(1))
                if amt > 100.0:
                    data['total_cost'] = amt
                    tokens_matched += 1
                    break
            except ValueError:
                pass

    # Computed total if rate and litres found
    if 'fuel_litres' in data and 'rate_per_litre' in data and 'total_cost' not in data:
        data['total_cost'] = round(data['fuel_litres'] * data['rate_per_litre'], 2)
        tokens_matched += 1

    # 7. Date
    date_patterns = [
        r'(\d{2}[/\-]\d{2}[/\-]\d{4})',
        r'(\d{4}[/\-]\d{2}[/\-]\d{2})'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, raw_text)
        if match:
            data['bill_date_str'] = match.group(1)
            tokens_matched += 1
            break

    # 8. Payment Method
    if re.search(r'\b(?:UPI|GPAY|PHONEPE|PAYTM|BHIM)\b', raw_text, re.IGNORECASE):
        data['payment_method'] = 'UPI'
    elif re.search(r'\b(?:CARD|DEBIT|CREDIT|VISA|MASTER|RUPAY|POS)\b', raw_text, re.IGNORECASE):
        data['payment_method'] = 'CARD'
    elif re.search(r'\b(?:CASH)\b', raw_text, re.IGNORECASE):
        data['payment_method'] = 'CASH'

    # 9. Vehicle Registration (e.g. KA-01-AB-1234 or DL 01 A 1234)
    veh_match = re.search(r'\b([A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4})\b', raw_text)
    if veh_match:
        data['vehicle_registration'] = veh_match.group(1).upper()

    # Arithmetic verification
    data = validate_receipt_arithmetic(data)

    confidence_score = round((tokens_matched / total_tokens_tested) * 100.0, 2)
    return {
        'parsed_fields': data,
        'confidence_score': min(100.0, confidence_score),
        'raw_text_length': len(raw_text)
    }


def scan_receipt_with_gemini(file_path: str, api_key: str) -> dict:
    """
    Extracts fuel receipt data using Google Gemini Vision API.
    Strictly forbids inventing or hallucinating fields.
    """
    if not GEMINI_AVAILABLE:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        with Image.open(file_path) as img:
            prompt = """Analyze this fuel receipt image carefully and extract only the clearly visible details.
CRITICAL INSTRUCTIONS:
- Do NOT guess, assume, or hallucinate missing information.
- If a field is not present or is illegible, return null for that field.
- Extract numbers exactly as printed on the receipt.

Return a JSON object with strictly these keys:
{
  "fuel_station_name": string or null,
  "station_address": string or null,
  "receipt_number": string or null,
  "bill_date_str": string (DD/MM/YYYY or YYYY-MM-DD) or null,
  "bill_time_str": string or null,
  "fuel_type": "DIESEL" or "PETROL" or "CNG" or null,
  "fuel_litres": float or null,
  "rate_per_litre": float or null,
  "subtotal_amount": float or null,
  "tax_amount": float or null,
  "total_cost": float or null,
  "vehicle_registration": string or null,
  "payment_method": "CASH" or "CARD" or "UPI" or null
}
Return ONLY raw JSON, with no markdown formatting or commentary."""

            response = model.generate_content([prompt, img])
            text_resp = response.text.strip()
            # Clean markdown code blocks if present
            if text_resp.startswith("```"):
                text_resp = re.sub(r"^```(?:json)?\n?", "", text_resp)
                text_resp = re.sub(r"\n?```$", "", text_resp)
            
            parsed = json.loads(text_resp)
            # Remove null entries
            clean_data = {k: v for k, v in parsed.items() if v is not None}
            clean_data = validate_receipt_arithmetic(clean_data)

            # Score confidence based on core field presence
            core_fields = ['fuel_station_name', 'fuel_litres', 'rate_per_litre', 'total_cost', 'bill_date_str']
            found_core = sum(1 for f in core_fields if f in clean_data)
            confidence = round((found_core / len(core_fields)) * 100.0, 2)

            return {
                'extracted_data': clean_data,
                'confidence_score': confidence,
                'ocr_status': 'PARSED_HIGH_CONFIDENCE' if confidence >= 60 else 'PARSED_LOW_CONFIDENCE',
                'message': f'AI Vision extracted {len(clean_data)} fields with {confidence}% confidence.'
            }
    except Exception as e:
        print(f"[WARN] Gemini Vision extraction error: {e}")
        return None


def scan_receipt_image(file_path: str) -> dict:
    """
    Processes bill receipt image.
    Uses Gemini Vision if GEMINI_API_KEY is configured; otherwise uses Tesseract OCR.
    Gracefully falls back to manual entry mode without failing.
    """
    if not os.path.exists(file_path):
        return {
            'extracted_data': {},
            'confidence_score': 0.0,
            'ocr_status': 'MANUAL_FALLBACK',
            'message': 'Receipt file does not exist on disk.'
        }

    ext = file_path.rsplit('.', 1)[-1].lower()
    if ext not in ('png', 'jpg', 'jpeg', 'webp', 'bmp'):
        return {
            'extracted_data': {},
            'confidence_score': 0.0,
            'ocr_status': 'MANUAL_FALLBACK',
            'message': f'Document format .{ext} submitted. Human verification required.'
        }

    # 1. Attempt Gemini Vision if API key is present
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key.strip():
        gemini_result = scan_receipt_with_gemini(file_path, gemini_key.strip())
        if gemini_result:
            return gemini_result

    # 2. Tesseract OCR Fallback
    tesseract_bin = find_tesseract_binary()
    if not PYTESSERACT_AVAILABLE or not tesseract_bin:
        return {
            'extracted_data': {},
            'confidence_score': 0.0,
            'ocr_status': 'MANUAL_FALLBACK',
            'message': 'OCR engine (Tesseract) not found on system. Please enter details manually.'
        }

    try:
        pytesseract.pytesseract.tesseract_cmd = tesseract_bin
        with Image.open(file_path) as img:
            processed_img = preprocess_image_for_ocr(img)
            extracted_text = pytesseract.image_to_string(processed_img, timeout=10)

        parse_result = parse_fuel_receipt_text(extracted_text)
        confidence = parse_result['confidence_score']
        
        status = 'PARSED_HIGH_CONFIDENCE' if confidence >= 60.0 else 'PARSED_LOW_CONFIDENCE'
        if confidence == 0:
            status = 'MANUAL_FALLBACK'

        return {
            'extracted_data': parse_result['parsed_fields'],
            'confidence_score': confidence,
            'ocr_status': status,
            'message': f'OCR processed successfully with {confidence}% confidence score.'
        }
    except Exception as e:
        return {
            'extracted_data': {},
            'confidence_score': 0.0,
            'ocr_status': 'MANUAL_FALLBACK',
            'message': f'OCR scanning encountered an issue: {str(e)[:100]}. Please review manually.'
        }
