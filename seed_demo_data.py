"""
Seed script for MediPredict AI.
Populates admin, verified doctors, demo patients, health measurements,
sample laboratory reports with parameters, disease predictions, appointments, and reviews.
"""

import os
import sys
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medipredict.settings')
import django
django.setup()

from core.models import CustomUser, PatientProfile, DoctorProfile
from predictions.models import PredictionRecord
from reports.models import MedicalReport, LabParameter
from tracker.models import HealthMeasurement
from appointments.models import Appointment, DoctorReview
from predictions.ml_engine import predict_disease_risk

def run_seed():
    print("Seeding MediPredict AI database...")

    # 1. Admin Account
    admin, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@medipredict.ai',
            'first_name': 'MediPredict',
            'last_name': 'Administrator',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("[OK] Admin created: username='admin', password='admin123'")

    # 2. Demo Patient
    patient, created = CustomUser.objects.get_or_create(
        username='patient_john',
        defaults={
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'PATIENT',
            'phone': '+91 98765 43210',
            'gender': 'Male',
            'date_of_birth': date(1985, 6, 15),
        }
    )
    if created:
        patient.set_password('patient123')
        patient.save()
        print("[OK] Patient created: username='patient_john', password='patient123'")

    # Update patient profile
    pp, _ = PatientProfile.objects.get_or_create(user=patient)
    pp.blood_group = 'B+'
    pp.city = 'New Delhi'
    pp.address = 'A-42, Defence Colony, New Delhi'
    pp.emergency_contact_name = 'Emily Doe'
    pp.emergency_contact_phone = '+91 98765 00000'
    pp.allergies = 'Penicillin, Shellfish'
    pp.chronic_conditions = 'Mild Borderline Hypertension'
    pp.save()

    # 3. Verified Doctors
    doctors_info = [
        {
            'username': 'dr_rajesh',
            'first_name': 'Rajesh',
            'last_name': 'Sharma',
            'email': 'rajesh.sharma@maxhealthcare.in',
            'qualification': 'MBBS, MD, DM (Cardiology)',
            'specialization': 'Cardiologist',
            'license_number': 'MCI-DEL-28491',
            'clinic_name': 'Max Heart & Vascular Institute',
            'clinic_address': 'Press Enclave Marg, Saket',
            'city': 'New Delhi',
            'latitude': 28.5286,
            'longitude': 77.2185,
            'fee': 900.00,
            'exp': 16,
            'bio': 'Senior Consultant Cardiologist specializing in preventive cardiology, coronary angioplasty, and lipid disorders.'
        },
        {
            'username': 'dr_priya',
            'first_name': 'Priya',
            'last_name': 'Verma',
            'email': 'priya.verma@metrohealth.org',
            'qualification': 'MBBS, MD (Medicine), Post-Doc Endocrinology',
            'specialization': 'Diabetologist / Endocrinologist',
            'license_number': 'MCI-DEL-34982',
            'clinic_name': 'Metro Diabetes & Endocrine Care',
            'clinic_address': 'Barakhamba Road, Connaught Place',
            'city': 'New Delhi',
            'latitude': 28.6315,
            'longitude': 77.2245,
            'fee': 750.00,
            'exp': 12,
            'bio': 'Endocrinologist focused on intensive Type 1 and Type 2 diabetes management, gestational diabetes, and metabolic syndrome.'
        },
        {
            'username': 'dr_amit',
            'first_name': 'Amit',
            'last_name': 'Mehra',
            'email': 'amit.mehra@apexkidney.org',
            'qualification': 'MBBS, MD, DNB (Nephrology)',
            'specialization': 'Nephrologist',
            'license_number': 'MCI-DEL-41095',
            'clinic_name': 'Apex Kidney Care & Dialysis Centre',
            'clinic_address': 'Ring Road, Lajpat Nagar IV',
            'city': 'New Delhi',
            'latitude': 28.5672,
            'longitude': 77.2433,
            'fee': 850.00,
            'exp': 14,
            'bio': 'Consultant Nephrologist specializing in chronic kidney disease surveillance, diabetic nephropathy, and renal hypertension.'
        },
        {
            'username': 'dr_sunita',
            'first_name': 'Sunita',
            'last_name': 'Rao',
            'email': 'sunita.rao@apolloclinic.com',
            'qualification': 'MBBS, MD (General Medicine)',
            'specialization': 'General Physician',
            'license_number': 'MCI-DEL-19842',
            'clinic_name': 'Apollo Comprehensive Health Clinic',
            'clinic_address': 'Greater Kailash II, Enclave 1',
            'city': 'New Delhi',
            'latitude': 28.5355,
            'longitude': 77.2410,
            'fee': 600.00,
            'exp': 10,
            'bio': 'Comprehensive family physician managing seasonal infections, preventive health screenings, and annual routine check-ups.'
        }
    ]

    doc_objects = []
    for info in doctors_info:
        u, u_created = CustomUser.objects.get_or_create(
            username=info['username'],
            defaults={
                'email': info['email'],
                'first_name': info['first_name'],
                'last_name': info['last_name'],
                'role': 'DOCTOR',
                'phone': '+91 98111 22334',
                'gender': 'Female' if info['username'] in ['dr_priya', 'dr_sunita'] else 'Male',
            }
        )
        if u_created:
            u.set_password('doctor123')
            u.save()

        dp, _ = DoctorProfile.objects.update_or_create(
            user=u,
            defaults={
                'qualification': info['qualification'],
                'specialization': info['specialization'],
                'license_number': info['license_number'],
                'clinic_name': info['clinic_name'],
                'clinic_address': info['clinic_address'],
                'city': info['city'],
                'latitude': info['latitude'],
                'longitude': info['longitude'],
                'consultation_fee': info['fee'],
                'experience_years': info['exp'],
                'bio': info['bio'],
                'is_verified': True,
                'available_days': 'Mon, Tue, Wed, Thu, Fri, Sat',
            }
        )
        doc_objects.append(dp)
        print(f"[OK] Doctor initialized: Dr. {info['first_name']} {info['last_name']} ({info['specialization']})")

    # 4. Seed Health Tracker Measurements for patient_john
    today = date.today()
    vitals_data = [
        (today - timedelta(days=28), 75.0, 175.0, 126, 84, 114.0, 76, 'Baseline checkup'),
        (today - timedelta(days=21), 74.5, 175.0, 124, 82, 108.0, 74, 'Morning fasting'),
        (today - timedelta(days=14), 74.0, 175.0, 122, 80, 102.0, 72, 'Post diet adjustment'),
        (today - timedelta(days=7),  73.2, 175.0, 120, 80, 99.0,  70, 'Light jogging week'),
        (today - timedelta(days=1),  72.8, 175.0, 118, 78, 96.0,  71, 'Current readings'),
    ]
    for d, w, h, s_bp, d_bp, glu, hr, notes in vitals_data:
        HealthMeasurement.objects.get_or_create(
            user=patient,
            recorded_at=d,
            defaults={
                'weight_kg': w,
                'height_cm': h,
                'systolic_bp': s_bp,
                'diastolic_bp': d_bp,
                'blood_glucose': glu,
                'heart_rate': hr,
                'notes': notes,
            }
        )
    print(f"[OK] Seeded 5 longitudinal vital measurements for {patient.username}.")

    # 5. Seed Real AI Disease Predictions
    diab_inputs = {'glucose': 118.0, 'bmi': 25.8, 'age': 40, 'blood_pressure': 80.0, 'insulin': 90.0, 'pregnancies': 0, 'pedigree': 0.42, 'skin_thickness': 22.0}
    diab_res = predict_disease_risk('diabetes', diab_inputs)
    PredictionRecord.objects.create(
        user=patient,
        disease_type='diabetes',
        input_features=diab_inputs,
        risk_score=diab_res['risk_score'],
        risk_level=diab_res['risk_level'],
        risk_label=diab_res['risk_label'],
        feature_contributions=diab_res['all_contributors'],
        model_version=diab_res['model_version']
    )

    heart_inputs = {'age': 40, 'sex': 1, 'cp': 1, 'trestbps': 122.0, 'chol': 210.0, 'thalach': 152.0, 'exang': 0, 'oldpeak': 0.6, 'slope': 0, 'fbs': 0}
    heart_res = predict_disease_risk('heart', heart_inputs)
    PredictionRecord.objects.create(
        user=patient,
        disease_type='heart',
        input_features=heart_inputs,
        risk_score=heart_res['risk_score'],
        risk_level=heart_res['risk_level'],
        risk_label=heart_res['risk_label'],
        feature_contributions=heart_res['all_contributors'],
        model_version=heart_res['model_version']
    )

    kidney_inputs = {'sc': 0.95, 'bu': 28.0, 'al': 0, 'hemo': 14.2, 'bp': 78.0, 'sg': 1.020, 'age': 40, 'sod': 140.0, 'pot': 4.3}
    kidney_res = predict_disease_risk('kidney', kidney_inputs)
    PredictionRecord.objects.create(
        user=patient,
        disease_type='kidney',
        input_features=kidney_inputs,
        risk_score=kidney_res['risk_score'],
        risk_level=kidney_res['risk_level'],
        risk_label=kidney_res['risk_label'],
        feature_contributions=kidney_res['all_contributors'],
        model_version=kidney_res['model_version']
    )
    print(f"[OK] Seeded 3 clinical AI disease prediction assessments.")

    # 6. Seed Sample Medical Laboratory Reports with Parameters
    r1, _ = MedicalReport.objects.get_or_create(
        user=patient,
        title='Annual Comprehensive Metabolic & Lipid Panel',
        report_category='cmp',
        report_date=today - timedelta(days=20),
        status='confirmed',
        defaults={'clinical_summary': {'total_tests': 5, 'abnormal_tests': 1}}
    )
    r1_tests = [
        ('Fasting Blood Glucose', 114.0, 'mg/dL', 70.0, 99.0, 'high',
         'Fasting glucose is slightly elevated above standard normal limits (prediabetes threshold).',
         'फास्टिंग ब्लड शुगर का स्तर सामान्य से थोड़ा अधिक है। मीठे से परहेज़ रखें।'),
        ('Total Serum Cholesterol', 195.0, 'mg/dL', 125.0, 200.0, 'normal',
         'Total cholesterol is within the desirable range.',
         'कुल कोलेस्ट्रॉल सामान्य सीमा के भीतर है।'),
        ('Serum Creatinine', 0.9, 'mg/dL', 0.7, 1.3, 'normal',
         'Normal renal filtration efficiency.',
         'किडनी की कार्यक्षमता पूरी तरह सामान्य है।'),
        ('Blood Urea Nitrogen', 26.0, 'mg/dL', 15.0, 45.0, 'normal',
         'Efficient protein metabolism clearance.',
         'ब्लड यूरिया का स्तर सामान्य है।'),
        ('Hemoglobin (Hb)', 14.5, 'g/dL', 12.0, 17.5, 'normal',
         'Optimal oxygen carrying capacity.',
         'हीमोग्लोबिन स्तर सामान्य है।'),
    ]
    for t_name, val, u, rmin, rmax, st, en, hi in r1_tests:
        LabParameter.objects.get_or_create(
            report=r1,
            test_name=t_name,
            defaults={'measured_value': val, 'unit': u, 'reference_min': rmin, 'reference_max': rmax, 'status': st, 'explanation_en': en, 'explanation_hi': hi}
        )

    r2, _ = MedicalReport.objects.get_or_create(
        user=patient,
        title='Follow-up Glycemic & Renal Evaluation',
        report_category='diabetes',
        report_date=today - timedelta(days=2),
        status='confirmed',
        defaults={'clinical_summary': {'total_tests': 5, 'abnormal_tests': 0}}
    )
    r2_tests = [
        ('Fasting Blood Glucose', 98.0, 'mg/dL', 70.0, 99.0, 'normal',
         'Normal fasting glucose level following lifestyle adjustments.',
         'जीवनशैली में सुधार के बाद फास्टिंग ब्लड शुगर सामान्य सीमा में आ गया है।'),
        ('Total Serum Cholesterol', 188.0, 'mg/dL', 125.0, 200.0, 'normal',
         'Desirable total cholesterol level.',
         'कोलेस्ट्रॉल का स्तर सामान्य और सुरक्षित है।'),
        ('Serum Creatinine', 0.88, 'mg/dL', 0.7, 1.3, 'normal',
         'Healthy renal filtration.',
         'किडनी फिल्टरेशन सामान्य है।'),
        ('Blood Urea Nitrogen', 22.0, 'mg/dL', 15.0, 45.0, 'normal',
         'Normal nitrogenous waste clearance.',
         'ब्लड यूरिया सामान्य है।'),
        ('Hemoglobin (Hb)', 14.8, 'g/dL', 12.0, 17.5, 'normal',
         'Normal oxygen-carrying capacity.',
         'हीमोग्लोबिन सामान्य है।'),
    ]
    for t_name, val, u, rmin, rmax, st, en, hi in r2_tests:
        LabParameter.objects.get_or_create(
            report=r2,
            test_name=t_name,
            defaults={'measured_value': val, 'unit': u, 'reference_min': rmin, 'reference_max': rmax, 'status': st, 'explanation_en': en, 'explanation_hi': hi}
        )
    print(f"[OK] Seeded 2 comparative medical reports with 10 lab parameters.")

    # 7. Seed Appointments & Reviews
    cardio_doc = doc_objects[0]
    diab_doc = doc_objects[1]

    # Completed appointment with Dr. Rajesh Sharma
    appt1, _ = Appointment.objects.get_or_create(
        patient=patient,
        doctor=cardio_doc,
        appointment_date=today - timedelta(days=10),
        time_slot='10:30 AM',
        defaults={
            'symptoms_reason': 'Routine cardiac preventive checkup and blood pressure monitoring.',
            'status': 'completed',
            'doctor_notes': 'Cardiovascular exam unremarkable. Heart sounds S1 S2 normal. Continue daily 30-min walking and low-sodium diet.'
        }
    )

    DoctorReview.objects.get_or_create(
        patient=patient,
        doctor=cardio_doc,
        defaults={
            'rating': 5,
            'comment': 'Dr. Rajesh Sharma was thorough, patient, and clearly explained my blood pressure trend without rushing.',
            'doctor_reply': 'Thank you John! Pleased to see your BP stabilizing with regular physical activity.'
        }
    )

    Appointment.objects.get_or_create(
        patient=patient,
        doctor=diab_doc,
        appointment_date=today + timedelta(days=4),
        time_slot='11:00 AM',
        defaults={
            'symptoms_reason': 'Follow-up consultation to review fasting blood sugar improvements and dietary guidance.',
            'status': 'confirmed',
            'doctor_notes': 'Please bring your latest fasting blood sugar log and lipid panel summary.'
        }
    )
    print("[OK] Seeded appointments and verified doctor reviews.")

    print("\nDatabase seeding completed successfully!")

if __name__ == '__main__':
    run_seed()
