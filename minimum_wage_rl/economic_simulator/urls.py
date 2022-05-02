from django.urls import path
from . import views
from rest_framework.authtoken import views as auth_view

urlpatterns = [
    path('start-game', views.start_game ,name="start-game-endpoint"),
    # path('test-obj', views.test_obj ,name="test-obj-endpoint"),
    path('perform-action', views.perform_action ,name="perform-action-endpoint"),
    path('reg-user', views.create_user ,name="reg-user-endpoint"),
    path("token-auth", auth_view.obtain_auth_token),
    path("del-user",views.delete_user,name="del-user"),
    path("end-game", views.end_game, name="end_game-endpoint"),
    path("train", views.train, name="train-endpoint"),
    # path("test", views.test_post, name="test-endpoint") /<int:action>
]