"""
Demo mode schemas — pre-loaded sample data for demonstrations.
"""

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from schemas.common import AnalysisType, RiskLabel


class DemoSample(BaseModel):
    """A pre-loaded demo sample."""
    id: str = Field(..., description="Unique demo sample ID")
    type: AnalysisType
    title: str = Field(..., description="Display title for the sample")
    description: Optional[str] = Field(None, description="Brief description")
    expected_label: RiskLabel
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Pre-filled form data (for email/URL)"
    )
    file_url: Optional[str] = Field(
        None,
        description="URL to download sample file (for audio/video/QR)"
    )


class DemoSamplesResponse(BaseModel):
    """List of all available demo samples."""
    samples: List[DemoSample]