from django.contrib.auth import get_user_model
from rest_framework import serializers

from flashcards_app.models import Flashcard

User = get_user_model()


class FlashCardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = [
            'id',
            'user',
            'question',
            'answer',
            'choices',
            'card_type',
            'stage',
            'notes',
            'search_terms',
            'created_at',
            'due_date',
            'categories',
        ]
        read_only_fields = [
            'id',
            'user',
            'stage',
            'created_at',
            'due_date',
        ]

    def validate_choices(self, value):
        if not value:
            return value

        for item in value:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise serializers.ValidationError(
                    "Each choice must be a pair of [text, is_correct]."
                )

            answer, is_correct = item

            if not isinstance(answer, str) or not isinstance(is_correct, bool):
                raise serializers.ValidationError(
                    "Wrong format of choices. First must be string, second must be boolean."
                )

        return value

    def _get_field(self, field_name, data):
        value = data.get(field_name)
        if value is None and self.instance is not None:
            return getattr(self.instance, field_name, None)
        return value

    def validate(self, data):
        card_type = self._get_field('card_type', data)
        choices = self._get_field('choices', data)
        answer = self._get_field('answer', data)

        if card_type == 'multiple_choice':
            if not choices or len(choices) < 2:
                raise serializers.ValidationError(
                    {'choices': "At least 2 options are required."}
                )
            data['answer'] = ''
        else:
            if not answer or answer.strip() == "":
                raise serializers.ValidationError(
                    {'answer': "An answer is required for this type."}
                )
            data['choices'] = []

        return data
