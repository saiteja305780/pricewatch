from datetime import datetime, timezone
from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite:///pricewatch.db")
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def now():
    return datetime.now(timezone.utc)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    store: Mapped[str] = mapped_column(String, index=True)
    variant_id: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str]
    title: Mapped[str]
    vendor: Mapped[str]
    category: Mapped[str]
    first_seen: Mapped[datetime] = mapped_column(default=now)

class PricePoint(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    price: Mapped[float]
    compare_at_price: Mapped[float | None]
    in_stock: Mapped[bool]
    scraped_at: Mapped[datetime] = mapped_column(default=now)

class ScrapeRun(Base):
    __tablename__ = "scrape_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    store: Mapped[str]
    started_at: Mapped[datetime] = mapped_column(default=now)
    finished_at: Mapped[datetime | None]
    new_count: Mapped[int] = mapped_column(default=0)
    changed_count: Mapped[int] = mapped_column(default=0)
    unchanged_count: Mapped[int] = mapped_column(default=0)

def init_db():
    Base.metadata.create_all(engine)