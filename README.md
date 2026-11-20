# MediPredict AI — Healthcare Intelligence & Diagnostic Platform

**MediPredict AI** is a modern, professional, full-stack healthcare web application providing probabilistic disease risk prediction, automated laboratory report extraction and interpretation, longitudinal health tracking, a bilingual conversational health assistant, and an interactive doctor directory.

---

## Key Highlights & Capabilities

### 1. Multi-Disease AI Risk Screening
- **Type 2 Diabetes Risk Model**: Assesses fasting blood glucose, BMI, age, diastolic blood pressure, serum insulin, pregnancies, and diabetes pedigree score.
- **Cardiovascular Disease Risk Model**: Evaluates 10 cardiac biomarkers (resting blood pressure, cholesterol, exercise angina, ST depression, ECG slope, maximum heart rate).
- **Chronic Kidney Disease (CKD) Risk Model**: Analyzes serum creatinine, urinary albumin, blood urea nitrogen (BUN), hemoglobin, specific gravity, and blood pressure.
- **Biomarker Attribution**: SHAP-style breakdown displaying local additive feature contributions, showing which biomarkers elevated or lowered estimated risk.
- **Strict Clinical Guardrails**: Clear, prominent non-diagnostic medical disclaimers; no automated medicine prescription.

### 2. AI Medical Report Analyzer
- **Multi-Format Ingestion**: Supports PDF, JPG, JPEG, and PNG document uploads (up to 10MB).
- **Digital & OCR Extraction**: Native text extraction via **PyMuPDF (fitz)**, paired with **OpenCV & PyTesseract** image preprocessing.
- **35+ Clinical Tests Knowledge Base**: Pre-configured with reference intervals across Complete Blood Count (CBC), Lipid Profiles, Comprehensive Metabolic Panels (CMP), Renal Function Tests (KFT), Liver Function Tests (LFT), and Thyroid Panels.
- **Interactive Verification Table**: Human-in-the-loop review allowing users to adjust or add test values, units, and reference ranges before analysis.
- **Bilingual Insights**: Instant clinical classification (Within range, Below range, Above range, Context needed) with explanations in **simple English and Hindi (हिंदी)**.
- **ReportLab PDF Summaries**: One-click download of branded medical summary PDFs.

### 3. Report History & Longitudinal Comparison
- Chronological archive of all uploaded and verified laboratory panels.
- Side-by-side comparison between any two past reports.
- Computes numeric deltas and percentage changes, rendered via interactive Chart.js bar visualizations.

### 4. Personal Health Vitals Tracker
- Track Weight, Height, Blood Pressure (Systolic/Diastolic), Blood Glucose, and Heart Rate.
- **Automatic BMI Calculation**: Dynamically categorizes BMI into Underweight, Normal, Overweight, or Obese.
- Chart.js trends for weekly and monthly vitals tracking.

### 5. Bilingual AI Health Assistant
- Conversational chatbot for health education, terminology explanations, and lab findings review.
- Understands English and Hindi (उदा. *"HbA1c क्या है?"*, *"बीपी कंट्रोल करने के आसान उपाय"*).
- Direct report analysis query: *"Explain my latest report"* summarizes recent confirmed findings.

### 6. Doctor Directory & Smart Appointment Scheduling
- Search and filter verified practitioners by medical specialization, city, or name.
- **Interactive Clinic Map**: Powered by **Leaflet.js & OpenStreetMap** with GPS clinic pins and booking links.
- Appointment booking with preferred time slots.
- Doctor consultation portal to confirm/reschedule appointments and enter clinical prescription notes.
- 5-Star patient review and rating system with physician reply capability.

---

## Role-Based Access Architecture

| Role | Default Demo Credentials | Key Permissions & Views |
|---|---|---|
| **Administrator** | `admin` / `admin123` | Platform analytics, verify/revoke doctor profiles, model monitoring |
| **Verified Doctor** | `dr_rajesh` / `doctor123`<br>`dr_priya` / `doctor123` | Appointment schedule, patient notes, clinic settings, review replies |
| **Patient** | `patient_john` / `patient123` | 12-item dashboard, AI predictions, report analyzer, vitals tracker, booking |

---

## Technology Stack

- **Backend**: Python 3.11, Django 5.2, Django Authentication & ORM
- **Database**: Dual Engine — MySQL (via PyMySQL) with automatic graceful fallback to SQLite
- **Machine Learning & Math**: Scikit-learn, NumPy, Pandas, Joblib
- **Report Processing**: PyMuPDF, OpenCV, Pillow, PyTesseract
- **PDF Generation**: ReportLab
- **Mapping**: Leaflet.js & OpenStreetMap
- **Frontend**: Bootstrap 5, FontAwesome 6, Chart.js, Custom Healthcare Design System

---

## Running the Application

### Option A: Using the Launcher Script
Double-click `run_server.bat` in this folder, or run:
```cmd
run_server.bat
```

### Option B: From Command Line
```powershell
& "..\python311\python.exe" manage.py runserver 127.0.0.1:8000
```
Open your web browser at: **`http://127.0.0.1:8000/`**

---

## MySQL Configuration

To switch from the default fallback SQLite to a live MySQL server:
1. Ensure MySQL Server is running on port 3306.
2. Create the database:
   ```sql
   CREATE DATABASE medipredict_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Set environment variables (or edit `medipredict/settings.py`):
   ```cmd
   set USE_MYSQL=1
   set MYSQL_DB=medipredict_db
   set MYSQL_USER=root
   set MYSQL_PASSWORD=your_password
   set MYSQL_HOST=127.0.0.1
   set MYSQL_PORT=3306
   ```
4. Run migrations:
   ```powershell
   & "..\python311\python.exe" manage.py migrate
   & "..\python311\python.exe" seed_demo_data.py
   ```
