from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

_now = lambda: datetime.now(timezone.utc)


class Territory(Base):
    __tablename__ = "territories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    seed_data = relationship("SeedData", back_populates="territory")
    news = relationship("News", back_populates="territory")


class SeedData(Base):
    __tablename__ = "seed_data"
    __table_args__ = (
        UniqueConstraint("territory_id", "name", "date", name="uq_seed_data_territory_crop_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    territory_id = Column(Integer, ForeignKey("territories.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    date = Column(DateTime(timezone=True), default=_now, nullable=False)

    territory = relationship("Territory", back_populates="seed_data")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    territory_id = Column(Integer, ForeignKey("territories.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), default=_now, nullable=False)

    territory = relationship("Territory", back_populates="news")


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint("currency", "date", name="uq_exchange_rate_currency_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(3), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    rate = Column(Numeric(12, 4), nullable=False)


class ETLRun(Base):
    __tablename__ = "etl_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    status = Column(String, nullable=False, default="running")  # running | success | failed
    seed_data_count = Column(Integer, default=0)
    news_count = Column(Integer, default=0)
    data_source = Column(String)  # world_bank | mock
    error = Column(Text)
