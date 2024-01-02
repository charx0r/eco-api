from __future__ import annotations
from typing import Optional, Dict, List, Any
from zoneinfo import ZoneInfo

import uuid as uuid_pkg
from fastapi.encoders import jsonable_encoder
from sqlmodel import Field, SQLModel, create_engine
from datetime import datetime
from sqlalchemy import (
    CursorResult, Insert, Select,Update,
)
from pydantic import BaseModel, ConfigDict, model_validator

sqlite_file_name = "../databases/efdatabase.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")

class EF(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    line_type: str
    elemnt_id: int
    structure: str
    element_status: str
    franch_base_name: str
    french_attribute_name: str = Field(nullable=True)
    other_french_name: str = Field(nullable=True)
    category_code: str = Field(index=True)
    french_tags: str = Field(nullable=True)
    french_unit: str = Field(nullable=True)
    contributor: str = Field(nullable=True)
    program: str = Field(nullable=True)
    program_url: str = Field(nullable=True)
    source: str = Field(nullable=True)
    location: str = Field(nullable=True)
    sub_location: str = Field(nullable=True)
    creation_date: str = Field(nullable=True)
    last_update_date: str = Field(nullable=True)
    validity_period: str = Field(nullable=True)
    uncertainty: str = Field(nullable=True)
    reglementations: str = Field(nullable=True)
    transparency: str = Field(nullable=True)
    quality: str = Field(nullable=True)
    quality_TeR: str = Field(nullable=True)
    quality_GR: str = Field(nullable=True)
    quality_TiR: str = Field(nullable=True)
    quality_C: str = Field(nullable=True)
    quality_P: str = Field(nullable=True)
    quality_M: str = Field(nullable=True)
    french_comment: str = Field(nullable=True)
    emission_type: str = Field(nullable=True)
    french_emission_type_name: str = Field(nullable=True)
    unaggregated_total: float = Field(nullable=True)
    CO2f: float = Field(nullable=True)
    CH4f: float = Field(nullable=True)
    CH4b: float = Field(nullable=True)
    N2O: float = Field(nullable=True)
    additional_gaz_1: str = Field(nullable=True)
    additional_gaz_1: str = Field(nullable=True)
    additional_gaz_value_1: float = Field(nullable=True)
    additional_gaz_1: str = Field(nullable=True)
    additional_gaz_2: str = Field(nullable=True)
    additional_gaz_value_2: float = Field(nullable=True)
    additional_gaz_3: str = Field(nullable=True)
    additional_gaz_value_3: float = Field(nullable=True)
    additional_gaz_4: str = Field(nullable=True)
    additional_gaz_value_4: float = Field(nullable=True)
    additional_gaz_5: str = Field(nullable=True)
    additional_gaz_value_5: float = Field(nullable=True)
    other_greenhouse_gas: float = Field(nullable=True)
    CO2b: float = Field(nullable=True)
    cat_1: str = Field(index=True) 
    cat_2: str = Field(index=True)
    cat_3: str = Field(index=False, nullable=True)
    cat_4: str = Field(index=False, nullable=True)
    cat_5: str = Field(index=False, nullable=True)
    cat_6: str = Field(index=False, nullable=True)
    creation_date_format: str = Field(nullable=True)
    update_date_format: str = Field(nullable=True)
    validity_period_format: str = Field(nullable=True)
    cat_id: int

class AuthTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, max_length=128)
    password: str = Field(max_length=128)

class RefreshTokens(SQLModel, table=True):
    uuid: Optional[uuid_pkg.UUID] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    refresh_token: str = Field(max_length=128)
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }

        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)

async def fetch_one(select_query: Select | Insert | Update) -> Dict[str, Any] | None:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(select_query: Select | Insert | Update) -> List[Dict[str, Any]]:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r._asdict() for r in cursor.all()]


async def execute(select_query: Insert | Update) -> None:
    async with engine.begin() as conn:
        await conn.execute(select_query)