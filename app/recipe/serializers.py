from rest_framework import serializers
from core.models import Tag
from core.models import Ingredient


# Serializer for tag objects
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ('id',)


# Serializer for ingredient objects
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)
