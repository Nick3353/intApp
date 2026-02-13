from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class UserProfile:
    name: str = "Candidate"
    role_target: str = "the role"
    top_strength: str = "structured problem-solving"
    project_highlight: str = "a cross-functional delivery project"


@dataclass
class Suggestion:
    title: str
    text: str


class SuggestionEngine:
    def generate(self, question: str, profile: UserProfile, limit: int = 3) -> List[Suggestion]:
        intent = self._detect_intent(question)
        builders = {
            "intro": self._intro,
            "challenge": self._challenge,
            "motivation": self._motivation,
            "strengths": self._strengths,
            "generic": self._generic,
        }
        drafts = builders.get(intent, self._generic)(question, profile)
        return drafts[:limit]

    def _detect_intent(self, question: str) -> str:
        q = question.lower()
        if "tell me about yourself" in q:
            return "intro"
        if "challenging" in q or "challenge" in q:
            return "challenge"
        if "why do you want" in q or "motivat" in q:
            return "motivation"
        if "strength" in q or "team" in q:
            return "strengths"
        return "generic"

    def _intro(self, question: str, p: UserProfile) -> List[Suggestion]:
        _ = question
        return [
            Suggestion("Concise", f"I am {p.name}, and I focus on {p.top_strength}. I am excited to contribute in {p.role_target}."),
            Suggestion("STAR-flavored", f"Recently, I led {p.project_highlight}, which improved outcomes through {p.top_strength}."),
            Suggestion("Fallback", "I can share a brief summary of my background and most relevant achievements.")
        ]

    def _challenge(self, question: str, p: UserProfile) -> List[Suggestion]:
        _ = question
        return [
            Suggestion("STAR", f"Situation: In {p.project_highlight}, timelines slipped. Task: Recover delivery. Action: I prioritized risks and aligned stakeholders. Result: We shipped on time with quality."),
            Suggestion("Concise", "I break challenges into clear steps, communicate trade-offs, and maintain momentum with the team."),
            Suggestion("Fallback", "One challenge I handled required balancing quality and speed while keeping stakeholders aligned.")
        ]

    def _motivation(self, question: str, p: UserProfile) -> List[Suggestion]:
        _ = question
        return [
            Suggestion("Role fit", f"I am motivated by this role because it aligns with my strength in {p.top_strength} and the impact I want to create."),
            Suggestion("Company fit", "I value the organization’s mission and collaborative culture, and I can contribute quickly."),
            Suggestion("Fallback", "This role fits both my experience and long-term growth goals.")
        ]

    def _strengths(self, question: str, p: UserProfile) -> List[Suggestion]:
        _ = question
        return [
            Suggestion("Teamwork", "My strength is collaborative execution: clear communication, proactive support, and accountability."),
            Suggestion("Technical", f"I bring {p.top_strength}, especially when projects require structure under deadlines."),
            Suggestion("Fallback", "I’m strongest when translating complex tasks into clear, achievable plans.")
        ]

    def _generic(self, question: str, p: UserProfile) -> List[Suggestion]:
        _ = p
        return [
            Suggestion("Clarify", f"Thanks for the question. My understanding is: {question}"),
            Suggestion("Concise answer", "I can provide a concise response with one example and one measurable result."),
            Suggestion("Fallback", "Could I take a moment to organize my response? I’ll keep it focused.")
        ]
