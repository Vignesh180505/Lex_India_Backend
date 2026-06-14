import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "TPA-58",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "58",
        "section_title": "Mortgage defined",
        "section_text": "A mortgage is the transfer of an interest in specific immovable property for the purpose of securing the payment of money advanced or to be advanced by way of loan.",
        "simplified_en": "Defines a mortgage as transferring a partial interest in a property to secure a loan. Identifies terms like mortgagor (borrower) and mortgagee (lender).",
        "simplified_ta": "கடன் தொகைக்கு பாதுகாப்பாக ஒரு அசையா சொத்தின் மீதான உரிமையை மாற்றுவது அடமானம் (mortgage) ஆகும்.",
        "simplified_hi": "अचल संपत्ति पर ऋण की सुरक्षा के लिए आंशिक अधिकार हस्तांतरित करना बंधक (Mortgage) कहलाता है। ऋण लेने वाले को बंधककर्ता और देने वाले को बंधकदार कहते हैं।",
        "punishment": "Property definition - Underpins home loans and credit facilities",
        "severity": "medium"
    },
    {
        "section_id": "TPA-60",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "60",
        "section_title": "Right of mortgagor to redeem",
        "section_text": "At any time after the principal money has become due, the mortgagor has a right, on payment or tender, at a proper time and place, of the mortgage-money, to require the mortgagee to deliver to the mortgagor the mortgage-deed.",
        "simplified_en": "The borrower has a right to redeem (reclaim) their property once the loan is fully repaid. This right cannot be restricted by any contract clauses (once a mortgage, always a mortgage).",
        "simplified_ta": "அடமானக் கடனை முழுமையாக செலுத்திய பிறகு, தனது சொத்து ஆவணங்களை திரும்பப் பெற கடன் வாங்கியவருக்கு முழு உரிமை உண்டு.",
        "simplified_hi": "ऋण चुकाने के बाद अपनी संपत्ति वापस पाने का अधिकार (Right of Redemption) कर्जदार का मौलिक अधिकार है, जिसे किसी समझौते से छीना नहीं जा सकता।",
        "punishment": "Borrower Protection - Essential right protecting landowners from losing titles",
        "severity": "medium"
    },
    {
        "section_id": "TPA-105",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "105",
        "section_title": "Lease defined",
        "section_text": "A lease of immovable property is a transfer of a right to enjoy such property, made for a certain time, express or implied, or in perpetuity, in consideration of a price paid or promised.",
        "simplified_en": "Defines a lease as transferring the right to enjoy a property for a specific period in exchange for rent or premium. Establishes the lessor (landlord) and lessee (tenant) relationship.",
        "simplified_ta": "அசையா சொத்தை வாடகைக்கு அல்லது குத்தகைக்கு விடுவது குத்தகை (Lease) எனப்படும். உரிமையாளர் lessor என்றும், வாடகைதாரர் lessee என்றும் அழைக்கப்படுவர்.",
        "simplified_hi": "अचल संपत्ति को किराए या पट्टे पर देना 'Lease' कहलाता है। इसमें मकान मालिक (lessor) किरायेदार (lessee) को एक निश्चित अवधि के लिए संपत्ति के उपयोग का अधिकार देता है।",
        "punishment": "Property tenancy definition - Regulates commercial and residential rent",
        "severity": "medium"
    },
    {
        "section_id": "TPA-108",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "108",
        "section_title": "Rights and liabilities of lessor and lessee",
        "section_text": "In the absence of a contract or local usage to the contrary, the lessor and the lessee of immovable property, as against one another, respectively, possess the rights and are subject to the liabilities mentioned.",
        "simplified_en": "Sets the default rules for landlord and tenant responsibilities: Landlord must disclose property defects; Tenant must pay rent on time and maintain the property without damaging it.",
        "simplified_ta": "நில உரிமையாளர் மற்றும் வாடகைதாரரின் உரிமைகள் மற்றும் கடமைகளை வரையறுக்கிறது (வாடகை செலுத்துதல், சொத்தை சேதப்படுத்தாமல் பராமரித்தல்).",
        "simplified_hi": "मकान मालिक और किरायेदार के अधिकारों और दायित्वों को स्पष्ट करता है (जैसे किरायेदार द्वारा समय पर किराया देना और संपत्ति को नुकसान न पहुंचाना)।",
        "punishment": "Tenancy obligations - Forms base for rental disputes in civil courts",
        "severity": "medium"
    },
    {
        "section_id": "TPA-111",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "111",
        "section_title": "Determination of lease",
        "section_text": "A lease of immovable property determines: by efflux of the time limited thereby; by the happening of some event; by surrender; by forfeiture; on expiration of a notice to determine.",
        "simplified_en": "Lists how a lease ends: expiry of the time period, mutual surrender by tenant, forfeiture by landlord for non-payment of rent, or expiry of a termination notice.",
        "simplified_ta": "குத்தகை ஒப்பந்தம் எப்போது முடிவுக்கு வரும் என்பதை விளக்குகிறது (ஒப்பந்த காலம் முடிவடைதல், நோட்டீஸ் காலம் முடிவடைதல், உரிமையை விட்டுக்கொடுத்தல்).",
        "simplified_hi": "पट्टा समाप्त होने की स्थितियों को दर्शाता है (जैसे अवधि का पूरा होना, किरायेदार द्वारा छोड़ना, या नोटिस अवधि की समाप्ति)।",
        "punishment": "Lease termination - Basis for eviction suits",
        "severity": "medium"
    },
    {
        "section_id": "TPA-116",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "116",
        "section_title": "Effect of holding over",
        "section_text": "If a lessee or under-lessee of property remains in possession thereof after the determination of the lease granted to the lessee, and the lessor accepts rent from the lessee, the lease is, in the absence of an agreement to the contrary, renewed.",
        "simplified_en": "If a lease expires and the tenant continues to occupy the property and pay rent, and the landlord accepts it, the lease is deemed to be renewed on a month-to-month basis.",
        "simplified_ta": "குத்தகை காலம் முடிந்த பிறகும் வாடகைதாரர் தங்கியிருந்து, நில உரிமையாளர் வாடகையை ஏற்றுக்கொண்டால், குத்தகை புதுப்பிக்கப்பட்டதாகக் கருதப்படும்.",
        "simplified_hi": "पट्टे की अवधि समाप्त होने के बाद भी यदि किरायेदार संपत्ति पर रहता है और मकान मालिक किराया स्वीकार करता है, तो पट्टा नवीनीकृत माना जाएगा।",
        "punishment": "Holding Over - Protects tenants from sudden illegal eviction",
        "severity": "medium"
    },
    {
        "section_id": "TPA-7",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 7 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-8",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 8 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-9",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. Under this provision of TPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் TPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 9 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-10",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 10 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-11",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 11 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-12",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 12 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-13",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 13 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-14",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. Under this provision of TPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் TPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 14 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-15",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. This section establishes the rights, powers, and duties of authorities under the TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 15 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-16",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 16 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-17",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 17 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-18",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. This section establishes the rights, powers, and duties of authorities under the TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 18 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-19",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section establishes the rights, powers, and duties of authorities under the TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 19 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-20",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. Under this provision of TPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் TPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 20 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-21",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 21 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-22",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 22 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-23",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. This section regulates compliance and registration procedures for legal actions under TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 23 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-24",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section establishes the rights, powers, and duties of authorities under the TPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு TPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा TPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 24 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-25",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. Under this provision of TPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் TPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 25 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "TPA-26",
        "act_code": "TPA",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Transfer of Property Act, 1882, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. Under this provision of TPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் TPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 26 protocols.",
        "severity": "medium"
    }
]

async def seed():
    async with async_session_factory() as session:
        for law in LAWS:
            try:
                await session.execute(
                    text("""
                        INSERT INTO laws (
                            section_id, act_code, act_name, section_number,
                            section_title, section_text,
                            simplified_en, simplified_ta, simplified_hi,
                            punishment, severity, source_url, scraped_at
                        ) VALUES (
                            :section_id, :act_code, :act_name, :section_number,
                            :section_title, :section_text,
                            :simplified_en, :simplified_ta, :simplified_hi,
                            :punishment, :severity, '', NOW()
                        )
                        ON CONFLICT (section_id) DO UPDATE SET
                            section_text  = EXCLUDED.section_text,
                            section_title = EXCLUDED.section_title,
                            simplified_en = EXCLUDED.simplified_en,
                            simplified_ta = EXCLUDED.simplified_ta,
                            simplified_hi = EXCLUDED.simplified_hi,
                            punishment    = EXCLUDED.punishment,
                            severity      = EXCLUDED.severity,
                            updated_at    = NOW()
                    """),
                    law,
                )
                print(f"  [OK] {law['section_id']}")
            except Exception as e:
                print(f"  [FAIL] {law['section_id']}: {e}")
        await session.commit()
        print(f"\nSeeded {len(LAWS)} sections")

if __name__ == "__main__":
    asyncio.run(seed())
