from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from recipe import serializers
from core.models import Tag


# Manage tags in the database
class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # Return objects for the current authenticated user only
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')
