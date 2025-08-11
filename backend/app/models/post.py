from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database.database import Base

# Posts table - Core post content
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    post_metadata = relationship("PostMetadata", back_populates="post", uselist=False, cascade="all, delete-orphan")
    engagement = relationship("PostEngagement", back_populates="post", uselist=False, cascade="all, delete-orphan")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")

# Post metadata - Publishing and feature status
class PostMetadata(Base):
    __tablename__ = "post_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, unique=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    is_published = Column(Boolean, default=True, index=True)
    published_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reading_time_minutes = Column(Integer, default=0)
    seo_title = Column(String(255))
    seo_description = Column(String(500))
    
    # Relationships
    post = relationship("Post", back_populates="post_metadata")

# Post engagement metrics - Separate table for analytics
class PostEngagement(Base):
    __tablename__ = "post_engagement"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, unique=True, index=True)
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime(timezone=True))
    
    # Relationships
    post = relationship("Post", back_populates="engagement")

# Post media - Images, videos, files
class PostMedia(Base):
    __tablename__ = "post_media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, index=True)
    media_type = Column(String(20), nullable=False)  # image, video, file
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    caption = Column(Text)
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    is_primary = Column(Boolean, default=False)  # Primary/featured image
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    post = relationship("Post", back_populates="media")

# Post likes - User engagement
class PostLike(Base):
    __tablename__ = "post_likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")

# Categories - Post categorization
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7), default="#3B82F6")  # Hex color
    icon = Column(String(50))  # Icon name/class
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))  # For subcategories
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    posts = relationship("Post", back_populates="category")
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")

# Tags - Flexible tagging system
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#6B7280")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    post_tags = relationship("PostTag", back_populates="tag")

# Post-Tag relationship
class PostTag(Base):
    __tablename__ = "post_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, index=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    post = relationship("Post", back_populates="tags")
    tag = relationship("Tag", back_populates="post_tags")

# User profiles - Extended user information
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    display_name = Column(String(100))
    full_name = Column(String(150))
    bio = Column(Text)
    location = Column(String(100))
    timezone = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="profile", uselist=False)
    avatar = relationship("UserAvatar", back_populates="profile", uselist=False, cascade="all, delete-orphan")
    social_links = relationship("UserSocialLink", back_populates="profile", cascade="all, delete-orphan")
    permissions = relationship("UserPermission", back_populates="profile", cascade="all, delete-orphan")

# User avatar - Profile images
class UserAvatar(Base):
    __tablename__ = "user_avatars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, unique=True, index=True)
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    file_size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    profile = relationship("UserProfile", back_populates="avatar")

# User social links - Flexible social media links
class UserSocialLink(Base):
    __tablename__ = "user_social_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # github, linkedin, twitter, website
    url = Column(String(500), nullable=False)
    display_text = Column(String(100))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    profile = relationship("UserProfile", back_populates="social_links")

# User permissions - Role-based access control
class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    permission_type = Column(String(50), nullable=False)  # admin, editor, author, subscriber
    resource_type = Column(String(50))  # posts, users, categories, etc.
    resource_id = Column(UUID(as_uuid=True))  # Specific resource ID if applicable
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    granted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="permissions")
    granted_by_user = relationship("User", foreign_keys=[granted_by])