"""API endpoints for AI Document Drafting.

POST /api/draft/generate — Generate document text via LLM
POST /api/draft/export   — Convert finalized text to downloadable PDF

Security rules:
- PDFs are NEVER stored on the server
- Generated in-memory (BytesIO), streamed to user, immediately discarded
- Every PDF contains the mandatory AI disclaimer on page 1
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.draft import (
    DraftGenerateRequest,
    DraftGenerateResponse,
    DraftExportRequest,
    DocumentType,
)
from app.services.draft_service import (
    generate_draft_text,
    export_to_pdf,
    DOCUMENT_TITLES,
    DISCLAIMER_TEXT,
)

logger = logging.getLogger("lexindia.routers.draft")
router = APIRouter(tags=["Document Drafting"])


# ── Generate Document Text ────────────────────────────────────────────────

@router.post("/draft/generate", response_model=DraftGenerateResponse)
async def generate_draft(request: DraftGenerateRequest):
    """Generate an AI-drafted legal document.

    Accepts party details, incident information, and optional law context
    from search results. Returns the draft text for user review before
    PDF export.

    The draft is returned as plain text — not yet a PDF. The user can
    review and edit before calling /api/draft/export.
    """
    logger.info(
        f"Draft request: type={request.document_type.value}, "
        f"sender={request.sender.full_name}"
    )

    # Validate rental-specific requirements
    if (
        request.document_type == DocumentType.RENTAL_AGREEMENT
        and not request.rental_details
    ):
        raise HTTPException(
            status_code=422,
            detail="rental_details is required when document_type is 'rental_agreement'.",
        )

    try:
        draft_text = await generate_draft_text(request)
    except RuntimeError as e:
        logger.error(f"Draft generation failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="All AI providers are currently unavailable. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in draft generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the document.",
        )

    return DraftGenerateResponse(
        document_type=request.document_type,
        draft_text=draft_text,
        language=request.language,
        disclaimer=DISCLAIMER_TEXT,
    )


# ── Export to PDF ─────────────────────────────────────────────────────────

@router.post("/draft/export")
async def export_draft_pdf(request: DraftExportRequest):
    """Convert finalized document text into a downloadable PDF.

    The PDF is generated in-memory and streamed directly to the client.
    It is NEVER written to disk or stored in any database.

    Every PDF includes:
    - Page 1 bold disclaimer
    - Professional footer on every page
    """
    logger.info(
        f"PDF export: type={request.document_type.value}, "
        f"text_length={len(request.draft_text)}"
    )

    try:
        pdf_buffer = export_to_pdf(
            draft_text=request.draft_text,
            document_type=request.document_type,
            title=request.title,
        )
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF. Please try again.",
        )

    # Build a clean filename
    type_slug = request.document_type.value.replace("_", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"lexindia-{type_slug}-{timestamp}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
    )
