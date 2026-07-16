"""
Serializers for the flashcards API.

This module provides data validation and serialization for flashcard
instances, category trees, and bulk operation payloads.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from flashcards_app.models import Category, Flashcard

User = get_user_model()


class FlashCardModelSerializer(serializers.ModelSerializer):
    """
    Serializer for Flashcard objects.

    Includes field-level and object-level validation to enforce structures
    based on whether the card is a standard type or multiple-choice.
    """

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
            'last_interval_ms',
            'history',
        ]
        read_only_fields = [
            'id',
            'user',
            'stage',
            'created_at',
            'due_date',
            'last_interval_ms',
            'history',
        ]

    def validate_choices(self, value):
        """
        Validate the choices field format.

        Ensures each entry is an iterable pair containing a string
        and a boolean flag indicating if it is correct.
        """

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
        """
        Helper method to retrieve fields during partial updates.

        Returns the value from incoming data, or falls back to the instance
        value if the data dictionary does not provide it.
        """

        value = data.get(field_name)
        if value is None and self.instance is not None:
            return getattr(self.instance, field_name, None)
        return value

    def validate(self, data):
        """
        Object-level validation for flashcard data.

        Enforces mandatory answer texts for standard types and requires
        at least two available choices for multiple-choice formats.
        """

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


class CategoryModelSerializer(serializers.ModelSerializer):
    """
    Serializer for Category objects.

    Implements cross-user validation and deep-nested recursive checks
    to prevent infinite hierarchy loops within category assignments.
    """

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'user',
            'parent',
        ]
        read_only_fields = [
            'id',
            'user',
        ]

    def validate(self, data):
        """
        Validate hierarchy constraints for the parent category.

        Guarantees that a user only uses their own nodes and scans up
        the existing ancestral tree to rule out circular references.
        """

        instance = self.instance
        parent = data.get('parent')
        request_user = self.context['request'].user

        if parent and parent.user != request_user:
            raise serializers.ValidationError(
                {
                    "parent": "You can only select your own categories as parent categories."
                }
            )

        if instance and parent:
            if parent == instance:
                raise serializers.ValidationError(
                    {"parent": "A Category cannot be its own parent."}
                )

            current_parent = parent
            while current_parent is not None:
                if current_parent == instance:
                    raise serializers.ValidationError(
                        {
                            "parent": f"Circular referenze detected: Category '{parent.name}' is already a child category from '{instance.name}'."
                        }
                    )
                current_parent = current_parent.parent

        return data


class BulkAssignCategorySerializer(serializers.Serializer):
    """
    Non-model serializer to parse bulk category assignment requests.

    Verifies IDs and fetches fully evaluated QuerySets for secure processing.
    """

    category_id = serializers.IntegerField()
    card_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

    def validate(self, data):
        """
        Validate bulk payload entities against the active request user.

        Verifies ownership of the destination category and ensures that every
        submitted flashcard ID exists and belongs to the active account.
        """

        request_user = self.context['request'].user
        category_id = data['category_id']
        card_ids = data['card_ids']

        try:
            category = Category.objects.get(id=category_id, user=request_user)
        except Category.DoesNotExist:
            raise NotFound("Category not found.")

        unique_card_ids = list(set(card_ids))
        cards = Flashcard.objects.filter(id__in=unique_card_ids, user=request_user)

        if cards.count() != len(unique_card_ids):
            raise serializers.ValidationError(
                {"card_ids": "One or more card IDs are invalid or access is denied."}
            )

        data['category_obj'] = category
        data['cards_queryset'] = cards
        return data
