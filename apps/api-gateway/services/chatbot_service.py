"""
CyberShield AI Chatbot service — India-focused cybersecurity assistant.

Three modes:
  general    → Q&A on scams, safety, best practices
  india_news → Indian cybersecurity context, advisories, threat landscape
  quiz_gen   → Generate quiz questions as structured JSON
"""

from __future__ import annotations

import json
import logging
import random

from ml.llm_client import ask_chatbot, generate_quiz_llm

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# System prompts
# ─────────────────────────────────────────────────────────────────

SYSTEM_GENERAL = """You are **CyberShield Assistant**, an expert cybersecurity advisor built for Indian users.

IDENTITY & SCOPE:
• You are part of CyberShield AI — a platform that detects deepfakes, phishing, QR/UPI fraud.
• You are DEFENSIVE ONLY. You NEVER give exploitation, hacking, or offensive guidance.
• You explain things simply so any non-technical Indian citizen can understand.

INDIA KNOWLEDGE:
• CERT-In advisories, compliance (6-hour incident reporting rule).
• RBI digital-payment guidelines, KYC norms, UPI fraud reporting.
• UPI ecosystem — NPCI, BHIM, Google Pay, PhonePe, Paytm scam patterns.
• National Cyber Crime Portal: cybercrime.gov.in | Helpline: 1930.
• Common Indian scams: fake KYC calls, lottery SMS, OTP phishing, SIM swap, QR tampering, deepfake video calls, fake loan apps, sextortion.
• Cyber Surakshit Bharat, ISEA, Digital Personal Data Protection Act 2023 (DPDPA).
• India has 350M+ UPI users; 175%+ surge in financial-sector phishing in H1 2024.

SAFETY RULES — NEVER BREAK:
1. REFUSE any request to hack, exploit, create malware, bypass security, or do anything illegal.
2. If asked about offensive techniques, say: "I only provide defensive guidance. For security research, use authorized bug-bounty programs."
3. Never ask for or store Aadhaar, PAN, passwords, or OTPs.
4. Always recommend cybercrime.gov.in / 1930 for active fraud.

STYLE:
• Markdown with headers, bullets, **bold** for emphasis.
• Relevant emojis sparingly (🔒 🛡️ ⚠️ ✅ ❌).
• Concise but complete (200-400 words).
• Indian examples, laws, institutions when relevant.
• End with an actionable next step."""

SYSTEM_NEWS = """You are **CyberShield News Analyst** for Indian cybersecurity.

Provide a briefing covering:
1. Major cyber incidents affecting India (breaches, scam campaigns, ransomware).
2. CERT-In / government policy updates.
3. RBI / NPCI payment-security developments.
4. Emerging threat trends in the Indian context.
5. Actionable tips.

FORMAT:
• Header: "📰 India Cyber Brief"
• 3-5 news items, each with headline + 2-3 sentence summary.
• End with "🛡️ Stay Safe" section with 2-3 tips.
• Note your knowledge has a cutoff; recommend cert-in.org.in for latest.

RULES: Only factual info from training data. If unsure, say so. Defensive focus only."""

SYSTEM_QUIZ = """You are a cybersecurity quiz generator for Indian users.

RESPOND WITH ONLY VALID JSON — no markdown fences, no explanation text.

Output a JSON array of objects:
[
  {
    "question_text": "...",
    "options": ["A", "B", "C", "D"],
    "correct_option_index": 0,
    "explanation": "...",
    "difficulty": 1,
    "category": "phishing"
  }
]

Rules:
• Every question must be relevant to Indian cybersecurity (UPI, Aadhaar, banking, CERT-In, etc.).
• Exactly 4 options per question.
• One clearly correct answer.
• Educational explanation.
• Valid categories: "deepfake", "phishing", "upi_qr", "kyc_otp", "general".
• Valid difficulty: 1 (easy), 2 (medium), 3 (hard).

IMPORTANT: Output ONLY the JSON array. Nothing else."""

# ─────────────────────────────────────────────────────────────────
# India cyber facts (used offline / as sidebar content)
# ─────────────────────────────────────────────────────────────────

INDIA_FACTS = [
    "🇮🇳 India reported over 14 lakh cyber-security incidents to CERT-In in 2023.",
    "💳 UPI processed 13.4 billion transactions worth ₹20.64 lakh crore in Dec 2023 alone.",
    "📱 India has 350M+ UPI users — the world's largest real-time payment system.",
    "🔒 DPDPA 2023 mandates data protection with penalties up to ₹250 crore.",
    "📞 Call 1930 immediately for financial cyber fraud — India's national helpline.",
    "⚠️ CERT-In requires organisations to report incidents within 6 hours.",
    "🏦 RBI rules: banks must reverse unauthorised e-transactions reported within 3 working days.",
    "🎭 175% surge in phishing attacks on India's financial sector in H1 2024.",
    "📧 Phishing is India's #1 cyber-attack vector; banking & e-commerce are top targets.",
    "🤖 A BSE chief's deepfake video was circulated on social media in India.",
    "💡 Under IT Act Section 66D, impersonation via computer is punishable by up to 3 years.",
    "🌐 India is among the top 3 countries targeted by ransomware globally.",
    "📲 Never install apps from SMS/WhatsApp links — always use official app stores.",
    "🔐 CERT-In recommends enabling 2FA on all critical accounts.",
    "🏢 India's NCIIPC protects critical infrastructure: power, banking, telecom.",
]

# ─────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────

async def chat_response(
    messages: list[dict],
    mode: str = "general",
) -> dict:
    """
    Generate an assistant reply.

    Returns {"reply": str, "facts": list[str]}
    """
    # ✅ FIX: handle quiz_gen mode by generating quiz and formatting as chat
    if mode == "quiz_gen":
        return await _handle_quiz_mode(messages)

    system = SYSTEM_GENERAL if mode == "general" else SYSTEM_NEWS

    reply = await ask_chatbot(
        messages=messages,
        system_prompt=system,
        temperature=0.7,
        max_tokens=4096,
    )

    facts = random.sample(INDIA_FACTS, min(2, len(INDIA_FACTS)))
    return {"reply": reply, "facts": facts}


async def _handle_quiz_mode(messages: list[dict]) -> dict:
    """
    When user is in quiz_gen mode, extract their topic from the last message,
    generate quiz questions, and format them as a readable chat response.
    """
    last_msg = messages[-1]["content"] if messages else "cybersecurity basics"

    questions = await generate_quiz(
        topic=last_msg,
        num_questions=5,
        difficulty=1,
        category="general",
    )

    # Format questions as readable markdown
    lines = [f"## 🧠 Quiz: {last_msg}\n"]
    for i, q in enumerate(questions, 1):
        lines.append(f"### Question {i}")
        lines.append(f"**{q['question_text']}**\n")
        for j, opt in enumerate(q["options"]):
            marker = "🟢" if j == q["correct_option_index"] else "⚪"
            lines.append(f"{marker} **{chr(65 + j)}.** {opt}")
        lines.append(f"\n💡 **Answer:** {chr(65 + q['correct_option_index'])}")
        lines.append(f"📝 {q['explanation']}\n")

    reply = "\n".join(lines)
    facts = random.sample(INDIA_FACTS, min(2, len(INDIA_FACTS)))
    return {"reply": reply, "facts": facts}


async def generate_quiz(
    topic: str,
    num_questions: int = 5,
    difficulty: int = 1,
    category: str = "general",
) -> list[dict]:
    """
    Generate quiz questions via AI.

    Returns list of question dicts or fallback questions on failure.
    """
    user_prompt = (
        f"Generate exactly {num_questions} cybersecurity quiz questions.\n"
        f"Topic: {topic}\n"
        f"Difficulty: {difficulty} (1=easy, 2=medium, 3=hard)\n"
        f"Category: {category}\n"
        f"All questions MUST be relevant to Indian users and context."
    )

    raw = await generate_quiz_llm(
        user_prompt=user_prompt,
        system_prompt=SYSTEM_QUIZ,
        temperature=0.8,
        max_tokens=4096,
    )

    if not raw:
        return _fallback_quiz(num_questions, difficulty, category)

    # Parse JSON
    try:
        cleaned = raw.strip()
        # strip markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        questions = json.loads(cleaned)

        validated = []
        for q in questions:
            validated.append({
                "question_text": str(q.get("question_text", "")),
                "options": list(q.get("options", []))[:4],
                "correct_option_index": int(q.get("correct_option_index", 0)) % 4,
                "explanation": str(q.get("explanation", "")),
                "difficulty": min(max(int(q.get("difficulty", difficulty)), 1), 3),
                "category": q.get("category", category),
            })

        return validated[:num_questions] if validated else _fallback_quiz(num_questions, difficulty, category)

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Quiz JSON parse failed: %s — raw: %s", exc, raw[:200])
        return _fallback_quiz(num_questions, difficulty, category)


async def get_daily_tip() -> dict:
    """Random India-specific cybersecurity tip."""
    return {"tip": random.choice(INDIA_FACTS), "source": "CyberShield AI"}


# ─────────────────────────────────────────────────────────────────
# Fallback quiz (when LLM fails)
# ─────────────────────────────────────────────────────────────────

def _fallback_quiz(count: int, difficulty: int, category: str) -> list[dict]:
    bank = [
        {
            "question_text": "You get an SMS: 'Your SBI account is blocked. Click http://sbi-verify.xyz to reactivate.' What should you do?",
            "options": [
                "Click the link and enter your details",
                "Ignore — SBI's real domain is sbi.co.in, not sbi-verify.xyz",
                "Forward it to friends as a warning",
                "Reply STOP to the SMS",
            ],
            "correct_option_index": 1,
            "explanation": "sbi-verify.xyz is NOT an official SBI domain. Banks never send blocking messages with links. Visit sbi.co.in directly.",
            "difficulty": difficulty,
            "category": category,
        },
        {
            "question_text": "Someone calls from 'your bank' and asks for your OTP to 'verify your account'. What's correct?",
            "options": [
                "Share the OTP — they said they're from the bank",
                "Ask them to call back later",
                "Hang up — banks NEVER ask for OTPs over phone",
                "Share only the first 3 digits",
            ],
            "correct_option_index": 2,
            "explanation": "No bank employee will ever ask for your OTP, PIN, or password. Report such calls to 1930.",
            "difficulty": difficulty,
            "category": category,
        },
        {
            "question_text": "What is India's national helpline for reporting cyber fraud?",
            "options": ["100", "112", "1930", "181"],
            "correct_option_index": 2,
            "explanation": "1930 is India's Cyber Crime Helpline. Also report at cybercrime.gov.in. Fast reporting increases recovery chances.",
            "difficulty": difficulty,
            "category": category,
        },
        {
            "question_text": "A QR code at a tea stall shows payee name 'Random Person' instead of the shop name. You should:",
            "options": [
                "Pay anyway, you're at the shop",
                "Refuse this QR and ask for alternative payment",
                "Pay ₹1 to test",
                "Scan with another phone first",
            ],
            "correct_option_index": 1,
            "explanation": "Mismatched payee names = potential QR fraud. Scammers paste their own QR over legitimate ones.",
            "difficulty": difficulty,
            "category": category,
        },
        {
            "question_text": "How quickly must Indian organisations report cyber incidents to CERT-In?",
            "options": ["24 hours", "12 hours", "6 hours", "48 hours"],
            "correct_option_index": 2,
            "explanation": "CERT-In mandates reporting within 6 hours of detection (April 2022 directive).",
            "difficulty": difficulty,
            "category": category,
        },
        {
            "question_text": "What is the maximum penalty under India's DPDPA 2023 for data protection violations?",
            "options": ["₹50 crore", "₹100 crore", "₹250 crore", "₹500 crore"],
            "correct_option_index": 2,
            "explanation": "The Digital Personal Data Protection Act 2023 prescribes penalties up to ₹250 crore for significant data breaches.",
            "difficulty": difficulty,
            "category": category,
        },
    ]
    return bank[:count]