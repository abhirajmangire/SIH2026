from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class DocumentType(str, Enum):
    PASSPORT = "passport"
    VISA = "visa"
    NATIONAL_ID = "national_id"
    RESIDENCE_PERMIT = "residence_permit"

class ProcessingStatus(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    WARNING = "warning"
    FAILED = "failed"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class OfficerLogin(BaseModel):
    officer_id: str
    password: str

class OfficerResponse(BaseModel):
    id: int
    officer_id: str
    name: str
    rank: str
    
    class Config:
        from_attributes = True

class DocumentUpload(BaseModel):
    document_type: DocumentType
    case_id: Optional[int] = None

class DocumentResponse(BaseModel):
    id: int
    case_id: int
    document_type: DocumentType
    original_filename: str
    ocr_data: Optional[str]
    mrz_data: Optional[str]
    mrz_status: Optional[str]
    checksum_status: Optional[str]
    ocr_mrz_match: Optional[str]
    validation_status: Optional[str]
    processing_status: ProcessingStatus
    progress: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PassengerCaseCreate(BaseModel):
    passenger_name: str
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    passport_number: Optional[str] = None

class PassengerCaseResponse(BaseModel):
    id: int
    case_id: str
    passenger_name: str
    nationality: Optional[str]
    date_of_birth: Optional[str]
    passport_number: Optional[str]
    risk_level: RiskLevel
    overall_status: str
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []
    
    class Config:
        from_attributes = True

class VerificationResultResponse(BaseModel):
    id: int
    case_id: int
    check_name: str
    status: str
    details: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TamperingResultResponse(BaseModel):
    id: int
    case_id: int
    document_id: int
    tampering_status: str
    confidence: float
    suspicious_region: Optional[str]
    heatmap_path: Optional[str]
    noise_residual_path: Optional[str]
    details: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class FaceVerificationResponse(BaseModel):
    id: int
    case_id: int
    document_photo_path: Optional[str]
    live_photo_path: Optional[str]
    similarity_score: float
    match_status: str
    details: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RiskAssessmentResponse(BaseModel):
    id: int
    case_id: int
    risk_level: RiskLevel
    reasons: Optional[str]
    score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class PassengerCaseDetailResponse(PassengerCaseResponse):
    verifications: List[VerificationResultResponse] = []
    tampering_results: List[TamperingResultResponse] = []
    face_verification: Optional[FaceVerificationResponse] = None
    risk_assessment: Optional[RiskAssessmentResponse] = None

class DashboardStats(BaseModel):
    passengers_screened: int
    documents_verified: int
    valid_documents: int
    suspicious_documents: int
    high_risk_cases: int
    risk_distribution: dict

class ProcessingStep(BaseModel):
    step: str
    status: str
    details: Optional[str] = None