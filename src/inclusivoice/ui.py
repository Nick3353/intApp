from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from .audio import AudioCaptureService
from .config import AppConfig
from .controller import InclusiVoiceController
from .nlp import SuggestionEngine, UserProfile
from .stt import STTService
from .tts_engine import TTSEngine


class InclusiVoiceApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = AppConfig()
        self.config.ensure_dirs()

        self.audio = AudioCaptureService(chunk_seconds=self.config.chunk_seconds)
        self.controller = InclusiVoiceController(
            stt=STTService(),
            suggestion_engine=SuggestionEngine(),
            tts=TTSEngine(),
            profile=UserProfile(),
            max_suggestions=self.config.max_suggestions,
        )

        self._build_ui()
        self._running = False

    def _build_ui(self) -> None:
        self.root.title("InclusiVoice (Prototype)")
        self.root.geometry("560x500")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.config.window_alpha)

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=(0, 6))
        self.privacy_var = tk.StringVar(value="Private Mode: ON | TTS Output: OFF")
        ttk.Label(status_frame, textvariable=self.privacy_var, foreground="#126f2a").pack(anchor="w")

        ttk.Label(frame, text="Live Interview Transcript", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.transcript_var = tk.StringVar(value=self.controller.state.transcript)
        ttk.Label(frame, textvariable=self.transcript_var, wraplength=520).pack(anchor="w", pady=(4, 10))

        ttk.Label(frame, text="Suggested Responses", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.suggestion_box = tk.Listbox(frame, height=7)
        self.suggestion_box.pack(fill=tk.BOTH, expand=False, pady=(4, 10))

        ttk.Label(frame, text="Editable response", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.editor = tk.Text(frame, height=7, wrap=tk.WORD)
        self.editor.pack(fill=tk.BOTH, expand=True)

        consent_frame = ttk.Frame(frame)
        consent_frame.pack(fill=tk.X, pady=(8, 0))
        self.tts_consent_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            consent_frame,
            text="Enable text-to-speech output (user consent)",
            variable=self.tts_consent_var,
            command=self._toggle_tts_consent,
        ).pack(anchor="w")

        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=(10, 0))

        self.start_btn = ttk.Button(controls, text="Start Assist", command=self.start)
        self.start_btn.pack(side=tk.LEFT)
        self.speak_btn = ttk.Button(controls, text="Speak Selected", command=self.speak_editor_text, state=tk.DISABLED)
        self.speak_btn.pack(side=tk.LEFT, padx=8)
        self.stop_btn = ttk.Button(controls, text="Stop Assist", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        ttk.Button(controls, text="Minimize", command=self.minimize).pack(side=tk.RIGHT)

        self.suggestion_box.bind("<<ListboxSelect>>", self._on_select_suggestion)
        self.root.bind("<Control-Shift-M>", lambda _: self.minimize())

    def _toggle_tts_consent(self) -> None:
        enabled = self.tts_consent_var.get()
        self.controller.set_tts_enabled(enabled)
        self.speak_btn.configure(state=tk.NORMAL if enabled else tk.DISABLED)
        self.privacy_var.set(f"Private Mode: ON | TTS Output: {'ON' if enabled else 'OFF'}")

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.audio.start()
        threading.Thread(target=self._processing_loop, daemon=True).start()

    def stop(self) -> None:
        self._running = False
        self.audio.stop()
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)

    def _processing_loop(self) -> None:
        while self._running:
            chunk = self.audio.output.get()
            state = self.controller.process_audio_chunk(chunk)
            self.root.after(0, self._render_update, state)

    def _render_update(self, state) -> None:
        self.transcript_var.set(state.transcript)
        self.suggestion_box.delete(0, tk.END)
        for s in state.suggestions:
            self.suggestion_box.insert(tk.END, f"{s.title}: {s.text}")

    def _on_select_suggestion(self, _event) -> None:
        if not self.suggestion_box.curselection():
            return
        index = self.suggestion_box.curselection()[0]
        content = self.controller.select_suggestion(index)
        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, content)

    def speak_editor_text(self) -> None:
        text = self.editor.get("1.0", tk.END).strip()
        self.controller.speak(text)

    def minimize(self) -> None:
        self.root.iconify()


def run() -> None:
    root = tk.Tk()
    app = InclusiVoiceApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()
