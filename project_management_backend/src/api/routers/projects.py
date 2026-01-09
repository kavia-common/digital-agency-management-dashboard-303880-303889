import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.api.schemas.project import ProjectCreateRequest, ProjectResponse, ProjectStatus, ProjectUpdateRequest
from src.db.models import Client, Project, User
from src.db.session import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


def _to_project_response(project: Project) -> ProjectResponse:
    """Convert ORM Project to API response."""
    return ProjectResponse(
        id=project.id,
        owner_user_id=project.owner_user_id,
        client_id=project.client_id,
        name=project.name,
        description=project.description,
        status=ProjectStatus(project.status),
        start_date=project.start_date,
        due_date=project.due_date,
        budget_cents=project.budget_cents,
        revenue_cents=project.revenue_cents,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _ensure_client_belongs_to_user(db: Session, current_user: User, client_id: uuid.UUID) -> None:
    """Raise 404 if client doesn't exist for this user."""
    client = db.scalar(select(Client.id).where(Client.id == client_id, Client.owner_user_id == current_user.id))
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List projects",
    description=(
        "List the authenticated user's projects with optional pagination and search. "
        "You can also filter by status and client_id."
    ),
    operation_id="projects_list",
)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: str | None = Query(None, description="Optional search query (matches project name/description)."),
    status_filter: ProjectStatus | None = Query(None, alias="status", description="Optional status filter."),
    client_id: uuid.UUID | None = Query(None, description="Optional filter by client id."),
    limit: int = Query(50, ge=1, le=200, description="Page size."),
    offset: int = Query(0, ge=0, description="Offset for pagination."),
) -> list[ProjectResponse]:
    """List projects for the current user with optional filters."""
    stmt = select(Project).where(Project.owner_user_id == current_user.id)

    if q:
        like = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(Project.name).like(like) | func.lower(func.coalesce(Project.description, "")).like(like)
        )

    if status_filter is not None:
        stmt = stmt.where(Project.status == status_filter)

    if client_id is not None:
        # If a client filter is provided, ensure the client belongs to the user.
        _ensure_client_belongs_to_user(db, current_user, client_id)
        stmt = stmt.where(Project.client_id == client_id)

    stmt = stmt.order_by(Project.created_at.desc()).limit(limit).offset(offset)
    projects = list(db.scalars(stmt).all())
    return [_to_project_response(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by id",
    description="Fetch a single project belonging to the authenticated user.",
    operation_id="projects_get",
)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Get a project by id for the current user."""
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_user_id == current_user.id)
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _to_project_response(project)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    description="Create a new project owned by the authenticated user.",
    operation_id="projects_create",
)
def create_project(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Create a project owned by the current user."""
    if payload.client_id is not None:
        _ensure_client_belongs_to_user(db, current_user, payload.client_id)

    project = Project(
        id=uuid.uuid4(),
        owner_user_id=current_user.id,
        client_id=payload.client_id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        start_date=payload.start_date,
        due_date=payload.due_date,
        budget_cents=payload.budget_cents,
        revenue_cents=payload.revenue_cents,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_project_response(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    description="Update fields on an existing project owned by the authenticated user.",
    operation_id="projects_update",
)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Update a project belonging to the current user."""
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_user_id == current_user.id)
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if payload.client_id is not None:
        _ensure_client_belongs_to_user(db, current_user, payload.client_id)
        project.client_id = payload.client_id
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.status is not None:
        project.status = payload.status
    if payload.start_date is not None:
        project.start_date = payload.start_date
    if payload.due_date is not None:
        project.due_date = payload.due_date
    if payload.budget_cents is not None:
        project.budget_cents = payload.budget_cents
    if payload.revenue_cents is not None:
        project.revenue_cents = payload.revenue_cents

    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_project_response(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Delete a project owned by the authenticated user.",
    operation_id="projects_delete",
)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a project belonging to the current user."""
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_user_id == current_user.id)
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
