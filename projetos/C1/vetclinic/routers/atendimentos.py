"""Rotas de consulta de atendimentos."""

from fastapi import APIRouter

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.atendimentos import TreatmentOutput
from vetclinic.services import atendimentos as treatment_service

router = APIRouter(prefix="/atendimentos", tags=["atendimentos"])


@router.get("/{treatment_id}", response_model=TreatmentOutput)
def get_treatment(treatment_id: int, connection: ConnectionDependency):
    """Consulta um atendimento."""
    return treatment_service.get_treatment_with_invoice(connection, treatment_id)
