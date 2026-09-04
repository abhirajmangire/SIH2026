import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, init_db, engine
from models import Base, Officer, PassengerCase, Document, VerificationResult, TamperingResult, FaceVerification, RiskAssessment, DocumentType, ProcessingStatus, RiskLevel
from schemas import *
from auth import verify_password, get_password_hash, create_access_token, decode_access_token, SECRET_KEY, ALGORITHM
from services.verification import MRZDecoder, OCRExtractor, DocumentValidator, CrossDocumentVerifier, TamperingDetector, FaceVerifier, RiskEngine

app = FastAPI(title="SIH 2026 - Fake Identity Screening System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("storage/uploads", exist_ok=True)
os.makedirs("storage/tampering", exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.on_event("startup")
def startup_event():
    init_db()
    create_demo_officer()
    create_demo_cases()

def create_demo_officer():
    db = next(get_db())
    officer = db.query(Officer).filter(Officer.officer_id == "OFFICER001").first()
    if not officer:
        officer = Officer(
            officer_id="OFFICER001",
            password_hash=get_password_hash("SecurePass123!"),
            name="Officer Rajesh Kumar",
            rank="Immigration Officer"
        )
        db.add(officer)
        db.commit()

def create_demo_cases():
    db = next(get_db())
    if db.query(PassengerCase).count() > 0:
        return
    
    demo_cases = [
        {
            "case_id": "CASE-2026-001",
            "passenger_name": "Aditi Sharma",
            "nationality": "IND",
            "date_of_birth": "15.03.1990",
            "passport_number": "Z1234567",
            "risk_level": RiskLevel.LOW,
            "overall_status": "completed",
            "documents": [
                {"type": DocumentType.PASSPORT, "filename": "valid_passport.jpg", "case_type": "valid"},
                {"type": DocumentType.VISA, "filename": "valid_visa.jpg", "case_type": "valid"}
            ]
        },
        {
            "case_id": "CASE-2026-002",
            "passenger_name": "Rahul Verma",
            "nationality": "IND",
            "date_of_birth": "22.07.1985",
            "passport_number": "A9876543",
            "risk_level": RiskLevel.MEDIUM,
            "overall_status": "completed",
            "documents": [
                {"type": DocumentType.PASSPORT, "filename": "suspicious_passport.jpg", "case_type": "suspicious"},
                {"type": DocumentType.VISA, "filename": "suspicious_visa.jpg", "case_type": "suspicious"}
            ]
        },
        {
            "case_id": "CASE-2026-003",
            "passenger_name": "Priya Kumari",
            "nationality": "IND",
            "date_of_birth": "10.11.1992",
            "passport_number": "X5555555",
            "risk_level": RiskLevel.HIGH,
            "overall_status": "completed",
            "documents": [
                {"type": DocumentType.PASSPORT, "filename": "high_risk_passport.jpg", "case_type": "high_risk"},
                {"type": DocumentType.VISA, "filename": "high_risk_visa.jpg", "case_type": "high_risk"}
            ]
        }
    ]
    
    for case_data in demo_cases:
        case = PassengerCase(
            case_id=case_data["case_id"],
            passenger_name=case_data["passenger_name"],
            nationality=case_data["nationality"],
            date_of_birth=case_data["date_of_birth"],
            passport_number=case_data["passport_number"],
            risk_level=case_data["risk_level"],
            overall_status=case_data["overall_status"]
        )
        db.add(case)
        db.flush()
        
        for doc_data in case_data["documents"]:
            doc = Document(
                case_id=case.id,
                document_type=doc_data["type"],
                file_path=f"storage/uploads/{doc_data['filename']}",
                original_filename=doc_data["filename"],
                processing_status=ProcessingStatus.COMPLETED,
                progress=100,
                processed_at=datetime.utcnow()
            )
            db.add(doc)
            db.flush()
            
            ocr_data = OCRExtractor.extract_from_image(doc.file_path, doc_data["type"].value)
            mrz_result = MRZDecoder.decode(ocr_data.get("mrz_lines", []))
            checksum_result = MRZDecoder.validate_checksum(mrz_result)
            ocr_mrz_match = OCRExtractor.compare_ocr_mrz(ocr_data, mrz_result)
            validation_result = DocumentValidator.validate(ocr_data, doc_data["type"].value)
            
            doc.ocr_data = json.dumps(ocr_data)
            doc.mrz_data = json.dumps(mrz_result)
            doc.mrz_status = "VALID" if mrz_result.get("valid") else "INVALID"
            doc.checksum_status = "VALID" if checksum_result.get("valid") else "INVALID"
            doc.ocr_mrz_match = "MATCH" if ocr_mrz_match.get("match") else "MISMATCH"
            doc.validation_status = "VALID" if validation_result.get("valid") else "INVALID"
            
            tampering_result = TamperingDetector.analyze(doc.file_path, doc_data["case_type"])
            tamper = TamperingResult(
                case_id=case.id,
                document_id=doc.id,
                tampering_status=tampering_result["tampering_status"],
                confidence=tampering_result["confidence"],
                suspicious_region=tampering_result["suspicious_region"],
                heatmap_path=tampering_result["heatmap_path"],
                noise_residual_path=tampering_result["noise_residual_path"],
                details=tampering_result["details"]
            )
            db.add(tamper)
            
            verifications = [
                ("OCR Extraction", "completed", f"Extracted {len(ocr_data)} fields"),
                ("MRZ Processing", "completed", f"Decoded MRZ: {mrz_result.get('passport_number', 'N/A')}"),
                ("MRZ Checksum", "completed" if checksum_result.get("valid") else "failed", json.dumps(checksum_result.get("details", {}))),
                ("OCR-MRZ Verification", "completed" if ocr_mrz_match.get("match") else "warning", json.dumps(ocr_mrz_match)),
                ("Document Validation", "completed" if validation_result.get("valid") else "warning", json.dumps(validation_result.get("checks", []))),
            ]
            
            for v_name, v_status, v_details in verifications:
                vr = VerificationResult(
                    case_id=case.id,
                    check_name=v_name,
                    status=v_status,
                    details=v_details
                )
                db.add(vr)
        
        all_docs = db.query(Document).filter(Document.case_id == case.id).all()
        cross_result = CrossDocumentVerifier.verify([
            {"document_type": d.document_type.value, "ocr_data": json.loads(d.ocr_data)} for d in all_docs
        ])
        
        vr = VerificationResult(
            case_id=case.id,
            check_name="Cross-Document Verification",
            status="completed" if cross_result.get("match") else "warning",
            details=json.dumps(cross_result)
        )
        db.add(vr)
        
        face_result = FaceVerifier.verify("", "", case_data["documents"][0]["case_type"])
        fv = FaceVerification(
            case_id=case.id,
            document_photo_path="storage/uploads/face_doc.jpg",
            live_photo_path="storage/uploads/face_live.jpg",
            similarity_score=face_result["similarity_score"],
            match_status=face_result["match_status"],
            details=face_result["details"]
        )
        db.add(fv)
        
        risk_result = RiskEngine.assess(
            mrz_checksum_valid=checksum_result.get("valid", True),
            ocr_mrz_match=ocr_mrz_match.get("match", True),
            document_valid=validation_result.get("valid", True),
            cross_doc_match=cross_result.get("match", True),
            tampering_status=tampering_result["tampering_status"],
            face_match=face_result["match_status"] == "MATCH"
        )
        
        ra = RiskAssessment(
            case_id=case.id,
            risk_level=RiskLevel(risk_result["risk_level"]),
            reasons=json.dumps(risk_result["reasons"]),
            score=risk_result["score"]
        )
        db.add(ra)
        
        case.risk_level = RiskLevel(risk_result["risk_level"])
    
    db.commit()

@app.post("/api/auth/login")
def login(credentials: OfficerLogin, db: Session = Depends(get_db)):
    officer = db.query(Officer).filter(Officer.officer_id == credentials.officer_id).first()
    if not officer or not verify_password(credentials.password, officer.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": officer.officer_id, "officer_id": officer.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "officer": OfficerResponse.from_orm(officer)
    }

def get_current_officer(authorization: str = None, db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    officer = db.query(Officer).filter(Officer.id == payload.get("officer_id")).first()
    if not officer:
        raise HTTPException(status_code=401, detail="Officer not found")
    return officer

@app.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(officer: Officer = Depends(get_current_officer), db: Session = Depends(get_db)):
    cases = db.query(PassengerCase).all()
    docs = db.query(Document).all()
    
    valid_docs = sum(1 for d in docs if d.validation_status == "VALID")
    suspicious_docs = sum(1 for d in docs if d.validation_status != "VALID" or d.mrz_status != "VALID" or d.ocr_mrz_match != "MATCH")
    high_risk = sum(1 for c in cases if c.risk_level == RiskLevel.HIGH)
    
    risk_dist = {"low": 0, "medium": 0, "high": 0}
    for c in cases:
        risk_dist[c.risk_level.value] += 1
    
    return DashboardStats(
        passengers_screened=len(cases),
        documents_verified=len(docs),
        valid_documents=valid_docs,
        suspicious_documents=suspicious_docs,
        high_risk_cases=high_risk,
        risk_distribution=risk_dist
    )

@app.get("/api/dashboard/cases", response_model=List[PassengerCaseResponse])
def get_cases(officer: Officer = Depends(get_current_officer), db: Session = Depends(get_db)):
    cases = db.query(PassengerCase).order_by(PassengerCase.created_at.desc()).all()
    return cases

@app.post("/api/cases", response_model=PassengerCaseResponse)
def create_case(case_data: PassengerCaseCreate, officer: Officer = Depends(get_current_officer), db: Session = Depends(get_db)):
    case_id = f"CASE-2026-{str(db.query(PassengerCase).count() + 1).zfill(3)}"
    case = PassengerCase(
        case_id=case_id,
        passenger_name=case_data.passenger_name,
        nationality=case_data.nationality,
        date_of_birth=case_data.date_of_birth,
        passport_number=case_data.passport_number
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@app.post("/api/cases/{case_id}/documents")
async def upload_document(
    case_id: int,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    officer: Officer = Depends(get_current_officer),
    db: Session = Depends(get_db)
):
    case = db.query(PassengerCase).filter(PassengerCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = f"storage/uploads/{filename}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    doc = Document(
        case_id=case.id,
        document_type=document_type,
        file_path=file_path,
        original_filename=file.filename,
        processing_status=ProcessingStatus.PROCESSING,
        progress=0
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return {"document_id": doc.id, "message": "Upload started"}

@app.post("/api/cases/{case_id}/process")
def process_case(case_id: int, officer: Officer = Depends(get_current_officer), db: Session = Depends(get_db)):
    case = db.query(PassengerCase).filter(PassengerCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    docs = db.query(Document).filter(Document.case_id == case.id).all()
    
    for i, doc in enumerate(docs):
        doc.processing_status = ProcessingStatus.PROCESSING
        doc.progress = 10
        db.commit()
        
        ocr_data = OCRExtractor.extract_from_image(doc.file_path, doc.document_type.value)
        doc.progress = 30
        db.commit()
        
        mrz_result = MRZDecoder.decode(ocr_data.get("mrz_lines", []))
        doc.progress = 50
        db.commit()
        
        checksum_result = MRZDecoder.validate_checksum(mrz_result)
        doc.progress = 60
        db.commit()
        
        ocr_mrz_match = OCRExtractor.compare_ocr_mrz(ocr_data, mrz_result)
        doc.progress = 70
        db.commit()
        
        validation_result = DocumentValidator.validate(ocr_data, doc.document_type.value)
        doc.progress = 80
        db.commit()
        
        case_type = "valid"
        if case.risk_level == RiskLevel.HIGH:
            case_type = "high_risk"
        elif case.risk_level == RiskLevel.MEDIUM:
            case_type = "suspicious"
        
        tampering_result = TamperingDetector.analyze(doc.file_path, case_type)
        doc.progress = 90
        db.commit()
        
        doc.ocr_data = json.dumps(ocr_data)
        doc.mrz_data = json.dumps(mrz_result)
        doc.mrz_status = "VALID" if mrz_result.get("valid") else "INVALID"
        doc.checksum_status = "VALID" if checksum_result.get("valid") else "INVALID"
        doc.ocr_mrz_match = "MATCH" if ocr_mrz_match.get("match") else "MISMATCH"
        doc.validation_status = "VALID" if validation_result.get("valid") else "INVALID"
        doc.processing_status = ProcessingStatus.COMPLETED
        doc.progress = 100
        doc.processed_at = datetime.utcnow()
        
        tamper = TamperingResult(
            case_id=case.id,
            document_id=doc.id,
            tampering_status=tampering_result["tampering_status"],
            confidence=tampering_result["confidence"],
            suspicious_region=tampering_result["suspicious_region"],
            heatmap_path=tampering_result["heatmap_path"],
            noise_residual_path=tampering_result["noise_residual_path"],
            details=tampering_result["details"]
        )
        db.add(tamper)
        
        verifications = [
            ("OCR Extraction", "completed", f"Extracted {len(ocr_data)} fields"),
            ("MRZ Processing", "completed", f"Decoded MRZ: {mrz_result.get('passport_number', 'N/A')}"),
            ("MRZ Checksum", "completed" if checksum_result.get("valid") else "failed", json.dumps(checksum_result.get("details", {}))),
            ("OCR-MRZ Verification", "completed" if ocr_mrz_match.get("match") else "warning", json.dumps(ocr_mrz_match)),
            ("Document Validation", "completed" if validation_result.get("valid") else "warning", json.dumps(validation_result.get("checks", []))),
        ]
        
        for v_name, v_status, v_details in verifications:
            vr = VerificationResult(
                case_id=case.id,
                check_name=v_name,
                status=v_status,
                details=v_details
            )
            db.add(vr)
        
        db.commit()
    
    all_docs = db.query(Document).filter(Document.case_id == case.id).all()
    cross_result = CrossDocumentVerifier.verify([
        {"document_type": d.document_type.value, "ocr_data": json.loads(d.ocr_data)} for d in all_docs
    ])
    
    vr = VerificationResult(
        case_id=case.id,
        check_name="Cross-Document Verification",
        status="completed" if cross_result.get("match") else "warning",
        details=json.dumps(cross_result)
    )
    db.add(vr)
    
    face_result = FaceVerifier.verify("", "", case_type)
    fv = FaceVerification(
        case_id=case.id,
        document_photo_path="storage/uploads/face_doc.jpg",
        live_photo_path="storage/uploads/face_live.jpg",
        similarity_score=face_result["similarity_score"],
        match_status=face_result["match_status"],
        details=face_result["details"]
    )
    db.add(fv)
    
    vr = VerificationResult(
        case_id=case.id,
        check_name="Face Verification",
        status="completed" if face_result["match_status"] == "MATCH" else "warning",
        details=json.dumps(face_result)
    )
    db.add(vr)
    
    tampering_results = db.query(TamperingResult).filter(TamperingResult.case_id == case.id).all()
    latest_tampering = tampering_results[-1].tampering_status if tampering_results else "CLEAN"
    
    risk_result = RiskEngine.assess(
        mrz_checksum_valid=checksum_result.get("valid", True),
        ocr_mrz_match=ocr_mrz_match.get("match", True),
        document_valid=validation_result.get("valid", True),
        cross_doc_match=cross_result.get("match", True),
        tampering_status=latest_tampering,
        face_match=face_result["match_status"] == "MATCH"
    )
    
    ra = RiskAssessment(
        case_id=case.id,
        risk_level=RiskLevel(risk_result["risk_level"]),
        reasons=json.dumps(risk_result["reasons"]),
        score=risk_result["score"]
    )
    db.add(ra)
    
    case.risk_level = RiskLevel(risk_result["risk_level"])
    case.overall_status = "completed"
    
    vr = VerificationResult(
        case_id=case.id,
        check_name="Risk Assessment",
        status="completed",
        details=json.dumps(risk_result)
    )
    db.add(vr)
    
    db.commit()
    
    return {"message": "Processing complete", "risk_level": risk_result["risk_level"]}

@app.post("/api/cases/{case_id}/face-verification")
async def upload_face_photos(
    case_id: int,
    document_photo: UploadFile = File(...),
    live_photo: UploadFile = File(...),
    officer: Officer = Depends(get_current_officer),
    db: Session = Depends(get_db)
):
    case = db.query(PassengerCase).filter(PassengerCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    doc_path = f"storage/uploads/face_doc_{case_id}.jpg"
    live_path = f"storage/uploads/face_live_{case_id}.jpg"
    
    with open(doc_path, "wb") as f:
        shutil.copyfileobj(document_photo.file, f)
    with open(live_path, "wb") as f:
        shutil.copyfileobj(live_photo.file, f)
    
    case_type = "valid"
    if case.risk_level == RiskLevel.HIGH:
        case_type = "high_risk"
    elif case.risk_level == RiskLevel.MEDIUM:
        case_type = "suspicious"
    
    face_result = FaceVerifier.verify(doc_path, live_path, case_type)
    
    existing = db.query(FaceVerification).filter(FaceVerification.case_id == case.id).first()
    if existing:
        existing.document_photo_path = doc_path
        existing.live_photo_path = live_path
        existing.similarity_score = face_result["similarity_score"]
        existing.match_status = face_result["match_status"]
        existing.details = face_result["details"]
    else:
        fv = FaceVerification(
            case_id=case.id,
            document_photo_path=doc_path,
            live_photo_path=live_path,
            similarity_score=face_result["similarity_score"],
            match_status=face_result["match_status"],
            details=face_result["details"]
        )
        db.add(fv)
    
    db.commit()
    return face_result

@app.get("/api/cases/{case_id}", response_model=PassengerCaseDetailResponse)
def get_case_detail(case_id: int, officer: Officer = Depends(get_current_officer), db: Session = Depends(get_db)):
    case = db.query(PassengerCase).filter(PassengerCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

import json

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)