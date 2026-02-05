import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from PIL import Image
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
from app.auth import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Upload an image file (requires authentication)."""
    # Check file extension
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE // 1024 // 1024}MB",
        )

    # Validate it's actually an image
    try:
        img = Image.open(file.file)
        img.verify()
        file.file.seek(0)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": unique_name,
        "url": f"/uploads/{unique_name}",
        "size": len(content),
    }


@router.delete("/image/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    filename: str,
    current_user: str = Depends(get_current_user),
):
    """Delete an uploaded image (requires authentication)."""
    # Sanitize filename to prevent path traversal
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    os.remove(file_path)
    return None
