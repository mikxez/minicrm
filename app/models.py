from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    source_assignments = relationship("OperatorSource", back_populates="operator")
    leads = relationship("LeadAssignment", back_populates="operator")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignments = relationship("LeadAssignment", back_populates="lead")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bot_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    operator_assignments = relationship("OperatorSource", back_populates="source")
    leads = relationship("LeadAssignment", back_populates="source")


class OperatorSource(Base):
    __tablename__ = "operator_sources"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    weight = Column(Integer, default=10)

    operator = relationship("Operator", back_populates="source_assignments")
    source = relationship("Source", back_populates="operator_assignments")


class LeadAssignment(Base):
    __tablename__ = "lead_assignments"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="assignments")
    source = relationship("Source", back_populates="leads")
    operator = relationship("Operator", back_populates="leads")
