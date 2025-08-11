from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.database.database import get_db
from app.core.auth import get_current_user
from app.models import User, Post, PostMetadata, PostEngagement, PostMedia, PostLike, Category, Tag, PostTag, UserProfile
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, PostListResponse,
    PostSearchRequest, PostStatsResponse, PostLikeCreate, PostLikeResponse
)

router = APIRouter(prefix="/api/posts", tags=["posts"])
security = HTTPBearer()

def create_post_response(post: Post, user_id: Optional[uuid.UUID] = None, db: Session = None) -> PostResponse:
    """Helper function to create PostResponse with all related data"""
    post_data = {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "summary": post.summary,
        "author_id": post.author_id,
        "category_id": post.category.id if post.category else None,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "likes_count": post.engagement.likes_count if post.engagement else 0,
        "views_count": post.engagement.views_count if post.engagement else 0,
        "is_featured": post.post_metadata.is_featured if post.post_metadata else False,
        "is_published": post.post_metadata.is_published if post.post_metadata else True,
        "published_at": post.post_metadata.published_at if post.post_metadata else post.created_at,
        "seo_title": post.post_metadata.seo_title if post.post_metadata else None,
        "seo_description": post.post_metadata.seo_description if post.post_metadata else None,
        "reading_time_minutes": post.post_metadata.reading_time_minutes if post.post_metadata else 0,
        "author_name": post.author.profile.display_name if post.author.profile else post.author.username,
        "author_email": post.author.email,
        "category": post.category.name if post.category else None,
        "category_color": post.category.color if post.category else "#3B82F6",
        "primary_image": next((media.url for media in post.media if media.is_primary), None),
        "tags": [{"id": pt.tag.id, "name": pt.tag.name, "slug": pt.tag.slug, "color": pt.tag.color} for pt in post.tags] if post.tags else [],
    }
    
    # Check if user liked the post
    if user_id and db:
        is_liked = db.query(PostLike).filter(
            and_(PostLike.user_id == user_id, PostLike.post_id == post.id)
        ).first() is not None
        post_data["is_liked"] = is_liked
    
    return PostResponse(**post_data)

@router.get("/", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    is_featured: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|likes_count|views_count|title|published_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of published posts"""
    
    query = db.query(Post).join(PostMetadata).join(PostEngagement).join(Category)
    
    # Filter by published posts only (unless admin)
    if not (current_user and hasattr(current_user, 'profile') and current_user.profile and current_user.profile.permissions):
        query = query.filter(PostMetadata.is_published == True)
    
    # Apply filters
    if category:
        query = query.filter(Category.slug == category)
    
    if is_featured is not None:
        query = query.filter(PostMetadata.is_featured == is_featured)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_term),
                Post.summary.ilike(search_term),
                Post.content.ilike(search_term)
            )
        )
    
    if tag:
        query = query.join(PostTag).join(Tag).filter(Tag.slug == tag)
    
    # Apply sorting
    sort_field = getattr(Post, sort_by) if hasattr(Post, sort_by) else getattr(PostEngagement, sort_by) if hasattr(PostEngagement, sort_by) else Post.created_at
    if sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Count total
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    posts = query.offset(offset).limit(size).all()
    
    # Convert to response format
    posts_response = [create_post_response(post, current_user.id if current_user else None, db) for post in posts]
    
    return PostListResponse(
        posts=posts_response,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific post by ID and increment view count"""
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if post is published (unless admin)
    if not (current_user and hasattr(current_user, 'profile') and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        if not post.post_metadata or not post.post_metadata.is_published:
            raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    if post.engagement:
        post.engagement.views_count += 1
        post.engagement.last_viewed_at = datetime.now(timezone.utc)
    else:
        # Create engagement record if it doesn't exist
        from app.models.post import PostEngagement
        engagement = PostEngagement(
            post_id=post.id,
            views_count=1,
            last_viewed_at=datetime.now(timezone.utc)
        )
        db.add(engagement)
    
    db.commit()
    
    return create_post_response(post, current_user.id if current_user else None, db)

@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a post by its slug"""
    
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if post is published (unless admin)
    if not (current_user and hasattr(current_user, 'profile') and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        if not post.post_metadata or not post.post_metadata.is_published:
            raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    if post.engagement:
        post.engagement.views_count += 1
        post.engagement.last_viewed_at = datetime.now(timezone.utc)
    else:
        from app.models.post import PostEngagement
        engagement = PostEngagement(
            post_id=post.id,
            views_count=1,
            last_viewed_at=datetime.now(timezone.utc)
        )
        db.add(engagement)
    
    db.commit()
    
    return create_post_response(post, current_user.id if current_user else None, db)

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Create a new post (requires authentication)"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check if user has permission to create posts
    if not (current_user.profile and any(p.permission_type in ['admin', 'editor', 'author'] 
                                       for p in current_user.profile.permissions)):
        raise HTTPException(status_code=403, detail="Insufficient permissions to create posts")
    
    # Generate unique slug
    base_slug = post_data.title.lower().replace(' ', '-').replace('_', '-')
    # Remove special characters and ensure slug is URL-safe
    import re
    base_slug = re.sub(r'[^a-z0-9\-]', '', base_slug)
    base_slug = re.sub(r'-+', '-', base_slug).strip('-')
    
    slug = base_slug
    counter = 1
    while db.query(Post).filter(Post.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create post
    new_post = Post(
        title=post_data.title,
        slug=slug,
        content=post_data.content,
        summary=post_data.summary,
        author_id=current_user.id,
        category_id=post_data.category_id
    )
    db.add(new_post)
    db.flush()  # Get the post ID
    
    # Create post metadata
    post_metadata = PostMetadata(
        post_id=new_post.id,
        is_featured=post_data.is_featured,
        is_published=post_data.is_published,
        reading_time_minutes=len(post_data.content.split()) // 200,  # Rough estimate
        seo_title=post_data.seo_title,
        seo_description=post_data.seo_description
    )
    db.add(post_metadata)
    
    # Create engagement record
    engagement = PostEngagement(
        post_id=new_post.id,
        views_count=0,
        likes_count=0
    )
    db.add(engagement)
    
    # Add primary image if provided
    if post_data.primary_image_url:
        media = PostMedia(
            post_id=new_post.id,
            media_type="image",
            url=post_data.primary_image_url,
            is_primary=True,
            display_order=0
        )
        db.add(media)
    
    # Add tags if provided
    if post_data.tag_ids:
        for tag_id in post_data.tag_ids:
            post_tag = PostTag(post_id=new_post.id, tag_id=tag_id)
            db.add(post_tag)
    
    db.commit()
    db.refresh(new_post)
    
    return create_post_response(new_post, current_user.id, db)

@router.post("/{post_id}/like", response_model=dict)
async def toggle_like(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Toggle like status for a post"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    existing_like = db.query(PostLike).filter(
        and_(PostLike.user_id == current_user.id, PostLike.post_id == post_id)
    ).first()
    
    if existing_like:
        # Remove like
        db.delete(existing_like)
        is_liked = False
    else:
        # Add like
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        is_liked = True
    
    db.commit()
    
    # Get updated like count
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    
    return {
        "is_liked": is_liked,
        "like_count": like_count
    }

@router.get("/stats/dashboard", response_model=PostStatsResponse)
async def get_post_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Get post statistics (admin only)"""
    
    if not (current_user and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get basic stats
    total_posts = db.query(Post).count()
    published_posts = db.query(Post).join(PostMetadata).filter(PostMetadata.is_published == True).count()
    draft_posts = total_posts - published_posts
    featured_posts = db.query(Post).join(PostMetadata).filter(PostMetadata.is_featured == True).count()
    
    # Get engagement stats
    total_views = db.query(func.sum(PostEngagement.views_count)).scalar() or 0
    total_likes = db.query(func.sum(PostEngagement.likes_count)).scalar() or 0
    
    # Get categories count
    categories_count = db.query(Category).filter(Category.is_active == True).count()
    
    # Get recent posts
    recent_posts = db.query(Post).join(PostMetadata).filter(
        PostMetadata.is_published == True
    ).order_by(desc(Post.created_at)).limit(5).all()
    
    recent_posts_response = [create_post_response(post, current_user.id, db) for post in recent_posts]
    
    return PostStatsResponse(
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=draft_posts,
        featured_posts=featured_posts,
        total_views=total_views,
        total_likes=total_likes,
        categories_count=categories_count,
        recent_posts=recent_posts_response
    )