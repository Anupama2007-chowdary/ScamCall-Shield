
def analyze_scam(transcript):

    text = transcript.lower()

    scam_patterns = {
        "OTP or PIN request": {
            "keywords": [
                "otp", "one time password", "pin",
                "share your otp", "tell me your otp"
            ],
            "score": 3
        },

        "Sensitive information request": {
            "keywords": [
                "password", "cvv", "card details",
                "debit card number", "credit card number"
            ],
            "score": 3
        },

        "Urgent threats": {
            "keywords": [
                "blocked today", "account will be blocked",
                "immediately", "urgent", "suspended",
                "within 24 hours", "ventane", "nokkandi"
            ],
            "score": 2
        },

        "Bank or government impersonation": {
            "keywords": [
                "bank officer", "bank representative",
                "from your bank", "police officer",
                "income tax department", "government official",
                "customs officer", "customs adhikari",
                "fedex", "courier service"
            ],
            "score": 2
        },

        "Money or payment pressure": {
            "keywords": [
                "transfer money", "send money",
                "pay now", "payment", "upi payment",
                "scan qr code"
            ],
            "score": 2
        },

        "Remote access request": {
            "keywords": [
                "install anydesk", "install teamviewer",
                "screen sharing", "remote access",
                "share your screen"
            ],
            "score": 3
        },

        "Suspicious links": {
            "keywords": [
                "click this link", "open this link",
                "verify through this link", "click here"
            ],
            "score": 1
        },

        "Fake prize or lottery claims": {
            "keywords": [
                "you won a prize", "lottery winner",
                "claim your reward", "won a lottery",
                "claim your prize"
            ],
            "score": 2
        },

        "KYC or account update pressure": {
            "keywords": [
                "update your kyc", "kyc expired",
                "verify your account", "account verification"
            ],
            "score": 2
        },

        "Suspicious parcel or illegal goods threat": {
            "keywords": [
                "illegal items", "illegal goods",
                "drugs", "narcotics", "passport",
                "parcel hold", "parcel is on hold",
                "customs officers", "press 9", "press nine",
                "chattaviruddhamaina vastuvulu"
            ],
            "score": 3
        }
    }

    risk_score = 0
    warning_signs = []

    for category, details in scam_patterns.items():

        matched = [
            keyword
            for keyword in details["keywords"]
            if keyword in text
        ]

        if matched:
            warning_signs.append(category)
            risk_score += details["score"]

    if risk_score >= 3:
        risk_level = "HIGH"
    elif risk_score >= 1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return risk_level, warning_signs
