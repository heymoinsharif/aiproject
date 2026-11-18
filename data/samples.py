"""
Curated Fictional Sample Emails for Demonstration & Testing.
DISCLAIMER: These emails are 100% fictional test cases created for educational evaluation.
They contain no real personally identifiable information or malicious payloads.
"""

SAMPLE_EMAILS = {
    "Phishing: Urgent Account Verification": {
        "title": "Simulated Phishing: Urgent Account Verification",
        "category": "Likely Phishing (Simulated)",
        "subject": "CRITICAL: Urgent Action Required - Verify Your Account Within 24 Hours",
        "sender": "Security Desk <alert-security@bank-verify-portal.top>",
        "body": (
            "Dear Valued Customer,\n\n"
            "We detected unauthorized access attempts to your online banking profile from an unrecognized "
            "IP address (185.220.101.45) on October 14, 2026. For your immediate protection, your account privileges "
            "have been temporarily suspended.\n\n"
            "To restore full access and prevent permanent account termination, you must verify your identity and "
            "confirm your secret passcode within the next 24 hours:\n\n"
            "http://192.168.1.105/secure-login/verify.php?user=id98231\n\n"
            "Failure to complete verification will result in permanent closure of your accounts and forfeiture of pending transfers.\n\n"
            "Sincerely,\n"
            "Central Fraud & Security Directorate"
        ),
        "urls": "http://192.168.1.105/secure-login/verify.php?user=id98231",
        "description": "Exhibits severe artificial urgency, threats of account suspension, credential harvesting, and a raw IP address hyperlink."
    },
    "Legitimate: Academic Announcement": {
        "title": "Simulated Legitimate: University Examination Schedule",
        "category": "Likely Legitimate (Simulated)",
        "subject": "End-Semester Examination Schedule - Winter 2026",
        "sender": "Office of the Controller of Examinations <coe@university.edu>",
        "body": (
            "Dear Faculty and Students,\n\n"
            "The final timetable for the Winter 2026 End-Semester Examinations has been officially ratified by the Academic Council. "
            "The theoretical examinations are scheduled to commence from November 18, 2026, across designated lecture halls.\n\n"
            "Students are requested to download their official hall tickets through the Student Information Portal "
            "beginning November 5, 2026. Please ensure that all lab evaluations and course registrations are completed with your "
            "respective academic advisors prior to this date.\n\n"
            "The detailed date-sheet and grievance guidelines are published on the official university portal at:\n"
            "https://portal.university.edu/academics/winter-2026-schedule.html\n\n"
            "Wishing all students the very best in their preparations.\n\n"
            "Dr. Sarah Jenkins\n"
            "Dean of Academic Affairs"
        ),
        "urls": "https://portal.university.edu/academics/winter-2026-schedule.html",
        "description": "Standard administrative announcement using formal academic terminology, legitimate .edu domain link, and zero coercive threats."
    },
    "Suspicious: Unexpected Vendor Invoice": {
        "title": "Simulated Suspicious: Unexpected Vendor Invoice",
        "category": "Suspicious (Simulated)",
        "subject": "Invoice OVERDUE: Payment Receipt Required - Inv #883910",
        "sender": "Global Billing Solutions <invoicing@quick-billing-solutions.work>",
        "body": (
            "Hello,\n\n"
            "Your recent purchase order for cloud server infrastructure renewal (Ref #INV-883910) for the amount of $4,850.00 "
            "is now 5 days overdue. Your credit card ending in 4102 was declined.\n\n"
            "Please review the attached statement details and settle the pending payment immediately to avoid late penal fees "
            "and legal escalation:\n\n"
            "https://bit.ly/3xInvoiceReviewBilling\n\n"
            "If you believe this charge was made in error, you must dispute the transaction by logging into the billing terminal within 12 hours.\n\n"
            "Accounts Receivable Team"
        ),
        "urls": "https://bit.ly/3xInvoiceReviewBilling",
        "description": "Contains ambiguous urgency, financial transaction demands, low-reputation .work sender domain, and a shortened URL (bit.ly)."
    },
    "Legitimate / Cautionary: IT Password Policy Reminder": {
        "title": "Simulated Legitimate (Cautionary): Internal IT Password Policy",
        "category": "Likely Legitimate / Edge Case (Simulated)",
        "subject": "Annual Password Expiration Notice - Enterprise Security Policy",
        "sender": "IT Infrastructure Services <helpdesk@corporate.org>",
        "body": (
            "Hello Team,\n\n"
            "In accordance with our organization's annual ISO 27001 information security compliance review, your domain password "
            "is scheduled to expire in 14 days. Please change your password prior to the expiration date.\n\n"
            "You may update your password directly through your standard Windows workstation (Ctrl+Alt+Del -> Change Password) "
            "or via the internal self-service intranet at:\n"
            "https://intranet.corporate.org/idm/change-password\n\n"
            "Note: The IT Department will NEVER ask you to email your password or provide login credentials over chat.\n\n"
            "Regards,\n"
            "Enterprise IT Support"
        ),
        "urls": "https://intranet.corporate.org/idm/change-password",
        "description": "Routine corporate IT compliance communication. Contains the word 'password' but includes standard defensive disclaimers and legitimate corporate intranet references."
    }
}
