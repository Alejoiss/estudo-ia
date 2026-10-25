"""Exceções de domínio, traduzidas para respostas HTTP na camada de aplicação."""


class DomainError(Exception):
    """Base das falhas de regra de negócio; carrega a mensagem exibida ao cliente."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ResourceNotFoundError(DomainError):
    """Recurso (ou recurso referenciado no corpo) inexistente → HTTP 404."""


class StateConflictError(DomainError):
    """Operação incompatível com o estado atual do recurso → HTTP 409."""


class InvalidDataError(DomainError):
    """Dados que violam uma regra de validação de negócio → HTTP 422."""
