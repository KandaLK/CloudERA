from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import uuid

from app.database.database import get_db
from app.core.auth import get_current_user
from app.models import User, Category, Post, PostMetadata
from app.schemas.post import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse

router = APIRouter(prefix="/api/categories", tags=["categories"])
security = HTTPBearer()

@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    include_post_count: bool = True,
    only_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all categories with optional post counts"""
    
    query = db.query(Category)
    
    if only_active:
        query = query.filter(Category.is_active == True)
    
    query = query.order_by(Category.display_order, Category.name)
    categories = query.all()
    
    categories_response = []
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "color": category.color,
            "icon": category.icon,
            "parent_id": category.parent_id,
            "display_order": category.display_order,
            "is_active": category.is_active,
            "created_at": category.created_at
        }
        
        if include_post_count:
            # Count published posts in this category
            post_count = db.query(Post).join(PostMetadata).filter(
                Post.category_id == category.id,
                PostMetadata.is_published == True
            ).count()
            category_data["post_count"] = post_count
        
        categories_response.append(CategoryResponse(**category_data))
    
    return CategoryListResponse(
        categories=categories_response,
        total=len(categories_response)
    )

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get a specific category by ID"""
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get post count
    post_count = db.query(Post).join(PostMetadata).filter(
        Post.category_id == category.id,
        PostMetadata.is_published == True
    ).count()
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        color=category.color,
        icon=category.icon,
        parent_id=category.parent_id,
        display_order=category.display_order,
        is_active=category.is_active,
        created_at=category.created_at,
        post_count=post_count
    )

@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a category by its slug"""
    
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get post count
    post_count = db.query(Post).join(PostMetadata).filter(
        Post.category_id == category.id,
        PostMetadata.is_published == True
    ).count()
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        color=category.color,
        icon=category.icon,
        parent_id=category.parent_id,
        display_order=category.display_order,
        is_active=category.is_active,
        created_at=category.created_at,
        post_count=post_count
    )

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Create a new category (admin only)"""
    
    if not (current_user and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Generate unique slug
    base_slug = category_data.name.lower().replace(' ', '-').replace('_', '-')
    import re
    base_slug = re.sub(r'[^a-z0-9\-]', '', base_slug)
    base_slug = re.sub(r'-+', '-', base_slug).strip('-')
    
    slug = base_slug
    counter = 1
    while db.query(Category).filter(Category.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create category
    new_category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        color=category_data.color,
        icon=category_data.icon,
        parent_id=category_data.parent_id,
        display_order=category_data.display_order or 0,
        is_active=True
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse(
        id=new_category.id,
        name=new_category.name,
        slug=new_category.slug,
        description=new_category.description,
        color=new_category.color,
        icon=new_category.icon,
        parent_id=new_category.parent_id,
        display_order=new_category.display_order,
        is_active=new_category.is_active,
        created_at=new_category.created_at,
        post_count=0
    )

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Update a category (admin only)"""
    
    if not (current_user and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update fields
    update_data = category_data.dict(exclude_unset=True)
    
    # Handle slug update if name changed
    if "name" in update_data and update_data["name"] != category.name:
        base_slug = update_data["name"].lower().replace(' ', '-').replace('_', '-')
        import re
        base_slug = re.sub(r'[^a-z0-9\-]', '', base_slug)
        base_slug = re.sub(r'-+', '-', base_slug).strip('-')
        
        slug = base_slug
        counter = 1
        while db.query(Category).filter(
            Category.slug == slug, 
            Category.id != category_id
        ).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        update_data["slug"] = slug
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    # Get post count
    post_count = db.query(Post).join(PostMetadata).filter(
        Post.category_id == category.id,
        PostMetadata.is_published == True
    ).count()
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        color=category.color,
        icon=category.icon,
        parent_id=category.parent_id,
        display_order=category.display_order,
        is_active=category.is_active,
        created_at=category.created_at,
        post_count=post_count
    )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Delete a category (admin only) - only if no posts are using it"""
    
    if not (current_user and current_user.profile and 
            any(p.permission_type == 'admin' for p in current_user.profile.permissions)):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if any posts are using this category
    post_count = db.query(Post).filter(Post.category_id == category_id).count()
    if post_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category with {post_count} associated posts. Move posts to another category first."
        )
    
    db.delete(category)
    db.commit()
    
    return None