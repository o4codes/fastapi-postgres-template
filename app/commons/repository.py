from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.commons.models import SoftDeleteMixin

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
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
            query = query.where(self.model.deleted_at.is_(None))
            
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
            query = query.where(self.model.deleted_at.is_(None))
            
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
            query = query.where(self.model.deleted_at.is_(None))
            
        # Apply any additional filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
                
        query = query.offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        id: UUID,
        schema: UpdateSchemaType,
        **kwargs: Any,
    ) -> Optional[ModelType]:
        """Update a record."""
        obj = await self.get_or_404(id)
        update_data = schema.model_dump(exclude_unset=True)
        update_data.update(kwargs)
        
        for field, value in update_data.items():
            setattr(obj, field, value)
            
        await self.db_session.commit()
        await self.db_session.refresh(obj)
        return obj

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
