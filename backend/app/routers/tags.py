from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tag, Post, post_tag
from app.schemas import TagCreate, TagResponse
from app.auth import get_current_user

router = APIRouter(prefix="/tags", tags=["tags"])


class TagWithCount(TagResponse):
    post_count: int


@router.get("", response_model=list[TagWithCount])
def list_tags(db: Session = Depends(get_db)):
    """Get all tags with post counts."""
    # Query tags with count of published posts
    tags_with_counts = (
        db.query(Tag, func.count(Post.id).label("post_count"))
        .outerjoin(post_tag, Tag.id == post_tag.c.tag_id)
        .outerjoin(Post, (post_tag.c.post_id == Post.id) & (Post.is_published == True))
        .group_by(Tag.id)
        .all()
    )

    return [
        TagWithCount(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            post_count=count,
        )
        for tag, count in tags_with_counts
    ]


@router.get("/{name}", response_model=TagResponse)
def get_tag(name: str, db: Session = Depends(get_db)):
    """Get a single tag by name."""
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse.model_validate(tag)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Create a new tag (requires authentication)."""
    existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")

    tag = Tag(name=tag_data.name, color=tag_data.color)
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return TagResponse.model_validate(tag)


@router.put("/{name}", response_model=TagResponse)
def update_tag(
    name: str,
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Update a tag (requires authentication)."""
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if new name conflicts
    if tag_data.name != name:
        existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag name already exists")

    tag.name = tag_data.name
    tag.color = tag_data.color

    db.commit()
    db.refresh(tag)

    return TagResponse.model_validate(tag)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Delete a tag (requires authentication)."""
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()
    return None
