from typing import Protocol
from uuid import UUID


class TreeNode(Protocol):
    id: UUID
    parent_id: UUID | None
    code: str