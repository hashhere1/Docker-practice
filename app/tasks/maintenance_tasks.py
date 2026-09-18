from datetime import datetime, timezone
from sqlalchemy import func
from app.core.celery_app import celery_app
from app.database import SessionLocal
from app.models.users import User, Profile


@celery_app.task(name="system_health_and_user_metrics_audit")
def system_health_and_user_metrics_audit() -> dict:

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        total_users = db.query(func.count(User.id)).scalar() or 0
        total_profiles = db.query(func.count(Profile.id)).scalar() or 0
        latest_user = db.query(User.username).order_by(User.id.desc()).first()
        latest_username = latest_user[0] if latest_user else "None"

        banner = "=" * 65
        print(f"\n{banner}", flush=True)
        print(f" [CELERY BEAT SCHEDULED AUDIT]  {now}", flush=True)
        print(f"{banner}", flush=True)
        print(f"  * Total Registered Users   : {total_users}", flush=True)
        print(f"  * Total Active Profiles    : {total_profiles}", flush=True)
        print(f"  * Most Recent User Created : {latest_username}", flush=True)
        print(f"  * System Status            : HEALTHY / CONNECTED", flush=True)
        print(f"{banner}\n", flush=True)

        return {
            "timestamp": now,
            "total_users": total_users,
            "total_profiles": total_profiles,
            "latest_user": latest_username,
            "status": "HEALTHY",
        }
    finally:
        db.close()