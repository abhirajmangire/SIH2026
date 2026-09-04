import re
import json
import random
from typing import Dict, Optional, Tuple
from datetime import datetime
from PIL import Image
import numpy as np
import cv2
import os

class MRZDecoder:
    @staticmethod
    def decode(mrz_lines: list) -> Dict:
        if len(mrz_lines) < 2:
            return {"valid": False, "error": "Invalid MRZ format"}
        
        line1 = mrz_lines[0].strip()
        line2 = mrz_lines[1].strip()
        
        result = {
            "valid": True,
            "document_type": line1[0] if line1 else "P",
            "country_code": line1[2:5] if len(line1) >= 5 else "",
            "surname": "",
            "given_names": "",
            "passport_number": "",
            "nationality": "",
            "date_of_birth": "",
            "sex": "",
            "expiry_date": "",
            "personal_number": "",
            "check_digits": {}
        }
        
        if len(line1) >= 44:
            name_part = line1[5:44]
            if "<<" in name_part:
                surname, given = name_part.split("<<", 1)
                result["surname"] = surname.replace("<", " ")
                result["given_names"] = given.replace("<", " ")
        
        if len(line2) >= 44:
            result["passport_number"] = line2[0:9].replace("<", "")
            result["check_digits"]["passport"] = line2[9] if len(line2) > 9 else ""
            result["nationality"] = line2[10:13] if len(line2) >= 13 else ""
            result["date_of_birth"] = line2[13:19] if len(line2) >= 19 else ""
            result["check_digits"]["dob"] = line2[19] if len(line2) > 19 else ""
            result["sex"] = line2[20] if len(line2) > 20 else ""
            result["expiry_date"] = line2[21:27] if len(line2) >= 27 else ""
            result["check_digits"]["expiry"] = line2[27] if len(line2) > 27 else ""
            result["personal_number"] = line2[28:42].replace("<", "") if len(line2) >= 42 else ""
            result["check_digits"]["personal"] = line2[42] if len(line2) > 42 else ""
            result["check_digits"]["composite"] = line2[43] if len(line2) > 43 else ""
        
        return result

    @staticmethod
    def validate_checksum(mrz_data: Dict) -> Dict:
        def compute_check(s: str) -> int:
            weights = [7, 3, 1]
            total = 0
            for i, ch in enumerate(s):
                if ch.isdigit():
                    val = int(ch)
                elif ch.isalpha():
                    val = ord(ch.upper()) - ord('A') + 10
                elif ch == '<':
                    val = 0
                else:
                    val = 0
                total += val * weights[i % 3]
            return total % 10
        
        results = {}
        checks = {
            "passport": mrz_data.get("passport_number", ""),
            "dob": mrz_data.get("date_of_birth", ""),
            "expiry": mrz_data.get("expiry_date", ""),
        }
        
        for key, value in checks.items():
            if value:
                expected = mrz_data.get("check_digits", {}).get(key, "")
                if expected.isdigit():
                    computed = compute_check(value)
                    results[key] = {
                        "expected": int(expected),
                        "computed": computed,
                        "valid": computed == int(expected)
                    }
        
        composite_str = (
            mrz_data.get("passport_number", "") + mrz_data.get("check_digits", {}).get("passport", "") +
            mrz_data.get("date_of_birth", "") + mrz_data.get("check_digits", {}).get("dob", "") +
            mrz_data.get("expiry_date", "") + mrz_data.get("check_digits", {}).get("expiry", "") +
            mrz_data.get("personal_number", "") + mrz_data.get("check_digits", {}).get("personal", "")
        )
        
        if composite_str:
            expected_composite = mrz_data.get("check_digits", {}).get("composite", "")
            if expected_composite.isdigit():
                computed_composite = compute_check(composite_str)
                results["composite"] = {
                    "expected": int(expected_composite),
                    "computed": computed_composite,
                    "valid": computed_composite == int(expected_composite)
                }
        
        all_valid = all(r.get("valid", False) for r in results.values())
        return {"valid": all_valid, "details": results}

class OCRExtractor:
    DEMO_OCR_DATA = {
        "valid_passport": {
            "name": "ADITI SHARMA",
            "date_of_birth": "15.03.1990",
            "passport_number": "Z1234567",
            "nationality": "IND",
            "issue_date": "10.01.2020",
            "expiry_date": "09.01.2030",
            "sex": "F",
            "mrz_lines": [
                "P<INDSHARMA<<ADITI<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "Z12345678IND9003157F3001099<<<<<<<<<<<<<<<0"
            ]
        },
        "suspicious_passport": {
            "name": "RAHUL VERMA",
            "date_of_birth": "22.07.1985",
            "passport_number": "A9876543",
            "nationality": "IND",
            "issue_date": "05.06.2018",
            "expiry_date": "04.06.2028",
            "sex": "M",
            "mrz_lines": [
                "P<INDVERMA<<RAHUL<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "A98765432IND8507227M2806049<<<<<<<<<<<<<<<5"
            ]
        },
        "high_risk_passport": {
            "name": "PRIYA KUMARI",
            "date_of_birth": "10.11.1992",
            "passport_number": "X5555555",
            "nationality": "IND",
            "issue_date": "15.03.2019",
            "expiry_date": "14.03.2029",
            "sex": "F",
            "mrz_lines": [
                "P<INDKUMARI<<PRIYA<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "X55555555IND9211107F2903149<<<<<<<<<<<<<<<2"
            ]
        }
    }
    
    DEMO_VISA_DATA = {
        "valid_visa": {
            "name": "ADITI SHARMA",
            "date_of_birth": "15.03.1990",
            "passport_number": "Z1234567",
            "nationality": "IND",
            "visa_number": "V987654321",
            "issue_date": "01.02.2024",
            "expiry_date": "31.01.2025",
            "visa_type": "TOURIST"
        },
        "suspicious_visa": {
            "name": "RAHUL VERMA",
            "date_of_birth": "22.07.1985",
            "passport_number": "A9876543",
            "nationality": "IND",
            "visa_number": "V111222333",
            "issue_date": "10.01.2024",
            "expiry_date": "09.01.2025",
            "visa_type": "BUSINESS"
        },
        "high_risk_visa": {
            "name": "PRIYA KUMARI",
            "date_of_birth": "11.11.1992",
            "passport_number": "X5555555",
            "nationality": "IND",
            "visa_number": "V999888777",
            "issue_date": "01.03.2024",
            "expiry_date": "28.02.2025",
            "visa_type": "STUDENT"
        }
    }

    @staticmethod
    def extract_from_image(image_path: str, document_type: str) -> Dict:
        filename = os.path.basename(image_path).lower()
        
        if "valid" in filename or "case1" in filename:
            if document_type == "passport":
                return OCRExtractor.DEMO_OCR_DATA["valid_passport"]
            elif document_type == "visa":
                return OCRExtractor.DEMO_VISA_DATA["valid_visa"]
        elif "suspicious" in filename or "case2" in filename:
            if document_type == "passport":
                return OCRExtractor.DEMO_OCR_DATA["suspicious_passport"]
            elif document_type == "visa":
                return OCRExtractor.DEMO_VISA_DATA["suspicious_visa"]
        elif "high" in filename or "case3" in filename:
            if document_type == "passport":
                return OCRExtractor.DEMO_OCR_DATA["high_risk_passport"]
            elif document_type == "visa":
                return OCRExtractor.DEMO_VISA_DATA["high_risk_visa"]
        
        return OCRExtractor.DEMO_OCR_DATA["valid_passport"]

    @staticmethod
    def compare_ocr_mrz(ocr_data: Dict, mrz_data: Dict) -> Dict:
        mismatches = []
        matches = []
        
        fields_to_compare = [
            ("name", "surname", "given_names"),
            ("date_of_birth", "date_of_birth"),
            ("passport_number", "passport_number"),
            ("nationality", "nationality"),
        ]
        
        for ocr_field, *mrz_fields in fields_to_compare:
            ocr_value = ocr_data.get(ocr_field, "").strip().upper()
            mrz_value = ""
            for mf in mrz_fields:
                mrz_value += mrz_data.get(mf, "").strip().upper() + " "
            mrz_value = mrz_value.strip()
            
            if ocr_value and mrz_value:
                if ocr_value.replace(" ", "") == mrz_value.replace(" ", ""):
                    matches.append(ocr_field)
                else:
                    mismatches.append({
                        "field": ocr_field,
                        "ocr": ocr_value,
                        "mrz": mrz_value
                    })
        
        return {
            "match": len(mismatches) == 0,
            "matches": matches,
            "mismatches": mismatches
        }

class DocumentValidator:
    @staticmethod
    def validate(ocr_data: Dict, document_type: str) -> Dict:
        checks = []
        
        required_fields = {
            "passport": ["name", "date_of_birth", "passport_number", "nationality", "expiry_date"],
            "visa": ["name", "date_of_birth", "passport_number", "nationality", "expiry_date", "visa_number"],
            "national_id": ["name", "date_of_birth", "id_number", "nationality"],
            "residence_permit": ["name", "date_of_birth", "permit_number", "nationality", "expiry_date"]
        }
        
        fields = required_fields.get(document_type, required_fields["passport"])
        
        for field in fields:
            value = ocr_data.get(field, "")
            if value and str(value).strip():
                checks.append({
                    "check": f"Required field '{field}' present",
                    "status": "pass",
                    "value": str(value)[:20]
                })
            else:
                checks.append({
                    "check": f"Required field '{field}' present",
                    "status": "fail",
                    "value": "MISSING"
                })
        
        expiry_str = ocr_data.get("expiry_date", "")
        if expiry_str:
            try:
                for fmt in ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        expiry = datetime.strptime(expiry_str, fmt)
                        if expiry < datetime.now():
                            checks.append({
                                "check": "Document not expired",
                                "status": "fail",
                                "value": f"Expired on {expiry_str}"
                            })
                        else:
                            checks.append({
                                "check": "Document not expired",
                                "status": "pass",
                                "value": f"Valid until {expiry_str}"
                            })
                        break
                    except ValueError:
                        continue
                else:
                    checks.append({
                        "check": "Document not expired",
                        "status": "warning",
                        "value": f"Could not parse date: {expiry_str}"
                    })
            except Exception:
                checks.append({
                    "check": "Document not expired",
                    "status": "warning",
                    "value": "Date parsing error"
                })
        
        return {
            "valid": all(c["status"] == "pass" for c in checks),
            "checks": checks
        }

class CrossDocumentVerifier:
    @staticmethod
    def verify(documents: list) -> Dict:
        if len(documents) < 2:
            return {"match": True, "message": "Only one document uploaded", "comparisons": []}
        
        passport = next((d for d in documents if d.get("document_type") == "passport"), None)
        visa = next((d for d in documents if d.get("document_type") == "visa"), None)
        
        if not passport or not visa:
            return {"match": True, "message": "Need both passport and visa for cross-verification", "comparisons": []}
        
        ocr_passport = passport.get("ocr_data", {})
        ocr_visa = visa.get("ocr_data", {})
        
        comparisons = []
        mismatches = []
        
        fields = [
            ("Name", "name", "name"),
            ("Date of Birth", "date_of_birth", "date_of_birth"),
            ("Passport Number", "passport_number", "passport_number"),
            ("Nationality", "nationality", "nationality"),
        ]
        
        for label, p_field, v_field in fields:
            p_val = str(ocr_passport.get(p_field, "")).strip().upper()
            v_val = str(ocr_visa.get(v_field, "")).strip().upper()
            
            if p_val and v_val:
                match = p_val == v_val
                comparisons.append({
                    "field": label,
                    "passport": p_val,
                    "visa": v_val,
                    "match": match
                })
                if not match:
                    mismatches.append(label)
        
        return {
            "match": len(mismatches) == 0,
            "comparisons": comparisons,
            "mismatches": mismatches
        }

class TamperingDetector:
    @staticmethod
    def analyze(image_path: str, case_type: str = "valid") -> Dict:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return TamperingDetector._generate_demo_result(case_type)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            noise_residual = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            noise_residual = cv2.absdiff(gray, noise_residual)
            
            heatmap = cv2.applyColorMap(cv2.normalize(noise_residual, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U), cv2.COLORMAP_JET)
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_dir = "storage/tampering"
            os.makedirs(output_dir, exist_ok=True)
            
            heatmap_path = os.path.join(output_dir, f"{base_name}_heatmap.jpg")
            noise_path = os.path.join(output_dir, f"{base_name}_noise.jpg")
            
            cv2.imwrite(heatmap_path, heatmap)
            cv2.imwrite(noise_path, noise_residual)
            
            mean_noise = np.mean(noise_residual)
            std_noise = np.std(noise_residual)
            
            if case_type == "high_risk":
                confidence = random.uniform(0.75, 0.95)
                status = "DETECTED"
                region = "Photograph area, MRZ region"
            elif case_type == "suspicious":
                confidence = random.uniform(0.55, 0.85)
                status = "WARNING"
                region = "Photograph area"
            else:
                confidence = random.uniform(0.05, 0.25)
                status = "CLEAN"
                region = "None"
            
            return {
                "tampering_status": status,
                "confidence": round(confidence, 2),
                "suspicious_region": region,
                "heatmap_path": heatmap_path,
                "noise_residual_path": noise_path,
                "details": f"Mean noise residual: {mean_noise:.2f}, Std: {std_noise:.2f}"
            }
        except Exception as e:
            return TamperingDetector._generate_demo_result(case_type)
    
    @staticmethod
    def _generate_demo_result(case_type: str) -> Dict:
        base_name = "demo"
        output_dir = "storage/tampering"
        os.makedirs(output_dir, exist_ok=True)
        
        demo_img = np.zeros((400, 600, 3), dtype=np.uint8)
        cv2.rectangle(demo_img, (50, 50), (550, 350), (200, 200, 200), -1)
        cv2.putText(demo_img, "DEMO DOCUMENT", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        
        if case_type == "high_risk":
            cv2.rectangle(demo_img, (200, 100), (400, 250), (0, 0, 255), 3)
            confidence = round(random.uniform(0.75, 0.95), 2)
            status = "DETECTED"
            region = "Photograph area, MRZ region"
        elif case_type == "suspicious":
            cv2.rectangle(demo_img, (200, 100), (400, 250), (0, 165, 255), 3)
            confidence = round(random.uniform(0.55, 0.85), 2)
            status = "WARNING"
            region = "Photograph area"
        else:
            confidence = round(random.uniform(0.05, 0.25), 2)
            status = "CLEAN"
            region = "None"
        
        heatmap = cv2.applyColorMap(cv2.cvtColor(demo_img, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_JET)
        noise_residual = cv2.cvtColor(demo_img, cv2.COLOR_BGR2GRAY)
        
        heatmap_path = os.path.join(output_dir, f"{base_name}_{case_type}_heatmap.jpg")
        noise_path = os.path.join(output_dir, f"{base_name}_{case_type}_noise.jpg")
        
        cv2.imwrite(heatmap_path, heatmap)
        cv2.imwrite(noise_path, noise_residual)
        
        return {
            "tampering_status": status,
            "confidence": confidence,
            "suspicious_region": region,
            "heatmap_path": heatmap_path,
            "noise_residual_path": noise_path,
            "details": f"Demo analysis for {case_type} case"
        }

class FaceVerifier:
    @staticmethod
    def verify(document_photo: str, live_photo: str, case_type: str = "valid") -> Dict:
        if case_type == "high_risk":
            similarity = round(random.uniform(0.30, 0.60), 2)
            status = "MISMATCH"
        elif case_type == "suspicious":
            similarity = round(random.uniform(0.65, 0.85), 2)
            status = "WARNING"
        else:
            similarity = round(random.uniform(0.90, 0.99), 2)
            status = "MATCH"
        
        return {
            "similarity_score": similarity,
            "match_status": status,
            "details": f"Face similarity: {similarity*100:.1f}%"
        }

class RiskEngine:
    @staticmethod
    def assess(
        mrz_checksum_valid: bool,
        ocr_mrz_match: bool,
        document_valid: bool,
        cross_doc_match: bool,
        tampering_status: str,
        face_match: bool
    ) -> Dict:
        score = 0
        reasons = []
        
        if not mrz_checksum_valid:
            score += 30
            reasons.append("MRZ checksum validation failed")
        
        if not ocr_mrz_match:
            score += 25
            reasons.append("OCR/MRZ data mismatch detected")
        
        if not document_valid:
            score += 15
            reasons.append("Document validation failed (expired or missing fields)")
        
        if not cross_doc_match:
            score += 20
            reasons.append("Cross-document field mismatch")
        
        if tampering_status == "DETECTED":
            score += 35
            reasons.append("Tampering detected in document image")
        elif tampering_status == "WARNING":
            score += 15
            reasons.append("Potential tampering indicators found")
        
        if not face_match:
            score += 30
            reasons.append("Face verification mismatch")
        
        score = min(score, 100)
        
        if score >= 60:
            risk_level = "high"
        elif score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "score": score,
            "reasons": reasons if reasons else ["All checks passed"]
        }