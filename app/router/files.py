from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from googleapiclient.errors import HttpError

from app.models.users import User
from app.repositories.file import FileRepository
from app.repositories.google_drive_repo import GoogleDriveRepository
from app.schema.files import FileResponse
from app.services.google_drive import GoogleDriveService
from app.utils.dependencies import (
    get_current_user,
    get_drive_service,
    get_file_repo,
    get_google_drive_repo,
)
from app.utils.validators import validate_file_upload

router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/upload",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    file_repo: FileRepository = Depends(get_file_repo),
    drive_repo: GoogleDriveRepository = Depends(get_google_drive_repo),
    drive_service: GoogleDriveService = Depends(get_drive_service),
):
    conn = drive_repo.get_by_user_id(user_id=current_user.id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Drive not connected. Please connect your Google Drive first.",
        )

    if conn.permission_type == "READ":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current connection is Read-Only. Write permission is required to upload files.",
        )

    file_size = validate_file_upload(file)

    try:
        drive_result = drive_service.upload_file(
            file_stream=file.file,
            file_name=file.filename or "uploaded_file",
            mime_type=file.content_type or "application/octet-stream",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Drive upload failed: {str(exc)}",
        )

    record_data = {
        "file_name": file.filename or "uploaded_file",
        "drive_file_id": drive_result["drive_file_id"],
        "drive_view_link": drive_result["drive_view_link"],
        "mime_type": file.content_type or "application/octet-stream",
        "file_size_bytes": file_size,
    }
    return file_repo.create(user_id=current_user.id, file_data=record_data)


@router.get("", response_model=List[FileResponse])
def list_user_files(
    current_user: User = Depends(get_current_user),
    file_repo: FileRepository = Depends(get_file_repo),
):
    return file_repo.get_all_by_user_id(user_id=current_user.id)


@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    file_repo: FileRepository = Depends(get_file_repo),
):
    file_record = file_repo.get_user_file_by_id(file_id=file_id, user_id=current_user.id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or unauthorized",
        )
    return file_record


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    file_repo: FileRepository = Depends(get_file_repo),
    drive_repo: GoogleDriveRepository = Depends(get_google_drive_repo),
    drive_service: GoogleDriveService = Depends(get_drive_service),
):
    conn = drive_repo.get_by_user_id(user_id=current_user.id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Drive not connected.",
        )

    if conn.permission_type == "READ":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current connection is Read-Only. Delete permission is not allowed.",
        )

    file_record = file_repo.get_user_file_by_id(file_id=file_id, user_id=current_user.id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or unauthorized",
        )

    try:
        drive_service.delete_file(drive_file_id=file_record.drive_file_id)
    except HttpError as exc:
        if exc.resp.status != 404:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Drive deletion failed: {str(exc)}",
            )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Drive deletion failed: {str(exc)}",
        )

    file_repo.delete(file_record=file_record)
    return None