import React, { useState, useRef } from "react";
import { Mic, MicOff, Sparkles, Volume2, Play } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";
import { startSpeechRecognition, speakText } from "../lib/speech";
import { INDIAN_STATES_AND_UTS } from "../data/states";
import { Locale } from "../types";

interface ConversationalIntakeProps {
  onDiscover: (transcriptText: string, stateName: string) => void;
  isLoading: boolean;
}

export const ConversationalIntake: React.FC<ConversationalIntakeProps> = ({ onDiscover, isLoading }) => {
  const { locale, t } = useLanguage();
  const [transcript, setTranscript] = useState("");
  const [selectedState, setSelectedState] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [speechNotice, setSpeechNotice] = useState("");
  const activeListenerRef = useRef<{ stop: () => void } | null>(null);

  const handleToggleRecording = () => {
    if (isRecording) {
      if (activeListenerRef.current) {
        activeListenerRef.current.stop();
        activeListenerRef.current = null;
      }
      setIsRecording(false);
    } else {
      setSpeechNotice("");
      setIsRecording(true);
      const listener = startSpeechRecognition(
        locale,
        (recognized) => {
          setTranscript((prev) => (prev ? `${prev} ${recognized}` : recognized));
          setIsRecording(false);
        },
        (err) => {
          console.warn("Speech recognition notice:", err);
          setSpeechNotice(t("voiceInputUnavailable"));
          setIsRecording(false);
        }
      );
      activeListenerRef.current = listener;
    }
  };

  const sampleVoiceChips: { id: string; label: string; text: Record<Locale, string> }[] = [
    {
      id: "sample-karthik",
      label: t("studentSample"),
      text: {
        en: "I am studying first-year PUC in Mandya. My family's annual income is 1.5 lakh rupees. I need a scholarship for college fees.",
        kn: "ನಾನು ಮಂಡ್ಯದಲ್ಲಿ ಪಿಯುಸಿಯ ಮೊದಲ ವರ್ಷ ಓದುತ್ತಿದ್ದೇನೆ. ನಮ್ಮ ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ 1.5 ಲಕ್ಷ ರೂಪಾಯಿ. ಕಾಲೇಜು ಶುಲ್ಕಕ್ಕೆ ವಿದ್ಯಾರ್ಥಿವೇತನ ಬೇಕು.",
        hi: "मैं मांड्या में पीयूसी के पहले वर्ष में पढ़ रहा हूँ। मेरे परिवार की वार्षिक आय 1.5 लाख रुपये है। कॉलेज की फीस के लिए छात्रवृत्ति चाहिए।",
        ta: "நான் மண்டியாவில் பியூசி முதல் ஆண்டு படிக்கிறேன். எங்கள் குடும்பத்தின் ஆண்டு வருமானம் 1.5 லட்சம் ரூபாய். கல்லூரிக் கட்டணத்திற்கு உதவித்தொகை வேண்டும்.",
        ml: "ഞാൻ മാണ്ഡ്യയിൽ പി.യു.സി ഒന്നാം വർഷം പഠിക്കുന്നു. എന്റെ കുടുംബത്തിന്റെ വാർഷിക വരുമാനം 1.5 ലക്ഷം രൂപയാണ്. കോളേജ് ഫീസിനായി സ്കോളർഷിപ്പ് വേണം.",
        te: "నేను మాండ్యాలో పీయూసీ మొదటి సంవత్సరం చదువుతున్నాను. మా కుటుంబ వార్షిక ఆదాయం 1.5 లక్షల రూపాయలు. కళాశాల ఫీజు కోసం స్కాలర్‌షిప్ కావాలి.",
      }
    },
    {
      id: "sample-manjula",
      label: t("farmerSample"),
      text: {
        en: "I am a farmer with 1.5 acres of dryland in Mandya. Drought damaged my crop. I need farming assistance and help with a borewell.",
        kn: "ನಾನು ಮಂಡ್ಯದಲ್ಲಿ 1.5 ಎಕರೆ ಒಣಭೂಮಿ ಹೊಂದಿರುವ ರೈತ ಮಹಿಳೆ. ಬರದಿಂದ ನನ್ನ ಬೆಳೆ ಹಾನಿಯಾಗಿದೆ. ಕೃಷಿ ಸಹಾಯ ಮತ್ತು ಕೊಳವೆಬಾವಿಗೆ ನೆರವು ಬೇಕು.",
        hi: "मैं मांड्या में 1.5 एकड़ सूखी जमीन वाली किसान हूँ। सूखे से मेरी फसल को नुकसान हुआ है। खेती की सहायता और बोरवेल के लिए मदद चाहिए।",
        ta: "நான் மண்டியாவில் 1.5 ஏக்கர் வறண்ட நிலம் கொண்ட விவசாயி. வறட்சியால் என் பயிர் பாதிக்கப்பட்டது. விவசாய உதவியும் ஆழ்துளைக் கிணற்றுக்கான உதவியும் வேண்டும்.",
        ml: "ഞാൻ മാണ്ഡ്യയിൽ 1.5 ഏക്കർ വരണ്ട ഭൂമിയുള്ള കർഷകയാണ്. വരൾച്ച മൂലം എന്റെ വിള നശിച്ചു. കൃഷി സഹായവും കുഴൽക്കിണറിനുള്ള സഹായവും വേണം.",
        te: "నేను మాండ్యాలో 1.5 ఎకరాల మెట్ట భూమి ఉన్న రైతును. కరువు వల్ల నా పంట దెబ్బతింది. వ్యవసాయ సహాయం, బోర్‌వెల్ కోసం మద్దతు కావాలి.",
      }
    },
    {
      id: "sample-ravi",
      label: t("graduateSample"),
      text: {
        en: "I completed my B.Sc. degree in 2024 and have been unemployed for six months. I want to apply for Yuva Nidhi.",
        kn: "ನಾನು 2024ರಲ್ಲಿ ಬಿ.ಎಸ್ಸಿ ಪದವಿ ಮುಗಿಸಿದೆ. ಆರು ತಿಂಗಳಿಂದ ನಿರುದ್ಯೋಗಿಯಾಗಿದ್ದೇನೆ. ಯುವ ನಿಧಿಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಬಯಸುತ್ತೇನೆ.",
        hi: "मैंने 2024 में बी.एससी. की डिग्री पूरी की और छह महीने से बेरोज़गार हूँ। मैं युवा निधि के लिए आवेदन करना चाहता हूँ।",
        ta: "நான் 2024-ல் பி.எஸ்சி பட்டம் முடித்தேன். ஆறு மாதங்களாக வேலை இல்லாமல் இருக்கிறேன். யுவ நிதிக்கு விண்ணப்பிக்க விரும்புகிறேன்.",
        ml: "ഞാൻ 2024-ൽ ബി.എസ്‌സി ബിരുദം പൂർത്തിയാക്കി. ആറുമാസമായി തൊഴിൽ ഇല്ല. യുവ നിധിക്ക് അപേക്ഷിക്കാൻ ആഗ്രഹിക്കുന്നു.",
        te: "నేను 2024లో బి.ఎస్సీ డిగ్రీ పూర్తి చేశాను. ఆరు నెలలుగా నిరుద్యోగిగా ఉన్నాను. యువ నిధికి దరఖాస్తు చేయాలనుకుంటున్నాను.",
      }
    }
  ];

  const handleSelectSample = (sample: typeof sampleVoiceChips[0]) => {
    const text = sample.text[locale];
    setTranscript(text);
    setSpeechNotice(speakText(text, locale) ? "" : t("voiceUnavailable"));
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
      <div className="p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-600" />
              {t("heroHeading")}
            </h2>
            <p className="text-sm text-slate-600 mt-1">{t("heroSubheading")}</p>
          </div>
        </div>

        {/* Input Area */}
        <div className="relative mt-2">
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder={isRecording ? t("listening") : t("typePlaceholder")}
            rows={4}
            className={`w-full p-4 rounded-xl border text-base focus:ring-2 focus:ring-emerald-500 focus:outline-none transition ${
              isRecording ? "border-emerald-500 bg-emerald-50/40" : "border-slate-300 bg-slate-50/50"
            }`}
          />

          {/* Voice Microphone Button */}
          <button
            type="button"
            onClick={handleToggleRecording}
            className={`absolute right-3 bottom-3 p-3 rounded-xl flex items-center justify-center transition shadow-md ${
              isRecording
                ? "bg-red-500 text-white animate-pulse"
                : "bg-emerald-600 hover:bg-emerald-700 text-white"
            }`}
            title={t("speakPrompt")}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
        </div>
        {speechNotice && <p role="status" className="mt-2 text-xs text-amber-700">{speechNotice}</p>}

        {/* Auditorium Demo Voice Chips */}
        <div className="mt-4 pt-4 border-t border-slate-100">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Volume2 className="w-3.5 h-3.5 text-emerald-600" />
            {t("sampleRecordings")}
          </div>
          <div className="flex flex-wrap gap-2">
            {sampleVoiceChips.map((chip) => (
              <button
                key={chip.id}
                onClick={() => handleSelectSample(chip)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-emerald-100 text-slate-700 hover:text-emerald-900 text-xs font-semibold rounded-lg border border-slate-200 transition"
              >
                <Play className="w-3 h-3 fill-current" />
                {chip.label}
              </button>
            ))}
          </div>
        </div>

        {/* State Selector */}
        <div className="mt-6">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Your state
          </label>
          <select
            aria-label="State"
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full sm:w-64 p-3 rounded-xl border border-slate-300 text-sm"
          >
            <option value="">Select your state</option>
            {INDIAN_STATES_AND_UTS.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>

        {/* Action Button */}
        <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="text-xs text-slate-400">
            * 100% Free • No Aadhaar or Phone Number collected
          </span>
          <button
            onClick={() => onDiscover(transcript, selectedState)}
            disabled={isLoading || !transcript.trim() || !selectedState}
            className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white text-sm font-bold rounded-xl shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Running Agent Swarm...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>{t("discoverBtn")}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
