import type { Locale } from "../types";
import taTranslations from "../data/scheme_translations_ta.json";
import mlTranslations from "../data/scheme_translations_ml.json";
import teTranslations from "../data/scheme_translations_te.json";

type Translation = { name?: string; benefit?: string; steps?: string[] };
type Translations = Record<string, Translation | string | undefined>;

const TRANSLATIONS: Partial<Record<Locale, Translations>> = {
  ta: taTranslations as Translations,
  ml: mlTranslations as Translations,
  te: teTranslations as Translations,
};

export type SchemeTextFields = {
  id: string;
  nameEn: string;
  nameKn: string;
  nameHi: string;
  benefitSummaryEn: string;
  benefitSummaryKn: string;
  benefitSummaryHi: string;
  applicationStepsEn: string[];
  applicationStepsKn: string[];
  applicationStepsHi: string[];
};

function translationFor(schemeId: string, locale: Locale): Translation | undefined {
  const table = TRANSLATIONS[locale];
  if (!table) return undefined;
  const entry = table[schemeId];
  return entry && typeof entry === "object" ? entry : undefined;
}

export function localizedName(scheme: SchemeTextFields, locale: Locale): string {
  const t = translationFor(scheme.id, locale);
  if (t?.name) return t.name;
  if (locale === "kn") return scheme.nameKn;
  if (locale === "hi") return scheme.nameHi;
  return scheme.nameEn;
}

export function localizedBenefit(scheme: SchemeTextFields, locale: Locale): string {
  const t = translationFor(scheme.id, locale);
  if (t?.benefit) return t.benefit;
  if (locale === "kn") return scheme.benefitSummaryKn;
  if (locale === "hi") return scheme.benefitSummaryHi;
  return scheme.benefitSummaryEn;
}

export function localizedSteps(scheme: SchemeTextFields, locale: Locale): string[] {
  const t = translationFor(scheme.id, locale);
  if (t?.steps && t.steps.length > 0) return t.steps;
  if (locale === "kn") return scheme.applicationStepsKn;
  if (locale === "hi") return scheme.applicationStepsHi;
  return scheme.applicationStepsEn;
}
