import random
from sqlalchemy.orm import Session
from app import models, crud
from app.models import *
from typing import List, Optional


class DistributionService:
    def __init__(self, db: Session):
        self.db = db

    def find_or_create_lead(self, external_id: Optional[str] = None,
                            phone: Optional[str] = None,
                            email: Optional[str] = None) -> models.Lead:
        lead = None

        if external_id:
            lead = crud.get_lead_by_external_id(self.db, external_id)
        if lead:
            return lead

        if phone:
            lead = crud.get_lead_by_phone(self.db, phone)
        if lead:
            return lead

        if email:
            lead = crud.get_lead_by_email(self.db, email)
        if lead:
            return lead

        lead_data = {
            "external_id": external_id,
            "phone": phone,
            "email": email
        }
        return crud.create_lead(self.db, lead_data)

    def get_available_operators(self, source_id: int) -> List:
        source = crud.get_source(self.db, source_id)
        if not source:
            return []

        available_operators = []

        for operator_source in source.operator_assignments:
            operator = operator_source.operator

            if not operator.is_active:
                continue

            current_load = crud.get_operator_active_assignments_count(self.db, operator.id)
            if current_load < operator.max_load:
                available_operators.append({
                    'operator': operator,
                    'weight': operator_source.weight
                })

        return available_operators

    def select_operator(self, available_operators: List) -> Optional[models.Operator]:
        if not available_operators:
            return None

        operators = [op['operator'] for op in available_operators]
        weights = [op['weight'] for op in available_operators]

        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(operators)

        selected_operator = random.choices(operators, weights=weights, k=1)[0]
        return selected_operator

    def distribute_lead(self, distribution_request) -> dict:
        lead = self.find_or_create_lead(
            external_id=distribution_request.external_id,
            phone=distribution_request.phone,
            email=distribution_request.email
        )

        source = crud.get_source_by_bot_id(self.db, distribution_request.source_bot_id)
        if not source:
            raise ValueError(f"Source with bot_id {distribution_request.source_bot_id} not found")

        available_operators = self.get_available_operators(source.id)
        selected_operator = self.select_operator(available_operators)

        assignment_data = {
            "lead_id": lead.id,
            "source_id": source.id,
            "operator_id": selected_operator.id if selected_operator else None,
            "status": "active" if selected_operator else "pending"
        }

        assignment = crud.create_lead_assignment(self.db, assignment_data)

        return {
            'lead_id': lead.id,
            'assignment_id': assignment.id,
            'operator_id': selected_operator.id if selected_operator else None,
            'status': assignment.status
        }


def redistribute_pending_assignments(self, source_id: int = None):
    query = self.db.query(LeadAssignment).filter(
        LeadAssignment.status == "pending",
        LeadAssignment.operator_id == None
    )

    if source_id:
        query = query.filter(LeadAssignment.source_id == source_id)

    pending_assignments = query.all()
    redistributed = 0

    for assignment in pending_assignments:
        available_operators = self.get_available_operators(assignment.source_id)
        selected_operator = self.select_operator(available_operators)

        if selected_operator:
            assignment.operator_id = selected_operator.id
            assignment.status = "active"
            redistributed += 1

    self.db.commit()
    return {"redistributed": redistributed, "total": len(pending_assignments)}
