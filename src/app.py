# app.py

from src.db import get_session
from src.models import Countries, Users
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, FastAPI
from uvicorn import run as serve

# initialise application object
app = FastAPI(
    title="Example API",
    description="A FastAPI application for demonstration purposes",
    version="0.0.1",
)


@app.get("/")
async def root() -> str:
    return f"Welcome to {app.title}!"


@app.post("/country")
async def create_country(session: AsyncSession = Depends(get_session)):
    """
    create_country

    """
    new_country = Countries(
        name="United Kingdom",
        iso2code="GB",
        iso3code="GBR",
    )
    session.add(new_country)
    return new_country


@app.get("/country/{iso2code}")
async def get_country(iso2code: str, session: AsyncSession = Depends(get_session)):
    """
    get_country

    """
    query = select(Countries).filter_by(iso2code=iso2code)

    result = await session.execute(query)

    return result.scalars().one()


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8765)
