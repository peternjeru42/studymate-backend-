from rest_framework import viewsets


class UserOwnedModelViewSet(viewsets.ModelViewSet):
    user_field = "user"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(**{self.user_field: self.request.user})

    def perform_create(self, serializer):
        serializer.save(**{self.user_field: self.request.user})
