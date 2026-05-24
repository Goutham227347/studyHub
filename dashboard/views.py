from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import Notification
from interactions.models import DownloadHistory, Like, Report
from materials.models import StudyMaterial


@login_required
def user_dashboard(request):
    user = request.user
    uploads = StudyMaterial.objects.filter(uploaded_by=user)
    approved = uploads.filter(status='approved')

    total_downloads = DownloadHistory.objects.filter(material__uploaded_by=user).count()
    total_likes = Like.objects.filter(material__uploaded_by=user).count()

    recent_uploads = uploads.order_by('-created_at')[:5]
    recent_downloads = DownloadHistory.objects.filter(
        material__uploaded_by=user
    ).select_related('user', 'material').order_by('-downloaded_at')[:10]

    return render(request, 'dashboard/user.html', {
        'total_uploads': uploads.count(),
        'approved_uploads': approved.count(),
        'total_downloads': total_downloads,
        'total_likes': total_likes,
        'recent_uploads': recent_uploads,
        'recent_downloads': recent_downloads,
    })


@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    stats = {
        'total_users': User.objects.count(),
        'new_users_week': User.objects.filter(date_joined__gte=week_ago).count(),
        'total_materials': StudyMaterial.objects.count(),
        'approved_materials': StudyMaterial.objects.filter(status='approved').count(),
        'pending_materials': StudyMaterial.objects.filter(status='pending').count(),
        'total_downloads': DownloadHistory.objects.count(),
        'downloads_week': DownloadHistory.objects.filter(downloaded_at__gte=week_ago).count(),
    }

    most_downloaded = StudyMaterial.objects.filter(status='approved').order_by('-download_count')[:10]
    reported = Report.objects.filter(resolved=False).select_related('material', 'reported_by')[:10]

    uploads_by_day = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = StudyMaterial.objects.filter(created_at__date=day).count()
        uploads_by_day.append({'day': day.strftime('%a'), 'count': count})

    users_by_day = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = User.objects.filter(date_joined__date=day).count()
        users_by_day.append({'day': day.strftime('%a'), 'count': count})

    return render(request, 'dashboard/admin.html', {
        'stats': stats,
        'most_downloaded': most_downloaded,
        'reported': reported,
        'uploads_by_day': uploads_by_day,
        'users_by_day': users_by_day,
    })


@staff_member_required
def manage_users(request):
    users = User.objects.select_related('profile').annotate(
        upload_count=Count('uploads'),
    ).order_by('-date_joined')

    q = request.GET.get('q', '')
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))

    return render(request, 'dashboard/manage_users.html', {'users': users, 'query': q})


@staff_member_required
def moderate_materials(request):
    status = request.GET.get('status', 'pending')
    materials = StudyMaterial.objects.select_related('uploaded_by', 'category').order_by('-created_at')
    if status:
        materials = materials.filter(status=status)

    return render(request, 'dashboard/moderate.html', {
        'materials': materials,
        'current_status': status,
    })


@staff_member_required
@require_POST
def moderate_action(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    action = request.POST.get('action')

    if action == 'approve':
        material.status = 'approved'
        material.save(update_fields=['status'])
        from core.utils import notify_user
        notify_user(
            material.uploaded_by,
            'Material Approved',
            f'Your upload "{material.title}" has been approved.',
            'approval',
            material.get_absolute_url(),
        )
        messages.success(request, f'Approved "{material.title}"')
    elif action == 'reject':
        material.status = 'rejected'
        material.save(update_fields=['status'])
        from core.utils import notify_user
        notify_user(
            material.uploaded_by,
            'Material Rejected',
            f'Your upload "{material.title}" was not approved.',
            'rejection',
        )
        messages.warning(request, f'Rejected "{material.title}"')
    elif action == 'delete':
        title = material.title
        material.delete()
        messages.error(request, f'Deleted "{title}"')
    elif action == 'resolve_report':
        report_id = request.POST.get('report_id')
        if report_id:
            Report.objects.filter(pk=report_id).update(resolved=True)

    return redirect('dashboard:moderate')


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)[:50]
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
@require_POST
def toggle_theme(request):
    profile = request.user.profile
    profile.theme_preference = 'light' if profile.theme_preference == 'dark' else 'dark'
    profile.save(update_fields=['theme_preference'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'theme': profile.theme_preference})
    return redirect(request.META.get('HTTP_REFERER', '/'))
