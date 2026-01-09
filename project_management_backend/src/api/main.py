from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.auth import router as auth_router
from src.api.routers.clients import router as clients_router
from src.api.routers.dashboard import router as dashboard_router
from src.api.routers.projects import router as projects_router
from src.api.routers.user import router as user_router
from src.core.config import get_settings

settings = get_settings()

openapi_tags = [
    {"name": "auth", "description": "Email/password signup and login (JWT access tokens)."},
    {"name": "user", "description": "Authenticated user profile endpoints."},
    {"name": "clients", "description": "Authenticated CRUD endpoints for managing clients."},
    {"name": "projects", "description": "Authenticated CRUD endpoints for managing projects."},
    {"name": "dashboard", "description": "Authenticated dashboard statistics endpoints."},
]

app = FastAPI(
    title="Project Management Backend API",
    description=(
        "Backend API for the Digital Agency Management Dashboard.\n\n"
        "Authentication:\n"
        "- Obtain an access token via POST /auth/signup or POST /auth/login\n"
        "- Send it on protected routes as: Authorization: Bearer <token>\n"
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS: allow React dev server by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(clients_router)
app.include_router(projects_router)
app.include_router(dashboard_router)


@app.get("/", tags=["health"], summary="Health check", operation_id="health_check")
def health_check():
    """Simple health check endpoint."""
    return {"message": "Healthy"}


@app.get("/docs/auth", tags=["auth"], summary="Auth usage help", operation_id="auth_usage_help")
def auth_usage_help():
    """Return a short guide for using JWT auth with this API."""
    return {
        "signup": {"method": "POST", "path": "/auth/signup", "body": {"email": "user@example.com", "password": "********"}},
        "login": {"method": "POST", "path": "/auth/login", "body": {"email": "user@example.com", "password": "********"}},
        "use_token": "Send header: Authorization: Bearer <access_token>",
        "profile": {"get": "/user/me", "put": "/user/me"},
    }
