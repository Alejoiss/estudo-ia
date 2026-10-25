"""Rotas de faturas."""

from fastapi import APIRouter

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.faturas import InvoiceItemInput, InvoiceOutput
from vetclinic.services import faturas as invoice_service

router = APIRouter(prefix="/faturas", tags=["faturas"])


@router.get("/{invoice_id}", response_model=InvoiceOutput)
def get_invoice(invoice_id: int, connection: ConnectionDependency):
    """Consulta uma fatura."""
    return invoice_service.get_invoice(connection, invoice_id)


@router.post("/{invoice_id}/itens", response_model=InvoiceOutput)
def add_item_to_invoice(
    invoice_id: int, data: InvoiceItemInput, connection: ConnectionDependency
):
    """Acrescenta um item a uma fatura aberta."""
    return invoice_service.add_item_to_invoice(connection, invoice_id, data)


@router.post("/{invoice_id}/pagar", response_model=InvoiceOutput)
def pay_invoice(invoice_id: int, connection: ConnectionDependency):
    """Paga uma fatura aberta."""
    return invoice_service.pay_invoice(connection, invoice_id)
