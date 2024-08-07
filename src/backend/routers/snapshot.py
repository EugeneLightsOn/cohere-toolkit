from typing import Any

from fastapi import APIRouter, HTTPException, Request

from backend.chat.collate import to_dict
from backend.config.routers import RouterName
from backend.crud import snapshot as snapshot_crud
from backend.database_models import Snapshot as SnapshotModel
from backend.database_models import SnapshotAccess as SnapshotAccessModel
from backend.database_models import SnapshotLink as SnapshotLinkModel
from backend.database_models.database import DBSessionDep
from backend.schemas.snapshot import (
    CreateSnapshot,
    CreateSnapshotResponse,
    Snapshot,
    SnapshotAccess,
    SnapshotAgent,
    SnapshotData,
    SnapshotLink,
    SnapshotWithLinks,
)
from backend.services.snapshot import (
    create_conversation_dict,
    remove_private_keys,
    validate_conversation,
    validate_last_message,
    validate_snapshot_exists,
    validate_snapshot_link,
    wrap_create_snapshot,
    wrap_create_snapshot_access,
    wrap_create_snapshot_link,
)

router = APIRouter(prefix="/v1/snapshots")
router.name = RouterName.SNAPSHOT

PRIVATE_KEYS = ["organization_id", "user_id", "conversation_id"]


@router.post("", response_model=CreateSnapshotResponse)
async def create_snapshot(
    snapshot_request: CreateSnapshot, session: DBSessionDep, request: Request
) -> CreateSnapshotResponse:
    """
    Create a new snapshot and snapshot link to share the conversation.

    Args:
        snapshot_request (CreateSnapshot): Snapshot creation request.
        session (DBSessionDep): Database session.
        request (Request): HTTP request object.

    Returns:
        CreateSnapshotResponse: Snapshot creation response.
    """
    user_id = request.headers.get("User-Id")
    conversation_id = snapshot_request.conversation_id

    # Check if conversation exists, if it has messages and if a snapshot already exists
    conversation = validate_conversation(session, conversation_id, user_id)

    last_message_id = conversation.messages[-1].id if conversation.messages else None
    validate_last_message(last_message_id)

    snapshot = snapshot_crud.get_snapshot_by_last_message_id(session, last_message_id)

    if not snapshot:
        snapshot = wrap_create_snapshot(session, last_message_id, user_id, conversation)

    snapshot_link = wrap_create_snapshot_link(session, snapshot.id, user_id)

    return CreateSnapshotResponse(
        link_id=snapshot_link.id,
        snapshot_id=snapshot.id,
        user_id=user_id,
        messages=snapshot.snapshot.get("messages", []),
    )


@router.get("", response_model=list[SnapshotWithLinks])
async def list_snapshots(
    session: DBSessionDep, request: Request
) -> list[SnapshotWithLinks]:
    """
    List all snapshots.

    Args:
        session (DBSessionDep): Database session.
        request (Request): HTTP request object.

    Returns:
        list[Snapshot]: List of all snapshots.
    """
    user_id = request.headers.get("User-Id")

    snapshots = snapshot_crud.list_snapshots(session, user_id)

    # Get snapshot links for each snapshot
    response = []
    for snapshot in snapshots:
        snapshot_links = snapshot_crud.list_snapshot_links(session, snapshot.id)
        snapshot_links = [link.id for link in snapshot_links]
        snapshot_dict = to_dict(Snapshot.model_validate(snapshot))
        snapshot_with_links = SnapshotWithLinks.model_validate(
            snapshot_dict | {"links": snapshot_links}
        )
        response.append(snapshot_with_links)

    return response


@router.get("/link/{link_id}", response_model=Snapshot)
async def get_snapshot(
    link_id: str, session: DBSessionDep, request: Request
) -> Snapshot:
    """
    Get a snapshot by link ID.

    Args:
        link_id (str): Snapshot link ID.
        session (DBSessionDep): Database session.
        request (Request): HTTP request object.

    Returns:
        Snapshot: Snapshot with the given link ID.
    """
    user_id = request.headers.get("User-Id")

    snapshot = validate_snapshot_link(session, link_id)

    wrap_create_snapshot_access(session, snapshot.id, user_id, link_id)

    return snapshot


@router.delete("/link/{link_id}")
async def delete_snapshot_link(
    link_id: str, session: DBSessionDep, request: Request
) -> Any:
    """
    Delete a snapshot link by ID.

    Args:
        link_id (str): Snapshot link ID.
        session (DBSessionDep): Database session.
        request (Request): HTTP request object.

    Returns:
        Any: Empty response.
    """
    user_id = request.headers.get("User-Id")

    snapshot = validate_snapshot_link(session, link_id)

    # Anyone can get the snapshot link, but only the user that created it can delete it
    if user_id != snapshot.user_id:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to delete this snapshot link",
        )

    snapshot_crud.delete_snapshot_link(session, link_id, user_id)

    return {}


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: str, session: DBSessionDep, request: Request
) -> Any:
    """
    Delete a snapshot by ID.

    Args:
        snapshot_id (str): Snapshot ID.
        session (DBSessionDep): Database session.
        request (Request): HTTP request object.

    Returns:
        Any: Empty response.
    """
    user_id = request.headers.get("User-Id")

    snapshot = validate_snapshot_exists(session, snapshot_id)

    # Anyone can get the snapshot, but only the user that created it can delete it
    if user_id != snapshot.user_id:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to delete this snapshot",
        )

    snapshot_crud.delete_snapshot(session, snapshot_id, user_id)

    return {}
