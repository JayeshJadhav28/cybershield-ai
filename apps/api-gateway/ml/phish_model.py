"""
Phishing ML model — TF-IDF + Ensemble classifier.
Handles model loading, training, and inference.
Gracefully falls back to heuristics-only if model files are missing.
"""

import os
import pickle
import warnings
from typing import Dict, Tuple, Optional

import numpy as np

warnings.filterwarnings("ignore")

# Check for scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, VotingClassifier
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class PhishingModel:
    """
    TF-IDF + Ensemble classifier for phishing detection.
    
    Falls back to rule-based scoring if model files not found.
    """

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        self.vectorizer_path = os.path.join(model_dir, "phishing_tfidf_vectorizer.pkl")
        self.classifier_path = os.path.join(model_dir, "phishing_classifier.pkl")

        self.vectorizer = None
        self.classifier = None
        self.is_trained = False

        self._load_or_create()

    def _load_or_create(self):
        """Load trained model if available, otherwise prepare for rule-based fallback."""
        if not SKLEARN_AVAILABLE:
            print("⚠️  scikit-learn not available — using heuristics only")
            return

        if os.path.exists(self.vectorizer_path) and os.path.exists(self.classifier_path):
            try:
                with open(self.vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(self.classifier_path, "rb") as f:
                    self.classifier = pickle.load(f)
                self.is_trained = True
                print("✅ Phishing model loaded from disk")
            except Exception as e:
                print(f"⚠️  Failed to load phishing model: {e} — using heuristics only")
        else:
            print("ℹ️  No trained phishing model found — using heuristics only")
            print(f"   Expected: {self.vectorizer_path}")
            print("   Run notebooks/01_phishing_model_training.ipynb to train")

    def predict_proba(self, text: str) -> float:
        """
        Predict phishing probability for given text.
        Returns probability in [0, 1].
        """
        if not self.is_trained or self.vectorizer is None or self.classifier is None:
            return self._heuristic_fallback(text)

        try:
            features = self.vectorizer.transform([text])
            proba = self.classifier.predict_proba(features)[0]
            # Index 1 = phishing class probability
            phishing_proba = float(proba[1]) if len(proba) > 1 else float(proba[0])
            return phishing_proba
        except Exception as e:
            print(f"⚠️  Model inference error: {e}")
            return self._heuristic_fallback(text)

    def _heuristic_fallback(self, text: str) -> float:
        """
        Rule-based fallback when model is not available.
        Uses keyword frequency analysis.
        """
        from utils.text_preprocessing import (
            URGENCY_PHRASES, CREDENTIAL_PHRASES, FINANCIAL_SCAM_PHRASES
        )

        text_lower = text.lower()
        score = 0.0

        # Count urgency phrases
        urgency_count = sum(1 for p in URGENCY_PHRASES if p in text_lower)
        score += min(0.4, urgency_count * 0.08)

        # Count credential request phrases
        cred_count = sum(1 for p in CREDENTIAL_PHRASES if p in text_lower)
        score += min(0.4, cred_count * 0.10)

        # Count financial scam phrases
        scam_count = sum(1 for p in FINANCIAL_SCAM_PHRASES if p in text_lower)
        score += min(0.3, scam_count * 0.08)

        return min(1.0, score)

    def train_baseline(self, X_texts: list, y_labels: list):
        """
        Train a baseline model from data.
        X_texts: list of text strings
        y_labels: list of 0 (safe) or 1 (phishing)
        """
        if not SKLEARN_AVAILABLE:
            print("❌ Cannot train: scikit-learn not available")
            return False

        print(f"Training phishing model on {len(X_texts)} samples...")

        # TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            strip_accents="unicode",
            lowercase=True,
            sublinear_tf=True,
        )

        X_features = self.vectorizer.fit_transform(X_texts)

        # Ensemble classifier
        lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

        self.classifier = VotingClassifier(
            estimators=[("lr", lr), ("rf", rf)],
            voting="soft",
        )
        self.classifier.fit(X_features, y_labels)
        self.is_trained = True

        # Save to disk
        os.makedirs(self.model_dir, exist_ok=True)
        with open(self.vectorizer_path, "wb") as f:
            pickle.dump(self.vectorizer, f)
        with open(self.classifier_path, "wb") as f:
            pickle.dump(self.classifier, f)

        print(f"✅ Model trained and saved to {self.model_dir}")
        return True

    def create_demo_model(self):
        """
        Create a minimal demo model from hard-coded examples.
        Provides decent baseline without any external dataset.
        """
        if not SKLEARN_AVAILABLE:
            return False

        phishing_examples = [
            "urgent your account has been suspended click here to verify immediately your account will be blocked",
            "dear customer verify your sbi account kyc update required enter password",
            "congratulations you have won prize money claim your reward click link",
            "URGENT security alert your hdfc bank account login credentials required",
            "your account will be suspended within 24 hours complete kyc verification",
            "dear user your otp for transaction enter your otp immediately",
            "income tax refund approved click here to claim your tds refund",
            "suspicious activity detected on your account verify now to avoid suspension",
            "your debit card has been blocked enter card details to unblock",
            "limited time offer claim your cashback verify upi id now",
            "dear customer your kyc has expired update immediately or account will close",
            "click here to verify your credentials account blocking in 24 hours urgent",
            "unauthorized access detected on your account confirm your password now",
            "your sbi net banking will be suspended verify your account immediately",
            "government scheme cashback verify upi account claim money now",
            "enter your credit card cvv number to complete verification process",
            "you have been selected for insurance claim verify your aadhaar pan",
            "loan approved instantly transfer fee to receive amount enter bank details",
            "your phone number is linked to fraud unlink by sharing otp immediately",
            "gpay phonepe paytm cashback offer verify account get reward now",
        ]

        safe_examples = [
            "your account statement for january is ready please check online banking",
            "thank you for your transaction payment successful amount debited",
            "your fixed deposit has matured please contact branch for renewal",
            "meeting scheduled for tomorrow please review the attached agenda",
            "your order has been shipped tracking number provided below",
            "newsletter january 2024 new features updates from our team",
            "reminder your emi payment is due on 15th of this month",
            "your card ending 1234 was used for transaction at amazon",
            "welcome to our service your account has been created successfully",
            "please find attached the quarterly report for your review",
            "your appointment has been confirmed for tomorrow at 10am",
            "thank you for contacting customer support ticket number created",
            "your subscription renewal is due next month current plan active",
            "important announcement upcoming maintenance scheduled for weekend",
            "your profile has been updated successfully changes will reflect shortly",
            "invoice number 12345 payment received thank you for your business",
            "your request has been processed successfully please allow 24 hours",
            "new security feature enabled two factor authentication is now active",
            "your salary has been credited account balance updated successfully",
            "greetings from our team wishing you a happy new year ahead",
        ]

        X = phishing_examples + safe_examples
        y = [1] * len(phishing_examples) + [0] * len(safe_examples)

        success = self.train_baseline(X, y)
        if success:
            print("✅ Demo phishing model created")
        return success


# Singleton instance
phishing_model = PhishingModel()