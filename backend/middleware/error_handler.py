"""
EduPath AI - Centralized Error Handling Middleware & Handlers
Catches unhandled exceptions and prevents stack trace leakage in responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("edupath.errors")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format Pydantic schema validation errors cleanly."""
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        errors.append({"field": field, "message": msg})
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Unprocessable Entity",
            "message": "Input validation failed. Please check the supplied parameters.",
            "details": errors
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for internal server errors preventing stack trace exposure."""
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An internal error occurred while processing your request. Please try again shortly."
        }
    )
