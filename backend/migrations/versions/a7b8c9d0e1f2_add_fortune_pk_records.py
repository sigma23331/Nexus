"""add fortune pk records

Revision ID: a7b8c9d0e1f2
Revises: a1b2c3d4e5f6
Create Date: 2026-05-31 14:30:00.000000

"""

from alembic import op


revision = "a7b8c9d0e1f2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE fortune_pk_result AS ENUM ('challenger_win', 'defender_win', 'draw');
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE fortune_pk_status AS ENUM ('pending', 'completed', 'expired');
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END $$;
        """
    )
    op.execute(
        """
        CREATE TABLE fortune_pk_records (
            id VARCHAR(64) NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
            token VARCHAR(32) NOT NULL,
            challenger_id VARCHAR(64) NOT NULL,
            challenger_score INTEGER NOT NULL,
            defender_id VARCHAR(64),
            defender_score INTEGER,
            result fortune_pk_result,
            status fortune_pk_status DEFAULT 'pending' NOT NULL,
            date DATE NOT NULL,
            completed_at TIMESTAMP WITHOUT TIME ZONE,
            FOREIGN KEY(challenger_id) REFERENCES users (id),
            FOREIGN KEY(defender_id) REFERENCES users (id),
            PRIMARY KEY (id)
        )
        """
    )
    with op.batch_alter_table("fortune_pk_records", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_token"), ["token"], unique=True)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_challenger_id"), ["challenger_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_defender_id"), ["defender_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_status"), ["status"], unique=False)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_date"), ["date"], unique=False)


def downgrade():
    with op.batch_alter_table("fortune_pk_records", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_date"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_status"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_defender_id"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_challenger_id"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_token"))
    op.execute("DROP TABLE fortune_pk_records")
    op.execute("DROP TYPE IF EXISTS fortune_pk_status")
    op.execute("DROP TYPE IF EXISTS fortune_pk_result")
