import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/0")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.maintenance_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "run-database-audit-every-minute": {
            "task": "system_health_and_user_metrics_audit",
            "schedule": 60.0,  # runs every 60 seconds
        },
    },
)