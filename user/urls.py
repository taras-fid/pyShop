from django.urls import path
from . import views

urlpatterns = [
    path('all', views.users, name='users'),
    path('<int:user_id>', views.user_detail, name='user_detail'),
    path('<int:user_id>/set-user-role', views.set_user_role, name='set_user_role'),
]
