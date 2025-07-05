"""create_security_desc_index

Revision ID: 52af0f9a71cb
Revises: e19ebbc6acf5
Create Date: 2025-07-05 16:33:25.843716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '52af0f9a71cb'
down_revision: Union[str, None] = 'e19ebbc6acf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f("ix_regular_market_security_desc"), "regular_market", ["security_desc"], unique=False)



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_regular_market_security_desc"), table_name="regular_market")

