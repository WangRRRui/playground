import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import SiteSetting
from app.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingUpdate(BaseModel):
    value: str


class SettingResponse(BaseModel):
    key: str
    value: str

    class Config:
        from_attributes = True


class ExperienceItem(BaseModel):
    period: str = ""  # e.g., "2021 - 2023"
    title: str = ""   # e.g., "Senior Engineer"
    org: str = ""     # e.g., "Company Name" or "University Name"
    desc: str = ""    # description


class AboutContent(BaseModel):
    name: str = ""
    title: str = ""
    bio: str = ""
    avatar: str = ""
    skills: list[str] = []
    education: list[ExperienceItem] = []
    experience: list[ExperienceItem] = []
    social_github: str = ""
    social_twitter: str = ""
    social_email: str = ""


@router.get("/about", response_model=AboutContent)
def get_about(db: Session = Depends(get_db)):
    """Get about page content."""
    settings = db.query(SiteSetting).filter(SiteSetting.key.startswith("about_")).all()

    result = AboutContent()
    for setting in settings:
        key = setting.key.replace("about_", "")
        if key == "skills":
            result.skills = [s.strip() for s in setting.value.split(",") if s.strip()]
        elif key in ("education", "experience"):
            try:
                items = json.loads(setting.value) if setting.value else []
                setattr(result, key, [ExperienceItem(**item) for item in items])
            except (json.JSONDecodeError, TypeError):
                setattr(result, key, [])
        elif hasattr(result, key):
            setattr(result, key, setting.value)

    return result


@router.put("/about", response_model=AboutContent)
def update_about(
    content: AboutContent,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Update about page content (requires authentication)."""
    fields = {
        "about_name": content.name,
        "about_title": content.title,
        "about_bio": content.bio,
        "about_avatar": content.avatar,
        "about_skills": ",".join(content.skills),
        "about_education": json.dumps([e.model_dump() for e in content.education]),
        "about_experience": json.dumps([e.model_dump() for e in content.experience]),
        "about_social_github": content.social_github,
        "about_social_twitter": content.social_twitter,
        "about_social_email": content.social_email,
    }

    for key, value in fields.items():
        setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteSetting(key=key, value=value)
            db.add(setting)

    db.commit()
    return content


@router.get("/{key}", response_model=SettingResponse)
def get_setting(key: str, db: Session = Depends(get_db)):
    """Get a single setting by key."""
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return SettingResponse.model_validate(setting)


@router.put("/{key}", response_model=SettingResponse)
def update_setting(
    key: str,
    data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Update or create a setting (requires authentication)."""
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if setting:
        setting.value = data.value
    else:
        setting = SiteSetting(key=key, value=data.value)
        db.add(setting)

    db.commit()
    db.refresh(setting)
    return SettingResponse.model_validate(setting)
