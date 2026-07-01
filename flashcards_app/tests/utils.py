from django.contrib.auth import get_user_model

from flashcards_app.models import CardType

User = get_user_model()


def get_user_kwargs():
    return {
        "username": "TestUser",
        "email": "testuser@example.com",
        "password": "testpassword123",
    }


def get_user_dict(**kwargs):
    return {**get_user_kwargs(), **kwargs}


def get_card_kwargs():
    return {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "choices": [],
        "search_terms": ["capital", "France", "city"],
        "notes": "Remember to check the spelling.",
        "card_type": CardType.SELF_ASSESSMENT.value,
    }


def get_card_dict(user=None, choices=None, **kwargs):
    """
    Returns a dictionary representing a flashcard with default values.
    Allows overriding of default values via kwargs.
    """
    result = {**get_card_kwargs(), "user": user, **kwargs}

    if choices is not None:
        result["answer"] = ""
        result["choices"] = choices

    return result
