from django.urls import path
from . import views
from rest_framework.authtoken import views as auth_view
# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Your API",
#         default_version='v1',
#         description="API Documentation",
#         terms_of_service="https://www.example.com/terms/",
#         contact=openapi.Contact(email="contact@example.com"),
#         license=openapi.License(name="MIT License"),
#     ),
#     public=True,
# )

urlpatterns = [
    path('start-game', views.start_game ,name="start-game-endpoint"),
    # path('test-obj', views.test_obj ,name="test-obj-endpoint"),
    path('perform-action', views.perform_action ,name="perform-action-endpoint"),
    # path('perform-get-action', views.perform_get_action ,name="perform-get-action-endpoint"),
    path('reg-user', views.create_user ,name="reg-user-endpoint"),
    path("token-auth", auth_view.obtain_auth_token),
    path("del-user",views.delete_user,name="del-user"),
    path("stop-game", views.stop_game, name="stop_game-endpoint"),
    path("save-game", views.end_and_save_game, name="end_game-endpoint"),
    path("test-url", views.test_url, name="test-endpoint"),
    path("api-token-auth", views.CustomAuthToken.as_view()),
    path('clear-cache', views.clear_cache, name="clear-cache"),
    path('get-game-stats', views.get_stats, name="game-stats-endpoint"),
]

    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
