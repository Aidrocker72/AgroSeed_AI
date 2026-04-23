from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

_now = lambda: datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)

    forecasts = relationship("Forecast", back_populates="user")


class Territory(Base):
    __tablename__ = "territories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    seed_data = relationship("SeedData", back_populates="territory")
    news = relationship("News", back_populates="territory")
    forecasts = relationship("Forecast", back_populates="territory")


class SeedData(Base):
    __tablename__ = "seed_data"

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


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    territory_id = Column(Integer, ForeignKey("territories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    raw_data = Column(JSON, nullable=False)
    ai_result = Column(JSON, nullable=False)

    user = relationship("User", back_populates="forecasts")
    territory = relationship("Territory", back_populates="forecasts")
