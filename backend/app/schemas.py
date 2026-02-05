from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Tag schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="cyan", max_length=20)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True


# Post schemas
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = Field(None, max_length=300)
    version: Optional[str] = Field(None, max_length=20)
    read_time: Optional[str] = Field(None, max_length=20)
    author: str = Field(default="Admin", max_length=100)


class PostCreate(PostBase):
    slug: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")
    tags: list[str] = Field(default_factory=list)  # List of tag names
    is_published: bool = False


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = Field(None, max_length=300)
    version: Optional[str] = Field(None, max_length=20)
    read_time: Optional[str] = Field(None, max_length=20)
    author: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None
    is_published: Optional[bool] = None


class PostResponse(PostBase):
    id: int
    slug: str
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse]

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: Optional[str]
    cover_image: Optional[str]
    version: Optional[str]
    read_time: Optional[str]
    author: str
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    tags: list[TagResponse]

    class Config:
        from_attributes = True


# Pagination
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# Auth schemas
class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
