# College Bus Fuel Management System — Demonstration Credentials & Guide

> **DISCLAIMER:**  
> This file contains sample credentials and data generated **strictly for college laboratory demonstration and academic presentation purposes**. All sample locations, transactions, fuel slips, and odometer numbers are clearly marked as **DEMO / TEST ONLY**.

---

## 1. System Role Accounts

| Role | Username | Full Name | Official Email | Demo Password | Purpose / Access |
|---|---|---|---|---|---|
| **Fleet Administrator** | `admin` | System Administrator | `admin@college.edu` | *(Your original admin password)* | Full management, fleet register, user accounts, approvals, bunk settings |
| **Vice-Chancellor Auditor** | `vc_office` | Prof. K. R. Sharma | `vc@college.edu` | `DemoAuditor#2026` | Institutional oversight, audit trail, read-only analytics |

---

## 2. Five Demo Driver Accounts & Vehicle Allocations

| Driver ID | Username | Driver Name | Contact | Assigned Bus | Reg. Number | Model | Fuel Type | Tank | Initial Odometer | Demo Password |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | `driver1` | Driver One *(Existing)* | — | `bus20` | `KA-01-AK2528` | Tata Starbus | DIESEL | 150 L | 120,415 km | *(Original password)* |
| **2** | `driver2` | Rajesh Kumar | +91 98450 11002 | `bus04` | `KA-01-BK1044` | Ashok Leyland Viking | DIESEL | 160 L | 84,740 km | `DemoDriver#2026` |
| **3** | `driver3` | Suresh Nair | +91 98450 11003 | `bus09` | `KA-01-CK2009` | Eicher Skyline Pro | CNG | 140 kg | 62,705 km | `DemoDriver#2026` |
| **4** | `driver4` | Anand Sharma | +91 98450 11004 | `bus14` | `KA-01-DK3014` | BharatBenz 1017 | DIESEL | 180 L | 47,780 km | `DemoDriver#2026` |
| **5** | `driver5` | Vikram Patil | +91 98450 11005 | `bus27` | `KA-01-EK4027` | Force Traveller | DIESEL | 90 L | 31,380 km | `DemoDriver#2026` |

---

## 3. Sample Demo Fuel Transactions Summary

All records have been computed with strict mathematical precision: `total_cost = round(fuel_litres * rate_per_litre, 2)`.

| Ref Code | Bus # | Driver | Fuel Qty | Rate | Total (₹) | Odometer | Station / Location | Status | Key Feature Demonstrated |
|---|---|---|---|---|---|---|---|---|---|
| `DEMO-FL-D103` | `bus20` | `driver1` | 45.00 L | ₹89.50 | ₹4,027.50 | 120,225 km | `[DEMO] IOCL Campus Auto Care` | **APPROVED** | Verified GPS geofence, 5.00 km/L sequence mileage |
| `DEMO-FL-D104` | `bus20` | `driver1` | 38.00 L | ₹90.00 | ₹3,420.00 | 120,415 km | `[DEMO] IOCL Campus Auto Care` | **PENDING** | **Ready for live approval during demonstration** |
| `DEMO-FL-D201` | `bus04` | `driver2` | 50.00 L | ₹89.00 | ₹4,450.00 | 84,250 km | `[DEMO] BPCL Highway Station` | **APPROVED** | Baseline fill-up log, verified geofence (BPCL) |
| `DEMO-FL-D202` | `bus04` | `driver2` | 48.50 L | ₹89.20 | ₹4,326.20 | 84,485 km | `[DEMO] BPCL Highway Station` | **APPROVED** | Consecutive fill-up, 4.85 km/L verified efficiency |
| `DEMO-FL-D203` | `bus04` | `driver2` | 52.00 L | ₹89.50 | ₹4,654.00 | 84,740 km | `[DEMO] BPCL Highway Station` | **PENDING** | **Ready for live approval during demonstration** |
| `DEMO-FL-D301` | `bus09` | `driver3` | 30.00 kg | ₹82.00 | ₹2,460.00 | 62,280 km | `[DEMO] BPCL Highway Station` | **APPROVED** | CNG Fuel type handling (kg instead of Litres) |
| `DEMO-FL-D302` | `bus09` | `driver3` | 32.50 kg | ₹82.00 | ₹2,665.00 | 62,495 km | `[DEMO] BPCL Highway Station` | **APPROVED** | 6.62 km/kg eco-mileage computation |
| `DEMO-FL-D303` | `bus09` | `driver3` | 31.00 kg | ₹82.50 | ₹2,557.50 | 62,705 km | **CORRECTION_REQUIRED** | **Correction Loop:** Admin requested clear odometer photo |
| `DEMO-FL-D401` | `bus14` | `driver4` | 60.00 L | ₹89.00 | ₹5,340.00 | 47,520 km | `[DEMO] HPCL Tech Park Point` | **APPROVED** | Heavy bus baseline fill-up |
| `DEMO-FL-D402` | `bus14` | `driver4` | 55.00 L | ₹89.20 | ₹4,906.00 | 47,780 km | `[DEMO] HPCL Tech Park Point` | **APPROVED** | 4.73 km/L calculated economy |
| `DEMO-FL-D403` | `bus14` | `driver4` | 55.00 L | ₹89.20 | ₹4,906.00 | 47,780 km | **PENDING** (Flagged) | **AI / Duplicate Screening Warning:** Flagged identical cost & hash |
| `DEMO-FL-D501` | `bus27` | `driver5` | 28.00 L | ₹89.50 | ₹2,506.00 | 31,050 km | `[DEMO] IOCL Campus Auto Care` | **APPROVED** | Mini-bus baseline log |
| `DEMO-FL-D502` | `bus27` | `driver5` | 30.00 L | ₹89.50 | ₹2,685.00 | 31,230 km | `[DEMO] IOCL Campus Auto Care` | **APPROVED** | 6.00 km/L efficient route calculation |
| `DEMO-FL-D503` | `bus27` | `driver5` | 35.00 L | ₹92.00 | ₹3,220.00 | 31,380 km | `[DEMO] Unauthorized Outlet` | **REJECTED** | **Fraud/Off-Route Prevention:** 8.5 km outside authorized geofence |

---

## 4. Configured Approved Petrol Bunks (Demo Only)

* `[DEMO] IOCL Campus Auto Care (Demo Only)`: Lat `12.971600`, Lon `77.594600` (Radius: 500 m)
* `[DEMO] BPCL Highway Station (Demo Only)`: Lat `12.935200`, Lon `77.624500` (Radius: 600 m)
* `[DEMO] HPCL Tech Park Point (Demo Only)`: Lat `13.035800`, Lon `77.597000` (Radius: 500 m)

---

## 5. Live Demonstration Walkthrough Guide for Professor

1. **Fleet Overview (`/`):**
   * Log in as `admin`.
   * Observe KPI cards: Real total expenditure (₹), consumed litres, pending queue counter, and fleet economy average.
   * Observe the **Monthly Fuel Expenditure Trend** area chart rendered with historical data.
2. **Reviewing Pending Submissions (`/requests`):**
   * Show that all 5 drivers (`driver1` through `driver5`) appear in the queue.
   * Click **Inspect** on `DEMO-FL-D104` or `DEMO-FL-D203`.
   * Click **Inspect Receipt Document** to display the high-resolution receipt modal.
   * Click **Approve & Update Odometer** in the Action Center to demonstrate live status transition.
3. **Duplicate Prevention Showcase (`DEMO-FL-D403`):**
   * Filter requests by **"Duplicate Warnings Only"**.
   * Open `DEMO-FL-D403`. Show the yellow **Duplicate Warning** banner highlighting identical cost and perceptual hash match within 48h.
4. **Correction Workflow Showcase (`DEMO-FL-D303`):**
   * Open `DEMO-FL-D303` to show **Correction Needed** state and the administrative instructions sent to `driver3`.
5. **GPS Geofence & Rejection Showcase (`DEMO-FL-D503`):**
   * Open `DEMO-FL-D503`. Show the red **Off-site / Unverified** tag and distance telemetry (8.5 km away from authorized station) with rejection audit reason.
6. **Fleet & Personnel Management (`/fleet`, `/users`):**
   * Show all 5 college buses registered with their respective assigned drivers, fuel types (including CNG), and updated odometers.
   * Show user management with active driver roles and account statuses.
7. **Institutional Audit Trail (`/audit`):**
   * Demonstrate the immutable regulatory trail tracking all submissions, approvals, rejections, and user creations.
