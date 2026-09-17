"""Top-level HTTP routes."""

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse

from app.repositories.transaction_repository import TransactionRepository
from app.schemas import ImportResult
from app.services.import_service import ImportService, MissingColumnsError

router = APIRouter()

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ACCEPTED_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
    "application/octet-stream",
}

_repository = TransactionRepository()


def get_import_service() -> ImportService:
    """Provide the import service; overridable in tests for isolation."""
    return ImportService(_repository)


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return the service availability status."""
    return {"status": "ok"}


@router.post("/imports", tags=["imports"], status_code=201)
async def create_import(
    file: UploadFile | None = None,
    import_service: ImportService = Depends(get_import_service),
) -> JSONResponse:
    """Import a CSV file of transactions synchronously."""
    if file is None or not file.filename:
        return _error(400, "file_missing", "Fișierul CSV este obligatoriu.")

    if not _is_accepted(file):
        return _error(
            415,
            "unsupported_media_type",
            "Tipul de conținut al fișierului nu este acceptat.",
        )

    content = await file.read()
    if not content:
        return _error(400, "file_empty", "Fișierul CSV este gol.")
    if len(content) > MAX_FILE_SIZE_BYTES:
        return _error(
            413,
            "file_too_large",
            "Fișierul CSV depășește dimensiunea maximă permisă.",
        )

    try:
        stats = import_service.import_csv(content)
    except MissingColumnsError as error:
        return JSONResponse(
            status_code=422,
            content={
                "code": "invalid_csv_columns",
                "message": "Fișierul CSV nu conține toate coloanele obligatorii.",
                "details": {"missing_columns": error.missing_columns},
            },
        )

    return JSONResponse(status_code=201, content=ImportResult(**stats).model_dump())


def _is_accepted(file: UploadFile) -> bool:
    if file.content_type in ACCEPTED_CONTENT_TYPES:
        return True
    return bool(file.filename and file.filename.lower().endswith(".csv"))


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})