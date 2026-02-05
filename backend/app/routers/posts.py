from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Post, Tag
from app.schemas import PostCreate, PostUpdate, PostResponse, PostListResponse, PaginatedResponse
from app.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])


def get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    """Get existing tags or create new ones."""
    tags = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags


@router.get("", response_model=PaginatedResponse)
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    published_only: bool = True,
    db: Session = Depends(get_db),
):
    """Get paginated list of posts."""
    query = db.query(Post).options(joinedload(Post.tags))

    # Filter by published status
    if published_only:
        query = query.filter(Post.is_published == True)

    # Filter by tag
    if tag:
        query = query.filter(Post.tags.any(Tag.name == tag))

    # Search in title and content
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(Post.title.ilike(search_term), Post.content.ilike(search_term))
        )

    # Get total count
    total = query.count()

    # Apply pagination and sorting
    posts = (
        query.order_by(Post.published_at.desc().nullsfirst(), Post.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=[PostListResponse.model_validate(p) for p in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/latest", response_model=list[PostListResponse])
def get_latest_posts(
    limit: int = Query(3, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Get latest N published posts."""
    posts = (
        db.query(Post)
        .options(joinedload(Post.tags))
        .filter(Post.is_published == True)
        .order_by(Post.published_at.desc().nullsfirst(), Post.created_at.desc())
        .limit(limit)
        .all()
    )
    return [PostListResponse.model_validate(p) for p in posts]


@router.get("/{slug}", response_model=PostResponse)
def get_post(slug: str, db: Session = Depends(get_db)):
    """Get a single post by slug."""
    post = (
        db.query(Post)
        .options(joinedload(Post.tags))
        .filter(Post.slug == slug)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Create a new post (requires authentication)."""
    # Check if slug exists
    existing = db.query(Post).filter(Post.slug == post_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    # Get or create tags
    tags = get_or_create_tags(db, post_data.tags)

    # Create post
    post = Post(
        slug=post_data.slug,
        title=post_data.title,
        content=post_data.content,
        excerpt=post_data.excerpt,
        cover_image=post_data.cover_image,
        version=post_data.version,
        read_time=post_data.read_time,
        author=post_data.author,
        is_published=post_data.is_published,
        published_at=datetime.utcnow() if post_data.is_published else None,
        tags=tags,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return PostResponse.model_validate(post)


@router.put("/{slug}", response_model=PostResponse)
def update_post(
    slug: str,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Update a post (requires authentication)."""
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update fields
    update_data = post_data.model_dump(exclude_unset=True)

    # Handle tags separately
    if "tags" in update_data:
        tag_names = update_data.pop("tags")
        post.tags = get_or_create_tags(db, tag_names)

    # Handle publish status
    if "is_published" in update_data:
        if update_data["is_published"] and not post.is_published:
            post.published_at = datetime.utcnow()
        elif not update_data["is_published"]:
            post.published_at = None

    # Update other fields
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    return PostResponse.model_validate(post)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    slug: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Delete a post (requires authentication)."""
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return None
