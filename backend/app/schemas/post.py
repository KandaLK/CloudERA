from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
import uuid

# Post Schemas
class PostBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    summary: str
    image_url: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., max_length=50)  # cloud-services, security, technology, tutorials
    is_featured: bool = False
    is_published: bool = True

class PostCreate(PostBase):
    category_id: uuid.UUID
    primary_image_url: Optional[str] = None
    tag_ids: Optional[List[uuid.UUID]] = []
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None

class PostInDB(PostBase):
    id: uuid.UUID
    slug: str
    author_id: uuid.UUID
    likes_count: int = 0
    views_count: int = 0
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PostResponse(PostInDB):
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    category: Optional[str] = None
    category_color: Optional[str] = None
    primary_image: Optional[str] = None
    tags: Optional[List[dict]] = []
    is_liked: Optional[bool] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    reading_time_minutes: Optional[int] = None

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    size: int
    pages: int

# PostLike Schemas
class PostLikeBase(BaseModel):
    post_id: uuid.UUID

class PostLikeCreate(PostLikeBase):
    pass

class PostLikeInDB(PostLikeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostLikeResponse(PostLikeInDB):
    pass

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#3B82F6", max_length=7)

class CategoryCreate(CategoryBase):
    icon: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    display_order: Optional[int] = 0

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7)

class CategoryInDB(CategoryBase):
    id: uuid.UUID
    slug: str
    icon: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    display_order: int = 0
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class CategoryResponse(CategoryInDB):
    post_count: Optional[int] = None

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int

# UserProfile Schemas
class UserProfileBase(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=255)

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileInDB(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileResponse(UserProfileInDB):
    email: Optional[str] = None

# Extended User Response for website functionality
class WebsiteUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    profile: Optional[UserProfileResponse] = None
    
    class Config:
        from_attributes = True

# Search and Filter Schemas
class PostSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    is_featured: Optional[bool] = None
    author_id: Optional[uuid.UUID] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|likes_count|views_count|title)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

class PostStatsResponse(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    featured_posts: int
    total_views: int
    total_likes: int
    categories_count: int
    recent_posts: List[PostResponse]

class AdminDashboardResponse(BaseModel):
    post_stats: PostStatsResponse
    recent_activities: List[dict]
    top_posts: List[PostResponse]