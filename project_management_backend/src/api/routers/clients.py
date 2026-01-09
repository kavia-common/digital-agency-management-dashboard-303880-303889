import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.api.schemas.client import ClientCreateRequest, ClientResponse, ClientUpdateRequest
from src.db.models import Client, User
from src.db.session import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


def _to_client_response(client: Client) -> ClientResponse:
    """Convert ORM Client to API response."""
    return ClientResponse(
        id=client.id,
        owner_user_id=client.owner_user_id,
        name=client.name,
        email=client.email,
        phone=client.phone,
        company=client.company,
        notes=client.notes,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.get(
    "",
    response_model=list[ClientResponse],
    summary="List clients",
    description="List the authenticated user's clients, optionally filtered by a search string.",
    operation_id="clients_list",
)
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: str | None = Query(None, description="Optional search query (matches name/company/email)."),
    limit: int = Query(50, ge=1, le=200, description="Page size."),
    offset: int = Query(0, ge=0, description="Offset for pagination."),
) -> list[ClientResponse]:
    """List clients for the current user with optional pagination/search."""
    stmt = select(Client).where(Client.owner_user_id == current_user.id)

    if q:
        like = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(Client.name).like(like)
            | func.lower(func.coalesce(Client.company, "")).like(like)
            | func.lower(func.coalesce(Client.email, "")).like(like)
        )

    stmt = stmt.order_by(Client.created_at.desc()).limit(limit).offset(offset)
    clients = list(db.scalars(stmt).all())
    return [_to_client_response(c) for c in clients]


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client by id",
    description="Fetch a single client belonging to the authenticated user.",
    operation_id="clients_get",
)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Get a client by id for the current user."""
    client = db.scalar(
        select(Client).where(Client.id == client_id, Client.owner_user_id == current_user.id)
    )
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return _to_client_response(client)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a client",
    description="Create a new client owned by the authenticated user.",
    operation_id="clients_create",
)
def create_client(
    payload: ClientCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Create a client owned by the current user."""
    client = Client(
        id=uuid.uuid4(),
        owner_user_id=current_user.id,
        name=payload.name,
        email=str(payload.email) if payload.email is not None else None,
        phone=payload.phone,
        company=payload.company,
        notes=payload.notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return _to_client_response(client)


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update a client",
    description="Update fields on an existing client owned by the authenticated user.",
    operation_id="clients_update",
)
def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Update a client belonging to the current user."""
    client = db.scalar(
        select(Client).where(Client.id == client_id, Client.owner_user_id == current_user.id)
    )
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if payload.name is not None:
        client.name = payload.name
    if payload.email is not None:
        client.email = str(payload.email)
    if payload.phone is not None:
        client.phone = payload.phone
    if payload.company is not None:
        client.company = payload.company
    if payload.notes is not None:
        client.notes = payload.notes

    db.add(client)
    db.commit()
    db.refresh(client)
    return _to_client_response(client)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a client",
    description="Delete a client owned by the authenticated user.",
    operation_id="clients_delete",
)
def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a client belonging to the current user."""
    client = db.scalar(
        select(Client).where(Client.id == client_id, Client.owner_user_id == current_user.id)
    )
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    db.delete(client)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
