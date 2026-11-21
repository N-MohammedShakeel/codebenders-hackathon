import React from "react";
import { useAppState } from "../context/AppStateContext";
import { useLanguage } from "../context/LanguageContext";
import { WifiOff } from "lucide-react";

export const OfflineBanner: React.FC = () => {
  const { isOffline } = useAppState();
  const { t } = useLanguage();

  if (!isOffline) return null;

  return (
    <div className="bg-amber-500 text-white px-4 py-2 text-xs font-semibold flex items-center justify-center gap-2">
      <WifiOff className="w-4 h-4" />
      <span>{t("offlineNotice")}</span>
    </div>
  );
};
