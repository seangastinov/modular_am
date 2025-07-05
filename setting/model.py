from typing import Optional
from sqlalchemy import Integer
from sqlmodel import Field, SQLModel, String, DateTime
from sqlalchemy.dialects.mssql import REAL
import datetime

class RegularMarket(SQLModel, table=True):
    __tablename__ = "regular_market"

    id: Optional[int] = Field(sa_type=Integer, default=None, primary_key=True)
    security_desc: str = Field(sa_type=String(255), nullable=False)
    trades: int = Field(sa_type=Integer, nullable=False)
    tta: float = Field(sa_type=REAL, nullable=False)
    open: float = Field(sa_type=REAL, nullable=False)
    high: float = Field(sa_type=REAL, nullable=False)
    low: float = Field(sa_type=REAL, nullable=False)
    ltp: float = Field(sa_type=REAL, nullable=False)
    lty: float = Field(sa_type=REAL, nullable=False)
    timestamp: datetime.datetime = Field(sa_type=DateTime, nullable=False)
