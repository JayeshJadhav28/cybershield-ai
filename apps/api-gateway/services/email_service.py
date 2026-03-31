"""
Email delivery service for CyberShield AI.

Sends OTP emails via SMTP. Falls back to console logging
when SMTP is not configured.

Supports: Resend, Gmail, Brevo, any SMTP provider.
"""

from __future__ import annotations

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from config import settings

logger = logging.getLogger(__name__)


def _is_email_configured() -> bool:
    """Check if SMTP credentials are set."""
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


async def send_otp_email(to_email: str, otp: str, purpose: str = "login") -> bool:
    """
    Send OTP email to user.

    Returns True if sent successfully, False otherwise.
    Falls back to console logging if SMTP is not configured.
    """
    if not _is_email_configured():
        # ── Dev mode: print to console ──
        logger.warning("SMTP not configured — printing OTP to console")
        print("\n" + "=" * 50)
        print(f"  🔐 OTP for {to_email}: {otp}")
        print(f"  Purpose: {purpose}")
        print("=" * 50 + "\n")
        return True

    try:
        msg = _build_otp_email(to_email, otp, purpose)

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_PORT == 465,         # SSL for port 465
            start_tls=settings.SMTP_PORT == 587,       # STARTTLS for port 587
        )

        logger.info("OTP email sent to %s", to_email)
        return True

    except aiosmtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check SMTP_USER and SMTP_PASSWORD")
        # Fallback to console so users aren't locked out
        print(f"\n🔐 OTP for {to_email}: {otp} (email delivery failed)\n")
        return False

    except Exception as exc:
        logger.exception("Failed to send OTP email to %s: %s", to_email, exc)
        # Fallback to console
        print(f"\n🔐 OTP for {to_email}: {otp} (email delivery failed)\n")
        return False


def _build_otp_email(to_email: str, otp: str, purpose: str) -> MIMEMultipart:
    """Build a nicely formatted OTP email."""
    subject_map = {
        "login": "Your CyberShield Login Code",
        "signup": "Welcome to CyberShield — Verify Your Email",
        "verify": "CyberShield Email Verification Code",
    }
    subject = subject_map.get(purpose, "Your CyberShield Verification Code")

    # ── HTML email body ──
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#0a0a0f; font-family:'Segoe UI',Roboto,sans-serif;">
        <div style="max-width:480px; margin:40px auto; background:#111118; border-radius:16px; border:1px solid #2a2a3a; overflow:hidden;">
            
            <!-- Header -->
            <div style="background:linear-gradient(135deg,#06b6d4 0%,#8b5cf6 100%); padding:32px; text-align:center;">
                <h1 style="margin:0; color:#fff; font-size:24px; font-weight:700;">
                    🛡️ CyberShield AI
                </h1>
                <p style="margin:8px 0 0; color:rgba(255,255,255,0.85); font-size:14px;">
                    Secure Verification Code
                </p>
            </div>
            
            <!-- Body -->
            <div style="padding:32px;">
                <p style="color:#a1a1aa; font-size:14px; margin:0 0 24px; line-height:1.6;">
                    {"Welcome! Use this code to verify your email and create your account:" if purpose == "signup" else "Use this one-time code to sign in to your CyberShield account:"}
                </p>
                
                <!-- OTP Code -->
                <div style="background:#1a1a24; border:2px solid #06b6d4; border-radius:12px; padding:20px; text-align:center; margin:0 0 24px;">
                    <span style="font-family:'Courier New',monospace; font-size:36px; font-weight:700; color:#06b6d4; letter-spacing:8px;">
                        {otp}
                    </span>
                </div>
                
                <p style="color:#71717a; font-size:13px; margin:0 0 8px;">
                    ⏱️ This code expires in <strong style="color:#e4e4e7;">{settings.OTP_EXPIRE_MINUTES} minutes</strong>.
                </p>
                <p style="color:#71717a; font-size:13px; margin:0 0 24px;">
                    🔒 Never share this code with anyone. CyberShield will never ask for it.
                </p>
                
                <hr style="border:none; border-top:1px solid #2a2a3a; margin:24px 0;">
                
                <!-- Security tip -->
                <div style="background:#22c55e10; border:1px solid #22c55e30; border-radius:8px; padding:12px;">
                    <p style="color:#22c55e; font-size:12px; margin:0; font-weight:600;">
                        🛡️ Security Tip
                    </p>
                    <p style="color:#a1a1aa; font-size:12px; margin:4px 0 0; line-height:1.5;">
                        If you didn't request this code, ignore this email. Report suspicious activity at 
                        <a href="https://cybercrime.gov.in" style="color:#06b6d4;">cybercrime.gov.in</a> or call 1930.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background:#0a0a0f; padding:16px 32px; text-align:center;">
                <p style="color:#52525b; font-size:11px; margin:0;">
                    CyberShield AI — India-first Cybersecurity Platform
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    # ── Plain text fallback ──
    text = f"""
CyberShield AI — Verification Code

Your one-time code: {otp}

This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.
Never share this code with anyone.

If you didn't request this, ignore this email.
Report suspicious activity at cybercrime.gov.in or call 1930.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"CyberShield AI <{settings.FROM_EMAIL}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    return msg