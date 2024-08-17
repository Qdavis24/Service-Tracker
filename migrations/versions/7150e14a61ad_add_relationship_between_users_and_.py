"""add relationship between users and services

Revision ID: 7150e14a61ad
Revises: 0ad7a5fadfb2
Create Date: 2024-08-08 20:50:14.031814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7150e14a61ad'
down_revision = '0ad7a5fadfb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=False))
        batch_op.alter_column('picture',
               existing_type=sa.BLOB(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_unique_constraint('picture', ['picture'])
        batch_op.create_foreign_key('pictures', 'pictures', ['picture'], ['id'])
        batch_op.create_foreign_key('owners', 'users', ['owner_id'], ['id'])

    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.alter_column('picture',
               existing_type=sa.BLOB(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['picture'])
        batch_op.create_foreign_key(None, 'pictures', ['picture'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('picture',
               existing_type=sa.Integer(),
               type_=sa.BLOB(),
               existing_nullable=True)

    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('picture',
               existing_type=sa.Integer(),
               type_=sa.BLOB(),
               existing_nullable=True)
        batch_op.drop_column('owner_id')

    # ### end Alembic commands ###