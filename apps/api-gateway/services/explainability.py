"""
Generates human-readable explanations from scoring output.
"""

TIPS = {
    "email": {
        "safe": "This email appears legitimate, but never share passwords or OTPs via email.",
        "suspicious": "Be cautious. Verify the sender through official channels before clicking links.",
        "dangerous": "This email shows strong phishing signs. Do NOT click links. Report at cybercrime.gov.in or call 1930.",
    },
    "url": {
        "safe": "This URL appears legitimate. Always check for HTTPS before entering sensitive info.",
        "suspicious": "This URL has concerning characteristics. Avoid entering personal information.",
        "dangerous": "This URL is likely malicious. Do NOT visit it. Report at cybercrime.gov.in.",
    },
    "qr": {
        "safe": "This QR code appears legitimate. Always verify payee name before paying.",
        "suspicious": "This QR has red flags. Double-check payee name and amount.",
        "dangerous": "This QR code may be fraudulent. Do NOT pay. Verify with the merchant directly.",
    },
    "audio": {
        "safe": "This audio appears to be genuine human speech.",
        "suspicious": "This audio has characteristics that may indicate synthetic generation. Verify the caller.",
        "dangerous": "This audio shows strong signs of AI generation. If used for a request, verify by calling the person on their known number.",
    },
    "video": {
        "safe": "This video appears genuine. No significant manipulation artifacts detected.",
        "suspicious": "Some frames show potential manipulation artifacts. Verify through alternative means.",
        "dangerous": "This video shows strong deepfake indicators. Do NOT act on any requests in this video.",
    },
    "image": {
    "safe": "This image appears to show a genuine photograph. However, AI-generated faces are becoming increasingly realistic. When in doubt, look for subtle asymmetries in eyes, ears, and teeth.",
    "suspicious": "This image has some characteristics that may indicate AI generation or manipulation. Look for: unnatural skin smoothness, asymmetric accessories (earrings, glasses), blurred background-face boundaries, or distorted text.",
    "dangerous": "This image shows strong indicators of being AI-generated or manipulated. Common signs include: perfectly symmetric features, unnaturally smooth skin, warped accessories or backgrounds, and inconsistent lighting. Do NOT trust identity claims based solely on this image.",
    },
}


class ExplainabilityService:
    def generate(self, analysis_type: str, score_output, raw_features: dict) -> dict:
        explanation = {
            "summary": score_output.explanation_summary,
            "contributing_factors": score_output.contributing_factors,
        }

        # Type-specific highlights
        if analysis_type == "email":
            explanation["highlights"] = self._email_highlights(raw_features)
        elif analysis_type in ("url", "qr"):
            explanation["highlights"] = self._url_highlights(raw_features)
        elif analysis_type == "audio":
            explanation["highlights"] = self._audio_highlights(raw_features, score_output)
        elif analysis_type == "video":
            explanation["highlights"] = self._video_highlights(raw_features, score_output)

        return explanation

    def get_tip(self, analysis_type: str, risk_label: str) -> str:
        return TIPS.get(analysis_type, {}).get(risk_label, "Stay vigilant online.")

    def _email_highlights(self, features: dict) -> dict:
        highlights = {"phrases": [], "urls": [], "sender": {}}
        if "flagged_phrases" in features:
            for phrase in features["flagged_phrases"]:
                if isinstance(phrase, dict):
                    highlights["phrases"].append(phrase)
                else:
                    highlights["phrases"].append({"text": phrase, "reason": "Suspicious phrase"})
        if "flagged_urls" in features:
            for url_info in features["flagged_urls"]:
                if isinstance(url_info, dict):
                    highlights["urls"].append(url_info)
                else:
                    highlights["urls"].append({"url": url_info, "flags": ["Suspicious"]})
        if "sender_flags" in features:
            highlights["sender"] = features["sender_flags"]
        return highlights

    def _url_highlights(self, features: dict) -> dict:
        return {"domain_analysis": features.get("domain_analysis", {})}

    def _audio_highlights(self, features: dict, score_output) -> dict:
        highlights = {"indicators": []}

        scoring_method = features.get("scoring_method", "unknown")
        highlights["method"] = scoring_method

        if features.get("spectral_note"):
            highlights["indicators"].append({
                "type": "spectral",
                "description": features["spectral_note"],
            })
        if features.get("pitch_note"):
            highlights["indicators"].append({
                "type": "pitch",
                "description": features["pitch_note"],
            })

        flags = features.get("flags", [])
        flag_descriptions = {
            "low_high_freq_energy": "Low energy in 4-8kHz range, unusual for natural speech",
            "excessive_high_freq_energy": "Excessive high-frequency energy detected",
            "narrow_spectral_bandwidth": "Narrow spectral bandwidth typical of synthetic speech",
            "low_zero_crossing_rate": "Abnormally smooth audio signal",
            "unnaturally_stable_pitch": "Pitch is unnaturally stable across the sample",
            "erratic_pitch": "Erratic pitch changes detected",
            "low_voiced_ratio": "Low proportion of voiced speech",
            "uniform_mfcc_pattern": "MFCC patterns are unusually uniform",
            "silent_audio": "Audio is mostly silence",
            "very_short_audio": "Audio is very short (< 1 second)",
            "very_low_energy": "Audio energy is very low",
        }
        for flag in flags:
            desc = flag_descriptions.get(flag)
            if desc:
                highlights["indicators"].append({
                    "type": "flag",
                    "flag": flag,
                    "description": desc,
                })

        if "ml_raw_score" in features:
            highlights["ml_confidence"] = round(features["ml_raw_score"], 3)
        if "heuristic_score" in features:
            highlights["heuristic_score"] = round(features["heuristic_score"], 3)

        return highlights

    def _video_highlights(self, features: dict, score_output) -> dict:
        highlights = {"indicators": []}

        highlights["method"] = features.get("scoring_method", "unknown")
        highlights["frames_analyzed"] = features.get("total_frames_analyzed", 0)
        highlights["frames_with_faces"] = features.get("frames_with_faces", 0)

        if "frame_analysis" in features:
            highlights["frame_analysis"] = features["frame_analysis"]

        if "temporal_analysis" in features:
            ta = features["temporal_analysis"]
            highlights["temporal_consistency"] = round(ta.get("temporal_consistency", 1.0), 3)
            if ta.get("suspicious_segments"):
                highlights["indicators"].append({
                    "type": "temporal",
                    "description": f"Sudden probability jumps detected in {len(ta['suspicious_segments'])} frame transitions",
                })

        flags = features.get("flags", [])
        flag_descriptions = {
            "no_faces_detected": "No faces detected in the video",
            "insufficient_face_frames": "Very few frames contained detectable faces",
            "high_face_dropout": "Face detection drops out in many frames, common in deepfakes",
            "inconsistent_face_size": "Face size varies significantly between frames",
            "face_position_jitter": "Face position jitters unnaturally between frames",
            "face_position_jump": "Face position jumps significantly between frames",
            "low_resolution": "Video resolution is low, which limits analysis accuracy",
        }
        for flag in flags:
            desc = flag_descriptions.get(flag)
            if desc:
                highlights["indicators"].append({
                    "type": "flag",
                    "flag": flag,
                    "description": desc,
                })

        if "ml_aggregated_score" in features:
            highlights["ml_aggregated_score"] = features["ml_aggregated_score"]
        if "suspicious_frames" in features:
            highlights["suspicious_frames"] = features["suspicious_frames"]

        return highlights

