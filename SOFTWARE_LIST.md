# WorkExperio - Software and Dependencies List

This document lists all software, frameworks, libraries, and tools used in the WorkExperio project for academic submission.

---

## 1. CORE RUNTIME SOFTWARE

### 1.1 Python Environment
- **Python 3.11.0** (or Python 3.11+)
- pip (Python package installer)
- venv (Python virtual environment)

### 1.2 Node.js Environment
- **Node.js 18+** (JavaScript runtime)
- **npm** (Node Package Manager)

---

## 2. DATABASE SOFTWARE

### 2.1 PostgreSQL
- **PostgreSQL 15** (Primary relational database)
- **psycopg[binary] 3.2.12** (PostgreSQL adapter for Python)

### 2.2 MongoDB
- **MongoDB 7** (NoSQL database for resume parsing and document storage)
- **pymongo** (MongoDB driver for Python)

### 2.3 SQLite (Development)
- SQLite (Lightweight database for local development)

---

## 3. BACKEND FRAMEWORK & LIBRARIES

### 3.1 Core Framework
- **FastAPI 0.114.2** (Modern Python web framework)
- **Uvicorn 0.30.6** (ASGI server)
- **Starlette** (Lightweight ASGI framework)
- **Gunicorn** (WSGI HTTP Server for production)

### 3.2 Database ORM & Migrations
- **SQLAlchemy 2.0.36** (Python SQL toolkit and ORM)
- **Alembic 1.13.3** (Database migration tool)

### 3.3 Authentication & Security
- **bcrypt 4.2.0** (Password hashing)
- **passlib[bcrypt] 1.7.4** (Password hashing library)
- **python-jose 3.3.0** (JWT implementation)
- **cryptography** (Cryptographic library)

### 3.4 Data Validation & Serialization
- **Pydantic 2.9.2** (Data validation using Python type annotations)
- **Pydantic-settings 2.5.2** (Settings management)

### 3.5 File Processing
- **python-multipart 0.0.9** (File upload handling)
- **pdfplumber 0.11.4** (PDF parsing library)
- **aiofiles 24.1.0** (Async file operations)

### 3.6 HTTP & Networking
- **httpx 0.27.2** (Async HTTP client)
- **websockets 13.1** (WebSocket support)
- **wsproto 1.2.0** (WebSocket protocol implementation)

### 3.7 AI & Machine Learning
- **OpenAI 1.57.3** (OpenAI API client)
- **pandas** (Data manipulation and analysis)
- **numpy** (Numerical computing)
- **scikit-learn** (Machine learning library)
- **spacy** (Natural language processing)

### 3.8 Utilities
- **python-dateutil 2.9.0.post0** (Date utilities)
- **python-dotenv** (Environment variable management)
- **pytest 8.3.3** (Testing framework)
- **pytest-asyncio 0.24.0** (Async testing support)

---

## 4. FRONTEND FRAMEWORK & LIBRARIES

### 4.1 Core Framework
- **React 19.1.1** (JavaScript UI library)
- **React DOM 19.1.1** (React renderer)
- **Vite 7.1.0** (Build tool and dev server)

### 4.2 Routing
- **React Router DOM 7.8.0** (Client-side routing)

### 4.3 UI Components & Styling
- **Tailwind CSS 3.4.17** (Utility-first CSS framework)
- **tailwindcss-animate 1.0.7** (Animation utilities)
- **tailwind-merge 2.5.4** (Tailwind class merging)
- **@radix-ui/react-slot 1.1.2** (UI component primitives)
- **lucide-react 0.539.0** (Icon library)
- **class-variance-authority 0.7.0** (Component variants)
- **clsx 2.1.1** (Conditional class names)

### 4.4 State Management
- **Zustand 5.0.1** (Lightweight state management)

### 4.5 HTTP Client
- **Axios 1.7.9** (HTTP client library)

### 4.6 Data Visualization
- **Recharts 2.13.0** (Charting library)

### 4.7 Content Rendering
- **react-markdown 9.0.1** (Markdown renderer)

### 4.8 Development Tools
- **ESLint 9.32.0** (JavaScript linter)
- **Prettier 3.3.3** (Code formatter)
- **PostCSS 8.5.6** (CSS processing)
- **Autoprefixer 10.4.21** (CSS vendor prefixing)
- **@vitejs/plugin-react 4.7.0** (Vite React plugin)

---

## 5. CONTAINERIZATION & DEPLOYMENT

### 5.1 Docker
- **Docker** (Containerization platform)
- **Docker Compose** (Multi-container Docker applications)

### 5.2 Container Images Used
- **python:3.11-slim** (Python base image)
- **node:18-alpine** (Node.js base image)
- **nginx:alpine** (Web server for frontend)
- **postgres:15-alpine** (PostgreSQL database)
- **mongo:7** (MongoDB database)

---

## 6. DEVELOPMENT TOOLS

### 6.1 Version Control
- **Git** (Version control system)

### 6.2 Code Quality
- **ESLint** (JavaScript/TypeScript linter)
- **Prettier** (Code formatter)

### 6.3 Build Tools
- **Vite** (Frontend build tool)
- **npm** (Package manager)

---

## 7. DEPLOYMENT PLATFORMS (Optional - for reference)

- **Render** (Cloud hosting platform)
- **Vercel** (Frontend deployment - if used)

---

## 8. SYSTEM REQUIREMENTS

### 8.1 Operating System
- Windows 10/11, Linux, or macOS

### 8.2 Minimum System Requirements
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **Processor:** Multi-core processor recommended

---

## 9. INSTALLATION INSTRUCTIONS FOR DVD

### 9.1 Python Setup
1. Install Python 3.11.0 from python.org
2. Verify installation: `python --version`
3. Install pip (usually included with Python)

### 9.2 Node.js Setup
1. Install Node.js 18+ from nodejs.org
2. Verify installation: `node --version` and `npm --version`

### 9.3 PostgreSQL Setup
1. Install PostgreSQL 15 from postgresql.org
2. Set up database user and password
3. Create database: `workexperio`

### 9.4 MongoDB Setup (Optional)
1. Install MongoDB 7 from mongodb.com
2. Start MongoDB service

### 9.5 Docker Setup (Optional - for containerized deployment)
1. Install Docker Desktop from docker.com
2. Install Docker Compose (usually included)

---

## 10. PROJECT DEPENDENCIES INSTALLATION

### 10.1 Backend Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 10.2 Frontend Dependencies
```bash
cd frontend
npm install
```

### 10.3 AI Service Dependencies
```bash
cd ai_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 11. SOFTWARE VERSIONS SUMMARY

| Category | Software | Version |
|----------|----------|---------|
| Runtime | Python | 3.11.0+ |
| Runtime | Node.js | 18+ |
| Database | PostgreSQL | 15 |
| Database | MongoDB | 7 |
| Backend Framework | FastAPI | 0.114.2 |
| Backend Server | Uvicorn | 0.30.6 |
| Frontend Framework | React | 19.1.1 |
| Frontend Build Tool | Vite | 7.1.0 |
| CSS Framework | Tailwind CSS | 3.4.17 |
| Container | Docker | Latest |
| Container | Docker Compose | Latest |

---

## 12. ADDITIONAL NOTES

- All Python dependencies are listed in `backend/requirements.txt` and `ai_service/requirements.txt`
- All Node.js dependencies are listed in `frontend/package.json` and `package-lock.json`
- Docker configurations are in `docker-compose.yml` and individual `Dockerfile` files
- Environment variables are configured in `.env` files (see `backend/env.example`)

---

## 13. DVD CONTENTS CHECKLIST

- [ ] Complete project source code
- [ ] All dependency files (requirements.txt, package.json, package-lock.json)
- [ ] Python 3.11 installer (or installer link/documentation)
- [ ] Node.js 18+ installer (or installer link/documentation)
- [ ] PostgreSQL 15 installer (or installer link/documentation)
- [ ] MongoDB 7 installer (or installer link/documentation) - Optional
- [ ] Docker Desktop installer (or installer link/documentation) - Optional
- [ ] Project documentation (README.md, this file)
- [ ] Project report PDF
- [ ] Setup instructions
- [ ] Environment variable templates (.env.example files)

---

**Note:** For IoT projects, also include hardware components list and setup instructions in a separate document.

---

*Generated for WorkExperio Project Submission*
*Date: [Current Date]*

