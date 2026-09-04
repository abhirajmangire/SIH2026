# SIH 2026 - AI-Based Fake Identity & Document Screening System

**Problem Statement ID: 26188**

A presentation-ready prototype demonstrating an AI-based system for screening fake identities and documents at immigration checkpoints.

## 🎯 Project Overview

This prototype demonstrates the complete workflow for document verification, including:
- **OCR Extraction** - Text extraction from passport, visa, and ID documents
- **MRZ Processing** - Machine Readable Zone decoding and checksum validation
- **Cross-Document Verification** - Field comparison across multiple documents
- **Tampering Detection** - Image forensics with heatmap visualization
- **Face Verification** - Biometric face matching
- **Risk Assessment** - Rule-based risk scoring (LOW/MEDIUM/HIGH)

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** - [Download](https://python.org)
- **Node.js 18+** - [Download](https://nodejs.org)

### One-Command Startup

**Windows (Command Prompt):**
```cmd
start.bat
```

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Manual Start:**
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Demo Credentials
```
Officer ID: OFFICER001
Password:   SecurePass123!
```

## 📁 Project Structure

```
sih2026-proto/
├── backend/                 # FastAPI Backend
│   ├── main.py             # API routes & server
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── database.py         # SQLite configuration
│   ├── auth.py             # JWT authentication
│   ├── services/
│   │   └── verification.py # Core verification logic
│   ├── requirements.txt    # Python dependencies
│   ├── create_demo_images.py
│   └── storage/            # Uploaded files & generated images
├── frontend/               # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx         # Main app with routing
│   │   ├── main.jsx        # Entry point
│   │   ├── index.css       # Complete styling
│   │   ├── api.js          # API client
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── Dashboard.jsx
│   │       └── CaseDetail.jsx
│   ├── index.html
│   └── package.json
├── demo_data/              # Demo case data
├── storage/                # Shared storage
├── start.bat               # Windows batch startup
├── start.ps1               # PowerShell startup
└── README.md
```

## 🎬 Demo Flow (3-5 minutes)

### 1. Officer Login
- Enter demo credentials
- JWT-based authentication

### 2. Dashboard Overview
- Statistics cards (screened, verified, valid, suspicious, high-risk)
- Risk distribution (LOW/MEDIUM/HIGH)
- Passenger history table with 3 demo cases

### 3. Select Demo Passenger
Click one of three demo buttons:
- **✓ Valid Passenger** (Aditi Sharma) - LOW risk
- **⚠ Suspicious Document** (Rahul Verma) - MEDIUM risk
- **🔴 High-Risk Passenger** (Priya Kumari) - HIGH risk

### 4. Case Detail View - Complete Verification Pipeline

**Processing Timeline:**
```
✓ OCR Extraction
✓ MRZ Processing
✓ MRZ Checksum
✓ OCR ↔ MRZ Verification
✓ Document Validation
✓ Cross-Document Verification
✓ Tampering Detection
✓ Face Verification
✓ Risk Assessment
```

**MRZ Analysis Card:**
- Decoded MRZ lines
- Field extraction (name, DOB, passport#, nationality, etc.)
- Checksum validation results (PASS/FAIL)

**Cross-Document Verification:**
- Passport ↔ Visa field comparison
- Mismatch highlighting with explanations

**Tampering Detection (KEY FEATURE):**
- Three-panel visualization:
  1. Original RGB Document
  2. Tamper Heatmap
  3. Noise Residual Analysis
- Confidence score & suspicious region identification

**Face Verification:**
- Side-by-side document photo vs live photo
- Similarity percentage with match status

**Risk Assessment:**
- Visual risk meter (0-100)
- Detailed reason breakdown
- Final risk level: LOW / MEDIUM / HIGH

## 🎨 Design System

### Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Deep Navy | #0B1F3A | Headers, primary text |
| Royal Blue | #1769E0 | Primary actions, links |
| Cyan | #00A8E8 | Accent, technical data |
| Green | #16A34A | Success, LOW risk |
| Amber | #F59E0B | Warning, MEDIUM risk |
| Red | #DC2626 | Error, HIGH risk |
| Background | #F5F8FC | Page background |
| White | #FFFFFF | Cards, surfaces |

### UI Principles
- Government × Aviation Security × AI Forensics aesthetic
- Clean cards, professional typography
- Status badges, progress bars, tables
- Subtle animations, no gaming/cartoon effects

## 🔧 Technical Architecture

### Backend (FastAPI)
- **Framework:** FastAPI 0.109
- **Database:** SQLite (local, no setup required)
- **Auth:** JWT with bcrypt password hashing
- **Image Processing:** OpenCV for tampering detection
- **Verification Services:** Modular, extensible design

### Frontend (React + Vite)
- **Framework:** React 18 with React Router
- **Styling:** Custom CSS with CSS Variables
- **State:** React Context + Hooks
- **API:** Fetch-based client with error handling

### Demo Data
Three pre-configured cases with synthetic data:
1. **CASE-2026-001** - Aditi Sharma (Valid)
2. **CASE-2026-002** - Rahul Verma (Suspicious)
3. **CASE-2026-003** - Priya Kumari (High-Risk)

All data is synthetic - no real government data used.

## 🎯 SIH Presentation Features

### Demo Mode
One-click demo case selection:
- Instantly loads pre-processed results
- No internet required during presentation
- Reliable, consistent demonstrations

### Key Innovation Highlights
1. **Tampering Detection** - Real image forensics (noise residual + heatmap)
2. **MRZ Checksum Validation** - ICAO standard compliance
3. **Cross-Document Correlation** - Multi-document consistency
4. **Explainable AI** - Clear reasons for every risk decision

## 🛠 Development

### Backend Development
```bash
cd backend
venv\Scripts\activate
python main.py
# Server runs on http://localhost:8000
# Auto-reload enabled
```

### Frontend Development
```bash
cd frontend
npm run dev
# Server runs on http://localhost:5173
# Hot module replacement enabled
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Officer authentication |
| GET | /api/dashboard/stats | Dashboard statistics |
| GET | /api/dashboard/cases | List all cases |
| POST | /api/cases | Create new case |
| GET | /api/cases/{id} | Case detail with all verifications |
| POST | /api/cases/{id}/documents | Upload document |
| POST | /api/cases/{id}/process | Run full verification |
| POST | /api/cases/{id}/face-verification | Upload face photos |

## ⚠️ Important Notes

### Prototype Limitations
- **Not production-grade** - Built for SIH presentation
- **Simulated OCR** - Uses predefined results for reliability
- **Demo face verification** - Synthetic similarity scores
- **SQLite only** - No PostgreSQL required
- **No GPU required** - Runs on standard laptop

### Reliability First
- All ML components have fallback implementations
- Demo cases pre-loaded and pre-processed
- Works completely offline
- No external API dependencies

### Extensibility
The codebase is structured for future enhancement:
- Swap OCR engine (PaddleOCR, Tesseract)
- Integrate real face recognition (FaceNet, ArcFace)
- Add production ML models for tampering
- Connect to real databases

## 📋 Requirements Checklist

✅ Single-command startup (`start.bat` / `start.ps1`)  
✅ Three screens: Login, Dashboard, Case Detail  
✅ Officer login with demo credentials  
✅ Document upload (Passport, Visa, National ID, Residence Permit)  
✅ Processing queue with progress/status  
✅ Dashboard statistics & risk distribution  
✅ Passenger history table  
✅ Complete verification timeline  
✅ OCR demo with field extraction  
✅ MRZ decoding & checksum validation  
✅ OCR ↔ MRZ comparison  
✅ Document validation (expiry, format, consistency)  
✅ Cross-document verification  
✅ Tampering detection with 3-panel visualization  
✅ Face verification with similarity score  
✅ Rule-based risk assessment (LOW/MEDIUM/HIGH)  
✅ 3 demo cases (Valid, Suspicious, High-Risk)  
✅ Demo mode for presentation  
✅ Professional government/aviation/AI design  
✅ Simple architecture (React + FastAPI + SQLite)  
✅ No Docker, no cloud, no GPU required  
✅ Runs on student laptop  
✅ Complete 3-5 minute demo flow  

## 👥 Team

Built for **SIH 2026** - Smart India Hackathon  
Problem Statement: **26188** - AI-Based Fake Identity & Document Screening System

## 📄 License

Prototype for SIH 2026 presentation purposes only.