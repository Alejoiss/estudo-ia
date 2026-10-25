"""Ponto de entrada ASGI: `uvicorn main:app`."""

from vetclinic.application import create_application

app = create_application()
