"""
Demo routes — pre-loaded sample data for demonstrations and training sessions.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.demo import DemoSample, DemoSamplesResponse
from schemas.common import AnalysisType, RiskLabel

router = APIRouter()

DEMO_SAMPLES = [
    DemoSample(
        id="demo_phishing_email_dangerous",
        type=AnalysisType.EMAIL,
        title="🔴 Phishing Email — SBI Account Suspension",
        description="Classic phishing email impersonating SBI with urgency, credential request, and fake domain.",
        expected_label=RiskLabel.DANGEROUS,
        data={
            "subject": "URGENT: Your SBI account will be suspended in 24 hours",
            "body": (
                "Dear Valued Customer,\n\n"
                "We have detected suspicious activity on your SBI account ending in ****1234. "
                "Your account will be permanently suspended within 24 hours if you do not verify "
                "your identity immediately.\n\n"
                "Click the link below to verify your account:\n"
                "http://sbi-secure-verify.xyz/customer/login\n\n"
                "You will need to provide:\n"
                "- Your Internet Banking User ID\n"
                "- Password\n"
                "- Registered Mobile OTP\n\n"
                "Failure to comply will result in permanent account closure.\n\n"
                "Regards,\nSBI Security Team\nState Bank of India"
            ),
            "sender": "security.alert@sbi-notifications.xyz",
            "urls": ["http://sbi-secure-verify.xyz/customer/login"],
        },
    ),
    DemoSample(
        id="demo_safe_email",
        type=AnalysisType.EMAIL,
        title="🟢 Legitimate Email — Monthly Statement",
        description="A genuine bank email notification about a monthly account statement.",
        expected_label=RiskLabel.SAFE,
        data={
            "subject": "Your January 2024 Account Statement is Ready",
            "body": (
                "Dear Customer,\n\n"
                "Your account statement for the month of January 2024 is now available for viewing "
                "through HDFC Bank NetBanking.\n\n"
                "Please log in to your NetBanking account at www.hdfcbank.com to view and download "
                "your statement.\n\n"
                "For any queries, please call our 24x7 helpline at 1800-202-6161.\n\n"
                "Warm regards,\nHDFC Bank"
            ),
            "sender": "statements@hdfcbank.com",
            "urls": ["https://www.hdfcbank.com"],
        },
    ),
    DemoSample(
        id="demo_suspicious_email",
        type=AnalysisType.EMAIL,
        title="🟡 Suspicious Email — KYC Update Request",
        description="Email with some suspicious elements but not as obvious as typical phishing.",
        expected_label=RiskLabel.SUSPICIOUS,
        data={
            "subject": "Important: Complete Your KYC Update",
            "body": (
                "Dear Customer,\n\n"
                "As per RBI guidelines, all bank customers must update their KYC details periodically. "
                "Our records show that your KYC is pending verification.\n\n"
                "Please complete your KYC update by visiting the link below:\n"
                "https://kyc-update-portal.com/verify\n\n"
                "Documents required: Aadhaar Card, PAN Card\n\n"
                "If you have recently updated your KYC, please ignore this email.\n\n"
                "Thank you,\nCustomer Service Team"
            ),
            "sender": "kyc-update@bank-notifications.com",
            "urls": ["https://kyc-update-portal.com/verify"],
        },
    ),
    DemoSample(
        id="demo_suspicious_url",
        type=AnalysisType.URL,
        title="🟡 Suspicious URL — Fake Payment Portal",
        description="URL with suspicious domain keywords and non-standard TLD.",
        expected_label=RiskLabel.SUSPICIOUS,
        data={
            "url": "https://secure-payment-verify.com/upi/confirm",
        },
    ),
    DemoSample(
        id="demo_dangerous_url",
        type=AnalysisType.URL,
        title="🔴 Dangerous URL — IP Address Phishing",
        description="URL using raw IP address with bank-related path. Strong phishing indicator.",
        expected_label=RiskLabel.DANGEROUS,
        data={
            "url": "http://192.168.1.100/sbi/netbanking/login/verify",
        },
    ),
    DemoSample(
        id="demo_safe_url",
        type=AnalysisType.URL,
        title="🟢 Legitimate URL — Official HDFC Bank",
        description="Official HDFC Bank website URL.",
        expected_label=RiskLabel.SAFE,
        data={
            "url": "https://www.hdfcbank.com/personal/pay/cards/credit-cards",
        },
    ),
    DemoSample(
        id="demo_deepfake_audio",
        type=AnalysisType.AUDIO,
        title="🔴 Suspected Deepfake Voice Clone",
        description="Audio sample with potential AI-generated speech characteristics. Upload a WAV file to analyze.",
        expected_label=RiskLabel.DANGEROUS,
        file_url="/api/v1/demo/files/deepfake_audio.wav",
    ),
    DemoSample(
        id="demo_genuine_audio",
        type=AnalysisType.AUDIO,
        title="🟢 Genuine Human Speech",
        description="Natural human speech recording for comparison. Upload a WAV file to analyze.",
        expected_label=RiskLabel.SAFE,
        file_url="/api/v1/demo/files/genuine_audio.wav",
    ),
    DemoSample(
        id="demo_deepfake_video",
        type=AnalysisType.VIDEO,
        title="🟡 Suspected Deepfake Video",
        description="Video clip with potential face manipulation artifacts. Upload to analyze.",
        expected_label=RiskLabel.SUSPICIOUS,
        file_url="/api/v1/demo/files/deepfake_video.mp4",
    ),
]


@router.get(
    "/samples",
    response_model=DemoSamplesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get demo samples",
    description="Returns pre-loaded sample data for each analyzer. Use these for demonstrations and training.",
)
async def get_demo_samples():
    return DemoSamplesResponse(samples=DEMO_SAMPLES)


@router.get(
    "/samples/{sample_id}",
    response_model=DemoSample,
    status_code=status.HTTP_200_OK,
    summary="Get a specific demo sample",
)
async def get_demo_sample(sample_id: str):
    for sample in DEMO_SAMPLES:
        if sample.id == sample_id:
            return sample

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Demo sample not found")