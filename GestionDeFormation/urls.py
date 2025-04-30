from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from users.views import user_login, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface URL
    path('users/', include('users.urls', namespace='users')),
    path('', user_login, name='login'),  # Explicit login URL
    path('logout/', user_logout, name='logout'),

]