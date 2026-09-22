from typing import Optional
from fastapi import HTTPException, UploadFile, status

ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "docx", "xlsx", "csv", "txt"
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def check_username(v: Optional[str]) -> Optional[str]:
    if v is not None:
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty or white space only")
        if " " in v:
            raise ValueError("Username cannot contain spaces")
    return v


def check_password(v: Optional[str]) -> Optional[str]:
    if v is not None:
        v = v.strip()
        if not v:
            raise ValueError("Password cannot be empty or whitespaces only")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain atleast one number")
        return v


def validate_file_upload(file: UploadFile) -> int:
    filename = file.filename or ""
    extension = filename.split('.')[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension .{extension} not allowed "
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10mb"
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file"
        )
    return file_size