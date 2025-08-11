# Cloud ERA Agent Chatbot Backend

FastAPI backend for Cloud ERA - An AI-powered chatbot specialized in cloud services consultation.

## Features

- **User Authentication**: JWT-based registration and login
- **Chat Management**: Multi-threaded conversations with full CRUD operations
- **Message System**: Real-time messaging with reactions and editing capabilities
- **AI Integration**: Domain-specific responses for AWS, Azure, GCP, Security & Networking
- **Language Support**: English and Sinhala language preferences
- **Database**: SQLite with SQLAlchemy ORM for efficient data management

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### **Windows Installation Issues:**
If you encounter bcrypt installation errors on Windows:

```bash
# Option 1: Install Visual C++ Build Tools
# Download and install Microsoft C++ Build Tools
# Then run: pip install -r requirements.txt

# Option 2: Use pre-compiled wheels
pip install --only-binary=all -r requirements.txt

# Option 3: Install dependencies individually
pip install bcrypt==4.0.1
pip install passlib==1.7.4
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
SECRET_KEY=your-super-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here  # Optional
```

### 3. Run the Server

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### 4. API Documentation

Visit these URLs for interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### User Management
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `DELETE /api/users/me` - Delete user account

### Chat Threads
- `GET /api/threads/` - Get user's chat threads
- `POST /api/threads/` - Create new thread
- `GET /api/threads/{thread_id}` - Get specific thread with messages
- `PUT /api/threads/{thread_id}` - Update thread (rename)
- `DELETE /api/threads/{thread_id}` - Delete thread
- `DELETE /api/threads/` - Delete all user threads

### Chat & Messaging
- `POST /api/chat/` - Send message and get AI response
- `GET /api/chat/{thread_id}/messages` - Get thread messages
- `PUT /api/chat/messages/{message_id}` - Edit user message

### Reactions
- `POST /api/reactions/` - Add/update message reaction
- `DELETE /api/reactions/{message_id}` - Remove message reaction

## Testing

### Manual Testing with curl

1. **Register a user:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'
```

2. **Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

3. **Send a chat message:**
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"message": "Help me set up an AWS EC2 instance"}'
```

### Using the API Documentation

1. Go to http://localhost:8000/docs
2. Click "Authorize" and enter your JWT token
3. Test any endpoint directly from the browser

## Database

The application uses SQLite by default. The database file `cloud_era.db` will be created automatically in the backend directory.

### Database Schema:
- **Users**: User accounts and preferences
- **ChatThreads**: Conversation threads
- **Messages**: Individual messages with reactions

## AI Integration

The system includes domain-specific AI responses for:
- AWS services and troubleshooting
- Azure platform guidance  
- Google Cloud Platform help
- Security and compliance best practices
- Network configuration assistance

If no OpenAI API key is provided, the system will use fallback responses with helpful guidance.

## Development

### Project Structure:
```
backend/
├── app/
│   ├── core/          # Core utilities (auth, config, security)
│   ├── database/      # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── routers/       # API route handlers
│   └── schemas/       # Pydantic models for validation
├── main.py            # FastAPI application entry point
└── requirements.txt   # Python dependencies
```

### Adding New Features:
1. Create new models in `app/models/`
2. Add Pydantic schemas in `app/schemas/`
3. Implement routes in `app/routers/`
4. Register routes in `main.py`

## Production Deployment

1. Set strong `SECRET_KEY` in environment
2. Configure proper database (PostgreSQL recommended)
3. Set up proper CORS origins
4. Use a production ASGI server like Gunicorn with Uvicorn workers
5. Configure HTTPS/SSL termination
6. Set up proper logging and monitoring