# Cloud ERA - AI Cloud Services Assistant

A sophisticated AI chatbot application with FastAPI backend and React frontend, specialized for cloud and security assistance using advanced multi-agent architecture with LangGraph workflow orchestration.

## ✨ Features

- **🤖 Multi-Agent AI System**: Advanced LangGraph workflow with 6 specialized agents
- **🔍 Parallel Retrieval**: Simultaneous knowledge base queries and web search
- **👥 Multi-User Support**: Handles up to 10 concurrent users with thread-safe isolation
- **🔐 Secure Authentication**: JWT-based authentication with user management
- **💬 Chat Threading**: Persistent conversation history with reactions
- **🌐 Web Search Integration**: Real-time information from Tavily and JINA AI
- **🗄️ Knowledge Base**: LIGHTRAG integration with Neo4j and FAISS
- **🎨 Theme Support**: Dynamic light/dark mode with theme-aware logos
- **📱 PWA Ready**: Progressive Web App with offline capabilities
- **🐳 Production Ready**: Docker containerization with optimized deployment

## 🏗️ Architecture

### **Project Structure**
```
Cloud ERA/
├── frontend/              # React frontend application
│   ├── src/              # Source code
│   ├── public/           # Static assets  
│   ├── Dockerfile        # Frontend container
│   └── nginx.conf        # Web server config
├── backend/              # FastAPI backend application
│   ├── app/             # Application code
│   ├── data/            # Persistent data storage
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── .env                 # Unified configuration
├── .env.example         # Configuration template
├── docker-compose.yml   # Deployment orchestration
└── README.md           # This file
```

### **Multi-Agent Workflow**
```
User Query → IntentionExtractor → QuestionEnhancer → QuestionDecomposer → ReEvaluator → ParallelRetriever → ResponseGenerator
```

### **Technology Stack**
- **Backend**: FastAPI, SQLAlchemy, LangChain, LangGraph, ChromaDB, LIGHTRAG
- **Frontend**: React 19, TypeScript, Vite, TailwindCSS, CodeMirror  
- **Database**: SQLite, Neo4j, FAISS
- **AI Services**: OpenAI GPT-4, Tavily, JINA AI
- **Deployment**: Docker, Nginx, Docker Compose

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+ and **Docker Compose** v2.0+
- **Git** for version control

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI_Project
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (see Configuration section below)
nano .env
```

### 3. Deploy Application
```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Access Application
- **🌐 Frontend**: http://localhost
- **🔧 Backend API**: http://localhost:8000  
- **📚 API Documentation**: http://localhost:8000/docs
- **🗄️ Neo4j Browser**: http://localhost:7474

## ⚙️ Configuration

### Required Settings
Edit the `.env` file with your configuration:

```bash
# Security (REQUIRED)
BACKEND_SECRET_KEY=your-secure-32-character-secret-key
SHARED_NEO4J_PASSWORD=your-strong-neo4j-password

# AI Services (REQUIRED for full functionality)
SHARED_OPENAI_API_KEY=sk-your-openai-api-key

# Optional Services (Improves responses)
SHARED_TAVILY_API_KEY=tvly-your-tavily-key
SHARED_JINA_API_KEY=jina-your-jina-key

# Deployment (Update for your domain)
FRONTEND_API_BASE_URL=https://your-domain.com/api
```


## 🔧 Development

### Local Development
```bash
# Frontend development
cd frontend
npm install
npm run dev

# Backend development (separate terminal)
cd backend  
pip install -r requirements.txt
python main.py
```

## 📊 Monitoring

### Health Checks
```bash
# Check all services
curl http://localhost/health        # Frontend
curl http://localhost:8000/health   # Backend

# View service status
docker-compose ps

# Monitor logs
docker-compose logs -f [service-name]
```
