from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    ado_project: Mapped[str] = mapped_column(String(200), default="")
    ado_repo: Mapped[str] = mapped_column(String(200), default="")
    chart_path: Mapped[str] = mapped_column(String(300), default="charts")
    values_dir: Mapped[str] = mapped_column(String(300), default="charts/values")
    default_namespace: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
