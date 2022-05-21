from rest_framework import serializers
from core.models import Tag
from core.models import Ingredient, Recipe


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


# Serializer a recipe
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price',
                  'link', 'ingredients', 'tags'
                  )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
