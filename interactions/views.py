from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from core.utils import notify_user
from materials.models import StudyMaterial

from .forms import CommentForm, RatingForm, ReportForm
from .models import Bookmark, Comment, Like, Rating, Report


@login_required
@require_POST
def toggle_like(request, slug):
    material = get_object_or_404(StudyMaterial, slug=slug, status='approved')
    like, created = Like.objects.get_or_create(material=material, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if material.uploaded_by != request.user:
            notify_user(
                material.uploaded_by,
                'New Like',
                f'{request.user.username} liked your material "{material.title}"',
                'like',
                material.get_absolute_url(),
            )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': material.likes.count()})
    return redirect(material.get_absolute_url())


@login_required
@require_POST
def toggle_bookmark(request, slug):
    material = get_object_or_404(StudyMaterial, slug=slug, status='approved')
    bookmark, created = Bookmark.objects.get_or_create(material=material, user=request.user)
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})
    return redirect(material.get_absolute_url())


@login_required
@require_POST
def add_comment(request, slug):
    material = get_object_or_404(StudyMaterial, slug=slug, status='approved')
    form = CommentForm(request.POST)
    parent_id = request.POST.get('parent_id')

    if form.is_valid():
        comment = form.save(commit=False)
        comment.material = material
        comment.user = request.user
        if parent_id:
            comment.parent = get_object_or_404(Comment, pk=parent_id, material=material)
        comment.save()

        if material.uploaded_by != request.user:
            notify_user(
                material.uploaded_by,
                'New Comment',
                f'{request.user.username} commented on "{material.title}"',
                'comment',
                material.get_absolute_url(),
            )
        messages.success(request, 'Comment posted.')
    else:
        messages.error(request, 'Could not post comment.')

    return redirect(material.get_absolute_url() + '#comments')


@login_required
@require_POST
def rate_material(request, slug):
    material = get_object_or_404(StudyMaterial, slug=slug, status='approved')
    score = int(request.POST.get('score', 0))
    if 1 <= score <= 5:
        Rating.objects.update_or_create(
            material=material, user=request.user,
            defaults={'score': score},
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'average': material.average_rating,
            'user_score': score,
        })
    return redirect(material.get_absolute_url())


@login_required
@require_POST
def report_material(request, slug):
    material = get_object_or_404(StudyMaterial, slug=slug)
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.material = material
        report.reported_by = request.user
        report.save()
        messages.success(request, 'Report submitted. Our team will review it.')
    return redirect(material.get_absolute_url())
