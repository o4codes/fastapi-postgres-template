from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.file_management import schema
from app.api.file_management.services import FileService
from app.configs.db import get_db_session
from app.commons.dependencies.auth import CurrentUser
from app.commons.schemas import APIResponse

router = APIRouter(
    prefix="/files",
    tags=["File Management"],
)


@router.post(
    "/upload",
    response_model=APIResponse[schema.FileUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> schema.FileUploadResponse:
    """Upload a file."""
    service = FileService(db)
    file_record = await service.upload_file(file, current_user.id)

    download_url = await service.get_download_url(file_record.id, current_user.id)

    upload_response = schema.FileUploadResponse(
        file_id=file_record.id,
        filename=file_record.original_filename,
        size=file_record.size,
        download_url=download_url or "",
    )

    return APIResponse(
        status=True,
        message="File uploaded successfully",
        data=upload_response,
    )


@router.get(
    "/{file_id}",
    response_model=APIResponse[schema.FileResponse],
    summary="Get file details",
)
async def get_file(
    file_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> schema.FileResponse:
    """Get file details."""
    service = FileService(db)
    file_record = await service.get_file(str(file_id), current_user.id)

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    return APIResponse(
        status=True,
        message="Retrieved file details",
        data=file_record,
    )


@router.get(
    "/{file_id}/download",
    summary="Get file download URL",
)
async def get_download_url(
    file_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse[str]:
    """Get download URL for file."""
    service = FileService(db)
    download_url = await service.get_download_url(str(file_id), current_user.id)

    if not download_url:
        raise HTTPException(
            status_code=404, detail="File not found or download URL unavailable"
        )

    return APIResponse(
        status=True,
        message="Retrieved download URL",
        data=download_url,
    )


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
)
async def delete_file(
    file_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a file."""
    service = FileService(db)
    success = await service.delete_file(str(file_id), current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="File not found")
