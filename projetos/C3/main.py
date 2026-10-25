from contextlib import asynccontextmanager

from fastapi import FastAPI

import agendamentos
import atendimentos
import db
import faturas
import pets
import produtos
import tutores
import veterinarios


@asynccontextmanager
async def lifespan(_):
    db.iniciar()
    yield


app = FastAPI(title="VetClinic API", lifespan=lifespan)
for modulo in (tutores, pets, veterinarios, produtos, agendamentos, atendimentos, faturas):
    app.include_router(modulo.router)
