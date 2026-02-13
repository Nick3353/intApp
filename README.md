# InclusiVoice Prototype

InclusiVoice is a **Windows desktop accessibility prototype** for virtual interviews. It provides:
- Real-time transcript simulation pipeline (replaceable with real loopback capture + STT)
- Context-aware response suggestions
- **Explicit user-consent gate** before any text-to-speech output
- Always-on-top support UI with explicit minimize behavior

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src python src/main.py
```

## Build for Windows laptop

On Windows PowerShell:

```powershell
./build_windows.ps1
```

Output:
- `dist\InclusiVoice.exe`

## Prototype architecture

- `src/inclusivoice/controller.py`: orchestration and consent-enforced speech behavior
- `src/inclusivoice/audio.py`: prototype chunk capture (replace with WASAPI loopback)
- `src/inclusivoice/stt.py`: STT adapter scaffold (replace with whisper/Azure stream)
- `src/inclusivoice/nlp.py`: intent detection + suggestion templates
- `src/inclusivoice/tts_engine.py`: local TTS wrapper (`pyttsx3`)

## Notes for production hardening

This prototype currently uses simulated STT events in `src/inclusivoice/stt.py`. For production:
- Implement real loopback/mic capture
- Add encrypted local storage for profiles/session artifacts
- Add signed updates and enterprise deployment policy support

## Responsible-use boundary

This application is designed for accessibility and coaching workflows with explicit user consent.
It is not intended for stealth operation, bypassing screen sharing visibility, or deceptive use.
