from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class DocumentType(str, enum.Enum):
    PASSPORT = "passport"
    VISA = "visa"
    NATIONAL_ID = "national_id"
    RESIDENCE_PERMIT = "residence_permit"

class ProcessingStatus(str, enum.Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    WARNING = "warning"
    FAILED = "failed"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Officer(Base):
    __tablename__ = "officers"
    
    id = Column(Integer, primary_key=True, index=True)
    officer_id = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    rank = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PassengerCase(Base):
    __tablename__ = "passenger_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True, nullable=False)
    passenger_name = Column(String, nullable=False)
    nationality = Column(String)
    date_of_birth = Column(String)
    passport_number = Column(String)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    overall_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    verifications = relationship("VerificationResult", back_populates="case", cascade="all, delete-orphan")
    tampering_results = relationship("TamperingResult", back_populates="case", cascade="all, delete-orphan")
    face_verification = relationship("FaceVerification", back_populates="case", cascade="all, delete-orphan", uselist=False)
    risk_assessment = relationship("RiskAssessment", back_populates="case", cascade="all, delete-orphan", uselist=False)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("passenger_cases.id"), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    ocr_data = Column(Text)
    mrz_data = Column(Text)
    mrz_status = Column(String)
    checksum_status = Column(String)
    ocr_mrz_match = Column(String)
    validation_status = Column(String)
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.WAITING)
    progress = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    case = relationship("PassengerCase", back_populates="documents")

class VerificationResult(Base):
    __tablename__ = "verification_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("passenger_cases.id"), nullable=False)
    check_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("PassengerCase", back_populates="verifications")

class TamperingResult(Base):
    __tablename__ = "tampering_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("passenger_cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    tampering_status = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    suspicious_region = Column(String)
    heatmap_path = Column(String)
    noise_residual_path = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("PassengerCase", back_populates="tampering_results")
    document = relationship("Document")

class FaceVerification(Base):
    __tablename__ = "face_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("passenger_cases.id"), nullable=False)
    document_photo_path = Column(String)
    live_photo_path = Column(String)
    similarity_score = Column(Float, default=0.0)
    match_status = Column(String, nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("PassengerCase", back_populates="face_verification")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("passenger_cases.id"), nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    reasons = Column(Text)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("PassengerCase", back_populates="risk_assessment")