import React, { useEffect, useState } from "react";
import { X, Send, Volume2, ShieldCheck, Bot, User } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";
import { askPolicyQuestion } from "../lib/api";
import { speakText } from "../lib/speech";

interface PolicyChatDrawerProps {
  schemeId: string | null;
  onClose: () => void;
}

export const PolicyChatDrawer: React.FC<PolicyChatDrawerProps> = ({ schemeId, onClose }) => {
  const { locale, t } = useLanguage();
  const [messages, setMessages] = useState<Array<{ sender: "user" | "ai"; text: string; source?: string }>>([
    {
      sender: "ai",
      text: t("assistantGreeting")
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [voiceNotice, setVoiceNotice] = useState("");

  useEffect(() => {
    setMessages((current) => current.map((message, index) =>
      index === 0 && message.sender === "ai" && !message.source
        ? { ...message, text: t("assistantGreeting") }
        : message
    ));
    setVoiceNotice("");
  }, [locale]);

  if (!schemeId) return null;

  const handleSend = async (questionText?: string) => {
    const q = questionText || input;
    if (!q.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: q }]);
    setInput("");
    setIsTyping(true);

    const res = await askPolicyQuestion(q, schemeId, locale);
    setMessages((prev) => [
      ...prev,
      { sender: "ai", text: res.answer, source: res.sources?.[0] }
    ]);
    setIsTyping(false);
  };

  const handleSpeak = (text: string) => {
    setVoiceNotice(speakText(text, locale) ? "" : t("voiceUnavailable"));
  };

  const sampleQuestions = [
    "Can both my brother and I apply?",
    "What if college attendance is below 75%?",
    "Is my 3-year-old Income Certificate valid?"
  ];

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col justify-between">
      {/* Drawer Header */}
      <div className="p-4 bg-emerald-700 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-emerald-200" />
          <div>
            <h3 className="font-bold text-sm">Policy AI Assistant</h3>
            <span className="text-[10px] text-emerald-200 block">Verified Gazette Grounded</span>
          </div>
        </div>
        <button onClick={onClose} className="p-1 rounded-lg hover:bg-emerald-600 transition">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex items-start gap-2 ${m.sender === "user" ? "flex-row-reverse" : ""}`}
          >
            <div className={`p-1.5 rounded-full ${m.sender === "user" ? "bg-slate-900 text-white" : "bg-emerald-100 text-emerald-800"}`}>
              {m.sender === "user" ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>
            <div className={`p-3 rounded-2xl max-w-[80%] ${m.sender === "user" ? "bg-slate-900 text-white rounded-tr-none" : "bg-slate-100 text-slate-800 rounded-tl-none"}`}>
              <p className="leading-relaxed">{m.text}</p>
              {m.source && (
                <span className="text-[10px] text-emerald-700 font-semibold block mt-1.5 pt-1 border-t border-slate-200">
                  Citation: {m.source}
                </span>
              )}
              {m.sender === "ai" && (
                <button
                  onClick={() => handleSpeak(m.text)}
                  className="mt-2 flex items-center gap-1 text-[10px] text-slate-500 hover:text-emerald-700 font-semibold"
                >
                  <Volume2 className="w-3 h-3" />
                  Listen Audio
                </button>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce" />
            <span>Consulting official notifications...</span>
          </div>
        )}
        {voiceNotice && <p role="status" className="text-[11px] text-amber-700">{voiceNotice}</p>}
      </div>

      {/* Suggested Questions */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-100">
        <span className="text-[10px] font-bold text-slate-400 block mb-1">Quick Questions:</span>
        <div className="flex flex-wrap gap-1.5">
          {sampleQuestions.map((sq, i) => (
            <button
              key={i}
              onClick={() => handleSend(sq)}
              className="text-[10px] px-2 py-1 bg-white border border-slate-200 hover:border-emerald-300 rounded text-slate-700"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <div className="p-3 bg-white border-t border-slate-200 flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question..."
          className="flex-1 text-xs p-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
        <button
          onClick={() => handleSend()}
          className="p-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
