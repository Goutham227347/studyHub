from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, UpdateView

from interactions.models import DownloadHistory
from materials.models import StudyMaterial

from .forms import ProfileEditForm, RegisterForm
from .models import UserProfile


class StudyHubLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class StudyHubLogoutView(LogoutView):
    next_page = 'core:home'


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/dashboard/'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Welcome to StudyHub! Your account has been created.')
        return response


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    uploads = StudyMaterial.objects.filter(
        uploaded_by=profile_user, status='approved'
    ).order_by('-created_at')[:12]

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'uploads': uploads,
        'upload_count': StudyMaterial.objects.filter(uploaded_by=profile_user).count(),
        'is_own_profile': request.user.is_authenticated and request.user == profile_user,
    }

    if request.user.is_authenticated and request.user == profile_user:
        context['liked_materials'] = StudyMaterial.objects.filter(
            likes__user=profile_user, status='approved'
        ).distinct()[:12]
        context['bookmarks'] = StudyMaterial.objects.filter(
            bookmarks__user=profile_user, status='approved'
        ).distinct()[:12]
        context['download_history'] = DownloadHistory.objects.filter(
            user=profile_user
        ).select_related('material')[:20]

    return render(request, 'accounts/profile.html', context)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileEditForm
    template_name = 'accounts/edit_profile.html'

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        messages.success(self.request, 'Profile updated successfully.')
        return self.request.user.profile.get_absolute_url()
