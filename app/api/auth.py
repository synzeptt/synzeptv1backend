from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from authlib.integrations.httpx_client import AsyncOAuth2Client
import os

from app.core import security
from app.core.config import settings
from models import User, UserProfile
from app.db.session import get_db
from app.schemas.user import Token, TokenPayload, UserCreate, UserRead

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Google OAuth configuration
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user


@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=security.hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=8)
    access_token = security.create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = security.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = TokenPayload(**payload)
    if not token_data.sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).get(int(token_data.sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _is_google_oauth_configured() -> bool:
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and "YOUR_NEW_CLIENT_ID" not in GOOGLE_CLIENT_ID)


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    if not _is_google_oauth_configured():
        # Dev fallback: allow a local "fake" Google login without requiring real OAuth credentials.
        return {
            "dev_mode": True,
            "message": "Google OAuth not configured. Using local dev login.",
            "dev_login_url": "/api/auth/google/dev",
        }

    client = AsyncOAuth2Client(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )
    authorization_url, state = client.create_authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        scope=['openid', 'email', 'profile'],
    )
    return {"authorization_url": authorization_url, "state": state}


@router.get("/google/dev")
def google_dev_login(db: Session = Depends(get_db)):
    """Dev-only endpoint to simulate Google login without a real OAuth client."""
    # This is intentionally permissive and only meant for local development.
    # It will create or reuse a dev user and return a JWT token.
    dev_email = "dev@localhost"
    dev_name = "Dev User"

    user = get_user_by_email(db, dev_email)
    if not user:
        user = User(email=dev_email, password_hash="", name=dev_name)
        db.add(user)
        db.commit()
        db.refresh(user)
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()

    access_token_expires = timedelta(hours=8)
    access_token = security.create_access_token(subject=str(user.id), expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name},
        "dev_mode": True,
    }


@router.post("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )

    data = await request.json()
    code = data.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")

    client = AsyncOAuth2Client(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )

    try:
        token = await client.fetch_token(
            'https://oauth2.googleapis.com/token',
            code=code,
        )

        # Get user info from Google
        userinfo = await client.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_data = userinfo.json()

        email = user_data.get("email")
        name = user_data.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")

        # Check if user exists
        user = get_user_by_email(db, email)

        if not user:
            # Create new user
            user = User(
                email=email,
                password_hash="",  # No password for OAuth users
                name=name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create empty profile
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            db.commit()

        # Generate access token
        access_token_expires = timedelta(hours=8)
        access_token = security.create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
