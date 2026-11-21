import os
import unittest
from unittest.mock import patch

from api.agent.orchestrator import extract_profile_from_text


class MultilingualIntakeTests(unittest.TestCase):
    def test_student_samples_extract_education_occupation_and_income(self):
        samples = {
            "kn": "ನಾನು ಮಂಡ್ಯದಲ್ಲಿ ಪಿಯುಸಿಯ ಮೊದಲ ವರ್ಷ ಓದುತ್ತಿದ್ದೇನೆ. ನಮ್ಮ ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ 1.5 ಲಕ್ಷ ರೂಪಾಯಿ.",
            "hi": "मैं मांड्या में पीयूसी के पहले वर्ष में पढ़ रहा हूँ। मेरे परिवार की वार्षिक आय 1.5 लाख रुपये है।",
            "ta": "நான் மண்டியாவில் பியூசி முதல் ஆண்டு படிக்கிறேன். எங்கள் குடும்பத்தின் ஆண்டு வருமானம் 1.5 லட்சம் ரூபாய்.",
            "ml": "ഞാൻ മാണ്ഡ്യയിൽ പി.യു.സി ഒന്നാം വർഷം പഠിക്കുന്നു. എന്റെ കുടുംബത്തിന്റെ വാർഷിക വരുമാനം 1.5 ലക്ഷം രൂപയാണ്.",
            "te": "నేను మాండ్యాలో పీయూసీ మొదటి సంవత్సరం చదువుతున్నాను. మా కుటుంబ వార్షిక ఆదాయం 1.5 లక్షల రూపాయలు.",
        }
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            for language, text in samples.items():
                with self.subTest(language=language):
                    profile, mode = extract_profile_from_text(text, language)
                    self.assertEqual(mode, "HEURISTIC_FALLBACK")
                    self.assertEqual(profile.educationLevel, "PUC")
                    self.assertEqual(profile.occupation, "STUDENT")
                    self.assertEqual(profile.familyAnnualIncome, 150000)

    def test_unemployed_graduate_samples_extract_profile(self):
        samples = {
            "kn": "ನಾನು 2024ರಲ್ಲಿ ಬಿ.ಎಸ್ಸಿ ಪದವಿ ಮುಗಿಸಿದೆ. ಆರು ತಿಂಗಳಿಂದ ನಿರುದ್ಯೋಗಿಯಾಗಿದ್ದೇನೆ.",
            "hi": "मैंने 2024 में बी.एससी. की डिग्री पूरी की और छह महीने से बेरोज़गार हूँ।",
            "ta": "நான் 2024-ல் பி.எஸ்சி பட்டம் முடித்தேன். ஆறு மாதங்களாக வேலை இல்லாமல் இருக்கிறேன்.",
            "ml": "ഞാൻ 2024-ൽ ബി.എസ്‌സി ബിരുദം പൂർത്തിയാക്കി. ആറുമാസമായി തൊഴിൽ ഇല്ല.",
            "te": "నేను 2024లో బి.ఎస్సీ డిగ్రీ పూర్తి చేశాను. ఆరు నెలలుగా నిరుద్యోగిగా ఉన్నాను.",
        }
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            for language, text in samples.items():
                with self.subTest(language=language):
                    profile, _ = extract_profile_from_text(text, language)
                    self.assertEqual(profile.educationLevel, "GRADUATE")
                    self.assertEqual(profile.occupation, "UNEMPLOYED")

    def test_tamil_farmer_sample_extracts_land_details(self):
        text = "நான் மண்டியாவில் 1.5 ஏக்கர் வறண்ட நிலம் கொண்ட விவசாயி."
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            profile, _ = extract_profile_from_text(text, "ta")

        self.assertEqual(profile.occupation, "FARMER")
        self.assertEqual(profile.landHoldingAcres, 1.5)
        self.assertEqual(profile.landType, "DRYLAND")


if __name__ == "__main__":
    unittest.main()
