"""Update Task model with owner relationship

Revision ID: bb332ab521bf
Revises: 
Create Date: 2024-08-12 04:04:02.412774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb332ab521bf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
        batch_op.drop_column('admin')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('admin', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###
