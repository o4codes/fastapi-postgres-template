from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.commons.pagination import CursorPaginationParams, CursorPagination
from app.commons.models import SoftDeleteMixin

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def create(self, schema: CreateSchemaType, **kwargs: Any) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**schema.model_dump(), **kwargs)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get a record by ID."""
        query = select(self.model).where(self.model.id == id)

        # Handle soft delete if model supports it
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_datetime.is_(None))

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_attributes(
        self,
        *,
        raise_not_found: bool = False,
        **attributes: Any,
    ) -> Optional[ModelType]:
        """
        Get a record by any combination of attributes.

        Args:
            raise_not_found: If True, raise HTTP 404 when no record is found
            **attributes: Attribute-value pairs to filter by

        Returns:
            Optional[ModelType]: The found record or None

        Raises:
            HTTPException: If raise_not_found is True and no record is found
        """
        query = select(self.model)

        # Add conditions for each attribute
        for attr, value in attributes.items():
            if hasattr(self.model, attr):
                query = query.where(getattr(self.model, attr) == value)

        # Handle soft delete if model supports it
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_datetime.is_(None))

        result = await self.db_session.execute(query)
        obj = result.scalar_one_or_none()

        if obj is None and raise_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found with given attributes",
            )

        return obj

    async def get_or_404(self, id: UUID) -> ModelType:
        """Get a record by ID or raise 404."""
        obj = await self.get(id)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return obj

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ModelType]:
        """Get a list of records with optional filtering."""
        query = select(self.model)

        # Handle soft delete if model supports it
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_datetime.is_(None))

        # Apply any additional filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        instance: ModelType,
        fields: dict[str, Any],
    ) -> ModelType:
        """
        Update a record.

        Args:
            instance: Model instance to update
            fields: Dictionary of field names and values to update

        Returns:
            Updated model instance
        """
        for field, value in fields.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        await self.db_session.commit()
        await self.db_session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Delete a record."""
        obj = await self.get_or_404(id)

        if issubclass(self.model, SoftDeleteMixin):
            # Soft delete if model supports it
            obj.deleted_time = datetime.now(tz=timezone.utc)
            await self.db_session.commit()
        else:
            # Hard delete
            await self.db_session.delete(obj)
            await self.db_session.commit()

        return True

    async def list_with_cursor(
        self,
        params: CursorPaginationParams,
        filters: dict[str, Any] | None = None,
    ) -> Tuple[List[ModelType], bool, bool, str | None, str | None]:
        """
        Get a list of records using cursor-based pagination.

        Args:
            params: Cursor pagination parameters
            filters: Additional filters to apply

        Returns:
            Tuple containing:
            - List of records
            - Whether there are more records after
            - Whether there are more records before
            - Next cursor if there are more records
            - Previous cursor if applicable
        """
        # Start building the query
        query = select(self.model)

        # Handle soft delete
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_datetime.is_(None))

        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        # Get the order field, default to id
        order_field = getattr(self.model, params.order_by or "id")

        # Parse cursor if provided
        if params.cursor:
            try:
                cursor_data = CursorPagination.decode_cursor(params.cursor)
                cursor_value = cursor_data.get("value")
                if cursor_value:
                    if params.direction == "forward":
                        query = query.where(order_field > cursor_value)
                    else:
                        query = query.where(order_field < cursor_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid cursor format",
                )

        # Apply ordering
        if params.direction == "forward":
            query = query.order_by(asc(order_field))
        else:
            query = query.order_by(desc(order_field))

        # Fetch one extra to determine if there are more results
        query = query.limit(params.limit + 1)
        result = await self.db_session.execute(query)
        items = list(result.scalars().all())

        # Determine if there are more results
        has_extra = len(items) > params.limit
        if has_extra:
            if params.direction == "forward":
                items = items[:-1]  # Remove last item
            else:
                items = items[1:]  # Remove first item

        # Create cursors
        next_cursor = None
        previous_cursor = None

        if items:
            if params.direction == "forward" and has_extra:
                next_cursor = CursorPagination.encode_cursor(
                    {"value": getattr(items[-1], params.order_by or "id")}
                )

            if params.cursor:
                previous_cursor = CursorPagination.encode_cursor(
                    {"value": getattr(items[0], params.order_by or "id")}
                )

        return items, has_extra, bool(params.cursor), next_cursor, previous_cursor

    async def count(self, **filters: Any) -> int:
        """
        Count records with optional filtering.

        Args:
            **filters: Attribute-value pairs to filter by

        Returns:
            int: Number of records matching the filters
        """
        query = select(func.count()).select_from(self.model)

        # Handle soft delete if model supports it
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_datetime.is_(None))

        # Apply any additional filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        result = await self.db_session.execute(query)
        return result.scalar_one()
