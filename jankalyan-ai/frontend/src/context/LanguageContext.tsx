import React, { createContext, useContext, useState, useEffect } from "react";
import { Locale } from "../types";
import { dictionaries } from "../data/dictionaries";

interface LanguageContextType {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: keyof typeof dictionaries["en"]) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<Locale>(() => {
    return (localStorage.getItem("jankalyan_locale") as Locale) || "en";
  });

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("jankalyan_locale", l);
  };

  const t = (key: keyof typeof dictionaries["en"]): string => {
    const dict = dictionaries[locale] || dictionaries.en;
    return (dict as any)[key] || dictionaries.en[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used within LanguageProvider");
  return context;
};
