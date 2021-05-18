"""add column for invite code

Revision ID: c6e80a722e8e
Revises: db7e361dc1da
Create Date: 2021-05-18 11:36:28.138012

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c6e80a722e8e"
down_revision = "db7e361dc1da"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("invited_members", sa.Column("invite", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("invited_members", "invite")
    # ### end Alembic commands ###
