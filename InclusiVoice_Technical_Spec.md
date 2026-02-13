# InclusiVoice Technical Specification (Prototype)

## 1) Purpose and Scope

**Product name:** InclusiVoice  
**Type:** Windows desktop accessibility application (private assistive overlay)  
**Primary scenario:** Support interview candidates with speech impediments or communication difficulties during virtual interviews.

InclusiVoice captures incoming interview audio, transcribes questions in real time, proposes context-aware draft responses, and can speak user-approved responses using text-to-speech (TTS). The tool is designed as a **private, user-only accessibility aid** and should not appear in shared video streams, meeting chat, or remote desktop capture by default.

---

## 2) User and Accessibility Goals

### 2.1 Target Users
- Individuals with dysarthria, stuttering, apraxia of speech, selective mutism, post-stroke speech limitations, or neurodivergent communication challenges.
- Users in professional settings requiring time-sensitive, high-pressure verbal interaction.

### 2.2 Accessibility Objectives
- Reduce cognitive and verbal load during interviews.
- Preserve user agency: no automatic speaking unless explicitly triggered.
- Minimize social visibility and stigma by behaving like standard assistive software.
- Support keyboard-only, switch device, and screen-reader usage.

---

## 3) Functional Requirements

### 3.1 Real-Time Voice Capture During Calls
1. Capture **system loopback audio** (interviewer speech from Teams/Zoom/Meet).
2. Optionally capture microphone input for local transcript feedback.
3. Process audio with low latency (< 500 ms chunking target).
4. Handle sample rates 16 kHz–48 kHz with automatic resampling.

### 3.2 Speech-to-Text (STT)
1. Perform streaming transcription of interviewer speech.
2. Provide interim and final transcription segments.
3. Apply speaker labeling (minimum: Interviewer vs User if mic enabled).
4. Provide confidence scoring and low-confidence highlighting.

### 3.3 Context-Aware Suggested Responses
1. Detect question intent (behavioral, technical, background, logistics, follow-up).
2. Generate 1–3 concise response drafts per detected question.
3. Allow configurable style profiles (formal, concise, STAR format).
4. Support user profile context (resume highlights, achievements, role-specific keywords).
5. Never auto-send or auto-speak generated responses.

### 3.4 Text-to-Speech Output
1. Convert user-approved text to natural TTS audio.
2. Output audio to selected virtual microphone or local speaker path.
3. Provide explicit “Hold-to-Speak” / “Click-to-Speak” interaction.
4. Offer voice controls: rate, pitch, timbre, language/accent where available.

### 3.5 Private, Non-Intrusive Overlay
1. Display as always-on-top accessibility panel visible only locally.
2. Prevent inclusion in screen sharing and capture pipelines (where OS/app APIs permit).
3. Provide compact and expanded modes with unobtrusive visual design.
4. Include emergency hide shortcut (e.g., `Ctrl+Shift+H`).

---

## 4) Non-Functional Requirements

### 4.1 Performance
- End-to-end transcription latency target: **<= 1.5 s**.
- Suggestion generation latency target: **<= 2.5 s** (local + cloud hybrid).
- UI frame responsiveness: 60 FPS target for overlay transitions.
- Startup time: <= 5 s on mid-range Windows laptop.

### 4.2 Reliability
- Graceful degradation if cloud NLP is unavailable (fallback to template responses).
- Automatic reconnection for audio device changes and call handoffs.
- Crash-safe local session recovery.

### 4.3 Usability
- First-use onboarding <= 3 minutes.
- Keyboard-only flow for all core features.
- Large-text and high-contrast modes.

---

## 5) System Architecture (Windows-Ready)

### 5.1 High-Level Components
1. **Desktop Shell/UI Layer**
   - Technology: .NET 8 + WinUI 3 (recommended) or Electron + native audio bridge.
   - Responsibilities: overlay rendering, accessibility controls, consent prompts, hotkeys.

2. **Audio Ingestion Service**
   - Capture stack: Windows WASAPI loopback for system audio + mic capture.
   - Optional noise suppression and voice activity detection (VAD).

3. **Realtime STT Service**
   - Primary engine: Whisper.cpp (local) or Azure Speech SDK (cloud) with streaming mode.
   - Produces timestamped transcripts and confidence metadata.

4. **NLP Orchestration Service**
   - Question segmentation and intent classifier.
   - Response suggestion engine (LLM-backed with prompt guardrails).
   - Context manager (resume profile + role metadata + session history).

5. **TTS Service**
   - Primary: Microsoft Azure Neural TTS or Windows Speech Synthesis fallback.
   - Audio routing to virtual microphone when user activates output.

6. **Privacy/Security Layer**
   - Encryption, data minimization, consent logging, retention enforcement.

7. **Local Data Store**
   - SQLite (encrypted) for preferences, glossaries, and optional session notes.
   - No raw audio retention by default.

### 5.2 Recommended Process Model
- `InclusiVoice.UI.exe` (front-end overlay and controls)
- `InclusiVoice.AudioWorker.exe` (capture/resample/VAD)
- `InclusiVoice.AIWorker.exe` (STT/NLP/TTS orchestration)
- IPC via gRPC named pipes on localhost with ACL restrictions.

### 5.3 Data Flow
1. Loopback audio frames acquired in 20–40 ms chunks.
2. AudioWorker performs normalization/resampling.
3. STT returns interim transcript.
4. NLP engine identifies question boundary and intent.
5. Suggestion drafts generated and rendered in overlay.
6. User edits/selects response.
7. On explicit trigger, TTS synthesizes and routes audio output.

---

## 6) Audio Capture and Processing Specification

### 6.1 Windows Audio Interfaces
- Use **WASAPI loopback** for system output capture.
- Use `IAudioClient3` where available for lower-latency shared mode.
- Provide per-device selection UI (headset/speaker/microphone).

### 6.2 Signal Pipeline
- Preprocessing steps:
  1. Resample to model-required rate (16 kHz for many STT models).
  2. Loudness normalization.
  3. Optional denoise and dereverb.
  4. VAD segmentation to avoid transcribing silence.

### 6.3 Latency Budget (Target)
- Capture + buffering: 150–300 ms
- STT incremental decode: 400–700 ms
- NLP suggestions: 700–1200 ms
- UI update: < 100 ms

---

## 7) Speech Recognition Integration

### 7.1 Engine Options
1. **Local-first option:** Whisper.cpp (quantized model, e.g., small.en/int8).
   - Pros: privacy, offline capability.
   - Cons: CPU/GPU load on laptop.

2. **Cloud option:** Azure Speech-to-Text or Google STT streaming.
   - Pros: strong real-time accuracy.
   - Cons: network dependency and regulated data transfer needs.

### 7.2 Hybrid Strategy (Recommended)
- Default to local STT for privacy.
- Offer cloud STT as opt-in “Enhanced Accuracy Mode”.
- Provide transparent indicator for active mode.

### 7.3 Domain Adaptation
- Inject custom phrase list from:
  - User name and pronunciation variants.
  - Job title and technical terms.
  - Company-specific vocabulary.

---

## 8) NLP / Response Generation Design

### 8.1 Pipeline
1. **Question Detection:** punctuation/prosody/semantic triggers.
2. **Intent Classification:** behavioral, technical, situational, motivation, logistics.
3. **Response Planning:** choose template strategy (e.g., STAR).
4. **Draft Generation:** produce short, medium, and fallback concise answer.
5. **Safety Filtering:** remove hallucinated facts and sensitive content leakage.

### 8.2 Context Inputs
- User-provided profile:
  - resume summary
  - projects/accomplishments
  - preferred communication style
  - role target and industry

### 8.3 Guardrails
- No impersonation claims or fabricated credentials.
- No autonomous response delivery.
- Explicitly label generated text as “Draft suggestion”.

### 8.4 Suggested Model Architecture
- Local lightweight classifier (ONNX) for intent.
- Cloud/local LLM for generation via retrieval-augmented prompt context.
- Token and cost controls with max output length per draft.

---

## 9) Text-to-Speech Engine Specification

### 9.1 Functional Requirements
- Natural voice synthesis with low startup lag (< 500 ms after trigger).
- Interrupt/cancel support.
- Voice presets and accessibility-friendly playback controls.

### 9.2 Engine Options
- Primary: Azure Neural TTS (high-quality voices).
- Fallback: Windows `System.Speech` / SpeechSynthesizer for offline mode.

### 9.3 Audio Routing
- Route synthesized stream to:
  1. Local playback for rehearsal.
  2. Virtual audio cable / virtual microphone for interview app input.
- Include output test wizard during setup.

---

## 10) UI/UX Specification (Accessibility-Centered)

### 10.1 Overlay Design
- Modes:
  - **Compact:** latest transcript + one quick suggestion.
  - **Expanded:** full transcript pane, suggestion cards, TTS controls.
- Draggable, resizable, snap-to-corner behavior.
- Opacity control (20–100%) and font scaling (100–250%).

### 10.2 Accessibility Controls
- Full keyboard map with remappable shortcuts.
- Screen reader labels via UIA (Microsoft UI Automation).
- High contrast themes and dyslexia-friendly font option.
- Optional symbol-assisted quick responses.

### 10.3 Interaction Safety
- Distinct confirmation before TTS broadcast.
- “Private Mode” indicator showing no outgoing TTS path active.
- Panic hide and mute-all hotkeys.

### 10.4 Suggested Default Hotkeys
- Toggle overlay: `Ctrl+Shift+O`
- Generate new suggestions: `Ctrl+Shift+G`
- Speak selected text: `Ctrl+Shift+S`
- Panic hide: `Ctrl+Shift+H`

---

## 11) Privacy, Security, and Compliance

### 11.1 Privacy Principles
- Data minimization by default.
- Local processing preference.
- Explicit opt-in for cloud services and session storage.

### 11.2 Data Handling Policy (Prototype)
- **Stored by default:** user settings, hotkeys, voice prefs.
- **Not stored by default:** raw interview audio, full transcripts.
- **Optional storage:** redacted transcript snippets for practice analytics.

### 11.3 Security Controls
- Encrypt local data at rest (AES-256 via Windows DPAPI-protected keys).
- TLS 1.2+ for all cloud API traffic.
- Signed binaries and integrity checks for updates.
- Role-based local access profile (single-user desktop scope).

### 11.4 Interview-Sensitive Safeguards
- Pre-session disclosure reminder for user legal/ethical compliance by region.
- Visible “Recording Off” / “Cloud Off” status chips.
- Clear consent UX before enabling any external processing.

---

## 12) Windows Installation and Deployment Requirements

### 12.1 Supported Platforms
- Windows 10 (22H2+) and Windows 11.
- x64 architecture mandatory for prototype; ARM optional later.

### 12.2 Packaging
- Preferred installer: **MSIX** with code signing certificate.
- Alternate enterprise package: MSI with silent install flags.
- Auto-update strategy via MSIX app installer feed or enterprise management tools.

### 12.3 Runtime Dependencies
- .NET 8 Desktop Runtime (if framework-dependent deployment).
- Optional GPU acceleration path (DirectML/CUDA where available).
- Virtual audio driver dependency (if TTS-to-mic path required).

### 12.4 First-Run Setup Wizard
1. Accessibility onboarding and consent flow.
2. Audio input/output device calibration.
3. STT mode selection (local vs cloud).
4. Hotkey configuration and test.
5. Interview app compatibility check (Teams/Zoom/Meet desktop).

---

## 13) Prototype Technology Stack (Recommended)

- **UI:** WinUI 3 (.NET 8, C#)
- **Audio:** NAudio + WASAPI loopback APIs
- **STT:** Whisper.cpp local wrapper + optional Azure Speech SDK
- **NLP:** Local ONNX intent classifier + cloud/local LLM gateway
- **TTS:** Azure Neural TTS + Windows Speech fallback
- **Data:** SQLite + SQLCipher (or encrypted file store)
- **IPC:** gRPC over named pipes
- **Telemetry (opt-in):** OpenTelemetry with local buffering

---

## 14) Prototype Milestones

### Milestone 1: Foundational Accessibility Overlay (2–3 weeks)
- Overlay shell, hotkeys, device selector, private display behavior.

### Milestone 2: Real-time STT Pipeline (2–4 weeks)
- Loopback capture, streaming transcript pane, confidence display.

### Milestone 3: Suggestion Engine v1 (3–4 weeks)
- Intent classification + template-based and LLM-backed response drafts.

### Milestone 4: TTS Output and Routing (2–3 weeks)
- Speak-on-trigger flow + virtual mic routing + safety confirmations.

### Milestone 5: Privacy/Security Hardening + Pilot (2–3 weeks)
- Consent flows, encryption, retention controls, and pilot user testing.

---

## 15) Validation and Evaluation Plan (Case Study Ready)

### 15.1 Technical Metrics
- STT Word Error Rate (WER) across accent/speech variability scenarios.
- Suggestion latency and user edit distance.
- TTS trigger-to-audio delay.
- Crash-free session rate.

### 15.2 Accessibility/UX Metrics
- NASA-TLX cognitive load comparison with/without tool.
- SUS usability score target: >= 75.
- Self-reported communication confidence improvement.
- Interview task completion rate and response timing.

### 15.3 Ethical and Research Considerations
- Informed consent for all participant trials.
- Bias evaluation for NLP suggestions.
- Transparency regarding generated assistance boundaries.

---

## 16) Risks and Mitigations

1. **Risk:** Transcription errors in noisy calls.  
   **Mitigation:** noise suppression, phrase hints, confidence warnings.
2. **Risk:** Over-reliance on generated responses.  
   **Mitigation:** manual approval-only flow, concise suggestions, user editing emphasis.
3. **Risk:** Privacy concerns in live interviews.  
   **Mitigation:** local-first defaults, no raw audio retention, explicit cloud opt-in.
4. **Risk:** Compatibility variance across meeting platforms.  
   **Mitigation:** per-app capture profiles and diagnostic wizard.

---

## 17) Prototype Deliverables for University Case Study

1. Executable Windows prototype installer (MSIX/MSI).
2. Configuration guide and accessibility quick-start manual.
3. Architecture diagram and data flow documentation.
4. Security/privacy policy draft.
5. Evaluation protocol and metrics dashboard template.

---

## 18) Future Extensions

- Multilingual real-time translation.
- Personalized speech bank and voice cloning (with strict consent controls).
- Integration with AAC devices and eye-tracking inputs.
- Adaptive coaching mode for pre-interview practice sessions.

