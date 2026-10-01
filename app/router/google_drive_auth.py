import os
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, Query, status
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.core.config import settings
from app.models.users import User
from app.repositories.google_drive_repo import GoogleDriveRepository
from app.schema.google_drive import (
    GoogleDriveAuthUrlResponse,
    GoogleDriveConnectionCreate,
    GoogleDriveConnectionResponse,
)
from app.utils.dependencies import get_current_user, get_google_drive_repo

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

router = APIRouter(prefix="/google-drive", tags=["Google Drive Auth"])


class DrivePermissionMode(str, Enum):
    READ = "read"
    WRITE = "write"
    ALL = "all"


def _get_scopes_for_mode(mode: DrivePermissionMode) -> list[str]:
    base_scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
    ]

    if mode == DrivePermissionMode.READ:
        return base_scopes + ["https://www.googleapis.com/auth/drive.readonly"]
    elif mode == DrivePermissionMode.WRITE:
        return base_scopes + ["https://www.googleapis.com/auth/drive.file"]
    else:
        return base_scopes + [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.file",
        ]


def _build_oauth_flow(scopes: list[str] | None = None) -> Flow:
    return Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=scopes or settings.GOOGLE_DRIVE_SCOPES,
        redirect_uri=settings.GOOGLE_DRIVE_REDIRECT_URI,
        autogenerate_code_verifier=False,
    )


@router.get(
    "/connect",
    response_model=GoogleDriveAuthUrlResponse,
    status_code=status.HTTP_200_OK,
)
def connect_google_drive(
    mode: DrivePermissionMode = Query(DrivePermissionMode.ALL),
    current_user: User = Depends(get_current_user),
):
    scopes = _get_scopes_for_mode(mode)
    flow = _build_oauth_flow(scopes=scopes)
    state_payload = f"{current_user.id}:{mode.value}"

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state_payload,
    )

    return GoogleDriveAuthUrlResponse(authorization_url=auth_url)


@router.get("/callback", response_model=GoogleDriveConnectionResponse)
def google_drive_callback(
    code: str | None = Query(None),
    error: str | None = Query(None),
    state: str = Query(...),
    drive_repo: GoogleDriveRepository = Depends(get_google_drive_repo),
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google drive authentication cancelled or denied by user: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code missing from Google redirect.",
        )

    try:
        user_id_str, requested_mode = state.split(":")
        user_id = int(user_id_str)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or malformed state parameter.",
        )

    all_potential_scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
    ]
    flow = _build_oauth_flow(scopes=all_potential_scopes)

    try:
        flow.fetch_token(code=code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch token from Google: {str(exc)}",
        )

    creds = flow.credentials

    if not creds.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Google did not return a refresh token. Revoke access from your"
                " Google account security settings and retry."
            ),
        )

    granted_scopes = set(creds.scopes or [])
    has_read = "https://www.googleapis.com/auth/drive.readonly" in granted_scopes
    has_write = "https://www.googleapis.com/auth/drive.file" in granted_scopes

    if not has_read and not has_write:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Drive Permission granted. Please grant at least one permission.",
        )

    if requested_mode == DrivePermissionMode.READ.value:
        if not has_read:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Read permission was requested but not granted by Google.",
            )
        permission_type = "READ"

    elif requested_mode == DrivePermissionMode.WRITE.value:
        if not has_write:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Write permission was requested but not granted by Google.",
            )
        permission_type = "WRITE"

    else:
        if has_write and has_read:
            permission_type = "READ_WRITE"
        elif has_read:
            permission_type = "READ"
        else:
            permission_type = "WRITE"

    user_info_service = build(
        "oauth2", "v2", credentials=creds, cache_discovery=False
    )
    user_info = user_info_service.userinfo().get().execute()
    google_email = user_info.get("email")

    connection_data = GoogleDriveConnectionCreate(
        user_id=user_id,
        google_email=google_email,
        refresh_token=creds.refresh_token,
        access_token=creds.token,
        token_expiry=creds.expiry,
        permission_type=permission_type,
    )

    connection = drive_repo.upsert_connection(schema=connection_data)
    return connection