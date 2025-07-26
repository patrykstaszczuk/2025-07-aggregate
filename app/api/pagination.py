from typing import Generic, Type, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import BinaryExpression, ColumnElement, UnaryExpression, func, select
from sqlalchemy.orm import Session

from app.core.session import Base

T = TypeVar("T", bound=BaseModel)


class PaginatedInput:
    def __init__(self, page: int = Query(1, ge=1), per_page: int = Query(100, ge=1)):
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    meta: PageMeta
    items: list[T]


class Paginator(Generic[T]):
    def __init__(
        self,
        query,
        response_model_cls: Type[T],
        page: int = 1,
        page_size: int = 10,
        filters: list[BinaryExpression] | None = None,
        search: ColumnElement[bool] | None = None,
        sort_by: UnaryExpression | None = None,
        scalar_fields: list[str] | None = None,
    ):
        self.query = query
        self.page = page
        self.model_cls = response_model_cls
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.filters = filters or []
        self.search = search
        self.sort_by = sort_by
        self.scalar_fields = scalar_fields or []  # fields that are selected explicitly in query

    def paginate(self, session: Session) -> PaginatedResponse[T]:
        stmt = self.query.offset(self.offset).limit(self.page_size)
        count_subquery = self.query
        for f in self.filters:
            stmt = stmt.where(f)
            count_subquery = count_subquery.where(f)
        if self.search is not None:
            stmt = stmt.where(self.search)
            count_subquery = count_subquery.where(self.search)
        if self.sort_by is not None:
            stmt = stmt.order_by(self.sort_by)

        count_query = select(func.count()).select_from(count_subquery.subquery())
        total = session.execute(count_query).one()
        total = total if isinstance(total, int) else total[0]
        total_pages = (total + self.page_size - 1) // self.page_size  # type: ignore

        results = []
        for row in session.execute(stmt).all():
            result = {}
            additional_fld_idx = 0
            for item in row:
                if isinstance(item, Base):
                    result.update({col.name: getattr(item, col.name) for col in item.__table__.columns})
                else:
                    result[self.scalar_fields[additional_fld_idx]] = item
                    additional_fld_idx += 1
            results.append(result)

        items = [self.model_cls.model_validate(obj, from_attributes=True) for obj in results]  # type: ignore

        meta = PageMeta(
            page=self.page,
            page_size=self.page_size,
            total=total,  # type: ignore
            total_pages=total_pages,
        )

        return PaginatedResponse[T](meta=meta, items=items)
