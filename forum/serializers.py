from rest_framework import serializers
from .models import Thread, Post, Like, Report

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'thread', 'author', 'content', 'image', 'video', 'parent', 'likes_count', 'replies', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_replies(self, obj):
        if obj.replies.exists():
            return PostSerializer(obj.replies.all(), many=True).data
        return []

class ThreadSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'course', 'title', 'author', 'created_at', 'posts']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'post', 'user', 'reason', 'created_at']
