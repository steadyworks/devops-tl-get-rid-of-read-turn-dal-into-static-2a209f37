from enum import Enum
from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import ColumnElement, and_, asc, desc, func, select
from sqlalchemy import exists as sa_exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from backend.db.schemas import WritableModel


class FilterOp(str, Enum):
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    IN = "in"


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


# === TypeVars ===

ModelType = TypeVar("ModelType", bound=SQLModel)

CreateSchemaType = TypeVar("CreateSchemaType", bound=WritableModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=WritableModel)


# === Exceptions ===


class InvalidFilterFieldError(ValueError):
    def __init__(self, field: str, model: type[SQLModel]) -> None:
        super().__init__(f"Invalid field '{field}' for model '{model.__name__}'")


# === DAL ===


class AsyncPostgreSQLDAL(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    IMMUTABLE_FIELDS: set[str] = {"id", "created_at"}

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def _add_and_flush(
        self,
        session: AsyncSession,
        objs: ModelType | list[ModelType],
    ) -> None:
        if isinstance(objs, list):
            session.add_all(objs)
        else:
            session.add(objs)
        await session.flush()

    def _get_column(self, field: str) -> Any:
        if not hasattr(self.model, field):
            raise InvalidFilterFieldError(field, self.model)
        return getattr(self.model, field)

    async def get_by_id(self, session: AsyncSession, id: UUID) -> Optional[ModelType]:
        return await session.get(self.model, id)

    async def get_by_ids(
        self, session: AsyncSession, ids: list[UUID]
    ) -> list[ModelType]:
        if not ids:
            return []
        id_col = getattr(self.model, "id")
        stmt = select(self.model).where(id_col.in_(ids))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        db_obj: ModelType = self.model.model_validate(obj_in)
        await self._add_and_flush(session, db_obj)
        return db_obj

    async def update_by_id(
        self, session: AsyncSession, id: UUID, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        db_obj = await session.get(self.model, id)
        if db_obj is None:
            return None
        return await self._update(session, db_obj, obj_in)

    async def _update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        update_data: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field not in self.IMMUTABLE_FIELDS and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self._add_and_flush(session, db_obj)
        return db_obj

    def _resolve_filter_condition(
        self,
        field: str,
        op: FilterOp,
        value: Any,
    ) -> ColumnElement[bool]:
        column = self._get_column(field)
        if op == FilterOp.EQ:
            return column == value
        if op == FilterOp.NE:
            return column != value
        if op == FilterOp.LT:
            return column < value
        if op == FilterOp.LTE:
            return column <= value
        if op == FilterOp.GT:
            return column > value
        if op == FilterOp.GTE:
            return column >= value
        if op == FilterOp.IN and isinstance(value, list):
            return column.in_(value)
        raise ValueError(f"Unsupported filter op: {op}")

    def _build_filter_conditions(
        self,
        filters: Optional[dict[str, tuple[FilterOp, Any]]],
    ) -> list[ColumnElement[bool]]:
        if not filters:
            return []
        return [
            self._resolve_filter_condition(f, op, v) for f, (op, v) in filters.items()
        ]

    async def list_all(
        self,
        session: AsyncSession,
        filters: Optional[dict[str, tuple[FilterOp, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[list[tuple[str, OrderDirection]]] = None,
    ) -> list[ModelType]:
        stmt = select(self.model)

        conditions = self._build_filter_conditions(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        if order_by:
            stmt = stmt.order_by(
                *[
                    desc(self._get_column(field))
                    if direction == OrderDirection.DESC
                    else asc(self._get_column(field))
                    for field, direction in order_by
                ]
            )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        session: AsyncSession,
        filters: Optional[dict[str, tuple[FilterOp, Any]]] = None,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        conditions = self._build_filter_conditions(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await session.execute(stmt)
        return result.scalar_one()

    async def exists(
        self,
        session: AsyncSession,
        filters: Optional[dict[str, tuple[FilterOp, Any]]] = None,
    ) -> bool:
        conditions = self._build_filter_conditions(filters)
        stmt = (
            select(sa_exists().where(and_(*conditions)))
            if conditions
            else select(sa_exists().select_from(self.model))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is True

    async def create_many(
        self,
        session: AsyncSession,
        objs_in: list[CreateSchemaType],
    ) -> list[ModelType]:
        db_objs = [self.model.model_validate(obj) for obj in objs_in]
        await self._add_and_flush(session, db_objs)
        return db_objs
