from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import mapped_column

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Common timestamp columns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MultiTenantBase(Base):
    __abstract__ = True
    # Tenant ID enforced for all multi-tenant tables
    tenant_id = Column(String, ForeignKey("tenant.id"), index=True, nullable=False)
