from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),  # List all users
    path('create/', views.UserCreateView.as_view(), name='user_create'),  # Create a user
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),  # View user details
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),  # Update a user
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),  # Delete a user
]