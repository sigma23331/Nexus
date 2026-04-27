from abc import ABC, abstractmethod
from datetime import date


class LLMProvider(ABC):
    @abstractmethod
    def generate_answer(self, question, user_id):
        raise NotImplementedError

    @abstractmethod
    def generate_fortune(self, user_id, target_date: date):
        raise NotImplementedError

    @abstractmethod
    def analyze_user_profile(self, diary_entries: list, answer_questions: list) -> dict:
        raise NotImplementedError
