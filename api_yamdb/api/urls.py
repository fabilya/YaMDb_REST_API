from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import GetTokenView, SignUp, UserViewSet
from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

auth_urls = [
    path('auth/signup/', SignUp.as_view(), name='signup'),
    path('auth/token/', GetTokenView.as_view(), name='get_token'),
]

urlpatterns = [
    path('v1/', include(auth_urls)),
    path('v1/', include(router_v1.urls)),
]
