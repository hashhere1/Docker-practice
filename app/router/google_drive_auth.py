from app.core.config import settings
from app.models.users import User
from app.repositories.google_drive_repo import GoogleDriveRepository
from app.schema.google_drive import (
    GoogleDriveAuthUrlResponse,
    GoogleDriveConnectionCreate,
    GoogleDriveConnectionResponse,
)
from app.utils.dependencies import get_current_user, get_google_drive_repo
from fastapi import APIRouter, Depends, HTTPException, Query, status
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

router = APIRouter(prefix="/google-drive", tags=["Google Drive Auth"])


def _build_oauth_flow() -> Flow:
    return Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=settings.GOOGLE_DRIVE_SCOPES,
        redirect_uri=settings.GOOGLE_DRIVE_REDIRECT_URI,
        autogenerate_code_verifier=False,  
    )


@router.get(
    "/connect",
    response_model=GoogleDriveAuthUrlResponse,
    status_code=status.HTTP_200_OK,
)
def connect_google_drive(current_user: User = Depends(get_current_user)):
    flow = _build_oauth_flow()

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=str(current_user.id),
    )

    return GoogleDriveAuthUrlResponse(authorization_url=auth_url)


@router.get("/callback", response_model=GoogleDriveConnectionResponse)
def google_drive_callback(
    code: str = Query(...),
    state: str = Query(...),
    drive_repo: GoogleDriveRepository = Depends(get_google_drive_repo),
):
    try:
        user_id = int(state)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter.",
        )

    flow = _build_oauth_flow()

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
    )

    connection = drive_repo.upsert_connection(schema=connection_data)
    return connection