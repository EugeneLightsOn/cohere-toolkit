"""Modify Agent Tool metadata

Revision ID: a48691a80366
Revises: 2d766d30a3d2
Create Date: 2024-06-28 17:09:51.378370

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a48691a80366"
down_revision: Union[str, None] = "2d766d30a3d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "_user_agent_tool_name_type_uc", "agent_tool_metadata", type_="unique"
    )
    op.create_unique_constraint(
        "_user_agent_tool_name_uc",
        "agent_tool_metadata",
        ["user_id", "agent_id", "tool_name"],
    )
    op.drop_column("agent_tool_metadata", "type")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "agent_tool_metadata",
        sa.Column("type", sa.TEXT(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(
        "_user_agent_tool_name_uc", "agent_tool_metadata", type_="unique"
    )
    op.create_unique_constraint(
        "_user_agent_tool_name_type_uc",
        "agent_tool_metadata",
        ["user_id", "agent_id", "tool_name", "type"],
    )
