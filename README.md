class ValidationPrompt:

    @staticmethod
    def build(
        policy: str,
        document: str
    ) -> str:

        return f"""
You are an enterprise compliance officer.

Your responsibility is to validate whether a submitted document complies with the company policy.

========================
POLICY
========================

{policy}

========================
DOCUMENT
========================

{document}

========================
TASK
========================

Compare the document against every rule in the policy.

Return ONLY valid JSON.

Schema:

{{
    "approved": true,
    "confidence": 0.95,
    "reason": "Short explanation",
    "violations": [
        "Violation 1",
        "Violation 2"
    ]
}}

Do not return markdown.

Do not return code blocks.

Return only JSON.
"""
