"""add ingestion data models

Revision ID: a1b2c3d4e5f6
Revises: f7a8b9c0d1e2
Create Date: 2026-07-22 01:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum(
                "url",
                "pdf",
                "book_note",
                "manual",
                "generated",
                name="resource_source_type",
            ),
            nullable=False,
        ),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("publisher", sa.String(length=200), nullable=True),
        sa.Column("license", sa.String(length=120), nullable=True),
        sa.Column("attribution", sa.Text(), nullable=True),
        sa.Column("domain_reputation_score", sa.Float(), nullable=True),
        sa.Column("content_length_score", sa.Float(), nullable=True),
        sa.Column("formula_density_score", sa.Float(), nullable=True),
        sa.Column("code_example_score", sa.Float(), nullable=True),
        sa.Column("educational_structure_score", sa.Float(), nullable=True),
        sa.Column("human_review_score", sa.Float(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("raw_text_hash", sa.String(length=64), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft",
                "approved",
                "rejected",
                name="content_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_resources_raw_text_hash"), "resources", ["raw_text_hash"], unique=False
    )
    op.create_index(op.f("ix_resources_source_type"), "resources", ["source_type"], unique=False)
    op.create_index(op.f("ix_resources_status"), "resources", ["status"], unique=False)

    op.create_table(
        "topic_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("concept_id", sa.Integer(), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("target_source_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "queued",
                "collecting",
                "extracting",
                "reviewing",
                "completed",
                "failed",
                name="topic_job_status",
            ),
            nullable=False,
        ),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column(
            "created_by",
            sa.Enum(
                "user",
                "admin",
                "active_learning",
                name="topic_job_created_by",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topic_jobs_concept_id"), "topic_jobs", ["concept_id"], unique=False)
    op.create_index(op.f("ix_topic_jobs_created_by"), "topic_jobs", ["created_by"], unique=False)
    op.create_index(op.f("ix_topic_jobs_priority"), "topic_jobs", ["priority"], unique=False)
    op.create_index(op.f("ix_topic_jobs_status"), "topic_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_topic_jobs_topic_id"), "topic_jobs", ["topic_id"], unique=False)

    op.create_table(
        "extracted_objects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("topic_job_id", sa.Integer(), nullable=True),
        sa.Column(
            "object_type",
            sa.Enum(
                "concept",
                "formula",
                "example",
                "question",
                "flashcard",
                name="extracted_object_type",
            ),
            nullable=False,
        ),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("duplicate_cluster_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft",
                "approved",
                "rejected",
                name="content_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("extraction_method", sa.String(length=120), nullable=True),
        sa.Column("model_version", sa.String(length=120), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resource_id"], ["resources.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_job_id"], ["topic_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_extracted_objects_duplicate_cluster_id"),
        "extracted_objects",
        ["duplicate_cluster_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_extracted_objects_object_type"),
        "extracted_objects",
        ["object_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_extracted_objects_resource_id"),
        "extracted_objects",
        ["resource_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_extracted_objects_status"),
        "extracted_objects",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_extracted_objects_topic_job_id"),
        "extracted_objects",
        ["topic_job_id"],
        unique=False,
    )

    op.create_table(
        "job_execution_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_job_id", sa.Integer(), nullable=False),
        sa.Column(
            "stage",
            sa.Enum(
                "collecting",
                "policy_check",
                "quality_scoring",
                "extracting",
                "ai_extraction",
                "deduplication",
                "reviewing",
                "publishing",
                name="job_execution_stage",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "running",
                "succeeded",
                "failed",
                name="job_execution_status",
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("runtime_ms", sa.Integer(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("ai_usage_log_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["ai_usage_log_id"], ["ai_usage_logs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_job_id"], ["topic_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_job_execution_logs_ai_usage_log_id"),
        "job_execution_logs",
        ["ai_usage_log_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_execution_logs_stage"),
        "job_execution_logs",
        ["stage"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_execution_logs_status"),
        "job_execution_logs",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_execution_logs_topic_job_id"),
        "job_execution_logs",
        ["topic_job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_job_execution_logs_topic_job_id"), table_name="job_execution_logs")
    op.drop_index(op.f("ix_job_execution_logs_status"), table_name="job_execution_logs")
    op.drop_index(op.f("ix_job_execution_logs_stage"), table_name="job_execution_logs")
    op.drop_index(op.f("ix_job_execution_logs_ai_usage_log_id"), table_name="job_execution_logs")
    op.drop_table("job_execution_logs")
    op.execute("DROP TYPE IF EXISTS job_execution_status")
    op.execute("DROP TYPE IF EXISTS job_execution_stage")

    op.drop_index(op.f("ix_extracted_objects_topic_job_id"), table_name="extracted_objects")
    op.drop_index(op.f("ix_extracted_objects_status"), table_name="extracted_objects")
    op.drop_index(op.f("ix_extracted_objects_resource_id"), table_name="extracted_objects")
    op.drop_index(op.f("ix_extracted_objects_object_type"), table_name="extracted_objects")
    op.drop_index(
        op.f("ix_extracted_objects_duplicate_cluster_id"),
        table_name="extracted_objects",
    )
    op.drop_table("extracted_objects")
    op.execute("DROP TYPE IF EXISTS extracted_object_type")

    op.drop_index(op.f("ix_topic_jobs_topic_id"), table_name="topic_jobs")
    op.drop_index(op.f("ix_topic_jobs_status"), table_name="topic_jobs")
    op.drop_index(op.f("ix_topic_jobs_priority"), table_name="topic_jobs")
    op.drop_index(op.f("ix_topic_jobs_created_by"), table_name="topic_jobs")
    op.drop_index(op.f("ix_topic_jobs_concept_id"), table_name="topic_jobs")
    op.drop_table("topic_jobs")
    op.execute("DROP TYPE IF EXISTS topic_job_created_by")
    op.execute("DROP TYPE IF EXISTS topic_job_status")

    op.drop_index(op.f("ix_resources_status"), table_name="resources")
    op.drop_index(op.f("ix_resources_source_type"), table_name="resources")
    op.drop_index(op.f("ix_resources_raw_text_hash"), table_name="resources")
    op.drop_table("resources")
    op.execute("DROP TYPE IF EXISTS resource_source_type")
