from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Ingredient, Recipe, Tag


# Base viewset for user owned recipe attributes
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Return objects for the current authenticated user only
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # Create a new tag
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Manage tags in the database
class TagViewSet(BaseRecipeAttrViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


# Manage ingredients in database
class IngredientViewSet(BaseRecipeAttrViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


# Manage recipes in database
class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Retrieve the recipes for the authenticated user
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class
