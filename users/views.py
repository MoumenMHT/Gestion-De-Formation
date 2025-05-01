from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import User, Formation, UserFormation, Notification, Structure, Department
from .forms import UserForm, RegistrationForm
import json

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, user_email=email, password=password)
        if user is not None:
            if user.state != 'approved':
                messages.error(request, "Your account is not yet approved. Please wait for admin approval.")
            else:
                login(request, user)
                if user.user_role == 'DRH':
                    return redirect('admin/users/accountsdemanded/')
                else:
                    messages.success(request, f"Welcome, {user.user_username}!")
                    return redirect('users:user_list')
        else:
            messages.error(request, "Invalid email or password.")
    structures = Structure.objects.all()
    departments = Department.objects.all()
    return render(request, 'login.html', {'structures': structures, 'departments': departments})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Registration submitted successfully. Please wait for admin approval.'
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({
                'status': 'error',
                'message': 'Registration failed.',
                'errors': json.loads(errors)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def participate_formation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            formation_id = data.get('formation_id')
            formation = Formation.objects.get(formation_id=formation_id)
            user = request.user
            if UserFormation.objects.filter(user=user, formation=formation).exists():
                return JsonResponse({'status': 'error', 'message': 'You are already registered for this formation.'})
            user_formation = UserFormation(
                user=user,
                formation=formation,
                state_formation='pending'
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
            notification = Notification.objects.get(notification_id=notification_id, user=request.user)
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

class UserListView(ListView):
    model = User
    template_name = 'users/index.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.structure:
            context['formations'] = Formation.objects.all()
        else:
            context['formations'] = Formation.objects.none()
        if user.is_authenticated:
            context['user_formations'] = UserFormation.objects.filter(user=user)
            context['notifications'] = Notification.objects.filter(user=user, is_read=False)
            if user.user_role == 'manager' and user.structure:
                context['subordinate_employees'] = User.objects.filter(
                    structure=user.structure,
                    state='approved'
                ).exclude(user_id=user.user_id).select_related('department', 'structure')
            elif user.user_role == 'department_chief' and user.department:
                context['subordinate_employees'] = User.objects.filter(
                    department=user.department,
                    state='approved'
                ).exclude(user_id=user.user_id).select_related('department', 'structure')
            else:
                context['subordinate_employees'] = User.objects.none()
        else:
            context['user_formations'] = UserFormation.objects.none()
            context['notifications'] = Notification.objects.none()
            context['subordinate_employees'] = User.objects.none()
        context['user'] = user
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
    success_url = reverse_lazy('users:index')

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
    success_url = reverse_lazy('users:index')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)

class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:index')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_role == 'DRH':
            return redirect('admin:index')
        return super().get(request, *args, **kwargs)