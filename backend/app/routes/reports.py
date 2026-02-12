"""
Reports API Routes
PDF report generation endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Report generator will be injected as dependency
_report_generator = None


def get_report_generator():
    """Dependency to get report generator"""
    if _report_generator is None:
        raise HTTPException(status_code=500, detail="Report generator not initialized")
    return _report_generator


def set_report_generator(generator):
    """Set the report generator (called during app initialization)"""
    global _report_generator
    _report_generator = generator


@router.get("/{patient_id}/cognitive-report")
async def download_cognitive_report(
    patient_id: str,
    days: int = Query(30, ge=7, le=90, description="Number of days to include in report")
):
    """
    Download cognitive health report as PDF
    
    Generates a comprehensive report including:
    - Patient profile summary
    - Cognitive metric trends (vocabulary, coherence, etc.)
    - Baseline comparison
    - Alert history
    - Recommendations for family
    
    Args:
        patient_id: Patient identifier
        days: Report period in days (7-90, default 30)
    
    Returns:
        PDF file download
    """
    generator = get_report_generator()
    
    # Generate PDF
    pdf_bytes = await generator.generate_cognitive_report(patient_id, days)
    
    if not pdf_bytes:
        raise HTTPException(status_code=500, detail="Failed to generate report")
    
    # Return as downloadable PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=cognitive-report-{patient_id}-{days}days.pdf"
        }
    )
