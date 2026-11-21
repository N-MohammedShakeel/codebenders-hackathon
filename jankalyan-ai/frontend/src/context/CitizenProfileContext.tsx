import React, { createContext, useContext, useState, useEffect } from "react";
import { CitizenProfile } from "../types";

interface CitizenProfileContextType {
  profile: CitizenProfile;
  setProfile: (p: CitizenProfile) => void;
  updateProfileField: (field: keyof CitizenProfile, val: any) => void;
}

const defaultProfile: CitizenProfile = {
  name: "Karthik",
  state: "Karnataka",
  district: "Mandya",
  educationLevel: "PUC",
  familyAnnualIncome: 120000,
  casteCategory: "OBC",
  landHoldingAcres: 1.5,
  landType: "DRYLAND",
  occupation: "STUDENT",
  isAadhaarBankLinked: true
};

const CitizenProfileContext = createContext<CitizenProfileContextType | undefined>(undefined);

export const CitizenProfileProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [profile, setProfileState] = useState<CitizenProfile>(() => {
    try {
      const saved = localStorage.getItem("jankalyan_profile");
      return saved ? JSON.parse(saved) : defaultProfile;
    } catch (e) {
      return defaultProfile;
    }
  });

  const setProfile = (p: CitizenProfile) => {
    setProfileState(p);
    localStorage.setItem("jankalyan_profile", JSON.stringify(p));
  };

  const updateProfileField = (field: keyof CitizenProfile, val: any) => {
    setProfileState((prev) => {
      const updated = { ...prev, [field]: val };
      localStorage.setItem("jankalyan_profile", JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <CitizenProfileContext.Provider value={{ profile, setProfile, updateProfileField }}>
      {children}
    </CitizenProfileContext.Provider>
  );
};

export const useCitizenProfile = () => {
  const context = useContext(CitizenProfileContext);
  if (!context) throw new Error("useCitizenProfile must be used within CitizenProfileProvider");
  return context;
};
