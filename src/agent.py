import logging
import re

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    ConversationItemAddedEvent,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
    room_io,
)
from livekit.plugins import ai_coustics

from call_control import create_call_control_tools
from config import (
    AGENT_NAME,
    EXPRESSIVE_VOICE,
    INTERRUPTION_MODE,
    LLM_MODEL,
    PREEMPTIVE_GENERATION,
    STT_LANGUAGE,
    STT_MODEL,
    TTS_MODEL,
    TTS_VOICE,
)
from prompts import SYSTEM_PROMPT
from state import VerificationState
from tools import (
    create_status_tools,
    create_verification_tools,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    "customer-verification-agent"
)


# ============================================================
# TRANSCRIPT HELPER
# ============================================================

def clean_transcript(text: str) -> str:
    """
    Remove LiveKit expressive voice tags from transcript logs.
    """

    if not text:
        return ""

    text = re.sub(
        r"<expr\b[^>]*/>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return " ".join(
        text.split()
    ).strip()


# ============================================================
# CUSTOMER VERIFICATION AGENT
# ============================================================

class CustomerVerificationAgent(Agent):

    def __init__(self) -> None:

        self.verification = VerificationState()

        tools = []

        tools.extend(
            create_verification_tools(
                self.verification
            )
        )

        tools.extend(
            create_status_tools()
        )

        tools.extend(
            create_call_control_tools()
        )

        super().__init__(
            llm=inference.LLM(
                model=LLM_MODEL,
            ),
            instructions=SYSTEM_PROMPT,
            tools=tools,
        )


# ============================================================
# AGENT SERVER
# ============================================================

server = AgentServer()


@server.rtc_session(
    agent_name=AGENT_NAME
)
async def my_agent(
    ctx: JobContext,
):

    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # ========================================================
    # CREATE AGENT
    # ========================================================

    agent = CustomerVerificationAgent()

    # ========================================================
    # AGENT SESSION
    # ========================================================

    session = AgentSession(

        # ----------------------------------------------------
        # STT
        # ----------------------------------------------------

        stt=inference.STT(
            model=STT_MODEL,
            language=STT_LANGUAGE,
        ),

        # ----------------------------------------------------
        # LLM
        # ----------------------------------------------------

        llm=inference.LLM(
            model=LLM_MODEL,
        ),

        # ----------------------------------------------------
        # TTS
        # ----------------------------------------------------

        tts=inference.TTS(
            model=TTS_MODEL,
            voice=TTS_VOICE,
        ),

        # ----------------------------------------------------
        # TURN HANDLING
        # ----------------------------------------------------

        turn_handling=TurnHandlingOptions(

            turn_detection=inference.TurnDetector(),

            interruption={
                "mode": INTERRUPTION_MODE,
            },

            preemptive_generation={
                "enabled": PREEMPTIVE_GENERATION,
            },
        ),

        expressive=EXPRESSIVE_VOICE,
    )

    # ========================================================
    # USER TRANSCRIPT
    # ========================================================

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event):

        if not event.is_final:
            return

        transcript = event.transcript.strip()

        if not transcript:

            logger.warning(
                "EMPTY USER TRANSCRIPTION"
            )

            return

        transcript = clean_transcript(
            transcript
        )

        if transcript:

            logger.info(
                "USER: %s",
                transcript,
            )

    # ========================================================
    # CONVERSATION TRANSCRIPT
    # ========================================================

    @session.on(
        "conversation_item_added"
    )
    def on_conversation_item_added(
        event: ConversationItemAddedEvent,
    ):

        item = event.item

        if not hasattr(
            item,
            "text_content",
        ):
            return

        text = item.text_content

        if not text:
            return

        text = clean_transcript(
            text
        )

        if not text:
            return

        logger.info(
            "%s: %s",
            item.role.upper(),
            text,
        )

        # ----------------------------------------------------
        # INTERRUPTION DETECTION
        # ----------------------------------------------------

        if getattr(
            item,
            "interrupted",
            False,
        ):

            logger.info(
                "MESSAGE WAS INTERRUPTED"
            )

    # ========================================================
    # START SESSION
    # ========================================================

    await session.start(

        agent=agent,

        room=ctx.room,

        room_options=room_io.RoomOptions(

            audio_input=room_io.AudioInputOptions(

                noise_cancellation=(
                    ai_coustics.audio_enhancement(
                        model=(
                            ai_coustics.EnhancerModel.QUAIL_VF_S
                        ),
                    )
                ),

            ),
        ),
    )

    # ========================================================
    # CONNECT TO LIVEKIT ROOM
    # ========================================================

    await ctx.connect()

    # ========================================================
    # AUTOMATIC INITIAL GREETING
    # ========================================================

    logger.info(
        "Starting automatic agent greeting..."
    )

    await session.generate_reply(
        instructions=(
            "Start the conversation immediately. "
            "Do not wait for the customer to say hello. "
            "Greet the customer warmly and introduce yourself "
            "as the Customer Verification Assistant. "
            "Briefly explain that you will help with their "
            "verification status, then ask for their name. "
            "Keep the greeting short and natural."
        )
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    cli.run_app(server)