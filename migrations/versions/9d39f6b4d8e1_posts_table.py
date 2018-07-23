"""posts table

Revision ID: 9d39f6b4d8e1
Revises: fcfc0e43a982
Create Date: 2018-07-23 06:10:05.010517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d39f6b4d8e1'
down_revision = 'fcfc0e43a982'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('bracket', sa.PickleType(), nullable=True))
    op.drop_column('post', 'body')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('body', sa.VARCHAR(length=140), nullable=True))
    op.drop_column('post', 'bracket')
    # ### end Alembic commands ###
