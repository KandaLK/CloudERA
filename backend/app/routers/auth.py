from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from app.database.database import get_db
from app.models.user import User
from app.models.chat_thread import ChatThread, ThreadType
from app.models.message import Message, MessageAuthor
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

router = APIRouter()

def get_thread_config():
    """Get thread configuration with names and welcome messages"""
    return {
        ThreadType.AWS_DISCUSSION: {
            "name": "AWS Discussion",
            "welcome_en": "Welcome to AWS Discussion! I'm here to help you with Amazon Web Services including EC2, S3, Lambda, RDS, VPC, and all other AWS services. What AWS topic would you like to explore today?",
            "welcome_si": "AWS සංවාදයට ආයුබෝවන්! මම ඔබට Amazon Web Services ඇතුළුව EC2, S3, Lambda, RDS, VPC සහ අනෙකුත් AWS සේවා සමඟ උදව් කළ හැකිය. ඔබ අද AWS හි කුමන මාතෘකාව ගවේෂණය කිරීමට කැමතිද?"
        },
        ThreadType.AZURE_DISCUSSION: {
            "name": "Azure Discussion", 
            "welcome_en": "Welcome to Azure Discussion! I can assist you with Microsoft Azure services including Virtual Machines, Storage, App Services, SQL Database, and more. How can I help with your Azure journey?",
            "welcome_si": "Azure සංවාදයට ආයුබෝවන්! මට Microsoft Azure සේවා ඇතුළුව Virtual Machines, Storage, App Services, SQL Database සහ තවත් බොහෝ දේ සමඟ ඔබට උපකාර කළ හැකිය. ඔබගේ Azure ගමනට මම කෙසේ උපකාර කළ හැකිද?"
        },
        ThreadType.SMART_LEARNER: {
            "name": "Smart Learner",
            "welcome_en": "Welcome to Smart Learner! I'm your guide for learning cloud technologies, best practices, architecture patterns, and staying updated with the latest trends. What would you like to learn today?",
            "welcome_si": "Smart Learner වෙත ආයුබෝවන්! මම වලාකුළු තාක්ෂණයන්, හොඳම පරිචයන්, ගෘහ නිර්මාණ රටා ඉගෙනීම සහ නවතම ප්‍රවණතා සමඟ යාවත්කාලීනව සිටීම සඳහා ඔබගේ මාර්ගෝපදේශකයා වෙමි. ඔබ අද කුමක් ඉගෙන ගැනීමට කැමතිද?"
        }
    }

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=uuid.uuid4(),
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create 4 permanent threads for the new user
    thread_config = get_thread_config()
    user_language = getattr(new_user, 'language', 'ENG') or 'ENG'
    
    for thread_type, config in thread_config.items():
        # Create thread
        thread = ChatThread(
            id=uuid.uuid4(),
            user_id=new_user.id,
            name=config["name"],
            language=user_language,
            is_permanent=True,
            thread_type=thread_type,
            is_active=False
        )
        db.add(thread)
        db.flush()  # Get thread ID without committing
        
        # Create welcome message
        welcome_message = config["welcome_si"] if user_language == "SIN" else config["welcome_en"]
        message = Message(
            id=uuid.uuid4(),
            thread_id=thread.id,
            user_id=new_user.id,
            author=MessageAuthor.ASSISTANT,
            content=welcome_message
        )
        db.add(message)
    
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}