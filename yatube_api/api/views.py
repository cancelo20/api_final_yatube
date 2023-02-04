from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Post, Group, Comment, Follow
from .permissions import IsAuthorOrReadOnly, FollowPermission
from .viewsets import CreateListMixinViewSet
from . import serializers


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()


class CommentViewSet(ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return super().get_queryset().filter(post=post_id)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()


class FollowViewSet(CreateListMixinViewSet):
    queryset = Follow.objects.all()
    serializer_class = serializers.FollowSerializer
    permission_classes = [IsAuthenticated, FollowPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ("user__username", "following__username")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.request.user.follower.all()
