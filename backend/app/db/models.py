from sqlalchemy import Column, String, Float, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base, MultiTenantBase

class Tenant(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    license_tier = Column(String, default="standard")
    
    assets = relationship("Asset", back_populates="tenant", cascade="all, delete-orphan")

class Asset(MultiTenantBase):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String) # e.g., "Pump", "Compressor", "Turbine"
    operational_status = Column(String, default="healthy")
    design_life_damage = Column(Float, default=1.0) # Cumulative damage threshold
    
    tenant = relationship("Tenant", back_populates="assets")
    telemetry = relationship("TelemetrySnapshot", back_populates="asset", uselist=False)

class TelemetrySnapshot(MultiTenantBase):
    __tablename__ = "telemetry_snapshot"
    asset_id = Column(String, ForeignKey("asset.id"), primary_key=True)
    current_load = Column(Float, default=0.0)
    current_temp = Column(Float, default=0.0)
    current_damage = Column(Float, default=0.0)
    current_rul = Column(Float)
    confidence_score = Column(Float, default=1.0)
    last_update = Column(JSON) # Store raw telemetry snippet

    asset = relationship("Asset", back_populates="telemetry")

class User(MultiTenantBase):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String) # admin, engineer, viewer
    is_active = Column(Boolean, default=True)

    tenant = relationship("Tenant")

class AuditLog(MultiTenantBase):
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False) # e.g., "Asset", "RUL"
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False) # e.g., "damage_update", "violation_detected"
    old_value = Column(JSON)
    new_value = Column(JSON)
    metadata_info = Column(JSON) # e.g., source_engine, env_data
