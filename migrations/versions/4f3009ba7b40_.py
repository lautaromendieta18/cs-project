"""empty message

Revision ID: 4f3009ba7b40
Revises: a9132df31f3c
Create Date: 2022-08-21 16:29:30.365453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f3009ba7b40'
down_revision = 'a9132df31f3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('direccion', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('dni', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('enfermedades', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('medicamentos', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('operaciones', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('protesis', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('alergias', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('deporte', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'deporte')
    op.drop_column('users', 'alergias')
    op.drop_column('users', 'protesis')
    op.drop_column('users', 'operaciones')
    op.drop_column('users', 'medicamentos')
    op.drop_column('users', 'enfermedades')
    op.drop_column('users', 'dni')
    op.drop_column('users', 'direccion')
    # ### end Alembic commands ###
