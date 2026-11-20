"""
MediPredict AI — Conversational Health Assistant Engine.
Provides health education, laboratory parameter interpretation,
medical terminology definitions, and bilingual support (English & Hindi)
with clinical safety guardrails.
"""

import re
from reports.models import MedicalReport

DISCLAIMER_EN = (
    "\n\n*Medical Notice: I am an AI educational assistant. My responses are for informational awareness "
    "only and do not constitute a medical diagnosis or prescription. Please consult a licensed doctor for clinical care.*"
)

DISCLAIMER_HI = (
    "\n\n*चिकित्सा सूचना: मैं एक एआई सहायक हूँ। यह जानकारी केवल स्वास्थ्य जागरूकता के लिए है, किसी बीमारी का निदान "
    "या दवा का परामर्श नहीं। किसी भी चिकित्सीय निर्णय के लिए योग्य डॉक्टर से संपर्क करें।*"
)

def is_hindi(text):
    """Detects Devanagari script or common transliterated Hindi words."""
    hindi_regex = re.compile(r'[\u0900-\u097F]')
    if bool(hindi_regex.search(text)):
        return True
    lower = text.lower()
    hindi_keywords = ['kya', 'kaise', 'kare', 'ilaj', 'batao', 'dard', 'khoon', 'sugar', 'creatinine', 'report']
    matches = sum(1 for w in hindi_keywords if w in lower)
    return matches >= 2


def generate_assistant_response(user, user_message):
    query = user_message.strip().lower()
    hindi_query = is_hindi(user_message)

    # 1. User asking about their latest medical report
    if any(k in query for k in ['my report', 'latest report', 'meri report', 'mera report', 'check report']):
        latest_report = MedicalReport.objects.filter(user=user, status='confirmed').order_by('-report_date').first()
        if not latest_report:
            if hindi_query:
                return (
                    "आपके खाते में अभी तक कोई पुष्ट (Confirmed) मेडिकल रिपोर्ट नहीं मिली है। "
                    "कृपया 'Medical Report Analyzer' सेक्शन में जाकर अपनी लैब रिपोर्ट अपलोड करें, फिर मैं उसका सरल विश्लेषण कर सकूँगा।"
                    + DISCLAIMER_HI
                )
            return (
                "You do not have any confirmed laboratory reports in your account yet. "
                "Please upload your diagnostic report under the 'Medical Report Analyzer' tab, and I will gladly provide an educational summary of your findings."
                + DISCLAIMER_EN
            )

        # Summarize latest report
        total = latest_report.total_tests_count
        abnormal = latest_report.parameters.filter(status__in=['low', 'high'])
        if hindi_query:
            resp = f"**आपकी नवीनतम रिपोर्ट ({latest_report.title} - {latest_report.report_date.strftime('%d-%b-%Y')}):**\n"
            resp += f"कुल {total} जाँचों में से {abnormal.count()} जाँच सामान्य सीमा से बाहर हैं:\n"
            for p in abnormal:
                resp += f"• **{p.test_name}:** {p.measured_value} {p.unit} ({p.get_status_display()})\n  {p.explanation_hi}\n"
            if not abnormal:
                resp += "• सभी जाँचे सामान्य सीमा में हैं। आपका स्वास्थ्य अच्छा दिख रहा है।\n"
            return resp + DISCLAIMER_HI
        else:
            resp = f"**Summary of your latest report ({latest_report.title} on {latest_report.report_date.strftime('%d-%b-%Y')}):**\n"
            resp += f"Out of {total} analyzed biomarkers, {abnormal.count()} require your attention:\n"
            for p in abnormal:
                resp += f"• **{p.test_name}:** {p.measured_value} {p.unit} ({p.get_status_display()})\n  *{p.explanation_en}*\n"
            if not abnormal:
                resp += "• Great news! All recorded test values fall within standard healthy reference ranges.\n"
            return resp + DISCLAIMER_EN

    # 2. HbA1c / Diabetes
    if 'hba1c' in query:
        if hindi_query:
            return (
                "**HbA1c (ग्लाइकेटेड हीमोग्लोबिन) क्या है?**\n\n"
                "• **परिभाषा:** HbA1c टेस्ट पिछले 2 से 3 महीनों के औसत ब्लड शुगर (ग्लूकोज) स्तर को मापता है।\n"
                "• **सामान्य सीमा (Normal):** 4.0% से 5.6%\n"
                "• **प्री-डायबिटीज (Prediabetes):** 5.7% से 6.4%\n"
                "• **डायबिटीज (Diabetes):** 6.5% या उससे अधिक\n"
                "• **सुझाव:** फाइबर युक्त भोजन, नियमित व्यायाम, मीठे और रिफाइंड कार्ब्स का कम सेवन।"
                + DISCLAIMER_HI
            )
        return (
            "**What is HbA1c (Glycated Hemoglobin)?**\n\n"
            "• **Overview:** HbA1c reflects your average blood glucose control over the past 8 to 12 weeks.\n"
            "• **Normal Range:** < 5.7%\n"
            "• **Prediabetes:** 5.7% – 6.4%\n"
            "• **Diabetes:** ≥ 6.5%\n"
            "• **Clinical Significance:** It does not fluctuate with day-to-day meals, making it the gold standard for long-term glycemic monitoring."
            + DISCLAIMER_EN
        )

    # 3. Creatinine / Kidney
    if any(k in query for k in ['creatinine', 'kidney', 'गुर्दा', 'किडनी', 'cr']):
        if hindi_query:
            return (
                "**सीरम क्रिएटिनिन और किडनी स्वास्थ्य:**\n\n"
                "• **क्रिएटिनिन क्या है?** यह मांसपेशियों के सामान्य घिसाव से बनने वाला एक अपशिष्ट उत्पाद है, जिसे स्वस्थ किडनियां पेशाब के जरिए बाहर निकालती हैं।\n"
                "• **सामान्य सीमा:** 0.7 से 1.3 mg/dL (वयस्कों के लिए)।\n"
                "• **बढ़े होने के कारण:** पानी की कमी (डिहाइड्रेशन), अत्यधिक प्रोटीन या क्रिएटिन सप्लीमेंट्स, या किडनी के फिल्टर करने की गति में गिरावट।\n"
                "• **सलाह:** पर्याप्त पानी पिएं, नमक कम खाएं, और दर्द निवारक दवाओं (NSAIDs) का अनावश्यक सेवन न करें।"
                + DISCLAIMER_HI
            )
        return (
            "**Understanding Serum Creatinine & Kidney Health:**\n\n"
            "• **What it is:** Creatinine is a chemical metabolic waste product produced by normal muscle breakdown, filtered exclusively by kidney glomeruli.\n"
            "• **Healthy Reference Interval:** 0.7 – 1.3 mg/dL for men, 0.6 – 1.1 mg/dL for women.\n"
            "• **Elevated Levels:** May indicate acute dehydration, strenuous exertion, high dietary meat, or impaired glomerular filtration rate (GFR).\n"
            "• **Action Steps:** Ensure adequate hydration, minimize sodium intake, avoid unnecessary painkillers (NSAIDs), and consult a nephrologist if persistent."
            + DISCLAIMER_EN
        )

    # 4. Blood Pressure / Hypertension
    if any(k in query for k in ['blood pressure', 'bp', 'बीपी', 'hypertension', 'systolic']):
        if hindi_query:
            return (
                "**ब्लड प्रेशर (रक्तचाप) की जानकारी:**\n\n"
                "• **सामान्य BP:** 120/80 mm Hg से कम\n"
                "• **बढ़ा हुआ BP (Elevated):** सिस्टोलिक 120-129 और डायस्टोलिक 80 से कम\n"
                "• **हाई BP स्टेज 1:** 130-139 / 80-89 mm Hg\n"
                "• **हाई BP स्टेज 2:** 140/90 mm Hg या अधिक\n"
                "• **बचाव के उपाय:** नमक (सोडियम) कम करें, रोज़ाना 30 मिनट टहलें, तनाव नियंत्रित करें, और पर्याप्त नींद लें।"
                + DISCLAIMER_HI
            )
        return (
            "**Understanding Blood Pressure Categories:**\n\n"
            "• **Normal:** Less than 120/80 mm Hg\n"
            "• **Elevated:** Systolic 120–129 and Diastolic < 80 mm Hg\n"
            "• **Hypertension Stage 1:** 130–139 or Diastolic 80–89 mm Hg\n"
            "• **Hypertension Stage 2:** ≥ 140 or Diastolic ≥ 90 mm Hg\n"
            "• **Key Measures:** Reduce sodium (<2,300 mg/day), engage in aerobic physical activity, maintain healthy body weight, and sleep 7-8 hours nightly."
            + DISCLAIMER_EN
        )

    # 5. Cholesterol / Lipids
    if any(k in query for k in ['cholesterol', 'lipid', 'triglyceride', 'hdl', 'ldl', 'कोलेस्ट्रॉल']):
        if hindi_query:
            return (
                "**लिपिड प्रोफाइल (कोलेस्ट्रॉल) की जानकारी:**\n\n"
                "• **कुल कोलेस्ट्रॉल:** 200 mg/dL से कम वांछनीय है।\n"
                "• **HDL (अच्छा कोलेस्ट्रॉल):** 40-60 mg/dL (यह धमनियों से फैट हटाता है)।\n"
                "• **LDL (खराब कोलेस्ट्रॉल):** 100 mg/dL से कम होना चाहिए (यह धमनियों में रुकावट पैदा करता है)।\n"
                "• **ट्राइग्लिसराइड्स:** 150 mg/dL से कम होना चाहिए।\n"
                "• **सलाह:** तला-भुना और ट्रांस फैट कम करें, बादाम, अखरोट और अलसी के बीज डाइट में शामिल करें।"
                + DISCLAIMER_HI
            )
        return (
            "**Overview of Lipid Profile Markers:**\n\n"
            "• **Total Cholesterol:** Desirable is < 200 mg/dL.\n"
            "• **LDL ('Bad' Cholesterol):** Optimal is < 100 mg/dL. Primary factor in arterial plaque deposition.\n"
            "• **HDL ('Good' Cholesterol):** Protective is > 50 mg/dL. Transports excess lipids back to the liver.\n"
            "• **Triglycerides:** Normal is < 150 mg/dL. Strongly influenced by sugar and refined carbohydrate intake."
            + DISCLAIMER_EN
        )

    # 6. Hemoglobin / CBC
    if any(k in query for k in ['hemoglobin', 'hb', 'anemia', 'platelet', 'wbc', 'हीमोग्लोबिन', 'खून की कमी']):
        if hindi_query:
            return (
                "**हीमोग्लोबिन और सीबीसी (CBC) जानकारी:**\n\n"
                "• **सामान्य हीमोग्लोबिन:** पुरुषों में 13.5-17.5 g/dL, महिलाओं में 12.0-15.5 g/dL।\n"
                "• **कम हीमोग्लोबिन (एनीमिया):** इसके लक्षणों में थकान, चक्कर आना, पीलापन और सांस फूलना शामिल हैं।\n"
                "• **बढ़ाने के उपाय:** पालक, चुकंदर, अनार, दालें, गुड़ और विटामिन C युक्त फल (जैसे संतरा, नींबू)।\n"
                "• **प्लेटलेट्स:** 1.5 से 4.5 लाख सामान्य है। यह रक्त का थक्का बनाने के लिए आवश्यक है।"
                + DISCLAIMER_HI
            )
        return (
            "**Hemoglobin and Complete Blood Count (CBC) Insights:**\n\n"
            "• **Normal Hemoglobin:** 13.5–17.5 g/dL in men; 12.0–15.5 g/dL in women.\n"
            "• **Low Hemoglobin (Anemia):** Impairs systemic oxygenation. Common causes include iron deficiency, vitamin B12 deficiency, or chronic inflammation.\n"
            "• **Platelet Count:** Standard range is 150,000 to 450,000 /mcL, essential for blood coagulation.\n"
            "• **Dietary Support:** Iron-rich greens, legumes, beets, lean proteins, paired with vitamin C to enhance bio-absorption."
            + DISCLAIMER_EN
        )

    # Default general response
    if hindi_query:
        return (
            f"नमस्ते {user.first_name or user.username}! मैं MediPredict AI का स्वास्थ्य सहायक हूँ।\n\n"
            "मैं आपकी निम्नलिखित विषयों में मदद कर सकता हूँ:\n"
            "1. **लैब टेस्ट को समझना:** जैसे HbA1c, क्रिएटिनिन, सीरम यूरिया, कोलेस्ट्रॉल, सीबीसी आदि।\n"
            "2. **आपकी रिपोर्ट की समीक्षा:** पूछें *'मेरी रिपोर्ट समझाओ'* या *'latest report'*।\n"
            "3. **सामान्य स्वास्थ्य सलाह:** बीपी, वजन, संतुलित आहार और जीवनशैली से जुड़े प्रश्न।\n\n"
            "आप अपना प्रश्न हिंदी या अंग्रेज़ी किसी भी भाषा में पूछ सकते हैं।"
            + DISCLAIMER_HI
        )
    return (
        f"Hello {user.first_name or user.username}! I am your MediPredict AI Health Education Assistant.\n\n"
        "Here are key things I can assist you with:\n"
        "1. **Explaining Diagnostic Lab Tests:** e.g., 'What does elevated creatinine mean?', 'Explain HbA1c'.\n"
        "2. **Analyzing Your Uploaded Reports:** Ask 'Explain my latest report' to see your verified biomarkers.\n"
        "3. **Cardiovascular & Metabolic Education:** Guidance on Blood Pressure, BMI, Lipids, and Kidney health.\n"
        "4. **Bilingual Assistance:** You can communicate with me in English or Hindi (हिंदी).\n\n"
        "What health topic or lab result would you like to explore today?"
        + DISCLAIMER_EN
    )
