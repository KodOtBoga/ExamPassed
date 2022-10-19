from rest_framework import serializers
from apps.library.models import *

class WritersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writers
        fields = (
            'id',
            'first_name',
            'last_name',
            'country'
        )

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'description',
            'author',
            'rating',
            'published_year'
        )
        depth = 1

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            'id',
            'pageNumber',
            'bookId',
            'image'
        )

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = (
            'id',
            'bookId',
            'userId',
            'time',
            'comment'
        )
        #depth = 1

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "last_login"
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
