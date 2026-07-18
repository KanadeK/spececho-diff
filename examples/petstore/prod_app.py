from __future__ import annotations

from fastapi import FastAPI

from examples.petstore.fixture_data import PRODUCTION_ORDER, PRODUCTION_PET, PRODUCTION_PETS

app = FastAPI(title="SpecEcho production fixture")


@app.get("/pets/1")
def get_pet() -> dict[str, object]:
    return PRODUCTION_PET


@app.get("/pets")
def list_pets() -> dict[str, object]:
    return PRODUCTION_PETS


@app.get("/orders/1")
def get_order() -> dict[str, object]:
    return PRODUCTION_ORDER
