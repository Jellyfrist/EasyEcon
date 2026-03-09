from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import Base, engine
from app.routers import auth, course, flashcard, learning, exam, admin, user, search
from app.env_detector import should_auto_create_tables
import logging
import os
from fastapi.responses import JSONResponse
from jose import JWTError
from jose.exceptions import ExpiredSignatureError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from jose import jwt

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("app")

# Detect if running on Vercel (Vercel sets VERCEL=1 automatically)
api_prefix = "/api" if os.getenv("VERCEL") else ""
logger.info(f"Running with api_prefix: '{api_prefix}' (VERCEL={os.getenv('VERCEL')})")

fastapi_app = FastAPI(
    title="FastAPI Backend",
    debug=settings.debug,
    docs_url=f"{api_prefix}/docs",
    redoc_url=f"{api_prefix}/redoc",
    openapi_url=f"{api_prefix}/openapi.json"
)
fastapi_app.logger = logger

# fastapi_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.allowed_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Remember to add CORSMiddleware LAST so it wraps the custom JWT middleware!


class JWTAndCSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        # Paths that skip JWT/CSRF check entirely
        # - GET requests are always allowed (read-only)
        # - Auth endpoints (login, register, SSO callbacks) must be excluded
        #   so users can reach them before they have a token
        excluded_paths = [
            "/",
            # auth: login & register never have a token yet
            "/auth/token",
            "/auth/register",
            "/auth/login/google",
            "/auth/google/callback",
            "/auth/login/github",
            "/auth/github/callback",
            #try idk
            f"{api_prefix}/auth/token",
            f"{api_prefix}/auth/register",
            f"{api_prefix}/auth/login/google",
            f"{api_prefix}/auth/google/callback",
            f"{api_prefix}/auth/login/github",
            f"{api_prefix}/auth/github/callback",
            # ... and so on
            # legacy paths kept for backward compatibility
            "/login",
            "/google/auth",
            "/logout",
            # docs
            f"{api_prefix}/docs",
            f"{api_prefix}/redoc",
            f"{api_prefix}/openapi.json",
            # verify
            "/auth/verify-email"
        ]

        logger.debug(f"Request method: {request.method}, path: {request.url.path}")

        # skip middleware for GET/HEAD/OPTIONS or excluded paths
        if request.method not in ["POST", "PUT", "DELETE", "PATCH"] \
                or request.url.path in excluded_paths:
            logger.debug("Skipping JWT/CSRF validation for this request")
            return await call_next(request)

        token = request.cookies.get("jwt")
        logger.debug(f"JWT cookie: {token}")
        if not token:
            logger.error("Missing JWT cookie in middleware")
            raise HTTPException(status_code=401, detail="Missing JWT cookie")

        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=["HS256"])
            logger.debug(f"JWT payload: {payload}")
        except JWTError as e:
            logger.error(f"JWT decoding failed in middleware: {e}")
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")

        client_csrf = request.headers.get("X-CSRF-Token")
        server_csrf = payload.get("csrf_token")
        logger.debug(f"Client CSRF token: {client_csrf}, Server CSRF token: {server_csrf}")
        
        # Only validate CSRF if both client sent a token AND server has one
        # This allows grace period after login before frontend has stored the token
        if client_csrf and server_csrf:
            if server_csrf != client_csrf:
                logger.error(f"CSRF token mismatch: expected {server_csrf}, got {client_csrf}")
                raise HTTPException(status_code=403, detail="CSRF token mismatch")
        elif server_csrf and not client_csrf:
            # Server has CSRF token but client didn't send it - warn but don't fail
            logger.warning(f"Client missing CSRF token header (path: {request.url.path})")
        elif not server_csrf:
            # JWT doesn't have CSRF token - this shouldn't happen but allow it
            logger.warning(f"JWT missing CSRF claim (path: {request.url.path})")

        response = await call_next(request)
        return response

fastapi_app.add_middleware(JWTAndCSRFMiddleware)

fastapi_app.add_middleware(
    CORSMiddleware,
    # 1. This handles your explicit production domains from your .env
    allow_origins=settings.allowed_origins, 
    
    # 2. This safely catches ANY Vercel preview deployment for your specific project
    allow_origin_regex=r"https://easy-econ-.*-jellyfrists-projects\.vercel\.app", 
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# fastapi_app.add_middleware(JWTAndCSRFMiddleware)
fastapi_app.state.settings = settings

# Auto-detect environment and conditionally create tables
try:
    if should_auto_create_tables():
        logger.info("Auto-creating database tables (Docker)")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Skipping table creation (Vercel/Local)")
except Exception as e:
    logger.error(f"Error during table creation: {e}")
    # Don't fail the app if table creation fails

# router registration
fastapi_app.include_router(auth.router,      prefix=api_prefix)
fastapi_app.include_router(course.router,    prefix=api_prefix)
fastapi_app.include_router(flashcard.router, prefix=api_prefix)
fastapi_app.include_router(learning.router,  prefix=api_prefix)
fastapi_app.include_router(learning.teacher_router, prefix=api_prefix)
fastapi_app.include_router(exam.router,      prefix=api_prefix)
fastapi_app.include_router(admin.router,     prefix=api_prefix)
fastapi_app.include_router(user.router,      prefix=api_prefix)
fastapi_app.include_router(search.router,    prefix=api_prefix)


@fastapi_app.exception_handler(JWTError)
async def jwt_error_handler(request: Request, exc: JWTError):
    fastapi_app.logger.error(f"JWT Error: {exc}")
    return JSONResponse(status_code=401, content={"error": "Invalid token"})


@fastapi_app.exception_handler(ExpiredSignatureError)
async def jwt_expired_error_handler(request: Request, exc: ExpiredSignatureError):
    fastapi_app.logger.error(f"JWT Expired Token Error: {exc}")
    return JSONResponse(status_code=401, content={"error": "Token expired"})

fastapi_app.logger.info(f"Starting FastAPI app with DATABASE_URL: {settings.database_url}")
fastapi_app.logger.debug(f"Allowed origins: {settings.allowed_origins}")
