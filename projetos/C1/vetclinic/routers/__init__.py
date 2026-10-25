"""Rotas HTTP: traduzem requisições em chamadas aos serviços."""

import sqlite3
from typing import Annotated

from fastapi import Depends

from vetclinic.database import get_connection

ConnectionDependency = Annotated[sqlite3.Connection, Depends(get_connection)]
