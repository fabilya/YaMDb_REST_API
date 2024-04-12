from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api_yamdb.settings import (
    CONFIRMATION_CODE_LENGTH,
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
)
from reviews.validators import username_validator

SCORE_ERROR = 'Score has to be a value from 1 to 10.'
REVIEW_DUPLICATE_ERROR = 'You can have only one review per title.'


class UserNameValidatorMixin:
    def validate_username(self, value):
        return username_validator(value)


class SignUpSerializer(serializers.Serializer, UserNameValidatorMixin):
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
    )
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
    )


class UserSerializer(serializers.ModelSerializer, UserNameValidatorMixin):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserMeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer, UserNameValidatorMixin):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LENGTH,
        required=True,
    )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(default=0)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = fields


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, attrs):
        request = self.context.get('request')
        if (
            request.method != 'POST'
            or not get_object_or_404(
                Title, pk=self.context.get('view').kwargs.get('title_id')
            ).reviews.filter(author=request.user).exists()
        ):
            return attrs
        raise serializers.ValidationError(REVIEW_DUPLICATE_ERROR)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
