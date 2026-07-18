from __future__ import annotations

STAGING_PET = {
    "id": "1",
    "name": "Miso",
    "species": "fox",
    "age": 4,
    "nickname": "Mimi",
}

PRODUCTION_PET = {
    "id": 1,
    "name": "Miso",
    "species": "cat",
    "status": "available",
    "age": 3,
}

STAGING_PETS = {
    "count": "1",
    "items": [STAGING_PET],
}

PRODUCTION_PETS = {
    "count": 1,
    "items": [PRODUCTION_PET],
}

STAGING_ORDER = {
    "id": 1,
    "petId": 1,
    "status": "cancelled",
    "total": "42.00",
    "coupon": "SUMMER",
}

PRODUCTION_ORDER = {
    "id": 1,
    "petId": 1,
    "status": "paid",
    "total": 42.0,
}
