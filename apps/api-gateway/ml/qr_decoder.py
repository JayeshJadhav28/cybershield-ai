"""
QR code decoding and UPI content parsing.
"""

import re
from typing import Dict, Optional
from urllib.parse import unquote

import cv2
import numpy as np
from PIL import Image
import io


class QRDecoder:
    """Decode QR codes from images and parse content."""

    def decode_image(self, image_bytes: bytes) -> Dict:
        """
        Decode QR code from image bytes.
        Returns decoded content or error.
        """
        result = {
            "success": False,
            "raw": "",
            "type": "unknown",
            "parsed": None,
            "error": None,
        }

        try:
            # Try OpenCV QR decoder first (faster)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                result["error"] = "Could not decode image"
                return result

            # Try multiple preprocessing strategies for better detection
            decoded_text = self._try_opencv_decode(img)

            # Fall back to pyzbar if OpenCV fails
            if not decoded_text:
                decoded_text = self._try_pyzbar_decode(image_bytes)

            if not decoded_text:
                result["error"] = "No QR code found in image"
                return result

            result["success"] = True
            result["raw"] = decoded_text
            result["type"], result["parsed"] = self._classify_and_parse(decoded_text)

        except Exception as e:
            result["error"] = f"QR decode error: {str(e)}"

        return result

    def _try_opencv_decode(self, img: np.ndarray) -> Optional[str]:
        """Try decoding with OpenCV QR code detector."""
        try:
            detector = cv2.QRCodeDetector()

            # Try original image
            decoded, _, _ = detector.detectAndDecode(img)
            if decoded:
                return decoded

            # Try grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            decoded, _, _ = detector.detectAndDecode(gray)
            if decoded:
                return decoded

            # Try with contrast enhancement
            enhanced = cv2.equalizeHist(gray)
            decoded, _, _ = detector.detectAndDecode(enhanced)
            if decoded:
                return decoded

        except Exception:
            pass
        return None

    def _try_pyzbar_decode(self, image_bytes: bytes) -> Optional[str]:
        """Try decoding with pyzbar library."""
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode
            pil_image = Image.open(io.BytesIO(image_bytes))
            barcodes = pyzbar_decode(pil_image)
            if barcodes:
                return barcodes[0].data.decode("utf-8")
        except ImportError:
            pass  # pyzbar not available
        except Exception:
            pass
        return None

    def _classify_and_parse(self, raw: str) -> tuple:
        """
        Classify QR content type and parse structured data.
        Returns (type_string, parsed_dict)
        """
        raw = raw.strip()

        # UPI payment URL
        if raw.lower().startswith("upi://"):
            return "upi", self._parse_upi_url(raw)

        # Regular URLs
        if raw.lower().startswith(("http://", "https://")):
            return "url", {"url": raw}

        # Phone number
        if re.match(r"^\+?[\d\s\-().]{7,15}$", raw):
            return "phone", {"number": raw}

        # Email address
        if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", raw):
            return "email", {"email": raw}

        # Plain text
        return "text", {"content": raw}

    def _parse_upi_url(self, url: str) -> Dict:
        """Parse UPI payment URL into structured fields."""
        parsed = {
            "upi_id": None,
            "payee_name": None,
            "amount": None,
            "currency": "INR",
            "note": None,
            "merchant_code": None,
        }

        try:
            # Extract query parameters
            query_start = url.find("?")
            if query_start == -1:
                return parsed

            query_str = url[query_start + 1:]
            for param in query_str.split("&"):
                if "=" not in param:
                    continue
                key, value = param.split("=", 1)
                value = unquote(value)

                mapping = {
                    "pa": "upi_id",
                    "pn": "payee_name",
                    "am": "amount",
                    "cu": "currency",
                    "tn": "note",
                    "mc": "merchant_code",
                }
                if key in mapping:
                    parsed[mapping[key]] = value

        except Exception:
            pass

        return parsed


# Singleton instance
qr_decoder = QRDecoder()