# Customer Verification Voice Agent

A browser-based, real-time **Customer Verification Assistant** built with **LiveKit Agents**, **LiveKit Cloud**, and **LiveKit Inference**.

The agent conducts a natural voice conversation with a customer, collects verification information, answers common verification questions, maintains conversation state, handles interruptions, generates a final verification summary, and closes the conversation politely.

---

## Features

* Real-time browser-based voice interaction
* LiveKit Agents for agent orchestration
* LiveKit Cloud for real-time communication
* LiveKit Inference for:

  * Speech-to-Text (STT)
  * Large Language Model (LLM)
  * Text-to-Speech (TTS)
* Automatic agent greeting
* Customer name collection
* PAN verification status
* Bank-account verification status
* Selfie verification status
* Verification status summary
* Common FAQ handling
* Conversation history
* User interruption / barge-in handling
* Real-time transcript logging
* Empty/no-speech transcription handling
* Configurable system prompt
* Structured verification state
* Tool/function calling
* Final verification JSON
* Graceful conversation closing
* Browser microphone and speaker support
* No separate OpenAI/Google/Anthropic API key required

---

## Use Case

The agent acts as a **Customer Verification Assistant**.

A typical conversation looks like:

```text
Agent:
Hello! I'm your Customer Verification Assistant.
I'll help you with your verification status.
May I know your name?

Customer:
Hi, I'm Ravi.

Agent:
Nice to meet you, Ravi.
Have you completed your PAN verification?

Customer:
Yes.

Agent:
Great. Have you completed your bank account verification?

Customer:
Yes.

Agent:
Have you uploaded your selfie for verification?

Customer:
Yes.

Agent:
Your verification is complete. Your PAN, bank account,
and selfie verification are all marked as completed.

Is there anything else I can help you with?

Customer:
No, that's all.

Agent:
Would you like me to end the call?

Customer:
Yes.

Agent:
All right, Ravi. Have a wonderful day. Goodbye!
```

---

# Architecture

```text
                         ┌──────────────────────────┐
                         │        Browser           │
                         │                          │
                         │  Microphone / Speaker    │
                         │  Agent Console           │
                         └────────────┬─────────────┘
                                      │
                                      │ WebRTC
                                      ▼
                         ┌──────────────────────────┐
                         │      LiveKit Cloud       │
                         │                          │
                         │  Room / Audio / Events   │
                         └────────────┬─────────────┘
                                      │
                                      │ Agent Session
                                      ▼
                    ┌────────────────────────────────────┐
                    │          LiveKit Agent              │
                    │                                    │
                    │  CustomerVerificationAgent         │
                    │                                    │
                    │  ┌──────────────────────────────┐  │
                    │  │ Conversation / Agent Logic   │  │
                    │  └──────────────┬───────────────┘  │
                    │                 │                   │
                    │       ┌─────────┴─────────┐         │
                    │       ▼                   ▼         │
                    │  Verification Tools   Call Tools   │
                    │       │                   │         │
                    │       ▼                   ▼         │
                    │ VerificationState     end_call      │
                    └──────────────┬─────────────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────────────┐
                    │       LiveKit Inference             │
                    │                                    │
                    │  STT → LLM → TTS                  │
                    └────────────────────────────────────┘
```

---

# Technology Stack

| Component               | Technology                     |
| ----------------------- | ------------------------------ |
| Language                | Python                         |
| Real-time framework     | LiveKit Agents                 |
| Real-time communication | LiveKit Cloud                  |
| Speech-to-Text          | LiveKit Inference              |
| LLM                     | LiveKit Inference              |
| Text-to-Speech          | LiveKit Inference              |
| Noise cancellation      | ai-coustics                    |
| Browser client          | LiveKit Agent Console          |
| Configuration           | Python + environment variables |
| Package management      | uv                             |
| Testing                 | pytest                         |
| Logging                 | Python logging                 |

---

# Project Structure

```text
voice/
│
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── call_control.py
│   ├── config.py
│   ├── prompts.py
│   ├── state.py
│   └── tools.py
│
├── tests/
│
├── .env.example
├── .env.local
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# File Responsibilities

## `src/agent.py`

Main LiveKit Agent implementation.

Responsibilities:

* Creates the LiveKit `AgentServer`
* Creates the `CustomerVerificationAgent`
* Configures STT
* Configures LLM
* Configures TTS
* Configures turn detection
* Configures interruption handling
* Starts the agent session
* Connects to the LiveKit room
* Generates the initial greeting
* Captures user transcripts
* Captures assistant messages
* Logs interrupted messages
* Handles audio input configuration

---

## `src/config.py`

Central configuration for the application.

It contains configurable values such as:

```text
AGENT_NAME
STT_MODEL
STT_LANGUAGE
LLM_MODEL
TTS_MODEL
TTS_VOICE
INTERRUPTION_MODE
PREEMPTIVE_GENERATION
EXPRESSIVE_VOICE
DISCONNECT_DELAY_SECONDS
```

Keeping these values separate makes the application easier to configure without modifying the core agent implementation.

---

## `src/prompts.py`

Contains the system prompt used by the customer verification agent.

The prompt defines:

* Agent identity
* Conversation behavior
* Verification workflow
* FAQ behavior
* Tool usage
* Confirmation behavior
* Closing behavior
* Natural conversation guidelines

The prompt is separated from application logic so it can be modified independently.

---

## `src/state.py`

Contains the verification state maintained during a call.

The state tracks:

```json
{
  "customer_name": "Ravi",
  "pan_verified": true,
  "bank_verified": true,
  "selfie_uploaded": true
}
```

This prevents the LLM from being solely responsible for remembering structured verification information.

---

## `src/tools.py`

Contains function tools used by the agent.

Examples include:

```text
record_customer_name
record_pan_status
record_bank_status
record_selfie_status
get_verification_summary
get_verification_status
```

The tools update or retrieve structured application state.

---

## `src/call_control.py`

Contains call-control functionality.

The primary tool is:

```text
end_call
```

The tool is invoked after the customer confirms that they want to end the conversation.

The agent then completes its closing response and initiates the LiveKit session shutdown process.

---

# Conversation Flow

The agent follows this general flow:

```text
Start
  │
  ▼
Automatic Greeting
  │
  ▼
Ask Customer Name
  │
  ▼
PAN Verification
  │
  ▼
Bank Verification
  │
  ▼
Selfie Verification
  │
  ▼
Generate Verification Summary
  │
  ▼
Ask if Customer Needs Further Help
  │
  ├── Yes ──► Answer Question ──► Continue Conversation
  │
  └── No
        │
        ▼
   Ask to End Call
        │
        ▼
     Customer Confirms
        │
        ▼
      Goodbye
        │
        ▼
   Session Shutdown
```

---

# Verification State

The application maintains structured state rather than relying only on conversation history.

Example:

```python
{
    "customer_name": "Ravi",
    "pan_verified": True,
    "bank_verified": True,
    "selfie_uploaded": True
}
```

This allows the agent to correctly handle corrections.

For example:

```text
Customer:
Actually, I haven't uploaded my selfie yet.

Agent:
No problem. I'll update that.

selfie_uploaded = False
```

The final summary is therefore based on the latest recorded state.

---

# Tool Calling

The agent uses LiveKit function tools to perform deterministic operations.

Example tool flow:

```text
Customer:
Yes, my PAN is verified.

        │
        ▼

LLM identifies required action

        │
        ▼

record_pan_status(True)

        │
        ▼

VerificationState

        │
        ▼

pan_verified = True
```

This separates conversational reasoning from structured application state.

---

# Final Verification Summary

At the end of the verification workflow, the agent can generate a structured summary.

Example:

```json
{
  "customer_name": "Ravi",
  "pan_verified": true,
  "bank_verified": true,
  "selfie_uploaded": true
}
```

This can later be extended into a production API payload or database record.

---

# Frequently Asked Questions

The agent can answer common customer questions during the conversation.

Examples include:

### Why is verification required?

The agent explains the purpose of customer verification in a concise and conversational manner.

### How long does verification take?

The agent provides the configured general verification guidance.

### Is my information secure?

The agent provides the configured privacy/security explanation without exposing sensitive implementation details.

The FAQ behavior is controlled through the system prompt and can be extended with a dedicated knowledge base or RAG system in a production implementation.

---

# Interruption Handling

Real-time voice conversations require users to be able to interrupt the assistant.

The agent uses LiveKit turn handling and interruption support.

Example:

```text
Agent:
Your PAN verification is complete and—

Customer:
Wait, I have a question.

Agent:
Sure. Go ahead.
```

The previous assistant response is interrupted instead of forcing the customer to wait until the entire response finishes.

Interrupted messages are also recorded in the application logs.

Example:

```text
ASSISTANT: Your verification is complete...
MESSAGE WAS INTERRUPTED
```

---

# Transcript Logging

The agent listens for conversation events and logs both sides of the conversation.

User messages:

```text
USER: My name is Ravi.
```

Assistant messages:

```text
ASSISTANT: Nice to meet you, Ravi.
```

Interrupted responses are also detected:

```text
MESSAGE WAS INTERRUPTED
```

This provides a server-side transcript/log trail that can be used for debugging and future observability improvements.

---

# Handling Empty Speech / No-Speech Input

The agent includes basic handling for empty transcription events.

If the STT system produces an empty final transcript:

```text
EMPTY USER TRANSCRIPTION
```

is logged and the empty message is ignored instead of being passed into the conversation logic.

This prevents empty input from corrupting the conversation state.

---

# Voice Processing

The application configures audio enhancement using the `ai-coustics` LiveKit plugin.

```python
noise_cancellation=ai_coustics.audio_enhancement(
    model=ai_coustics.EnhancerModel.QUAIL_VF_S
)
```

This improves audio input quality before it reaches the voice pipeline.

---

# LiveKit Inference

The application uses LiveKit Inference for the complete voice pipeline:

```text
Customer Speech
      │
      ▼
     STT
      │
      ▼
Transcript
      │
      ▼
     LLM
      │
      ▼
Response Text
      │
      ▼
     TTS
      │
      ▼
Agent Speech
```

The models are configured through:

```text
src/config.py
```

The exact model identifiers used by the project are intentionally centralized there so they can be changed without modifying the agent implementation.

---
## LiveKit Inference Models

This project uses **LiveKit Inference** for the complete real-time voice pipeline. No separate OpenAI, Anthropic, Google, AssemblyAI, or Fish Audio API account is required.

The models configured in `src/config.py` are:

| Component                  | Model                              | Configuration  |
| -------------------------- | ---------------------------------- | -------------- |
| Speech-to-Text (STT)       | `assemblyai/universal-3-5-pro`     | `STT_MODEL`    |
| Large Language Model (LLM) | `google/gemma-4-31b-it`            | `LLM_MODEL`    |
| Text-to-Speech (TTS)       | `fishaudio/s2.1-pro`               | `TTS_MODEL`    |
| TTS Voice                  | `fa4c9eb3dccc4806b382b40d61c6b10a` | `TTS_VOICE`    |
| STT Language               | `en`                               | `STT_LANGUAGE` |

### Voice Pipeline

```text
Customer Speech
       │
       ▼
┌─────────────────────────────────┐
│ STT                             │
│ assemblyai/universal-3-5-pro    │
└───────────────┬─────────────────┘
                │
                ▼
          Text Transcript
                │
                ▼
┌─────────────────────────────────┐
│ LLM                             │
│ google/gemma-4-31b-it           │
└───────────────┬─────────────────┘
                │
                ▼
          Response Text
                │
                ▼
┌─────────────────────────────────┐
│ TTS                             │
│ fishaudio/s2.1-pro              │
│ Voice: configured voice ID      │
└───────────────┬─────────────────┘
                │
                ▼
          Agent Speech
```

### STT

The agent uses:

```text
assemblyai/universal-3-5-pro
```

for real-time speech recognition.

Configuration:

```python
STT_MODEL = "assemblyai/universal-3-5-pro"
STT_LANGUAGE = "en"
```

### LLM

The conversational reasoning is handled by:

```text
google/gemma-4-31b-it
```

Configuration:

```python
LLM_MODEL = "google/gemma-4-31b-it"
```

The LLM is responsible for:

* Understanding customer speech
* Maintaining conversational context
* Deciding when to call verification tools
* Answering verification FAQs
* Handling corrections
* Generating natural responses
* Managing the conversation toward completion

### TTS

The agent uses:

```text
fishaudio/s2.1-pro
```

for speech synthesis.

Configuration:

```python
TTS_MODEL = "fishaudio/s2.1-pro"
TTS_VOICE = "fa4c9eb3dccc4806b382b40d61c6b10a"
```

The TTS output is streamed back to the browser through LiveKit.

### Voice Interaction Pipeline

The complete real-time flow is:

```text
Browser Microphone
       │
       ▼
LiveKit Cloud
       │
       ▼
LiveKit Agent
       │
       ▼
AssemblyAI Universal-3.5-Pro
       │
       ▼
Customer Transcript
       │
       ▼
Google Gemma 4 31B IT
       │
       ├──────────────► Verification Tools
       │
       ▼
Response Text
       │
       ▼
Fish Audio S2.1 Pro
       │
       ▼
LiveKit Cloud
       │
       ▼
Browser Speaker
```

All three inference components are configured through `src/config.py`, making the voice pipeline easy to modify without changing the main agent implementation.


# Requirements

* Python 3.10–3.14
* LiveKit Cloud account
* LiveKit CLI
* `uv`
* Git
* Modern web browser
* Microphone
* Speaker/headphones

No dedicated GPU is required.

No OpenAI, Anthropic, Google, or other separate AI provider API key is required for the implemented inference pipeline.

---

# Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd voice
```

Create/synchronize the project environment:

```bash
uv sync
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# Environment Configuration

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env.local
```

Configure the required LiveKit credentials in `.env.local`.

Example structure:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

Do **not** commit `.env.local`.

The `.gitignore` configuration prevents local secrets from being committed.

---

# Running Locally

From the project directory:

```powershell
$env:PYTHONUTF8="1"
lk agent dev
```

The LiveKit Agent development process starts the worker and registers the agent with LiveKit Cloud.

You should see logs indicating that the worker has registered successfully.

---

# Connecting Through the Browser

The agent can be tested using the LiveKit Agent Console.

Open the Agent Console from the LiveKit Cloud project and select the deployed/registered agent.

Allow browser microphone access when prompted.

The conversation should begin with the automatic greeting.

Example:

```text
Agent:
Hello! I'm your Customer Verification Assistant...
```

---

# Testing the Complete Conversation

A complete test should cover:

### 1. Greeting

The agent should automatically greet the customer.

### 2. Name

Say:

```text
My name is Ravi.
```

The agent should record the customer name.

### 3. PAN

Say:

```text
Yes, my PAN verification is complete.
```

### 4. Bank Account

Say:

```text
Yes, my bank verification is complete.
```

### 5. Selfie

Say:

```text
Yes, I uploaded my selfie.
```

### 6. Summary

The agent should produce a verification summary.

Example:

```json
{
  "customer_name": "Ravi",
  "pan_verified": true,
  "bank_verified": true,
  "selfie_uploaded": true
}
```

### 7. FAQ

Ask:

```text
Why do I need to complete verification?
```

or:

```text
How long does verification take?
```

or:

```text
Is my information secure?
```

### 8. Interruption

Interrupt the agent while it is speaking:

```text
Wait, I have another question.
```

The agent should stop its current response and respond to the new input.

### 9. Correction

Correct a previously provided verification status:

```text
Actually, I haven't uploaded my selfie.
```

The stored verification state should be updated.

### 10. Closing

Say:

```text
That's all, thank you.
```

The agent should ask whether the customer wants to end the call.

Confirm:

```text
Yes.
```

The agent should politely say goodbye and initiate its closing process.

---

# Example Logs

A successful interaction produces logs similar to:

```text
USER: My name is Ravi.
ASSISTANT: Nice to meet you, Ravi.

USER: Yes, my PAN is verified.
ASSISTANT: Great. Have you completed your bank verification?

USER: Yes.
ASSISTANT: Have you uploaded your selfie?

USER: Yes.

ASSISTANT: Your verification is complete...
```

Tool execution is also visible in the logs.

Example:

```text
CALL END CONFIRMED BY CUSTOMER
```

followed by the session shutdown process.

---

# Error Handling

The current implementation includes basic handling for empty user transcription.

Example:

```text
EMPTY USER TRANSCRIPTION
```

The event is ignored rather than creating an invalid conversation turn.

The implementation also relies on LiveKit Agents' session and worker lifecycle handling for connection/session failures.

For production, this can be extended with:

* Retry policies
* Model timeout handling
* Fallback responses
* API failure messages
* Structured error events
* Monitoring and alerting
* Circuit breakers
* Session recovery

---

# Configuration

The application keeps important configuration values outside the core agent logic.

For example:

```text
STT_MODEL
LLM_MODEL
TTS_MODEL
TTS_VOICE
STT_LANGUAGE
INTERRUPTION_MODE
PREEMPTIVE_GENERATION
EXPRESSIVE_VOICE
```

This allows different models or settings to be tested without rewriting the agent.

---

# Production Architecture Improvements

The current project is intentionally focused on the assignment requirements.

A production implementation could be extended with:

## 1. Persistent customer state

Store verification records in a database such as PostgreSQL.

```text
LiveKit Agent
      │
      ▼
Verification Service
      │
      ▼
PostgreSQL
```

---

## 2. Real verification APIs

Replace mock verification tools with actual backend services:

```text
record_pan_status()
        │
        ▼
PAN Verification API
```

```text
record_bank_status()
        │
        ▼
Bank Verification API
```

```text
record_selfie_status()
        │
        ▼
Identity Verification Service
```

---

## 3. Authentication

Authenticate the customer before exposing verification information.

Possible architecture:

```text
Browser
   │
   ▼
Authentication
   │
   ▼
LiveKit Session
   │
   ▼
Customer Verification Agent
```

---

## 4. Observability

Add production observability for:

* STT latency
* LLM latency
* TTS latency
* End-to-end response latency
* Interruption rate
* Failed sessions
* Tool execution failures
* Session duration

---

## 5. Persistent transcripts

Instead of only logging transcripts, store structured conversation events:

```json
{
  "session_id": "session-123",
  "role": "user",
  "text": "My name is Ravi",
  "timestamp": "2026-09-25T10:00:00Z"
}
```

This would allow customer-support auditing and analytics.

---

## 6. Secure PII Handling

A production version should treat PAN, bank information, identity documents, and biometric information as sensitive data.

Recommended improvements include:

* Encryption in transit
* Encryption at rest
* Strict access control
* Data retention policies
* Audit logging
* PII redaction
* Secure secret management
* Minimal data collection

---

# Future Extensions

Possible extensions include:

### Multilingual Verification

Support multiple Indian languages using multilingual STT/TTS models.

### RAG-based FAQ

Replace static FAQ instructions with a retrieval system:

```text
Customer Question
       │
       ▼
Retriever
       │
       ▼
Verification Knowledge Base
       │
       ▼
LLM
       │
       ▼
Voice Response
```

### Human Handoff

Add a tool such as:

```text
transfer_to_human()
```

when the customer requests human assistance.

### Verification Backend

Connect the voice agent to a real identity-verification backend.

### Analytics Dashboard

Track:

```text
Total Calls
Completed Verifications
Incomplete Verifications
Average Session Duration
Interruption Rate
Tool Errors
FAQ Categories
```

---

# Security Considerations

This project is a demonstration and does not process real identity documents.

For production deployment:

* Never hard-code API credentials.
* Never commit `.env.local`.
* Do not log raw PAN or bank-account information.
* Do not store biometric information unnecessarily.
* Use authenticated backend APIs.
* Apply least-privilege permissions.
* Encrypt sensitive data.
* Implement appropriate data retention/deletion policies.
* Add audit logging for sensitive operations.

---

# Assignment Requirement Mapping

| Requirement                | Implementation                   |
| -------------------------- | -------------------------------- |
| LiveKit Agents             | Implemented                      |
| LiveKit Cloud              | Implemented                      |
| LiveKit Inference          | Implemented                      |
| Browser microphone         | Supported                        |
| Browser speaker            | Supported                        |
| Automatic greeting         | Implemented                      |
| Ask customer name          | Implemented                      |
| PAN verification           | Implemented                      |
| Bank verification          | Implemented                      |
| Selfie verification        | Implemented                      |
| Verification summary       | Implemented                      |
| FAQ: why verification      | Implemented                      |
| FAQ: verification duration | Implemented                      |
| FAQ: privacy/security      | Implemented                      |
| Conversation history       | Implemented through AgentSession |
| Interruption/barge-in      | Implemented                      |
| Transcript logging         | Implemented                      |
| Empty/no-speech handling   | Implemented                      |
| Polite closing             | Implemented                      |
| Structured final JSON      | Implemented                      |
| Configurable prompt        | Implemented                      |
| Mock verification tools    | Implemented                      |

---

# Example Final JSON

The verification state can produce:

```json
{
  "customer_name": "Ravi",
  "pan_verified": true,
  "bank_verified": true,
  "selfie_uploaded": true
}
```

This structured output can later be passed to a backend verification workflow.

---

# Development Notes

The project was built and tested using:

```text
Python 3.13
LiveKit Agents 1.8.x
LiveKit RTC 1.1.x
LiveKit Inference
LiveKit Cloud
ai-coustics
```

The exact dependency versions are locked in:

```text
uv.lock
```

---

# GitHub

After configuring the project:

```bash
git status
git add -A
git commit -m "Build customer verification voice agent"
git push origin main
```

Make sure that local credentials and virtual environments are not included in the repository.

---

# Demo Checklist

Before recording the final demonstration, verify:

```text
[ ] Browser microphone works
[ ] Agent automatically greets
[ ] Customer name is captured
[ ] PAN status is recorded
[ ] Bank status is recorded
[ ] Selfie status is recorded
[ ] FAQ question works
[ ] Verification summary is generated
[ ] Interruption works
[ ] Correction works
[ ] Transcript appears in logs
[ ] Empty speech does not break the session
[ ] Agent asks whether further help is needed
[ ] Agent politely closes the conversation
[ ] Final verification JSON is visible in logs
```

---

# Demo Recording

The recommended demonstration should show:

### Part 1 — Normal Conversation

Demonstrate:

```text
Greeting
   ↓
Name
   ↓
PAN
   ↓
Bank
   ↓
Selfie
   ↓
Summary
```

### Part 2 — Interruption

Interrupt the agent while it is speaking and demonstrate that it responds to the new user input.

### Part 3 — Transcript / Logs

Show the terminal logs containing:

```text
USER: ...
ASSISTANT: ...
```

and tool execution/state information.

### Part 4 — Closing

Demonstrate:

```text
Customer:
That's all, thank you.

Agent:
Would you like me to end the call?

Customer:
Yes.

Agent:
All right, Ravi. Have a wonderful day. Goodbye!
```

---

# License

This project is intended as a technical demonstration of a real-time voice agent built using LiveKit Agents.
