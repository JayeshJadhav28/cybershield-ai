"""
QR code analysis service — self-contained, no ML dependencies.
Decodes QR codes and analyzes content using heuristics.
"""

import io
import re
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


@dataclass
class QRAnalysisResult:
    """Result from QR analysis."""
    decoded_raw: str
    decoded_type: str
    decoded_parsed: Optional[Dict[str, Any]]
    probability: float
    confidence: float
    flags: List[str] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)
    highlights: List[Dict] = field(default_factory=list)
    processing_time_ms: int = 0
    error: Optional[str] = None

    @property
    def decoded(self) -> Dict[str, Any]:
        """Structured decoded payload for the API response."""
        return {
            "raw": self.decoded_raw,
            "type": self.decoded_type,
            "parsed": self.decoded_parsed,
        }


class QRAnalyzer:
    """Decodes and analyzes QR codes without ML dependencies."""

    # ── Public API ────────────────────────────────────────────────

    def analyze(self, image_path: str) -> QRAnalysisResult:
        """
        Decode QR code from an image file and analyze its content.

        Args:
            image_path: Path to the saved image file on disk.
        """
        start_time = time.time()

        # ── Read image bytes ──
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
        except (OSError, IOError) as exc:
            return QRAnalysisResult(
                decoded_raw="",
                decoded_type="unknown",
                decoded_parsed=None,
                probability=0.0,
                confidence=0.0,
                error=f"Could not read image file: {exc}",
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        # ── Decode QR ──
        decode_result = self._decode_qr(image_bytes)

        if not decode_result["success"]:
            return QRAnalysisResult(
                decoded_raw="",
                decoded_type="unknown",
                decoded_parsed=None,
                probability=0.0,
                confidence=0.0,
                error=decode_result.get("error", "Failed to decode QR code"),
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        raw = decode_result["raw"]
        content_type = decode_result["type"]
        parsed = decode_result["parsed"]

        # ── Analyze the decoded content ──
        analysis = self._analyze_content(raw, content_type, parsed)

        processing_time_ms = int((time.time() - start_time) * 1000)

        return QRAnalysisResult(
            decoded_raw=raw,
            decoded_type=content_type,
            decoded_parsed=parsed,
            probability=analysis["probability"],
            confidence=analysis["confidence"],
            flags=analysis["flags"],
            features=analysis["features"],
            highlights=analysis["highlights"],
            processing_time_ms=processing_time_ms,
        )

    # ── QR Decoding ───────────────────────────────────────────────

    def _decode_qr(self, image_bytes: bytes) -> Dict[str, Any]:
        """Decode QR code from image bytes. Tries pyzbar → opencv → segno."""
        raw_text = None

        # Attempt 1: pyzbar (most reliable)
        try:
            from pyzbar import pyzbar
            from PIL import Image
            img = Image.open(io.BytesIO(image_bytes))
            decoded_objects = pyzbar.decode(img)
            if decoded_objects:
                raw_text = decoded_objects[0].data.decode("utf-8", errors="replace")
                logger.info("QR decoded via pyzbar")
        except ImportError:
            logger.debug("pyzbar not available")
        except Exception as e:
            logger.debug("pyzbar decode failed: %s", e)

        # Attempt 2: OpenCV QR detector
        if raw_text is None:
            try:
                import cv2
                import numpy as np
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is not None:
                    detector = cv2.QRCodeDetector()
                    data, _, _ = detector.detectAndDecode(img)
                    if data:
                        raw_text = data
                        logger.info("QR decoded via OpenCV")
            except ImportError:
                logger.debug("OpenCV not available")
            except Exception as e:
                logger.debug("OpenCV decode failed: %s", e)

        # Attempt 3: qreader
        if raw_text is None:
            try:
                from qreader import QReader
                from PIL import Image
                import numpy as np
                img = Image.open(io.BytesIO(image_bytes))
                reader = QReader()
                results = reader.detect_and_decode(image=np.array(img))
                if results and results[0]:
                    raw_text = results[0]
                    logger.info("QR decoded via qreader")
            except ImportError:
                logger.debug("qreader not available")
            except Exception as e:
                logger.debug("qreader decode failed: %s", e)

        if raw_text is None:
            return {
                "success": False,
                "error": (
                    "Could not decode QR code. "
                    "Ensure the image contains a clear, readable QR code. "
                    "Install pyzbar or opencv-python for best results."
                ),
            }

        # ── Determine content type ──
        content_type, parsed = self._classify_content(raw_text)

        return {
            "success": True,
            "raw": raw_text,
            "type": content_type,
            "parsed": parsed,
        }

    def _classify_content(self, raw: str) -> tuple:
        """Classify decoded QR content type and parse it."""
        stripped = raw.strip()

        # UPI
        if stripped.lower().startswith("upi://"):
            return "upi", self._parse_upi(stripped)

        # URL
        if re.match(r"^https?://", stripped, re.IGNORECASE):
            return "url", {"url": stripped}

        # URL without scheme
        if re.match(r"^www\.", stripped, re.IGNORECASE):
            return "url", {"url": f"https://{stripped}"}

        # Email (mailto:)
        if stripped.lower().startswith("mailto:"):
            return "email", {"email": stripped[7:]}

        # Phone (tel:)
        if stripped.lower().startswith("tel:"):
            return "phone", {"number": stripped[4:]}

        # SMS
        if stripped.lower().startswith("sms:") or stripped.lower().startswith("smsto:"):
            return "sms", {"raw": stripped}

        # WiFi config
        if stripped.upper().startswith("WIFI:"):
            return "wifi", self._parse_wifi(stripped)

        # vCard
        if stripped.upper().startswith("BEGIN:VCARD"):
            return "vcard", {"raw": stripped[:200]}

        # Geo location
        if stripped.lower().startswith("geo:"):
            return "geo", {"raw": stripped}

        # Bitcoin / crypto
        if re.match(r"^(bitcoin|ethereum|litecoin):", stripped, re.IGNORECASE):
            return "crypto", {"raw": stripped}

        # Plain text
        return "text", {"text": stripped[:500]}

    @staticmethod
    def _parse_upi(raw: str) -> Dict[str, str]:
        """Parse UPI deep link."""
        result = {}
        try:
            parsed = urlparse(raw)
            params = parse_qs(parsed.query)
            for key in ["pa", "pn", "am", "cu", "tn", "mc", "tr"]:
                if key in params:
                    result[key] = params[key][0]
            # Friendly names
            friendly = {
                "pa": "payee_address",
                "pn": "payee_name",
                "am": "amount",
                "cu": "currency",
                "tn": "note",
            }
            friendly_result = {}
            for k, v in result.items():
                friendly_key = friendly.get(k, k)
                friendly_result[friendly_key] = v
            return friendly_result
        except Exception:
            return {"raw": raw}

    @staticmethod
    def _parse_wifi(raw: str) -> Dict[str, str]:
        """Parse WiFi QR code config."""
        result = {}
        # WIFI:S:<SSID>;T:<WPA|WEP|nopass>;P:<password>;H:<hidden>;;
        matches = re.findall(r"([STPH]):([^;]*)", raw)
        field_map = {"S": "ssid", "T": "security", "P": "password", "H": "hidden"}
        for key, value in matches:
            if key in field_map:
                result[field_map[key]] = value
        return result

    # ── Content Analysis (Heuristics) ─────────────────────────────

    def _analyze_content(
        self, raw: str, content_type: str, parsed: Optional[Dict]
    ) -> Dict[str, Any]:
        """Analyze decoded QR content for threats using heuristics."""

        flags: List[str] = []
        features: Dict[str, Any] = {"content_type": content_type, "content_length": len(raw)}
        highlights: List[Dict] = []
        score = 0.0

        if content_type == "url":
            return self._analyze_url_content(raw, parsed)

        elif content_type == "upi":
            return self._analyze_upi_content(raw, parsed or {})

        elif content_type == "text":
            # Check for hidden URLs in plain text
            url_pattern = re.findall(r"https?://[^\s]+", raw)
            if url_pattern:
                flags.append("hidden_url_in_text")
                score += 0.20
                features["embedded_urls"] = url_pattern[:5]

            # Check for suspicious text patterns
            suspicious_patterns = [
                "password", "credit card", "ssn", "social security",
                "bank account", "wire transfer", "send money",
            ]
            for pat in suspicious_patterns:
                if pat in raw.lower():
                    flags.append(f"suspicious_text: {pat}")
                    score += 0.10

            score = min(score, 1.0)
            return {
                "probability": round(score, 4),
                "confidence": 0.60,
                "flags": flags,
                "features": features,
                "highlights": highlights,
            }

        elif content_type == "wifi":
            # WiFi with no security
            if parsed and parsed.get("security", "").lower() in ("nopass", ""):
                flags.append("open_wifi_network")
                score += 0.15
            features["wifi_config"] = parsed
            return {
                "probability": round(score, 4),
                "confidence": 0.65,
                "flags": flags,
                "features": features,
                "highlights": highlights,
            }

        elif content_type == "crypto":
            flags.append("cryptocurrency_payment_request")
            score += 0.30
            features["crypto_uri"] = raw[:100]
            return {
                "probability": round(score, 4),
                "confidence": 0.70,
                "flags": flags,
                "features": features,
                "highlights": highlights,
            }

        else:
            # email, phone, sms, vcard, geo, etc.
            return {
                "probability": round(score, 4),
                "confidence": 0.55,
                "flags": flags,
                "features": features,
                "highlights": highlights,
            }

    def _analyze_url_content(
        self, raw: str, parsed: Optional[Dict]
    ) -> Dict[str, Any]:
        """Use the URL analyzer for URL-type QR content."""
        try:
            from services.url_analyzer import url_analyzer
            url_to_check = (parsed or {}).get("url", raw)
            result = url_analyzer.analyze(url_to_check)
            # Add QR-specific flag
            flags = list(result.flags) + ["url_from_qr_code"]
            return {
                "probability": result.probability,
                "confidence": result.confidence,
                "flags": flags,
                "features": result.features,
                "highlights": result.highlights,
            }
        except Exception as e:
            logger.warning("URL analysis within QR failed: %s", e)
            return {
                "probability": 0.3,
                "confidence": 0.50,
                "flags": ["url_from_qr_code", "analysis_error"],
                "features": {"url": raw[:200]},
                "highlights": [],
            }

    def _analyze_upi_content(
        self, raw: str, parsed: Dict
    ) -> Dict[str, Any]:
        """Analyze UPI payment QR code for suspicious indicators."""
        flags: List[str] = []
        features: Dict[str, Any] = {"content_type": "upi", "upi_data": parsed}
        highlights: List[Dict] = []
        score = 0.0

        payee = parsed.get("payee_address", parsed.get("pa", ""))
        amount = parsed.get("amount", parsed.get("am", ""))
        payee_name = parsed.get("payee_name", parsed.get("pn", ""))

        features["payee_address"] = payee
        features["amount"] = amount
        features["payee_name"] = payee_name

        # High amount
        try:
            amt_float = float(amount) if amount else 0
            if amt_float > 10000:
                score += 0.20
                flags.append(f"high_upi_amount: ₹{amt_float:,.2f}")
            if amt_float > 50000:
                score += 0.15
                flags.append("very_high_upi_amount")
            features["amount_value"] = amt_float
        except (ValueError, TypeError):
            features["amount_value"] = None

        # Suspicious payee patterns
        if payee and not re.match(r"^[a-zA-Z0-9._-]+@[a-zA-Z]+$", payee):
            score += 0.10
            flags.append("unusual_payee_format")

        # Generic / suspicious payee names
        suspicious_names = ["unknown", "test", "fraud", "hack", "lottery", "prize", "winner"]
        if payee_name and any(s in payee_name.lower() for s in suspicious_names):
            score += 0.15
            flags.append("suspicious_payee_name")

        score = min(score, 1.0)

        return {
            "probability": round(score, 4),
            "confidence": 0.70,
            "flags": flags,
            "features": features,
            "highlights": highlights,
        }


# Singleton instance
qr_analyzer = QRAnalyzer()