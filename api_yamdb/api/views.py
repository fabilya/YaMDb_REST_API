import random

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import IsAdmin, IsAuthorOrStuffOrReadOnly, ReadOnly
from api_yamdb.settings import (
    DEFAULT_CONFIRMATION_CODE,
    CONFIRMATION_CODE_LENGTH,
    CONFIRMATION_CODE_SYMBOLS,
    DEFAULT_FROM_EMAIL,
)
from reviews.models import Category, Genre, Review, Title, User
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)

WRONG_CODE_MESSAGE = (
    'Confirmation code is already used or incorrect. '
    'Please request a new one.'
)
SIGNUP_ERROR = 'Username or email is already registered.'
TOKEN_SUBJECT = 'YamDB Confirmation Code'
TOKEN_MESSAGE = 'Confirmation code for user "{username}": {token}'


class SignUp(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, created = User.objects.get_or_create(
                username=serializer.validated_data.get('username'),
                email=serializer.validated_data.get('email'),
            )
        except IntegrityError:
            raise ValidationError(SIGNUP_ERROR)
        confirmation_code = ''.join(
            random.choices(
                CONFIRMATION_CODE_SYMBOLS,
                k=CONFIRMATION_CODE_LENGTH,
            )
        )
        user.confirmation_code = confirmation_code
        send_mail(
            subject=TOKEN_SUBJECT,
            message=TOKEN_MESSAGE.format(
                username=user.username,
                token=confirmation_code,
            ),
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        user.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if (
            user.confirmation_code == DEFAULT_CONFIRMATION_CODE
            or user.confirmation_code != data['confirmation_code']
        ):
            user.confirmation_code = DEFAULT_CONFIRMATION_CODE
            user.save()
            return Response(
                {'confirmation_code': [WRONG_CODE_MESSAGE]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.confirmation_code = DEFAULT_CONFIRMATION_CODE
        user.save()
        return Response({'token': str(AccessToken.for_user(user))})


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ('get', 'post', 'delete', 'patch')
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(
                UserMeSerializer(request.user, many=False).data,
                status=status.HTTP_200_OK,
            )
        serializer = UserMeSerializer(
            request.user,
            partial=True,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (ReadOnly | IsAdmin,)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (ReadOnly | IsAdmin,)
    http_method_names = ('get', 'post', 'delete', 'patch')
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = TitleFilter
    ordering_fields = ('rating', 'name')
    ordering = ('-rating', 'name')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStuffOrReadOnly)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStuffOrReadOnly)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
