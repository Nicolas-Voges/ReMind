from django.contrib.auth import get_user_model

from flashcards_app.models import CardType

User = get_user_model()


def get_user_kwargs():
    return {
        'username': "TestUser",
        'email': "testuser@example.com",
        'password': "testpassword123"
    }


def get_user_dict(**kwargs):
    return {**get_user_kwargs(), **kwargs}


def get_card_kwargs():
    return {
        'question': "What is the capital of France?",
        'answer': "Paris",
        'choices': None,
        'search_terms': ["capital", "France", "city"],
        'notes': "Remember to check the spelling.",
        'card_type': CardType.SELF_ASSESSMENT.value
    }


def get_card_dict(user=None, choices=None, **kwargs):
    """
    Returns a dictionary representing a flashcard with default values.
    Allows overriding of default values via kwargs.
    """
    if user is None:
        user = User.objects.create_user(**get_user_kwargs())
    if choices is not None:
        return {**get_card_kwargs(), **kwargs, 'answer': None, 'choices': choices, "user": user}
    return {**get_card_kwargs(), **kwargs, "user": user}