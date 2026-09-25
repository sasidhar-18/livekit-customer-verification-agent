import json
import logging

from livekit.agents import RunContext, function_tool

from state import VerificationState


logger = logging.getLogger("customer-verification-agent")


def create_verification_tools(state: VerificationState) -> list:
    """
    Create tools that operate on the shared verification state.
    """

    @function_tool
    async def record_customer_name(
        context: RunContext,
        name: str,
    ) -> str:
        """
        Record or update the customer's name.
        """

        name = name.strip()

        if not name:
            return (
                "The customer name was empty. "
                "Please ask for the customer's name."
            )

        state.customer_name = name

        logger.info(
            "STATE UPDATE: customer_name=%s",
            state.customer_name,
        )

        return (
            f"Customer name recorded as "
            f"{state.customer_name}."
        )

    @function_tool
    async def record_pan_status(
        context: RunContext,
        verified: bool,
    ) -> str:
        """
        Record or update PAN verification status.
        """

        state.pan_verified = verified

        logger.info(
            "STATE UPDATE: pan_verified=%s",
            verified,
        )

        return (
            f"PAN verification status recorded as {verified}."
        )

    @function_tool
    async def record_bank_status(
        context: RunContext,
        verified: bool,
    ) -> str:
        """
        Record or update bank-account verification status.
        """

        state.bank_verified = verified

        logger.info(
            "STATE UPDATE: bank_verified=%s",
            verified,
        )

        return (
            f"Bank verification status recorded as {verified}."
        )

    @function_tool
    async def record_selfie_status(
        context: RunContext,
        uploaded: bool,
    ) -> str:
        """
        Record or update selfie upload status.
        """

        state.selfie_uploaded = uploaded

        logger.info(
            "STATE UPDATE: selfie_uploaded=%s",
            uploaded,
        )

        return (
            f"Selfie upload status recorded as {uploaded}."
        )

    @function_tool
    async def get_verification_summary(
        context: RunContext,
    ) -> str:
        """
        Return the current structured verification state as JSON.
        """

        summary = state.summary()

        summary_json = json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )

        logger.info(
            "\n"
            "============================================================\n"
            "FINAL VERIFICATION SUMMARY JSON\n"
            "============================================================\n"
            "%s\n"
            "============================================================",
            summary_json,
        )

        return summary_json

    return [
        record_customer_name,
        record_pan_status,
        record_bank_status,
        record_selfie_status,
        get_verification_summary,
    ]


def create_status_tools() -> list:
    """
    Create demonstration-only verification lookup tools.
    """

    @function_tool
    async def check_verification_status(
        context: RunContext,
        customer_name: str,
    ) -> str:
        """
        Check a mock verification status for demonstration purposes.

        This does NOT access a real customer database.
        """

        logger.info(
            "MOCK VERIFICATION LOOKUP: customer=%s",
            customer_name,
        )

        mock_customer = {
            "rahul": {
                "pan_verified": True,
                "bank_verified": True,
                "selfie_uploaded": True,
            },
            "sasidhar": {
                "pan_verified": True,
                "bank_verified": False,
                "selfie_uploaded": True,
            },
        }

        result = mock_customer.get(
            customer_name.lower().strip()
        )

        if result is None:
            return json.dumps(
                {
                    "found": False,
                    "message": "No mock verification record found.",
                },
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "found": True,
                "customer_name": customer_name,
                **result,
            },
            ensure_ascii=False,
        )

    return [check_verification_status]