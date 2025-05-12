import os
import atexit
import datetime
from sqlalchemy import create_engine, Integer, String, DateTime, ForeignKey,func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship



POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "flaskhw")

DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password = mapped_column(String(100), nullable=False)
    registered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "registered_at": self.registered_at.isoformat(),
        }
    

class Ads(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    author_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship(User, backref="ads")

    @property
    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "author": self.author.name,
        }



Base.metadata.create_all(engine)

atexit.register(engine.dispose)
