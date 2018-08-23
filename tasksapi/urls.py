"""Contains URLs for the tasksapi app."""

from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from tasksapi import views


# A router to register Django REST Framework viewsets
class OptionalSlashRouter(DefaultRouter):
    """A router that makes a trailing slash optional

    Thanks to Ryan Allen on StackOverflow.
    """
    def __init__(self):
        """Make trailing slashes optional."""
        super().__init__()
        self.trailing_slash = '/?'


# Register the routes
router = OptionalSlashRouter()
router.register(
    'users',
    views.UserViewSet)
router.register(
    'containertaskinstances',
    views.ContainerTaskInstanceViewSet,)
router.register(
    'containertasktypes',
    views.ContainerTaskTypeViewSet)
router.register(
    'taskqueues',
    views.TaskQueueViewSet)


# Schema for Swagger API
schema_view = get_schema_view(
    openapi.Info(
        title="saltant API",
        default_version='v1',),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'auth/', include('rest_framework.urls')),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^swagger/(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    path(r'token/', views.TokenObtainPairPermissiveView.as_view(), name='token_obtain_pair'),
    path(r'token/refresh/', views.TokenRefreshPermissiveView.as_view(), name='token_refresh'),
]
