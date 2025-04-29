from django.urls import path
from . import views
from .views import user_logout

app_name = 'users'

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),  # List all users
    path('create/', views.UserCreateView.as_view(), name='user_create'),  # Create a user
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),  # View user details
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),  # Update a user
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),  # Delete a user
    path('logout/', user_logout, name='logout'),
    path('participate/', views.participate_formation, name='participate_formation'),  # Participate in a formation
    path('mark_notification_read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark_all_notifications_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('register/', views.register, name='register'),

]