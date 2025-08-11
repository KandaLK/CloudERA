from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta

from app.database.database import get_db
from app.core.auth import get_current_user
from app.models import (
    User, Post, PostMetadata, PostEngagement, PostMedia, Category, 
    Tag, PostTag, UserProfile, UserPermission, PostLike
)
from app.schemas.post import (
    PostResponse, PostListResponse, AdminDashboardResponse, 
    PostStatsResponse, UserProfileResponse, WebsiteUserResponse
)

router = APIRouter(prefix="/api/admin", tags=["website-admin"])
security = HTTPBearer()

def require_admin(current_user: User):
    """Helper function to check admin permissions"""
    if not (current_user and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        raise HTTPException(status_code=403, detail="Admin access required")

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Get comprehensive admin dashboard data"""
    
    require_admin(current_user)
    
    # Post statistics
    total_posts = db.query(Post).count()
    published_posts = db.query(Post).join(PostMetadata).filter(PostMetadata.is_published == True).count()
    draft_posts = total_posts - published_posts
    featured_posts = db.query(Post).join(PostMetadata).filter(PostMetadata.is_featured == True).count()
    
    # Engagement statistics
    total_views = db.query(func.sum(PostEngagement.views_count)).scalar() or 0
    total_likes = db.query(func.sum(PostEngagement.likes_count)).scalar() or 0
    
    # Categories count
    categories_count = db.query(Category).filter(Category.is_active == True).count()
    
    # Recent posts
    recent_posts = db.query(Post).order_by(desc(Post.created_at)).limit(5).all()
    recent_posts_response = []
    
    for post in recent_posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "author_name": post.author.profile.display_name if post.author.profile else post.author.username,
            "author_email": post.author.email,
            "category": post.category.name if post.category else "Uncategorized",
            "is_published": post.post_metadata.is_published if post.post_metadata else True,
            "is_featured": post.post_metadata.is_featured if post.post_metadata else False,
            "views_count": post.engagement.views_count if post.engagement else 0,
            "likes_count": post.engagement.likes_count if post.engagement else 0,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        }
        recent_posts_response.append(post_data)
    
    # Recent activities (simplified for now)
    recent_activities = [
        {"action": "post_created", "details": f"{recent_posts[0].title} was created", "timestamp": recent_posts[0].created_at} if recent_posts else {"action": "system", "details": "No recent activity", "timestamp": datetime.now(timezone.utc)}
    ]
    
    # Top posts by views
    top_posts = db.query(Post).join(PostEngagement).join(PostMetadata).filter(
        PostMetadata.is_published == True
    ).order_by(desc(PostEngagement.views_count)).limit(5).all()
    
    top_posts_response = []
    for post in top_posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "author_name": post.author.profile.display_name if post.author.profile else post.author.username,
            "views_count": post.engagement.views_count if post.engagement else 0,
            "likes_count": post.engagement.likes_count if post.engagement else 0,
            "created_at": post.created_at
        }
        top_posts_response.append(post_data)
    
    post_stats = PostStatsResponse(
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=draft_posts,
        featured_posts=featured_posts,
        total_views=total_views,
        total_likes=total_likes,
        categories_count=categories_count,
        recent_posts=recent_posts_response
    )
    
    return AdminDashboardResponse(
        post_stats=post_stats,
        recent_activities=recent_activities,
        top_posts=top_posts_response
    )

@router.get("/posts", response_model=PostListResponse)
async def get_all_posts_admin(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, pattern="^(published|draft|all)$"),
    author_id: Optional[uuid.UUID] = None,
    category_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Get all posts for admin management (includes drafts)"""
    
    require_admin(current_user)
    
    query = db.query(Post).join(PostMetadata, isouter=True).join(PostEngagement, isouter=True)
    
    # Apply filters
    if status_filter == "published":
        query = query.filter(PostMetadata.is_published == True)
    elif status_filter == "draft":
        query = query.filter(or_(PostMetadata.is_published == False, PostMetadata.is_published == None))
    
    if author_id:
        query = query.filter(Post.author_id == author_id)
    
    if category_id:
        query = query.filter(Post.category_id == category_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_term),
                Post.summary.ilike(search_term),
                Post.content.ilike(search_term)
            )
        )
    
    query = query.order_by(desc(Post.created_at))
    
    # Count total
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    posts = query.offset(offset).limit(size).all()
    
    # Convert to response format
    posts_response = []
    for post in posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "summary": post.summary,
            "author_id": post.author_id,
            "author_name": post.author.profile.display_name if post.author.profile else post.author.username,
            "author_email": post.author.email,
            "category": post.category.name if post.category else "Uncategorized",
            "category_color": post.category.color if post.category else "#3B82F6",
            "is_published": post.post_metadata.is_published if post.post_metadata else True,
            "is_featured": post.post_metadata.is_featured if post.post_metadata else False,
            "published_at": post.post_metadata.published_at if post.post_metadata else post.created_at,
            "views_count": post.engagement.views_count if post.engagement else 0,
            "likes_count": post.engagement.likes_count if post.engagement else 0,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        }
        posts_response.append(post_data)
    
    return PostListResponse(
        posts=posts_response,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.get("/users", response_model=List[WebsiteUserResponse])
async def get_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    role_filter: Optional[str] = Query(None, pattern="^(admin|editor|author|subscriber)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Get all users for admin management"""
    
    require_admin(current_user)
    
    query = db.query(User).join(UserProfile, isouter=True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                UserProfile.display_name.ilike(search_term),
                UserProfile.full_name.ilike(search_term)
            )
        )
    
    if role_filter:
        query = query.join(UserPermission).filter(UserPermission.permission_type == role_filter)
    
    query = query.order_by(desc(User.created_at))
    
    # Apply pagination
    offset = (page - 1) * size
    users = query.offset(offset).limit(size).all()
    
    users_response = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "profile": None
        }
        
        if user.profile:
            profile_data = {
                "id": user.profile.id,
                "user_id": user.profile.user_id,
                "display_name": user.profile.display_name,
                "full_name": user.profile.full_name,
                "bio": user.profile.bio,
                "location": user.profile.location,
                "created_at": user.profile.created_at,
                "updated_at": user.profile.updated_at,
                "email": user.email
            }
            user_data["profile"] = profile_data
        
        users_response.append(WebsiteUserResponse(**user_data))
    
    return users_response

@router.put("/posts/{post_id}/toggle-featured")
async def toggle_post_featured(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Toggle featured status of a post"""
    
    require_admin(current_user)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post.post_metadata:
        # Create metadata if it doesn't exist
        post_metadata = PostMetadata(
            post_id=post.id,
            is_featured=True,
            is_published=True
        )
        db.add(post_metadata)
    else:
        post.post_metadata.is_featured = not post.post_metadata.is_featured
    
    db.commit()
    
    return {"message": f"Post featured status updated", "is_featured": post.post_metadata.is_featured}

@router.put("/posts/{post_id}/toggle-published")
async def toggle_post_published(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Toggle published status of a post"""
    
    require_admin(current_user)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post.post_metadata:
        post_metadata = PostMetadata(
            post_id=post.id,
            is_featured=False,
            is_published=False
        )
        db.add(post_metadata)
    else:
        post.post_metadata.is_published = not post.post_metadata.is_published
        if post.post_metadata.is_published and not post.post_metadata.published_at:
            post.post_metadata.published_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"message": f"Post published status updated", "is_published": post.post_metadata.is_published}

@router.delete("/posts/{post_id}")
async def delete_post_admin(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Delete a post (admin only)"""
    
    require_admin(current_user)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

@router.put("/users/{user_id}/toggle-permission")
async def toggle_user_permission(
    user_id: uuid.UUID,
    permission_type: str = Query(..., pattern="^(admin|editor|author|subscriber)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Toggle user permission/role"""
    
    require_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ensure user has a profile
    if not user.profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()
    
    # Check if user already has this permission
    existing_permission = db.query(UserPermission).filter(
        and_(
            UserPermission.profile_id == user.profile.id,
            UserPermission.permission_type == permission_type,
            UserPermission.is_active == True
        )
    ).first()
    
    if existing_permission:
        # Deactivate permission
        existing_permission.is_active = False
        action = "removed"
    else:
        # Add permission
        new_permission = UserPermission(
            profile_id=user.profile.id,
            permission_type=permission_type,
            granted_by=current_user.id,
            is_active=True
        )
        db.add(new_permission)
        action = "granted"
    
    db.commit()
    
    return {"message": f"{permission_type.title()} permission {action} for user {user.username}"}

@router.get("/analytics/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Get website analytics overview"""
    
    require_admin(current_user)
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Posts created in period
    posts_in_period = db.query(Post).filter(
        Post.created_at >= start_date
    ).count()
    
    # Total engagement in period
    likes_in_period = db.query(PostLike).filter(
        PostLike.created_at >= start_date
    ).count()
    
    # Most popular posts
    popular_posts = db.query(Post).join(PostEngagement).join(PostMetadata).filter(
        PostMetadata.is_published == True
    ).order_by(desc(PostEngagement.views_count)).limit(10).all()
    
    popular_posts_data = [
        {
            "title": post.title,
            "slug": post.slug,
            "views": post.engagement.views_count,
            "likes": post.engagement.likes_count,
            "author": post.author.profile.display_name if post.author.profile else post.author.username
        }
        for post in popular_posts
    ]
    
    return {
        "period_days": days,
        "posts_created": posts_in_period,
        "likes_received": likes_in_period,
        "popular_posts": popular_posts_data,
        "total_users": db.query(User).count(),
        "total_published_posts": db.query(Post).join(PostMetadata).filter(PostMetadata.is_published == True).count(),
        "total_categories": db.query(Category).filter(Category.is_active == True).count()
    }