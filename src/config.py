from dotenv import load_dotenv

load_dotenv(".env.local")


# ============================================================
# LIVEKIT AGENT CONFIGURATION
# ============================================================

AGENT_NAME = "my-agent"


# ============================================================
# STT
# ============================================================

STT_MODEL = "assemblyai/universal-3-5-pro"
STT_LANGUAGE = "en"


# ============================================================
# LLM
# ============================================================

LLM_MODEL = "google/gemma-4-31b-it"


# ============================================================
# TTS
# ============================================================

TTS_MODEL = "fishaudio/s2.1-pro"

TTS_VOICE = "fa4c9eb3dccc4806b382b40d61c6b10a"


# ============================================================
# VOICE SETTINGS
# ============================================================

DISCONNECT_DELAY_SECONDS = 10

INTERRUPTION_MODE = "adaptive"

PREEMPTIVE_GENERATION = True
EXPRESSIVE_VOICE = True