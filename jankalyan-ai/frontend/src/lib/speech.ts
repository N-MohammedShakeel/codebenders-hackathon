import { Locale } from "../types";

export function getLocaleCode(locale: Locale): string {
  switch (locale) {
    case "kn": return "kn-IN";
    case "hi": return "hi-IN";
    case "ta": return "ta-IN";
    case "ml": return "ml-IN";
    case "te": return "te-IN";
    case "en":
    default: return "en-IN";
  }
}

export function startSpeechRecognition(
  locale: Locale,
  onResult: (text: string) => void,
  onError: (err: any) => void
): { stop: () => void } | null {
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

  if (!SpeechRecognition) {
    onError("Speech recognition is not supported in this browser.");
    return null;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = getLocaleCode(locale);
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event: any) => {
    if (event.results && event.results[0] && event.results[0][0]) {
      onResult(event.results[0][0].transcript);
    }
  };

  recognition.onerror = (e: any) => {
    onError(e);
  };

  try {
    recognition.start();
  } catch (err) {
    onError(err);
  }

  return {
    stop: () => {
      try {
        recognition.stop();
      } catch (e) {}
    }
  };
}

function findVoice(locale: Locale, voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | undefined {
  const code = getLocaleCode(locale).toLowerCase();
  const prefix = code.split("-")[0];
  return (
    voices.find((v) => v.lang.toLowerCase() === code) ||
    voices.find((v) => v.lang.toLowerCase().startsWith(prefix))
  );
}

function textUsesLocaleScript(text: string, locale: Locale): boolean {
  const scripts: Partial<Record<Locale, RegExp>> = {
    kn: /[\u0C80-\u0CFF]/,
    hi: /[\u0900-\u097F]/,
    ta: /[\u0B80-\u0BFF]/,
    ml: /[\u0D00-\u0D7F]/,
    te: /[\u0C00-\u0C7F]/,
  };
  return locale === "en" || scripts[locale]?.test(text) === true;
}

export function hasVoiceForLocale(locale: Locale): boolean {
  if (!("speechSynthesis" in window)) return false;
  return findVoice(locale, window.speechSynthesis.getVoices()) !== undefined;
}

let voicesListenerRegistered = false;
let pendingSpeech: { text: string; locale: Locale } | null = null;

export function speakText(text: string, locale: Locale): boolean {
  if (!textUsesLocaleScript(text, locale)) {
    console.warn(`Speech output skipped because the text is not in the selected ${locale} language.`);
    return false;
  }
  if (!("speechSynthesis" in window)) return false;
  const synth = window.speechSynthesis;
  synth.cancel();

  const voices = synth.getVoices();
  if (voices.length === 0) {
    pendingSpeech = { text, locale };
    if (!voicesListenerRegistered) {
      voicesListenerRegistered = true;
      synth.onvoiceschanged = () => {
        synth.onvoiceschanged = null;
        voicesListenerRegistered = false;
        const next = pendingSpeech;
        pendingSpeech = null;
        if (next) speakText(next.text, next.locale);
      };
    }
    return true;
  }

  const voice = findVoice(locale, voices);
  if (!voice) {
    console.warn(`Speech output skipped because no voice is installed for ${getLocaleCode(locale)}.`);
    return false;
  }

  try {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.lang = getLocaleCode(locale);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    synth.speak(utterance);
    return true;
  } catch (err) {
    console.warn("Speech synthesis failed:", err);
    return false;
  }
}
