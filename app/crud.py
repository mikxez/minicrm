from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OperatorBase(BaseModel):
    name: str
    email: str
    is_active: bool = True
    max_load: int = 10


class OperatorCreate(OperatorBase):
    pass


class Operator(OperatorBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SourceBase(BaseModel):
    name: str
    bot_id: str


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class OperatorSourceBase(BaseModel):
    operator_id: int
    source_id: int
    weight: int = 10


class OperatorSourceCreate(OperatorSourceBase):
    pass


class OperatorSource(OperatorSourceBase):
    id: int

    class Config:
        orm_mode = True


class LeadBase(BaseModel):
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class Lead(LeadBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class LeadAssignmentBase(BaseModel):
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None


class LeadAssignmentCreate(LeadAssignmentBase):
    pass


class LeadAssignment(LeadAssignmentBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class DistributionRequest(BaseModel):
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    source_bot_id: str


class DistributionResponse(BaseModel):
    lead_id: int
    assignment_id: int
    operator_id: Optional[int] = None
    status: str
