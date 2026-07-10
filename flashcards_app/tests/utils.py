from django.contrib.auth import get_user_model

from flashcards_app.models import CardType

User = get_user_model()


def get_user_dict(**kwargs):
    DEFAULTS = {
        'username': "TestUser",
        'email': "testuser@example.com",
        'password': "testpassword123",
    }
    return {**DEFAULTS, **kwargs}


def get_card_dict(user=None, choices=None, **kwargs):
    """
    Returns a dictionary representing a flashcard with default values.
    Allows overriding of default values via kwargs.
    """
    DEFAULTS = {
        'question': "What is the capital of France?",
        'answer': "Paris",
        'choices': [],
        'search_terms': ["capital", "France", "city"],
        'notes': "Remember to check the spelling.",
        'card_type': CardType.SELF_ASSESSMENT.value,
    }
    result = {**DEFAULTS, 'user': user, **kwargs}

    if choices is not None:
        result['answer'] = ""
        result['choices'] = choices
    else:
        result['choices'] = list(result['choices'])

    return result
