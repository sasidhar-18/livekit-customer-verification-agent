import asyncio
import logging

from livekit import api
from livekit.agents import RunContext, function_tool, get_job_context

from config import DISCONNECT_DELAY_SECONDS


logger = logging.getLogger("customer-verification-agent")


def create_call_control_tools() -> list:
    """
    Create tools responsible for controlled call termination.
    """

    closing_started = False

    @function_tool
    async def end_call(
        context: RunContext,
    ) -> str:
        """
        Start the controlled call-ending process.

        The agent will finish its response and then the LiveKit room
        will be deleted after the configured grace period.
        """

        nonlocal closing_started

        if closing_started:
            return "Call closing process has already started."

        closing_started = True

        logger.info(
            "CALL END CONFIRMED BY CUSTOMER"
        )

        logger.info(
            "Call will disconnect automatically in %s seconds.",
            DISCONNECT_DELAY_SECONDS,
        )

        asyncio.create_task(
            _disconnect_after_delay()
        )

        return (
            "The customer confirmed that the call should end. "
            "The call will disconnect in 10 seconds."
        )

    return [end_call]


async def _disconnect_after_delay() -> None:
    """
    Wait for the grace period, then terminate the entire
    LiveKit room so the browser participant is disconnected too.
    """

    try:
        await asyncio.sleep(DISCONNECT_DELAY_SECONDS)

        logger.info(
            "10-second closing period completed."
        )

        # ---------------------------------------------------------
        # STEP 1
        # Gracefully shut down the AgentSession
        # ---------------------------------------------------------

        job_context = get_job_context()

        logger.info(
            "Shutting down LiveKit AgentSession..."
        )

        job_context.shutdown(
            reason="customer_requested_call_end"
        )

        logger.info(
            "LiveKit AgentSession shutdown initiated successfully."
        )

        # ---------------------------------------------------------
        # STEP 2
        # Delete the ACTUAL LiveKit room.
        #
        # This disconnects the browser participant too.
        # ---------------------------------------------------------

        logger.info(
            "Deleting LiveKit room..."
        )

        await job_context.api.room.delete_room(
            api.DeleteRoomRequest(
                room=job_context.room.name
            )
        )

        logger.info(
            "LiveKit room deleted successfully."
        )

    except Exception:
        logger.exception(
            "Failed to terminate the LiveKit call."
        )