# Import all the models, so that Base clinical has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.db.models import Tenant, Asset, TelemetrySnapshot, User, AuditLog  # noqa
