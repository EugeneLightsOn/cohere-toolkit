"""Update conversations

Revision ID: 982bbef24559
Revises: 3f207ae41477
Create Date: 2024-06-18 13:56:50.044706

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "982bbef24559"
down_revision: Union[str, None] = "3f207ae41477"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("conversations", sa.Column("agent_id", sa.String(), nullable=True))
    op.drop_index("conversation_user_id", table_name="conversations")
    op.create_index(
        "conversation_user_agent_index",
        "conversations",
        ["user_id", "agent_id"],
        unique=False,
    )
    op.create_foreign_key(
        None, "conversations", "agents", ["agent_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "conversations", type_="foreignkey")
    op.drop_index("conversation_user_agent_index", table_name="conversations")
    op.create_index("conversation_user_id", "conversations", ["user_id"], unique=False)
    op.drop_column("conversations", "agent_id")
    # ### end Alembic commands ###
