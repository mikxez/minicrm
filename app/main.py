from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.models import *
from app.database import engine, get_db
from app.schemas import *
from app.services.distribution import DistributionService
from typing import Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini CRM", version="1.0.0")


@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    return crud.create_operator(db=db, operator=operator)


@app.get("/operators/", response_model=list[schemas.Operator])
def read_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operators = crud.get_operators(db, skip=skip, limit=limit)
    return operators


@app.post("/sources/", response_model=schemas.Source)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    return crud.create_source(db=db, source=source)


@app.get("/sources/", response_model=list[schemas.Source])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = crud.get_sources(db, skip=skip, limit=limit)
    return sources


@app.post("/sources/{source_id}/operators/")
def assign_operator_to_source(
        source_id: int,
        assignment: schemas.OperatorSourceCreate,
        db: Session = Depends(get_db)
):
    return crud.assign_operator_to_source(db=db, assignment=assignment)


@app.post("/distribute/", response_model=schemas.DistributionResponse)
def distribute_lead(request: schemas.DistributionRequest, db: Session = Depends(get_db)):
    distribution_service = DistributionService(db)

    try:
        result = distribution_service.distribute_lead(request)
        return schemas.DistributionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/leads/", response_model=list[schemas.Lead])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = crud.get_leads(db, skip=skip, limit=limit)
    return leads


@app.get("/assignments/", response_model=list[schemas.LeadAssignment])
def read_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assignments = crud.get_assignments(db, skip=skip, limit=limit)
    return assignments


@app.get("/")
def read_root():
    return {"message": "Mini CRM API is running"}


@app.get("/stats/operators-load")
def get_operators_load(db: Session = Depends(get_db)):
    operators = db.query(Operator).all()
    result = []
    for operator in operators:
        active_count = db.query(LeadAssignment).filter(
            LeadAssignment.operator_id == operator.id,
            LeadAssignment.status == "active"
        ).count()
        result.append({
            "operator_id": operator.id,
            "operator_name": operator.name,
            "current_load": active_count,
            "max_load": operator.max_load,
            "load_percentage": (active_count / operator.max_load) * 100 if operator.max_load > 0 else 0
        })
    return result


@app.get("/stats/distribution/{source_id}")
def get_distribution_stats(source_id: int, db: Session = Depends(get_db)):
    assignments = db.query(LeadAssignment).filter(
        LeadAssignment.source_id == source_id
    ).all()

    stats = {}
    for assignment in assignments:
        operator_id = assignment.operator_id
        if operator_id not in stats:
            stats[operator_id] = 0
        stats[operator_id] += 1

    return {"source_id": source_id, "distribution": stats}


@app.patch("/assignments/{assignment_id}")
def update_assignment_status(
        assignment_id: int,
        update: AssignmentUpdate,
        db: Session = Depends(get_db)
):
    assignment = db.query(LeadAssignment).filter(LeadAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.status = update.status
    db.commit()
    db.refresh(assignment)
    return assignment


@app.get("/leads/search")
def search_leads(
        phone: Optional[str] = None,
        email: Optional[str] = None,
        external_id: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Lead)

    if phone:
        query = query.filter(Lead.phone.contains(phone))
    if email:
        query = query.filter(Lead.email.contains(email))
    if external_id:
        query = query.filter(Lead.external_id.contains(external_id))

    return query.all()

@app.post("/redistribute-pending/")
def redistribute_pending(source_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = DistributionService(db)
    result = service.redistribute_pending_assignments(source_id)
    return result
