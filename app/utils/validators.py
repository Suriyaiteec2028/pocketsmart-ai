import re
import uuid
from pathlib import Path
from io import BytesIO
from PIL import Image
from fastapi import HTTPException, status
from app.config import settings

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_email_format(email: str) -> bool:
    """Validate email using regular expression."""
    if not email or len(email) > 255:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password length and basic safety."""
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if len(password) > 128:
        return False, "Password is too long."
    return True, ""

def validate_and_save_image(file_bytes: bytes, original_filename: str) -> str:
    """
    Validate uploaded image for size, extension, MIME, and actual image integrity.
    Saves to uploads directory with a safe unique filename.
    Returns the relative path string (e.g. /uploads/abc-123.jpg).
    """
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )
    
    # Check size
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )
    
    # Check extension
    ext = Path(original_filename).suffix.lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed extensions: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Verify image integrity with PIL
    try:
        image = Image.open(BytesIO(file_bytes))
        image.verify()  # Verifies image structure
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid image or is corrupted."
        )
    
    # Re-open for resizing/converting if excessively large
    try:
        image = Image.open(BytesIO(file_bytes))
        # Optional: resize if dimension > 2000px to optimize performance
        max_dim = 1600
        if image.width > max_dim or image.height > max_dim:
            image.thumbnail((max_dim, max_dim))
        
        # Generate safe unique filename
        safe_name = f"{uuid.uuid4().hex}{ext}"
        destination = settings.UPLOAD_DIR / safe_name
        
        # Save image safely
        image.save(destination)
        return f"/uploads/{safe_name}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and store image: {str(e)}"
        )
