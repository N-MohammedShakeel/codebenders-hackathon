export type Locale = "en" | "kn" | "hi" | "ta" | "ml" | "te";

export interface CitizenProfile {
  name?: string;
  age?: number;
  gender?: "MALE" | "FEMALE" | "OTHER";
  state: string;
  district?: string;
  educationLevel?: "CLASS_8_10" | "PUC" | "DIPLOMA" | "GRADUATE" | "POSTGRADUATE" | "NONE";
  familyAnnualIncome: number;
  casteCategory?: "GENERAL" | "OBC" | "SC" | "ST" | "MINORITY";
  landHoldingAcres?: number;
  landType?: "DRYLAND" | "IRRIGATED" | "NONE";
  occupation?: "STUDENT" | "FARMER" | "DAILY_WAGE" | "SELF_EMPLOYED" | "UNEMPLOYED";
  isAadhaarBankLinked?: boolean;
}

export interface RulePredicate {
  field: keyof CitizenProfile;
  operator: "EQUALS" | "LTE" | "GTE" | "IN";
  value: any;
  descriptionEn: string;
  descriptionKn: string;
  descriptionHi: string;
}

export interface DocumentRequirement {
  id: string;
  nameEn: string;
  nameKn: string;
  nameHi: string;
  authority: string;
  estimatedCost: string;
  turnaroundDays: number;
  mandatory: boolean;
  howToGetUrl?: string | null;
}

export type DocumentCategoryKey =
  | "identity"
  | "income"
  | "residence"
  | "education"
  | "caste"
  | "land"
  | "bank"
  | "other";

export type DocumentValidityStatus = "CURRENT" | "EXPIRED" | "REVIEW_REQUIRED" | "TYPE_MISMATCH";

export interface DocumentExtractedFields {
  documentCategory: DocumentCategoryKey | null;
  documentType: string | null;
  issueDate: string | null;
  expiryDate: string | null;
  annualIncomeINR: number | null;
}

export interface DocumentOCRResult {
  fileName: string;
  extracted: DocumentExtractedFields;
  validity: {
    status: DocumentValidityStatus;
    detail: string;
  };
  checks: Record<string, { status: string; detail: string }>;
  issues: string[];
  mode: string;
  note: string;
}

export interface StoredDocumentEvidence {
  documentId: string;
  category: DocumentCategoryKey;
  validityStatus: DocumentValidityStatus;
  extracted: DocumentExtractedFields;
  savedAt: string;
}

export interface SchemeDefinition {
  id: string;
  nameEn: string;
  nameKn: string;
  nameHi: string;
  nameTa?: string;
  nameMl?: string;
  nameTe?: string;
  department: string;
  state: string;
  category: string;
  lastVerifiedDate: string;
  officialPortalUrl: string;
  helpline: string;
  benefitSummaryEn: string;
  benefitSummaryKn: string;
  benefitSummaryHi: string;
  benefitSummaryTa?: string;
  benefitSummaryMl?: string;
  benefitSummaryTe?: string;
  annualValueINR: number | null;
  deadline: string;
  eligibilityMode?: "AUTOMATED" | "MANUAL_REVIEW";
  eligibilityNoteEn?: string;
  rules: RulePredicate[];
  requiredDocuments: DocumentRequirement[];
  applicationStepsEn: string[];
  applicationStepsKn: string[];
  applicationStepsHi: string[];
  applicationStepsTa?: string[];
  applicationStepsMl?: string[];
  applicationStepsTe?: string[];
}

export interface RuleEvaluationDetail {
  predicate: RulePredicate;
  userValue: any;
  requiredValue: any;
  passed: boolean;
}

export interface NearMissRemediation {
  actionTitleEn: string;
  actionTitleKn: string;
  actionTitleHi: string;
  instructionsEn: string;
  instructionsKn: string;
  instructionsHi: string;
  portalUrl?: string;
}

export interface EligibilityMatchResult {
  schemeId: string;
  scheme: SchemeDefinition;
  status: "LIKELY_ELIGIBLE" | "NEAR_MISS" | "INELIGIBLE";
  matchPercentage: number;
  passedRules: RuleEvaluationDetail[];
  failedRules: RuleEvaluationDetail[];
  nearMissRemediation?: NearMissRemediation | null;
}

export interface AgentExecutionTraceStep {
  stepNumber: number;
  timestamp: string;
  agentRole: string;
  action: string;
  input: any;
  output: any;
  durationMs: number;
}

export interface DiscoveryHistoryEntry {
  id: string;
  searchedAt: string;
  state: string;
  matchedSchemeIds: string[];
  nearMissSchemeIds: string[];
  manualReviewSchemeIds: string[];
}

export interface ApplicationTrackerItem {
  id: string;
  schemeId: string;
  schemeName: string;
  stage: "DISCOVERED" | "DOCS_READY" | "APPLIED" | "UNDER_VERIFICATION" | "DISBURSED";
  appliedDate?: string;
  deadline: string;
  referenceNumber?: string;
  notes?: string;
}
