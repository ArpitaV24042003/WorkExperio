# 🚀 WorkExperio

AI-driven student collaboration platform designed to help students build teams, discover project ideas, collaborate in real time, and track project performance.

WorkExperio combines **resume parsing, skill-based team formation, AI-powered project ideation, real-time collaboration, and performance analytics** into a single platform.

---

## 📌 Project Overview

WorkExperio is a collaborative platform that helps students find suitable teammates based on their skills, experience, and interests while providing tools to support the complete project collaboration process.

The platform includes AI-powered features for resume analysis, team formation, project idea generation, and project assistance, along with real-time communication and performance tracking.

---

## ✨ Key Features

### 🔐 Authentication & Profiles

- JWT-based authentication
- Resume-powered profile setup
- Education management
- Experience management
- Skill management
- User profile management

### 🤖 AI-Powered Features

- Resume parsing using `pdfplumber`
- AI-powered project idea generation
- Skill-based team selection
- Performance analytics
- AI assistant chat
- AI-generated project assistance and summaries

### 👥 Projects & Teams

- Manual project creation
- AI-generated project ideas
- Team formation workflows
- Waitlist management
- 7-day solo fallback logic
- Team assignment workflows

### 💬 Real-Time Collaboration

- WebSocket-based project chat
- AI assistant interaction
- Project-level communication
- AI-generated chat summaries
- XP and review system

### 📊 Performance Analytics

- Project performance tracking
- XP-based progress
- Review engine
- Performance-related analytics

---

## 🛠️ Tech Stack

### Backend

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **MongoDB**
- **JWT Authentication**

### Frontend

- **React 19**
- **Vite**
- **Tailwind CSS**
- **Zustand**
- **WebSockets**

### AI

- **OpenAI API**
- **pdfplumber** for resume parsing

### Deployment

- **Render**
- **Vercel**
- PostgreSQL on Render

---

## 📁 Project Structure

```text
WorkExperio/
│
├── ai_service/          # AI service components
│
├── backend/             # FastAPI backend application
│   ├── app/             # Backend application code
│   ├── migrations/      # Database migrations
│   └── tests/           # Backend tests
│
├── chat-interface/      # Chat interface components
│
├── frontend/            # React + Vite + Tailwind frontend
│   ├── public/
│   └── src/
│
├── Website images/      # Project visualization outputs
│
├── .gitignore
├── .gitattributes
├── docker-compose.yml
├── railway.json
├── render.yaml
├── render_build.sh
├── vercel.json
└── README.md
```

---

# 👩‍💻 My Contribution

WorkExperio was developed as a **collaborative team project**, with different members contributing to different parts of the application.

My primary contribution focused on **backend development and application integration**.

## 🔧 Backend Development

I contributed to the backend layer of the application using **Python and FastAPI**.

My backend-related work included:

- Working on backend API development
- Implementing backend application logic
- Working with database connectivity
- Working with SQLAlchemy for database operations
- Contributing to authentication and API workflows
- Supporting communication between backend components and other application services

## 🔗 Application Integration

I also contributed to connecting different components of the application.

This included:

- Connecting the React frontend with FastAPI backend APIs
- Working with API requests and responses
- Supporting frontend–backend data flow
- Connecting backend functionality with database services
- Contributing to integration between application components
- Troubleshooting API and service communication

## 🗄️ Database & Service Connectivity

My contribution also involved working with the application's database and service connections.

This included working with:

- PostgreSQL
- MongoDB
- SQLAlchemy
- Backend database connectivity
- API integration
- WebSocket-based communication

---

# 🔄 Application Workflow

The overall application follows a multi-layer architecture:

```text
                    WorkExperio
                         │
            ┌────────────┴────────────┐
            │                         │
      React Frontend            FastAPI Backend
            │                         │
            │                 ┌───────┴────────┐
            │                 │                │
            │            PostgreSQL         MongoDB
            │
            │
            └──── API / WebSocket Communication
                         │
                    AI Services
                         │
                    OpenAI API
```

---

# ⚙️ Prerequisites

Before running the project locally, make sure the following are installed:

- Python 3.11+
- Node.js 18+
- pip or Poetry
- PostgreSQL
- MongoDB

---

# 🔧 Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create the environment configuration:

```bash
cp env.example .env
```

Configure the required environment variables in `.env`.

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The backend will run locally at:

```text
http://localhost:8000
```

---

# 🗄️ Database Configuration

The development environment uses SQLite by default.

To use PostgreSQL, configure the `DATABASE_URL` environment variable in `.env`.

Example:

```text
postgresql+psycopg2://user:password@localhost:5432/workexperio
```

MongoDB configuration should also be provided through the appropriate environment variables.

---

# 🧪 Running Tests

From the backend directory:

```bash
pytest
```

---

# 💻 Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend communicates with the backend through the configured API URL.

---

# 🔑 Environment Variables

Backend configuration should be stored in:

```text
backend/.env
```

Frontend configuration can be stored in:

```text
frontend/.env
```

Example:

```text
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### ⚠️ Security

Do not commit:

- API keys
- Database passwords
- JWT secrets
- OpenAI credentials
- Production environment variables
- Other sensitive credentials

Use `.env.example` files to document required variables without exposing actual credentials.

---

# 🌐 Deployment

The project includes configuration for deployment using platforms such as **Render** and **Vercel**.

Production deployment requires:

- Production environment variables
- Correct allowed origins
- Production database configuration
- WebSocket configuration
- Correct frontend API URLs
- Secure storage of API keys and credentials

---

# 📸 Project Visualizations

Project screenshots and visualization outputs are available in the:

```text
Website images/
```

folder.

---

# 📚 Technologies & Concepts Demonstrated

### Backend

- Python
- FastAPI
- REST APIs
- SQLAlchemy
- JWT Authentication
- Backend Application Logic

### Databases

- PostgreSQL
- MongoDB
- SQLite
- Database Connectivity

### Frontend

- React
- Vite
- Tailwind CSS
- Zustand
- API Integration

### Real-Time Communication

- WebSockets
- Real-time chat
- Frontend–backend communication

### AI Integration

- OpenAI API
- Resume Parsing
- AI Project Generation
- AI Assistant
- Skill-based Team Matching

### Deployment

- Render
- Vercel
- Environment Configuration
- Production API Configuration

---

# 🤝 Team Project

WorkExperio was developed as a **collaborative team project**, with different team members contributing to different areas of the application.

My primary area of contribution was **backend development and application integration**, including backend APIs, database connectivity, frontend–backend communication, and service integration.

---

## 👩‍💻 Author

**Arpita V**

**Primary Contribution:** Backend Development | API Integration | Database Connectivity | Frontend–Backend Integration

**Technologies:** Python | FastAPI | SQLAlchemy | PostgreSQL | MongoDB | REST APIs | WebSockets
