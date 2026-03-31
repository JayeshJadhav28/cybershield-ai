export interface ScenarioStep {
  step: number;
  type: "message" | "choice";
  role?: "attacker" | "system" | "narrator";
  message?: string;
  prompt?: string;
  options?: string[];
  correct_index?: number;
  feedback?: Record<string, string>;
}

export interface Scenario {
  id: string;
  title: string;
  description: string;
  category: string;
  icon: string;
  difficulty: "Easy" | "Medium" | "Hard";
  estimated_time_minutes: number;
  steps: ScenarioStep[];
}

export const SCENARIOS: Scenario[] = [
  {
    id: "fake-kyc-call",
    title: "The Fake KYC Call",
    description:
      "A caller claims to be from your bank and says your KYC is expiring. Navigate this scenario to learn the right responses.",
    category: "KYC / OTP Fraud",
    icon: "📞",
    difficulty: "Easy",
    estimated_time_minutes: 4,
    steps: [
      {
        step: 1,
        type: "message",
        role: "narrator",
        message:
          "You receive a phone call from an unknown number. The caller ID shows a number similar to your bank's helpline.",
      },
      {
        step: 2,
        type: "message",
        role: "attacker",
        message:
          "Hello, this is Rajesh from SBI customer care. We've noticed your KYC documents have expired. Your account will be frozen in 24 hours if not updated immediately.",
      },
      {
        step: 3,
        type: "choice",
        prompt: "What do you do?",
        options: [
          "Ask them to send you an OTP to verify your identity",
          "Tell them you'll visit the branch directly to update KYC",
          "Share your Aadhaar number and PAN to update KYC quickly",
          "Hang up and call the official SBI helpline to verify",
        ],
        correct_index: 3,
        feedback: {
          "0": "❌ Never ask for or share OTPs over phone calls. Banks send OTPs only for transactions you initiate.",
          "1": "⚠️ Visiting the branch is safe, but the best immediate action is to verify the call through official channels first.",
          "2": "❌ Never share personal documents over phone. This is exactly what scammers want.",
          "3": "✅ Correct! Always hang up and call the bank's official helpline number (found on the back of your debit card or their website) to verify any such claims.",
        },
      },
      {
        step: 4,
        type: "message",
        role: "attacker",
        message:
          "Sir, please don't hang up. This is urgent! If you don't update now, your account will be permanently blocked. I just need your Aadhaar number to proceed.",
      },
      {
        step: 5,
        type: "choice",
        prompt: "The caller is pressuring you. What's your next move?",
        options: [
          "Give your Aadhaar number to avoid account blocking",
          "Ask for the caller's employee ID and verify it online",
          "Firmly say 'I will not share any details on call' and hang up",
          "Put them on hold and ask a family member what to do",
        ],
        correct_index: 2,
        feedback: {
          "0": "❌ A legitimate bank employee will never ask for your Aadhaar over the phone.",
          "1": "⚠️ Scammers can give fake employee IDs. Verifying on call is not reliable.",
          "2": "✅ Perfect! Never share personal information on unsolicited calls. Banks never call to ask for sensitive details.",
          "3": "⚠️ While consulting others is okay, the correct response is to not share anything and hang up immediately.",
        },
      },
      {
        step: 6,
        type: "message",
        role: "narrator",
        message:
          "🎓 Key Takeaways:\n\n• Banks NEVER call to ask for KYC details, Aadhaar, PAN, or OTPs\n• Always verify by calling the official number on your bank card\n• Report suspicious calls at cybercrime.gov.in or call 1930\n• Urgency and threats are classic scam tactics",
      },
    ],
  },
  {
    id: "phishing-email-work",
    title: "Phishing Email at Work",
    description:
      "You receive an email at your office asking you to reset your corporate credentials. Can you spot the red flags?",
    category: "Phishing",
    icon: "📧",
    difficulty: "Medium",
    estimated_time_minutes: 5,
    steps: [
      {
        step: 1,
        type: "message",
        role: "narrator",
        message:
          "Monday morning, 9:15 AM. You open your office email and find an urgent message from what appears to be your IT department.",
      },
      {
        step: 2,
        type: "message",
        role: "attacker",
        message:
          "From: it-security@yourcompany-verify.com\nSubject: ⚠️ URGENT: Password Reset Required\n\nDear Employee,\n\nOur security systems have detected unauthorized access to your corporate account. You must reset your password within 2 hours or your account will be locked.\n\nClick here to reset: http://yourcompany-secure-login.xyz/reset\n\nIT Security Team",
      },
      {
        step: 3,
        type: "choice",
        prompt: "What's the first thing you notice?",
        options: [
          "The email seems legitimate — I should reset my password quickly",
          "The sender domain 'yourcompany-verify.com' is NOT my company's real domain",
          "The urgency seems reasonable for a security issue",
          "I should forward this to colleagues so they can reset too",
        ],
        correct_index: 1,
        feedback: {
          "0": "❌ Always check the sender's email domain first. Scammers use lookalike domains.",
          "1": "✅ Great catch! The sender domain is 'yourcompany-verify.com', not your company's actual domain. This is a classic phishing indicator.",
          "2": "❌ Artificial urgency is a manipulation tactic. Legitimate IT departments give reasonable timelines.",
          "3": "❌ Never forward suspicious emails to others. You'd be spreading the phishing attack.",
        },
      },
      {
        step: 4,
        type: "choice",
        prompt: "What should you do with this email?",
        options: [
          "Click the link to check if the reset page looks real",
          "Reply to the email asking if it's genuine",
          "Report it to your real IT team and delete the email",
          "Ignore it and do nothing",
        ],
        correct_index: 2,
        feedback: {
          "0": "❌ Never click links in suspicious emails. Even visiting the page can install malware.",
          "1": "❌ Replying confirms your email is active and can lead to more targeted attacks.",
          "2": "✅ Correct! Report to your real IT department (using known contact info), then delete. Your IT team can warn others.",
          "3": "⚠️ Ignoring is better than clicking, but reporting helps protect your colleagues too.",
        },
      },
      {
        step: 5,
        type: "message",
        role: "narrator",
        message:
          "🎓 Key Takeaways:\n\n• Always check the sender's email domain character by character\n• Hover over links to see the actual URL before clicking\n• Legitimate IT teams use internal communication channels\n• Report phishing attempts — it protects the entire organization\n• When in doubt, contact IT directly via known phone/chat",
      },
    ],
  },
  {
    id: "upi-qr-scam",
    title: "The Tampered QR Code",
    description:
      "You're at a street vendor and scan a QR code for payment. Something doesn't seem right. Can you spot the scam?",
    category: "UPI / QR Fraud",
    icon: "📱",
    difficulty: "Easy",
    estimated_time_minutes: 4,
    steps: [
      {
        step: 1,
        type: "message",
        role: "narrator",
        message:
          "You're buying street food for ₹150. The vendor points to a QR code taped on a board. You scan it with your UPI app.",
      },
      {
        step: 2,
        type: "message",
        role: "narrator",
        message:
          "Your UPI app shows:\n\n💰 Pay ₹150\n👤 Payee: 'Random Person'\n🏦 UPI ID: randomxyz@ybl\n\nThe vendor's shop name is 'Sharma Ji Ki Chaat'.",
      },
      {
        step: 3,
        type: "choice",
        prompt: "The payee name doesn't match the shop. What do you do?",
        options: [
          "Pay anyway — the vendor is standing right here",
          "Ask the vendor why the name doesn't match and refuse to pay via this QR",
          "Pay a small amount first to test if it's safe",
          "Take a photo of the QR and pay later from home",
        ],
        correct_index: 1,
        feedback: {
          "0": "❌ Mismatched payee names are a major red flag. Scammers paste their QR codes over legitimate ones.",
          "1": "✅ Correct! Always verify the payee name matches the merchant. If it doesn't, someone may have tampered with the QR code.",
          "2": "❌ Even a small payment goes to the scammer. The amount doesn't matter — the destination does.",
          "3": "❌ The QR code is already suspicious. Don't use it at all.",
        },
      },
      {
        step: 4,
        type: "choice",
        prompt: "The vendor says 'Oh, that's my partner's account, it's fine.' What now?",
        options: [
          "Okay, pay to that account since the vendor confirmed",
          "Insist on paying cash instead",
          "Ask for the vendor's own UPI ID and verify the name before paying",
          "Both B and C are good options",
        ],
        correct_index: 3,
        feedback: {
          "0": "❌ Scammers often have convincing excuses. The mismatched name is still a red flag.",
          "1": "✅ Cash is always safe in uncertain situations.",
          "2": "✅ Getting a verified UPI ID directly from the vendor is a safe approach.",
          "3": "✅ Perfect! Either pay cash or get the vendor's own verified UPI ID. Both are safe choices.",
        },
      },
      {
        step: 5,
        type: "message",
        role: "narrator",
        message:
          "🎓 Key Takeaways:\n\n• ALWAYS check the payee name before confirming UPI payments\n• QR codes at shops can be tampered with by pasting a scammer's QR on top\n• If the payee name doesn't match, DO NOT pay\n• When in doubt, use cash or ask for the merchant's direct UPI ID\n• Report QR fraud at cybercrime.gov.in or call 1930",
      },
    ],
  },
  {
    id: "fake-customer-support",
    title: "Fake Customer Support",
    description:
      "You search online for a customer care number and call it. But is it really the company you're trying to reach?",
    category: "Impersonation",
    icon: "🎧",
    difficulty: "Medium",
    estimated_time_minutes: 5,
    steps: [
      {
        step: 1,
        type: "message",
        role: "narrator",
        message:
          "Your food delivery app is showing an error. You Google 'Swiggy customer care number' and find a number on a random website. You call it.",
      },
      {
        step: 2,
        type: "message",
        role: "attacker",
        message:
          "Thank you for calling Swiggy customer care. I'm Priya. I can see there's an issue with your account. To fix it, I'll need to verify your identity. Can you please share the OTP that I'm sending to your registered mobile number?",
      },
      {
        step: 3,
        type: "choice",
        prompt: "You receive an OTP on your phone. What do you do?",
        options: [
          "Share the OTP — they need it to verify my identity",
          "Ask why they need an OTP just to fix an app error",
          "Refuse to share and hang up immediately",
          "Share the OTP but change your password afterward",
        ],
        correct_index: 2,
        feedback: {
          "0": "❌ This is a scam! No legitimate company asks for OTPs over the phone. Sharing this OTP could give them access to your account or wallet.",
          "1": "⚠️ Good instinct to question, but the safest action is to refuse and hang up. The number itself is fake.",
          "2": "✅ Correct! Never share OTPs with anyone over the phone. This is a fake customer care scam.",
          "3": "❌ Once you share the OTP, the damage is done instantly. Changing passwords afterward may be too late.",
        },
      },
      {
        step: 4,
        type: "choice",
        prompt: "How should you find the real customer support number?",
        options: [
          "Google it and use the first result",
          "Use the contact/help option inside the official app",
          "Search for it on social media",
          "Ask friends for the number",
        ],
        correct_index: 1,
        feedback: {
          "0": "❌ Scammers run ads on Google to show fake numbers at the top of search results.",
          "1": "✅ Always use the help/contact option within the official app or website. This is the only reliable source.",
          "2": "❌ Scammers create fake social media accounts impersonating brands.",
          "3": "⚠️ Friends might share outdated or incorrect numbers they found online.",
        },
      },
      {
        step: 5,
        type: "message",
        role: "narrator",
        message:
          "🎓 Key Takeaways:\n\n• NEVER search for customer care numbers on Google — scammers buy top ad spots\n• Always use the Help section inside the official app\n• No company will ever ask for your OTP\n• If someone asks for OTP, it's 100% a scam\n• Report fake customer care numbers at cybercrime.gov.in",
      },
    ],
  },
  {
    id: "deepfake-ceo-fraud",
    title: "Deepfake Video Call from Boss",
    description:
      "Your 'CEO' calls you on video asking for an urgent fund transfer. The video looks real, but is it?",
    category: "Deepfake",
    icon: "🎭",
    difficulty: "Hard",
    estimated_time_minutes: 5,
    steps: [
      {
        step: 1,
        type: "message",
        role: "narrator",
        message:
          "It's Friday evening, 6:30 PM. You're about to leave office when you receive a video call on WhatsApp from what appears to be your company's CEO.",
      },
      {
        step: 2,
        type: "message",
        role: "attacker",
        message:
          "The person on video looks and sounds exactly like your CEO. They say:\n\n'Hi, I need you to urgently transfer ₹5 lakhs to a vendor. It's for a confidential deal. I'll send you the account details. Please do it before the bank closes. Don't tell anyone else about this.'",
      },
      {
        step: 3,
        type: "choice",
        prompt: "The video looks convincing. What do you do?",
        options: [
          "Transfer the money immediately — the CEO is watching",
          "Ask the CEO a personal question that only they would know",
          "Say you'll do it and hang up, then call the CEO's known number to verify",
          "Transfer half the amount as a compromise",
        ],
        correct_index: 2,
        feedback: {
          "0": "❌ This is likely a deepfake! AI can now create convincing video of anyone. Never make urgent transfers based on video calls alone.",
          "1": "⚠️ Good thinking, but deepfake operators may have researched answers. The safest approach is to verify independently.",
          "2": "✅ Correct! Always verify through a separate, known channel. Call the CEO's number that you already have saved, or verify in person.",
          "3": "❌ Any amount transferred to a scammer is lost. The amount doesn't matter.",
        },
      },
      {
        step: 4,
        type: "choice",
        prompt: "What are signs that a video call might be a deepfake?",
        options: [
          "Slight lag in lip-sync with audio",
          "Unusual lighting or blurry edges around the face",
          "Reluctance to turn head or show different angles",
          "All of the above",
        ],
        correct_index: 3,
        feedback: {
          "0": "✅ Yes, but there are more signs too.",
          "1": "✅ Yes, but there are more signs too.",
          "2": "✅ Yes, but there are more signs too.",
          "3": "✅ Correct! All of these are potential deepfake indicators. Also watch for: unnatural blinking, inconsistent background, and requests for urgency/secrecy.",
        },
      },
      {
        step: 5,
        type: "message",
        role: "narrator",
        message:
          "🎓 Key Takeaways:\n\n• Deepfake video calls are increasingly used for CEO/boss fraud\n• AI can clone faces and voices from public videos and photos\n• NEVER make financial decisions based solely on video calls\n• Always verify through a separate, known communication channel\n• Red flags: urgency, secrecy, unusual requests, after-hours calls\n• Report deepfake fraud at cybercrime.gov.in or call 1930",
      },
    ],
  },
  {
    id: "whatsapp-otp-scam",
    title: "WhatsApp Account Takeover",
    description:
      "A friend messages you asking for a '6-digit code' that was sent to your phone by mistake. It's actually your WhatsApp verification code.",
    category: "Social Engineering",
    icon: "💬",
    difficulty: "Easy",
    estimated_time_minutes: 3,
    steps: [
      {
        step: 1,
        type: "message",
        role: "narrator",
        message:
          "You receive a WhatsApp message from your friend Amit's account. At the same time, you get an SMS with a 6-digit verification code from WhatsApp.",
      },
      {
        step: 2,
        type: "message",
        role: "attacker",
        message:
          "Hey! 😊 Sorry to bother you. I accidentally sent a 6-digit verification code to your number instead of mine. Can you please forward it to me? It's urgent!",
      },
      {
        step: 3,
        type: "choice",
        prompt: "What do you do?",
        options: [
          "Send the code — Amit is a close friend and it seems like an honest mistake",
          "Realize this code is YOUR WhatsApp verification code and don't share it",
          "Ask Amit to explain how a code meant for him came to your number",
          "Share the code but immediately change your WhatsApp settings",
        ],
        correct_index: 1,
        feedback: {
          "0": "❌ This is a classic account takeover scam! Amit's account has already been compromised. The attacker is using it to steal YOUR account next.",
          "1": "✅ Correct! The 6-digit code is YOUR WhatsApp verification code. Sharing it would give the attacker access to YOUR WhatsApp account.",
          "2": "⚠️ The question is good, but you're chatting with a scammer who has taken over Amit's account. Don't engage — the answer they give will be a lie.",
          "3": "❌ Once you share the code, your account is instantly taken over. You can't change settings fast enough.",
        },
      },
      {
        step: 4,
        type: "choice",
        prompt: "What should you do next?",
        options: [
          "Call Amit on a regular phone call to warn him his account is hacked",
          "Just ignore the message and move on",
          "Report the WhatsApp account and enable 2-Step Verification on your account",
          "Both A and C",
        ],
        correct_index: 3,
        feedback: {
          "0": "✅ Good, but there's more you should do.",
          "1": "❌ Ignoring it means Amit doesn't know his account is compromised. He could lose money or data.",
          "2": "✅ Good, but you should also warn Amit directly.",
          "3": "✅ Perfect! Call Amit to warn him, report the compromised account to WhatsApp, and enable 2-Step Verification on your own account for extra security.",
        },
      },
      {
        step: 5,
        type: "message",
        role: "narrator",
        message:
          "🎓 Key Takeaways:\n\n• NEVER share any verification codes with anyone — not even friends or family\n• If a 'friend' asks for a code, their account is likely hacked\n• Enable WhatsApp 2-Step Verification: Settings → Account → Two-step verification\n• Contact the real person via phone call to warn them\n• Report compromised accounts to WhatsApp and cybercrime.gov.in",
      },
    ],
  },
];

export function getScenarioById(id: string): Scenario | undefined {
  return SCENARIOS.find((s) => s.id === id);
}