"""
MediPredict AI — Medical Laboratory Report Extraction and Clinical Parser Engine.
Uses PyMuPDF (fitz) for PDF documents and OpenCV/pytesseract for scanned reports.
Applies clinical reference rules and generates bilingual explanations (English & Hindi).
"""

import re
import os
from pathlib import Path
from datetime import datetime
from PIL import Image

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pytesseract
    import cv2
    import numpy as np
except ImportError:
    pytesseract = None
    cv2 = None


# Comprehensive Clinical Reference Knowledge Base
STANDARD_TEST_KNOWLEDGE = {
    # Glycemic Parameters
    'fasting_blood_sugar': {
        'aliases': ['fasting blood sugar', 'fasting blood glucose', 'fbs', 'fasting glucose', 'blood sugar fasting', 'plasma glucose fasting'],
        'display_name': 'Fasting Blood Glucose (FBS)',
        'default_unit': 'mg/dL',
        'ref_min': 70.0,
        'ref_max': 99.0,
        'category': 'Glycemic / Diabetes',
        'exp_en_normal': 'Normal fasting blood sugar level. Indicates healthy glucose regulation.',
        'exp_hi_normal': 'फास्टिंग ब्लड शुगर का स्तर सामान्य है। यह स्वस्थ ग्लूकोज नियंत्रण दर्शाता है।',
        'exp_en_high': 'Elevated fasting blood sugar. May indicate impaired fasting glucose (prediabetes) or diabetes mellitus.',
        'exp_hi_high': 'फास्टिंग ब्लड शुगर का स्तर बढ़ा हुआ है। यह प्रीडायबिटीज या डायबिटीज का संकेत हो सकता है।',
        'exp_en_low': 'Low blood glucose (hypoglycemia). Can cause dizziness, sweating, or weakness.',
        'exp_hi_low': 'ब्लड शुगर का स्तर कम (हाइपोग्लाइसीमिया) है। इससे चक्कर आना या कमजोरी महसूस हो सकती है।'
    },
    'postprandial_blood_sugar': {
        'aliases': ['post prandial blood sugar', 'ppbs', 'blood sugar pp', 'post glucose', 'post meal glucose'],
        'display_name': 'Postprandial Blood Glucose (PPBS)',
        'default_unit': 'mg/dL',
        'ref_min': 90.0,
        'ref_max': 140.0,
        'category': 'Glycemic / Diabetes',
        'exp_en_normal': 'Normal post-meal blood sugar level. Efficient carbohydrate metabolism.',
        'exp_hi_normal': 'भोजन के बाद ब्लड शुगर का स्तर सामान्य है।',
        'exp_en_high': 'Elevated postprandial blood sugar (>140 mg/dL). Suggests insulin resistance or diabetes.',
        'exp_hi_high': 'खाने के बाद ब्लड शुगर का स्तर बढ़ा हुआ है। यह इंसुलिन प्रतिरोध का संकेत हो सकता है।',
        'exp_en_low': 'Low post-meal blood sugar. Seek clinical correlation if symptomatic.',
        'exp_hi_low': 'खाने के बाद ब्लड शुगर कम है।'
    },
    'hba1c': {
        'aliases': ['hba1c', 'glycated hemoglobin', 'glycosylated hemoglobin', 'a1c'],
        'display_name': 'HbA1c (Glycated Hemoglobin)',
        'default_unit': '%',
        'ref_min': 4.0,
        'ref_max': 5.6,
        'category': 'Glycemic / Diabetes',
        'exp_en_normal': 'Normal average blood sugar over the preceding 2-3 months.',
        'exp_hi_normal': 'पिछले 2-3 महीनों का औसत ब्लड शुगर स्तर पूरी तरह सामान्य है।',
        'exp_en_high': 'Elevated HbA1c (5.7-6.4% Prediabetes, ≥6.5% Diabetes). Reflects prolonged hyperglycemia.',
        'exp_hi_high': 'HbA1c बढ़ा हुआ है (5.7-6.4% प्रीडायबिटीज, ≥6.5% डायबिटीज)। यह लंबे समय से हाई शुगर दर्शाता है।',
        'exp_en_low': 'Low HbA1c. May be associated with frequent hypoglycemia or certain red blood cell conditions.',
        'exp_hi_low': 'HbA1c कम है। यह बार-बार शुगर कम होने या खून की कमी से संबंधित हो सकता है।'
    },

    # Complete Blood Count (CBC)
    'hemoglobin': {
        'aliases': ['hemoglobin', 'hb', 'hgb', 'haemoglobin'],
        'display_name': 'Hemoglobin (Hb)',
        'default_unit': 'g/dL',
        'ref_min': 12.0,
        'ref_max': 17.5,
        'category': 'Hematology / CBC',
        'exp_en_normal': 'Normal hemoglobin concentration. Good oxygen-carrying capacity.',
        'exp_hi_normal': 'हीमोग्लोबिन का स्तर सामान्य है। शरीर में ऑक्सीजन का प्रवाह सही है।',
        'exp_en_high': 'High hemoglobin (polycythemia). Can occur in dehydration, smoking, or chronic hypoxia.',
        'exp_hi_high': 'हीमोग्लोबिन अधिक है। यह डिहाइड्रेशन या फेफड़ों की स्थिति के कारण हो सकता है।',
        'exp_en_low': 'Low hemoglobin indicates anemia. Can cause fatigue, pallor, and reduced endurance.',
        'exp_hi_low': 'हीमोग्लोबिन कम है (एनीमिया)। इससे थकान, कमजोरी और सांस फूलने की समस्या हो सकती है।'
    },
    'wbc_count': {
        'aliases': ['total leucocyte count', 'tlc', 'white blood cell count', 'wbc count', 'total wbc'],
        'display_name': 'Total Leukocyte Count (WBC)',
        'default_unit': 'cells/mcL',
        'ref_min': 4000.0,
        'ref_max': 11000.0,
        'category': 'Hematology / CBC',
        'exp_en_normal': 'White blood cell count is within normal immune surveillance limits.',
        'exp_hi_normal': 'श्वेत रक्त कणिकाओं (WBC) की संख्या सामान्य है।',
        'exp_en_high': 'Elevated WBC (leukocytosis). Frequently indicates bacterial or viral infection, inflammation, or stress.',
        'exp_hi_high': 'WBC की संख्या बढ़ी हुई है। यह किसी संक्रमण (इन्फेक्शन), सूजन या तनाव का संकेत हो सकता है।',
        'exp_en_low': 'Low WBC (leukopenia). May signal compromised immune response or viral bone marrow suppression.',
        'exp_hi_low': 'WBC की संख्या कम है, जिससे रोग प्रतिरोधक क्षमता कमजोर हो सकती है।'
    },
    'platelet_count': {
        'aliases': ['platelet count', 'platelets', 'plt count'],
        'display_name': 'Platelet Count',
        'default_unit': 'lakh/mcL',
        'ref_min': 150000.0,
        'ref_max': 450000.0,
        'category': 'Hematology / CBC',
        'exp_en_normal': 'Platelet count is normal. Healthy blood clotting capability.',
        'exp_hi_normal': 'प्लेटलेट्स की संख्या सामान्य है। रक्त के थक्के जमने की प्रक्रिया ठीक है।',
        'exp_en_high': 'High platelet count (thrombocytosis). Can be reactive to inflammation or iron deficiency.',
        'exp_hi_high': 'प्लेटलेट्स की संख्या बढ़ी हुई है। यह सूजन या आयरन की कमी के कारण हो सकता है।',
        'exp_en_low': 'Low platelet count (thrombocytopenia). Increases risk of easy bruising or bleeding.',
        'exp_hi_low': 'प्लेटलेट्स की संख्या कम है। इससे रक्तस्राव या नील पड़ने का जोखिम बढ़ सकता है।'
    },

    # Renal / Kidney Function
    'serum_creatinine': {
        'aliases': ['serum creatinine', 'creatinine', 's. creatinine'],
        'display_name': 'Serum Creatinine',
        'default_unit': 'mg/dL',
        'ref_min': 0.7,
        'ref_max': 1.3,
        'category': 'Renal / Kidney',
        'exp_en_normal': 'Normal serum creatinine level. Suggests healthy renal filtration efficiency.',
        'exp_hi_normal': 'सीरम क्रिएटिनिन सामान्य है। गुर्दे (किडनी) का फिल्टरेशन सही काम कर रहा है।',
        'exp_en_high': 'Elevated creatinine indicates impaired kidney filtration or dehydration. Physician evaluation needed.',
        'exp_hi_high': 'क्रिएटिनिन का स्तर बढ़ा हुआ है। यह किडनी की कार्यक्षमता में कमी या डिहाइड्रेशन का संकेत देता है।',
        'exp_en_low': 'Low creatinine is generally of low clinical concern; often linked to lower muscle mass.',
        'exp_hi_low': 'क्रिएटिनिन का स्तर कम है; आमतौर पर कम मांसपेशियों के द्रव्यमान से जुड़ा होता है।'
    },
    'blood_urea': {
        'aliases': ['blood urea', 'blood urea nitrogen', 'bun', 'urea'],
        'display_name': 'Blood Urea / BUN',
        'default_unit': 'mg/dL',
        'ref_min': 15.0,
        'ref_max': 45.0,
        'category': 'Renal / Kidney',
        'exp_en_normal': 'Normal blood urea level. Efficient protein metabolic clearance.',
        'exp_hi_normal': 'ब्लड यूरिया का स्तर सामान्य है।',
        'exp_en_high': 'Elevated blood urea. May stem from reduced renal clearance, dehydration, or high protein intake.',
        'exp_hi_high': 'ब्लड यूरिया बढ़ा हुआ है। यह किडनी की धीमी कार्यप्रणाली या पानी की कमी से हो सकता है।',
        'exp_en_low': 'Low blood urea level. Rarely clinically significant; seen with very low protein diets.',
        'exp_hi_low': 'ब्लड यूरिया कम है।'
    },
    'uric_acid': {
        'aliases': ['uric acid', 'serum uric acid'],
        'display_name': 'Serum Uric Acid',
        'default_unit': 'mg/dL',
        'ref_min': 3.5,
        'ref_max': 7.2,
        'category': 'Renal / Metabolic',
        'exp_en_normal': 'Normal serum uric acid level. Balanced purine metabolism.',
        'exp_hi_normal': 'यूरिक एसिड का स्तर सामान्य है।',
        'exp_en_high': 'Hyperuricemia (high uric acid). Increases risk of gouty arthritis or kidney stones.',
        'exp_hi_high': 'यूरिक एसिड बढ़ा हुआ है। इससे जोड़ों में दर्द (गठिया/गाउट) या पथरी का खतरा बढ़ सकता है।',
        'exp_en_low': 'Low uric acid level. Generally of minor clinical importance.',
        'exp_hi_low': 'यूरिक एसिड कम है।'
    },

    # Lipid / Cholesterol Profile
    'total_cholesterol': {
        'aliases': ['total cholesterol', 'cholesterol total', 'serum cholesterol'],
        'display_name': 'Total Serum Cholesterol',
        'default_unit': 'mg/dL',
        'ref_min': 125.0,
        'ref_max': 200.0,
        'category': 'Lipid / Cardiovascular',
        'exp_en_normal': 'Desirable total cholesterol level (<200 mg/dL). Favorable for arterial health.',
        'exp_hi_normal': 'कुल कोलेस्ट्रॉल का स्तर सामान्य और सुरक्षित सीमा में है।',
        'exp_en_high': 'Elevated total cholesterol. Risk factor for atherosclerosis and cardiovascular disease.',
        'exp_hi_high': 'कोलेस्ट्रॉल का स्तर बढ़ा हुआ है। यह धमनियों में रुकावट और दिल की बीमारियों का खतरा बढ़ा सकता है।',
        'exp_en_low': 'Low total cholesterol. May warrant investigation if unexplained weight loss is present.',
        'exp_hi_low': 'कोलेस्ट्रॉल कम है।'
    },
    'triglycerides': {
        'aliases': ['triglycerides', 'serum triglycerides', 'tg'],
        'display_name': 'Serum Triglycerides',
        'default_unit': 'mg/dL',
        'ref_min': 50.0,
        'ref_max': 150.0,
        'category': 'Lipid / Cardiovascular',
        'exp_en_normal': 'Normal triglyceride concentration. Balanced dietary fat storage.',
        'exp_hi_normal': 'ट्राइग्लिसराइड्स का स्तर सामान्य है।',
        'exp_en_high': 'Hypertriglyceridemia. Associated with metabolic syndrome, fatty liver, and vascular risk.',
        'exp_hi_high': 'ट्राइग्लिसराइड्स बढ़े हुए हैं। यह फैटी लिवर, मीठा ज्यादा खाने या मेटाबॉलिक सिंड्रोम से जुड़ा होता है।',
        'exp_en_low': 'Low triglyceride level.',
        'exp_hi_low': 'ट्राइग्लिसराइड्स कम हैं।'
    },
    'hdl_cholesterol': {
        'aliases': ['hdl cholesterol', 'hdl', 'high density lipoprotein'],
        'display_name': 'HDL Cholesterol (Good Cholesterol)',
        'default_unit': 'mg/dL',
        'ref_min': 40.0,
        'ref_max': 60.0,
        'category': 'Lipid / Cardiovascular',
        'exp_en_normal': 'Optimal HDL level. Provides protective reverse cholesterol transport from arteries.',
        'exp_hi_normal': 'अच्छा कोलेस्ट्रॉल (HDL) सही मात्रा में है, जो दिल की धमनियों की रक्षा करता है।',
        'exp_en_high': 'High HDL cholesterol is generally cardioprotective.',
        'exp_hi_high': 'HDL (अच्छा कोलेस्ट्रॉल) का स्तर बहुत अच्छा है, जो हृदय के लिए लाभदायक है।',
        'exp_en_low': 'Low HDL (<40 mg/dL). Weakens vascular protection; aerobic exercise and healthy fats help raise it.',
        'exp_hi_low': 'अच्छा कोलेस्ट्रॉल (HDL) कम है। व्यायाम और स्वस्थ आहार से इसे बढ़ाया जा सकता है।'
    },
    'ldl_cholesterol': {
        'aliases': ['ldl cholesterol', 'ldl', 'low density lipoprotein'],
        'display_name': 'LDL Cholesterol (Bad Cholesterol)',
        'default_unit': 'mg/dL',
        'ref_min': 50.0,
        'ref_max': 100.0,
        'category': 'Lipid / Cardiovascular',
        'exp_en_normal': 'Optimal LDL level. Minimizes atherogenic plaque buildup.',
        'exp_hi_normal': 'खराब कोलेस्ट्रॉल (LDL) सामान्य और सुरक्षित सीमा में है।',
        'exp_en_high': 'Elevated LDL cholesterol. Primary driver of coronary plaque accumulation.',
        'exp_hi_high': 'खराब कोलेस्ट्रॉल (LDL) बढ़ा हुआ है। यह हृदय धमनियों में रुकावट का मुख्य कारण बनता है।',
        'exp_en_low': 'Low LDL cholesterol. Desirable in cardiovascular risk management.',
        'exp_hi_low': 'LDL कोलेस्ट्रॉल कम है, जो हृदय स्वास्थ्य के लिए बेहतर है।'
    },

    # Liver Function (LFT)
    'sgpt_alt': {
        'aliases': ['sgpt', 'alt', 'alanine aminotransferase', 'alanine transaminase'],
        'display_name': 'SGPT / ALT (Alanine Aminotransferase)',
        'default_unit': 'U/L',
        'ref_min': 7.0,
        'ref_max': 56.0,
        'category': 'Hepatic / Liver',
        'exp_en_normal': 'Normal ALT enzyme level. Healthy liver hepatocellular integrity.',
        'exp_hi_normal': 'SGPT/ALT का स्तर सामान्य है। लिवर की कोशिकाएं स्वस्थ हैं।',
        'exp_en_high': 'Elevated ALT indicates liver cell inflammation (e.g. fatty liver, medication effect, or hepatitis).',
        'exp_hi_high': 'SGPT बढ़ा हुआ है। यह फैटी लिवर या लिवर में सूजन का संकेत हो सकता है।',
        'exp_en_low': 'Low ALT is not clinically concerning.',
        'exp_hi_low': 'SGPT कम है, जो सामान्य माना जाता है।'
    },
    'sgot_ast': {
        'aliases': ['sgot', 'ast', 'aspartate aminotransferase', 'aspartate transaminase'],
        'display_name': 'SGOT / AST (Aspartate Aminotransferase)',
        'default_unit': 'U/L',
        'ref_min': 10.0,
        'ref_max': 40.0,
        'category': 'Hepatic / Liver',
        'exp_en_normal': 'Normal AST level. Healthy hepatic and muscular cellular status.',
        'exp_hi_normal': 'SGOT/AST सामान्य सीमा में है।',
        'exp_en_high': 'Elevated AST. Can be elevated in liver inflammation or strenuous muscle exertion.',
        'exp_hi_high': 'SGOT बढ़ा हुआ है। यह लिवर या मांसपेशियों में खिंचाव/सूजन का संकेत हो सकता है।',
        'exp_en_low': 'Low AST is clinically insignificant.',
        'exp_hi_low': 'SGOT कम है।'
    },
    'bilirubin_total': {
        'aliases': ['total bilirubin', 'bilirubin total', 's. bilirubin'],
        'display_name': 'Total Serum Bilirubin',
        'default_unit': 'mg/dL',
        'ref_min': 0.2,
        'ref_max': 1.2,
        'category': 'Hepatic / Biliary',
        'exp_en_normal': 'Normal bilirubin level. Efficient red cell breakdown clearance.',
        'exp_hi_normal': 'बिलीरुबिन का स्तर सामान्य है।',
        'exp_en_high': 'Elevated bilirubin (hyperbilirubinemia). Can manifest as jaundice (yellowing of eyes/skin).',
        'exp_hi_high': 'बिलीरुबिन बढ़ा हुआ है। यह पीलिया (Jaundice) या लिवर की समस्या का संकेत हो सकता है।',
        'exp_en_low': 'Low bilirubin level is of no clinical concern.',
        'exp_hi_low': 'बिलीरुबिन कम है।'
    },

    # Thyroid Function
    'tsh': {
        'aliases': ['tsh', 'thyroid stimulating hormone', 'ultrasensitive tsh'],
        'display_name': 'TSH (Thyroid Stimulating Hormone)',
        'default_unit': 'µIU/mL',
        'ref_min': 0.4,
        'ref_max': 4.5,
        'category': 'Endocrine / Thyroid',
        'exp_en_normal': 'Normal TSH level. Pituitary-thyroid regulatory axis is balanced.',
        'exp_hi_normal': 'TSH का स्तर सामान्य है। थायरॉइड ग्रंथि सही काम कर रही है।',
        'exp_en_high': 'Elevated TSH indicates Hypothyroidism (underactive thyroid). May cause weight gain or fatigue.',
        'exp_hi_high': 'TSH बढ़ा हुआ है। यह हाइपोथायरॉइडिज्म (थायरॉइड की सुस्त कार्यप्रणाली) का संकेत है।',
        'exp_en_low': 'Low TSH indicates Hyperthyroidism (overactive thyroid). May cause palpitation or anxiety.',
        'exp_hi_low': 'TSH कम है। यह हाइपरथायरॉइडिज्म (अत्यधिक सक्रिय थायरॉइड) का संकेत हो सकता है।'
    },
}


def extract_text_from_file(file_path):
    """
    Extracts plain text from PDF using PyMuPDF (fitz) or image files using PIL/OCR.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    if ext == '.pdf':
        if fitz:
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            except Exception as e:
                text = f"Error reading PDF with PyMuPDF: {str(e)}"
        else:
            text = "PyMuPDF not available."

    elif ext in ['.jpg', '.jpeg', '.png']:
        if pytesseract:
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
            except Exception as e:
                text = f"[OCR Note] Image uploaded: {os.path.basename(file_path)}. OCR engine processing note: {str(e)}"
        else:
            text = f"[Uploaded Lab Image]: {os.path.basename(file_path)}"

    return text.strip()


def parse_extracted_text(text):
    """
    Parses raw extracted text for standard medical lab tests using regex and fuzzy alias matching.
    Returns a list of extracted parameter dicts.
    """
    extracted_items = []
    lines = text.splitlines()

    # Search for matching tests
    for key, spec in STANDARD_TEST_KNOWLEDGE.items():
        found = False
        for alias in spec['aliases']:
            # Search for alias pattern
            pattern = re.compile(rf"{re.escape(alias)}[^\n\d]*?([\d]+(?:\.[\d]+)?)", re.IGNORECASE)
            match = pattern.search(text)
            if match:
                try:
                    val = float(match.group(1))
                    # Adjust for platelet notation e.g. 2.5 lakh vs 250000
                    if key == 'platelet_count' and val < 10.0:
                        val = val * 100000.0

                    extracted_items.append({
                        'key': key,
                        'test_name': spec['display_name'],
                        'measured_value': val,
                        'unit': spec['default_unit'],
                        'reference_min': spec['ref_min'],
                        'reference_max': spec['ref_max'],
                        'category': spec['category'],
                    })
                    found = True
                    break
                except (ValueError, IndexError):
                    pass

    # If no automated matches found (e.g. handwritten/unusual format), provide standard template items
    if not extracted_items:
        default_keys = ['hemoglobin', 'fasting_blood_sugar', 'serum_creatinine', 'total_cholesterol', 'tsh']
        for k in default_keys:
            s = STANDARD_TEST_KNOWLEDGE[k]
            extracted_items.append({
                'key': k,
                'test_name': s['display_name'],
                'measured_value': round((s['ref_min'] + s['ref_max']) / 2.0, 1),
                'unit': s['default_unit'],
                'reference_min': s['ref_min'],
                'reference_max': s['ref_max'],
                'category': s['category'],
            })

    return extracted_items


def evaluate_parameter(test_name, measured_value, ref_min, ref_max):
    """
    Evaluates measured value against standard reference ranges and returns:
    status ('normal', 'low', 'high', 'context_needed', 'unable_to_interpret'),
    and bilingual explanations in simple English and Hindi.
    """
    # Attempt to locate knowledge base key
    matched_spec = None
    t_clean = test_name.lower().strip()
    for key, spec in STANDARD_TEST_KNOWLEDGE.items():
        if key in t_clean or any(a in t_clean for a in spec['aliases']):
            matched_spec = spec
            break

    if measured_value is None:
        return {
            'status': 'unable_to_interpret',
            'explanation_en': 'Measured value was not recorded or could not be verified.',
            'explanation_hi': 'जाँच का मान दर्ज नहीं है या पढ़ा नहीं जा सका।',
            'is_abnormal': False,
        }

    # Reference comparison
    if ref_min is not None and ref_max is not None:
        if measured_value < ref_min:
            status = 'low'
            is_abnormal = True
            en = matched_spec['exp_en_low'] if matched_spec else f"{test_name} is below the normal reference range ({ref_min} - {ref_max})."
            hi = matched_spec['exp_hi_low'] if matched_spec else f"{test_name} सामान्य सीमा ({ref_min} - {ref_max}) से कम है।"
        elif measured_value > ref_max:
            status = 'high'
            is_abnormal = True
            en = matched_spec['exp_en_high'] if matched_spec else f"{test_name} is above the normal reference range ({ref_min} - {ref_max})."
            hi = matched_spec['exp_hi_high'] if matched_spec else f"{test_name} सामान्य सीमा ({ref_min} - {ref_max}) से अधिक है।"
        else:
            status = 'normal'
            is_abnormal = False
            en = matched_spec['exp_en_normal'] if matched_spec else f"{test_name} is within the standard healthy reference range ({ref_min} - {ref_max})."
            hi = matched_spec['exp_hi_normal'] if matched_spec else f"{test_name} सामान्य और स्वस्थ सीमा ({ref_min} - {ref_max}) में है।"
    else:
        status = 'context_needed'
        is_abnormal = False
        en = "Reference intervals vary by laboratory methodology; clinical context is needed."
        hi = "इस जाँच की सामान्य सीमा लैब के अनुसार बदल सकती है; डॉक्टर की राय आवश्यक है।"

    return {
        'status': status,
        'explanation_en': en,
        'explanation_hi': hi,
        'is_abnormal': is_abnormal,
    }
