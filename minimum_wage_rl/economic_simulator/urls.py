from django.urls import path
from . import views

urlpatterns = [
    path('create-user', views.create_user ,name="create-user-endpoint"),
    path('test-obj', views.test_obj ,name="test-obj-endpoint"),
    path('perform-action/<int:action>', views.perform_action ,name="perform-action-endpoint"),

]