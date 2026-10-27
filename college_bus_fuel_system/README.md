# College Bus Fuel Management System

A robust, enterprise-grade College Bus Fuel Management and Audit platform tailored for higher-education campus fleets.

---

## Architecture Overview

1. **Flask REST API (`backend/`)**:
   - Python 3.12 + SQLAlchemy + Flask-JWT-Extended + bcrypt.
   - Dual Database Support: Connects to **MySQL 8.0**; automatically falls back to local SQLite if MySQL credentials are not configured, preserving existing data without loss.
   - **AI/OCR Scanning Engine**: Preprocesses receipt photos, runs Tesseract OCR or regex parsing with confidence scoring, and falls back gracefully to manual review when images are unreadable.
   - **Perceptual Duplicate Detection**: Calculates Hamming distance across 64-bit difference hashes (`dhash`) and screens 48-hour metadata windows, raising advisory warning flags rather than accusatory rejections.
   - **Privacy-Conscious Geofence Verification**: Computes Haversine distances against authorized fuel stations strictly upon submission.
   - **Sequential Mileage Computation**: Calculates $km/L = \Delta \text{Odometer} / \text{Litres}$ and flags statistical reliability only when consecutive forward readings exist.
   - **Secure Private Bill Vault**: Files stored outside web root with cryptographic UUID naming; authorized streaming validates JWT identity and ownership.
   - **Immutable Compliance Audit Trail**: Records every administrative decision and status transition.
   - **Automated Report Exports**: Generates CSV and formatted institutional PDF audit summaries via ReportLab.

2. **React Admin & Vice-Chancellor Dashboard (`frontend/`)**:
   - React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts.
   - Role-Based Access Control (Fleet Administrator vs. Vice-Chancellor).
   - Configurable VC Policy: VC can either act as an Executive Read-Only Auditor or be granted co-approval rights.
   - Unified Review Desk: Side-by-side receipt zoom, OCR comparison, duplicate warning banner, GPS distance feedback, and approval/rejection/correction controls.
   - Fleet Management & Approved Bunk Location Manager.

3. **Flutter Driver Mobile Application (`driver_app/`)**:
   - Flutter 3.47 / Dart 3.13 cross-platform mobile app.
   - Driver authentication and assigned bus telemetry.
   - Receipt camera/gallery upload with instant OCR extraction preview.
   - One-tap permission-aware GPS capture.
   - Correction resubmission workflow for flagged records.

---

## Windows Quick-Start Run Instructions

### 1. Configure Database & Environment
Copy `.env.example` to `.env` in the project root:
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=college_bus_fuel_db

# Vice Chancellor Approval Policy (true: VC can approve; false: VC is read-only auditor)
VC_CAN_APPROVE=false

# OCR Configuration
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

*(If MySQL password is blank or connection cannot be established, the application automatically uses local SQLite `college_bus_fuel.db` without data loss).*

### 2. Initial Administrator Setup
Create your primary administrator account safely:
```powershell
cd backend
.\venv\Scripts\activate.bat
python init_admin.py --username admin --email admin@college.edu --name "Prof. K. Sharma"
```
*(Or navigate to http://localhost:3000/initial-setup in your browser on first launch).*

### 3. Launching Services
Run the three dedicated Windows batch scripts from the project root:

- **Backend API (Port 5000):**
  ```powershell
  .\start_backend.bat
  ```
- **React Dashboard (Port 3000):**
  ```powershell
  .\start_frontend.bat
  ```
- **Driver Mobile App:**
  ```powershell
  .\start_driver_app.bat
  ```

---

## OCR Engine Setup & Fallback Handling

### Recommended Setup (Windows):
1. Download the Tesseract installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to the default location: `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. The backend automatically detects this path or uses the `TESSERACT_CMD` environment variable.

### Graceful Fallback Handling:
If Tesseract is not installed or the uploaded receipt image is blurry:
- The system returns `ocr_status: "MANUAL_FALLBACK"` and `confidence_score: 0.0`.
- The driver app and dashboard display a clear notification allowing driver and admin to review and enter values manually without crashing or blocking submissions.

---

## Automated Test Execution

Run the backend test suite:
```powershell
cd backend
.\venv\Scripts\pytest.exe -v tests
```

Run Flutter driver app tests:
```powershell
cd driver_app
flutter test
```
