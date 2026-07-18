from __future__ import annotations

from fastapi import FastAPI, Response

from examples.petstore.fixture_data import STAGING_ORDER, STAGING_PET, STAGING_PETS

app = FastAPI(title="SpecEcho staging fixture")


@app.get("/pets/1")
def get_pet() -> dict[str, object]:
    return STAGING_PET


@app.get("/pets")
def list_pets() -> dict[str, object]:
    return STAGING_PETS


@app.get("/orders/1")
def get_order(response: Response) -> dict[str, object]:
    response.status_code = 202
    return STAGING_ORDER
