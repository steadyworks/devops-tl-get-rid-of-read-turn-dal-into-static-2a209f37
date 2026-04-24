from backend.db.data_models import Assets, Jobs, Pages, PagesAssetsRel, Photobooks
from backend.db.schemas import (
    AssetsCreate,
    AssetsUpdate,
    JobsCreate,
    JobsUpdate,
    PagesAssetsRelCreate,
    PagesAssetsRelUpdate,
    PagesCreate,
    PagesUpdate,
    PhotobooksCreate,
    PhotobooksUpdate,
)

from .base import AsyncPostgreSQLDAL, FilterOp, InvalidFilterFieldError, OrderDirection


class AssetsDAL(AsyncPostgreSQLDAL[Assets, AssetsCreate, AssetsUpdate]):
    def __init__(self) -> None:
        super().__init__(Assets)


class JobsDAL(AsyncPostgreSQLDAL[Jobs, JobsCreate, JobsUpdate]):
    def __init__(self) -> None:
        super().__init__(Jobs)


class PagesDAL(AsyncPostgreSQLDAL[Pages, PagesCreate, PagesUpdate]):
    def __init__(self) -> None:
        super().__init__(Pages)


class PagesAssetsRelDAL(
    AsyncPostgreSQLDAL[PagesAssetsRel, PagesAssetsRelCreate, PagesAssetsRelUpdate]
):
    def __init__(self) -> None:
        super().__init__(PagesAssetsRel)


class PhotobooksDAL(AsyncPostgreSQLDAL[Photobooks, PhotobooksCreate, PhotobooksUpdate]):
    def __init__(self) -> None:
        super().__init__(Photobooks)


__all__ = [
    # DALs
    "AssetsDAL",
    "JobsDAL",
    "PagesDAL",
    "PagesAssetsRelDAL",
    "PhotobooksDAL",
    # DAL base
    "AsyncPostgreSQLDAL",
    "FilterOp",
    "InvalidFilterFieldError",
    "OrderDirection",
    # Schemas
    "AssetsCreate",
    "AssetsUpdate",
    "JobsCreate",
    "JobsUpdate",
    "PagesCreate",
    "PagesUpdate",
    "PagesAssetsRelCreate",
    "PagesAssetsRelUpdate",
    "PhotobooksCreate",
    "PhotobooksUpdate",
]
