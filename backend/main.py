from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.database.database import engine, Base, SessionLocal
from app.routers import auth, threads, chat, reactions, users, posts, categories, website_admin
from app.models import user, chat_thread, message, user_reaction_log, post  # Import models to register them
from app.models.user import User
from app.models.chat_thread import ChatThread, ThreadType
from app.models.message import Message, MessageAuthor
from app.core.security import get_password_hash
import uuid
import logging
import sys
from typing import Callable


def initialize_sample_data():
    """Initialize sample data on first run"""
    print("Checking sample data...")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Sample data already exists ({existing_users} users)")
            return
        
        print("Creating sample user and default threads...")
        
        # Create sample user
        sample_user = User(
            id=uuid.uuid4(),
            username="manelka",
            email="manelka@cloud.com",
            password_hash=get_password_hash("manelka1234"),
            preferred_language="ENG",
            theme="light"
        )
        db.add(sample_user)
        db.commit()
        db.refresh(sample_user)
        
        print(f"Created user: {sample_user.username}")
        
        # Create permanent threads for each type
        thread_configs = {
            ThreadType.AWS_DISCUSSION: {
                "name": "AWS Discussion",
                "welcome": "Welcome to AWS Discussion! I'm here to help you with Amazon Web Services including EC2, S3, Lambda, RDS, VPC, and all other AWS services. What AWS topic would you like to explore today?"
            },
            ThreadType.AZURE_DISCUSSION: {
                "name": "Azure Discussion", 
                "welcome": "Welcome to Azure Discussion! I can assist you with Microsoft Azure services including Virtual Machines, Storage, App Services, SQL Database, and more. How can I help with your Azure journey?"
            },
            ThreadType.SMART_LEARNER: {
                "name": "Smart Learner",
                "welcome": "Welcome to Smart Learner! I'm your guide for learning cloud technologies, best practices, architecture patterns, and staying updated with the latest trends. What would you like to learn today?"
            }
        }
        
        for thread_type, config in thread_configs.items():
            # Create thread
            thread = ChatThread(
                id=uuid.uuid4(),
                user_id=sample_user.id,
                name=config['name'],
                thread_type=thread_type,
                is_permanent=True,
                language="ENG"
            )
            db.add(thread)
            db.commit()
            db.refresh(thread)
            
            # Add welcome message
            welcome_message = Message(
                id=uuid.uuid4(),
                thread_id=thread.id,
                user_id=sample_user.id,
                author=MessageAuthor.ASSISTANT,
                content=config['welcome']
            )
            db.add(welcome_message)
            
            print(f"Created thread: {config['name']}")
        
        db.commit()
        
        # Display summary
        print(f"Sample data initialized successfully!")
        print(f"Users: {db.query(User).count()}")
        print(f"Threads: {db.query(ChatThread).count()}")
        print(f"Messages: {db.query(Message).count()}")
        print(f"Login: manelka / manelka1234")
        
    except Exception as e:
        print(f"Error initializing sample data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Create database tables
try:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {str(e)}")
    if "permission denied" in str(e).lower():
        print("Permission error detected!")
        print("Please run this command to fix permissions:")
        print("sudo -u postgres psql -d \"cloud-web\" -c \"GRANT ALL PRIVILEGES ON SCHEMA public TO cloud_era_user; GRANT CREATE ON SCHEMA public TO cloud_era_user;\"")
    sys.exit(1)

# Initialize sample data
try:
    initialize_sample_data()
except Exception as e:
    print(f"Error initializing sample data: {str(e)}")
    print("Tables created successfully, but sample data failed")
    print("You can still use the application, but you'll need to create a user manually")
    # Don't exit here, let the app start so user can register via API

app = FastAPI(
    title=settings.api_title,
    description="API for Cloud ERA ",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(reactions.router, prefix="/api/reactions", tags=["reactions"])

# Website functionality routers
app.include_router(posts.router, tags=["website-posts"])
app.include_router(categories.router, tags=["website-categories"])  
app.include_router(website_admin.router, tags=["website-admin"])

@app.get("/")
async def root():
    return {"message": settings.api_title, "version": settings.api_version}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Cloud ERA API Server...")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    
    if settings.debug:
        # Development mode with hot reload using import string
        uvicorn.run(
            "main:app", 
            host=settings.host, 
            port=settings.port, 
            reload=True,
            reload_dirs=["./app"],
            log_level="info"
        )
    else:
        # Production mode with app object
        uvicorn.run(
            app, 
            host=settings.host, 
            port=settings.port, 
            reload=False,
            log_level="warning"
        )