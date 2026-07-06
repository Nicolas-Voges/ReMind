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
            'shared',
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
        else:
            if choices:
                raise serializers.ValidationError(
                    {'choices': "Flashcards of this type must not contain any options."}
                )
            if not answer or answer.strip() == "":
                raise serializers.ValidationError(
                    {'answer': "An answer is required for this type."}
                )

        return data
