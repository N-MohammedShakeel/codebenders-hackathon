"""Pydantic v2 API contract models for JanKalyan AI.

These models are mirrored by the React frontend. Field names are part of the
public contract and must not be renamed.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal


class CitizenProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = "OTHER"
    state: str = "Karnataka"
    district: Optional[str] = "Mandya"
    educationLevel: Optional[str] = "PUC"
    familyAnnualIncome: float = 120000.0
    casteCategory: Optional[str] = "OBC"
    landHoldingAcres: Optional[float] = 1.5
    landType: Optional[str] = "DRYLAND"
    occupation: Optional[str] = "STUDENT"
    isAadhaarBankLinked: Optional[bool] = True
    disabilityPercentage: Optional[float] = None
    hasGovernmentEmployeeInFamily: Optional[bool] = None
    monthlySalaryINR: Optional[float] = None
    dayScholar: Optional[bool] = None
    collegeType: Optional[str] = None
    aicteApproved: Optional[bool] = None
    quota: Optional[str] = None
    attendancePercentage: Optional[float] = None
    academicTopper: Optional[bool] = None


class EligibilityCriterion(BaseModel):
    id: str
    group: str
    criterionEn: str


class RulePredicate(BaseModel):
    field: str
    operator: Literal["EQUALS", "LTE", "GTE", "IN"]
    value: Any
    descriptionEn: str
    descriptionKn: str
    descriptionHi: str


class DocumentRequirement(BaseModel):
    id: str
    nameEn: str
    nameKn: str
    nameHi: str
    authority: str
    estimatedCost: str
    turnaroundDays: int
    mandatory: bool
    howToGetUrl: Optional[str] = None


class SchemeDefinition(BaseModel):
    id: str
    nameEn: str
    nameKn: str
    nameHi: str
    nameTa: Optional[str] = None
    nameMl: Optional[str] = None
    nameTe: Optional[str] = None
    department: str
    state: str
    category: str
    lastVerifiedDate: str
    officialPortalUrl: str
    sourceUrls: List[str] = Field(default_factory=list)
    helpline: str
    benefitSummaryEn: str
    benefitSummaryKn: str
    benefitSummaryHi: str
    annualValueINR: Optional[float] = None
    deadline: str
    eligibilityMode: Optional[Literal["AUTOMATED", "MANUAL_REVIEW"]] = None
    eligibilityNoteEn: Optional[str] = None
    eligibilityCriteria: List[EligibilityCriterion] = Field(default_factory=list)
    rules: List[RulePredicate]
    requiredDocuments: List[DocumentRequirement]
    applicationStepsEn: List[str]
    applicationStepsKn: List[str]
    applicationStepsHi: List[str]


class EligibilityMatchResult(BaseModel):
    schemeId: str
    scheme: SchemeDefinition
    status: Literal["LIKELY_ELIGIBLE", "NEAR_MISS", "INELIGIBLE"]
    matchPercentage: float
    passedRules: List[Any]
    failedRules: List[Any]
    nearMissRemediation: Optional[Any] = None


class AgentExecutionTraceStep(BaseModel):
    stepNumber: int
    timestamp: str
    agentRole: str
    action: str
    input: Any
    output: Any
    durationMs: float


class IntakeRequest(BaseModel):
    text: str
    language: str = "en"


class IntakeResponse(BaseModel):
    profile: Dict[str, Any]
    extractionMode: str
    defaultedFields: List[str] = Field(default_factory=list)


class DocumentExtractedFields(BaseModel):
    documentCategory: Optional[str] = None
    documentType: Optional[str] = None
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    annualIncomeINR: Optional[float] = None


class DocumentEvidence(BaseModel):
    documentId: str
    category: Literal["identity", "income", "residence", "education", "caste", "land", "bank", "other"]
    validityStatus: Literal["CURRENT", "EXPIRED", "REVIEW_REQUIRED", "TYPE_MISMATCH"]
    extracted: DocumentExtractedFields
    savedAt: Optional[str] = None


class OrchestratorRequest(BaseModel):
    profile: CitizenProfile
    documentEvidence: List[DocumentEvidence] = Field(default_factory=list)


class OrchestratorResponse(BaseModel):
    profile: CitizenProfile
    matches: List[EligibilityMatchResult]
    nearMisses: List[EligibilityMatchResult]
    manualReviewSchemes: List[SchemeDefinition] = Field(default_factory=list)
    trace: List[AgentExecutionTraceStep]
    defaultedFields: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    question: str
    schemeId: Optional[str] = None
    language: str = "en"


class ChatResponse(BaseModel):
    answer: str
    sources: List[Any]
    mode: str


class DocumentOCRResponse(BaseModel):
    fileName: str
    extracted: Dict[str, Any]
    validity: Dict[str, Any]
    checks: Dict[str, Any]
    issues: List[str]
    mode: str
    note: str


class TavilySearchResponse(BaseModel):
    query: str
    results: List[Any]
    isMock: bool
    note: str
    verifiedAt: str
