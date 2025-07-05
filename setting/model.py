from typing import Optional, List, Dict
from uuid import UUID
from sqlalchemy import Integer
from sqlmodel import Column, Field, SQLModel, Text, JSON, ForeignKey
from sqlalchemy.dialects.mssql import REAL

class RegularMarket(SQLModel, table=True):
    __tablename__ = "regular_market"

    id: Optional[int] = Field(sa_type=Integer, default=None, primary_key=True)
    security_desc: str = Field(sa_type=Text, nullable=False)
    trades: int = Field(sa_type=Integer, nullable=False)
    tta: float = Field(sa_type=REAL, nullable=False)
    open: float = Field(sa_type=REAL, nullable=False)
    high: float = Field(sa_type=REAL, nullable=False)
    low: float = Field(sa_type=REAL, nullable=False)
    ltp: float = Field(sa_type=REAL, nullable=False)
    lty: float = Field(sa_type=REAL, nullable=False)
