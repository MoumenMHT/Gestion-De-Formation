from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import User, Formation, UserFormation, Notification
from .forms import UserForm
import json

class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter formations to only those belonging to the user's structure
        if self.request.user.is_authenticated and self.request.user.structure:
            context['formations'] = Formation.objects.filter(structure=self.request.user.structure)
        else:
            context['formations'] = Formation.objects.none()
        # Add user's participated formations
        if self.request.user.is_authenticated:
            context['user_formations'] = self.request.user.user_formations.all()
            # Add user's unread notifications
            context['notifications'] = self.request.user.notifications.filter(is_read=False)
        else:
            context['user_formations'] = UserFormation.objects.none()
            context['notifications'] = Notification.objects.none()
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)

class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)

class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)

class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)

class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, user_email=email, password=password)

        if user is not None:
            login(request, user)
            if user.user_role == 'DRH':
                return redirect('admin:index')
            else:
                messages.success(request, f"Welcome, {user.user_username}!")
                return redirect('users:user_list')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required
def participate_formation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            formation_id = data.get('formation_id')
            formation = Formation.objects.get(formation_id=formation_id)
            user = request.user

            # Check if formation belongs to user's structure
            if formation.structure != user.structure:
                return JsonResponse({'status': 'error', 'message': 'You cannot register for formations outside your structure.'})

            # Check if the user is already registered for this formation
            if UserFormation.objects.filter(user=user, formation=formation).exists():
                return JsonResponse({'status': 'error', 'message': 'You are already registered for this formation.'})

            # Create a new UserFormation entry
            user_formation = UserFormation(
                user=user,
                formation=formation,
                state_formation='pending'  # Initial state
            )
            user_formation.save()

            return JsonResponse({'status': 'success', 'message': 'Successfully registered for the formation!'})
        except Formation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Formation not found.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def mark_notification_read(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')
            notification = Notification.objects.get(pk=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success', 'message': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        try:
            request.user.notifications.filter(is_read=False).update(is_read=True)
            return JsonResponse({'status': 'success', 'message': 'All notifications marked as read.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})