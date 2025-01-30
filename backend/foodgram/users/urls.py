from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowApiView, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/<author_id>/subscribe/',
        FollowApiView.as_view(),
        name='follow',
    ),
]
