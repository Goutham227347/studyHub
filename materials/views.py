from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView, DetailView, ListView

from interactions.models import Bookmark, DownloadHistory, Like, Rating
from interactions.forms import CommentForm

from .forms import MaterialFilterForm, StudyMaterialForm
from .models import Category, MaterialView, StudyMaterial, Subject
from .utils import generate_thumbnail


def get_filtered_materials(request):
    """Apply search filters from GET params."""
    qs = StudyMaterial.objects.filter(status='approved').select_related(
        'uploaded_by', 'subject', 'category'
    )

    form = MaterialFilterForm(request.GET or None)
    q = request.GET.get('q', '').strip()
    subject = request.GET.get('subject')
    category = request.GET.get('category')
    file_type = request.GET.get('file_type')
    semester = request.GET.get('semester')
    uploader = request.GET.get('uploader', '').strip()
    sort = request.GET.get('sort', '-created_at')

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(tags__name__icontains=q) |
            Q(uploaded_by__username__icontains=q)
        ).distinct()
    if subject:
        qs = qs.filter(subject_id=subject)
    if category:
        qs = qs.filter(category_id=category)
    if file_type:
        qs = qs.filter(file_type=file_type)
    if semester:
        qs = qs.filter(semester=semester)
    if uploader:
        qs = qs.filter(uploaded_by__username__icontains=uploader)

    allowed_sorts = ['-created_at', 'created_at', '-download_count', '-view_count', 'title']
    if sort in allowed_sorts:
        qs = qs.order_by(sort, '-pk')
    else:
        qs = qs.order_by('-created_at', '-pk')

    return qs.distinct(), form


class HomeView(ListView):
    """Home page with bento grid sections."""
    template_name = 'core/home.html'
    context_object_name = 'featured'

    def get_queryset(self):
        return StudyMaterial.objects.filter(status='approved', is_featured=True)[:6]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        approved = StudyMaterial.objects.filter(status='approved')
        ctx['popular'] = approved.order_by('-download_count')[:8]
        ctx['recent'] = approved.order_by('-created_at')[:8]
        ctx['categories'] = Category.objects.annotate(
            material_count=Count('materials')
        ).order_by('-material_count')[:8]
        ctx['top_contributors'] = (
            approved.values('uploaded_by__username', 'uploaded_by__id')
            .annotate(upload_count=Count('id'))
            .order_by('-upload_count')[:6]
        )
        ctx['trending_subjects'] = Subject.objects.annotate(
            count=Count('materials')
        ).order_by('-count')[:8]
        ctx['popular_tags'] = self._popular_tags()
        ctx['filter_form'] = MaterialFilterForm()
        return ctx

    def _popular_tags(self):
        from taggit.models import Tag
        return Tag.objects.filter(
            taggit_taggeditem_items__content_type__model='studymaterial'
        ).annotate(
            num=Count('taggit_taggeditem_items')
        ).order_by('-num')[:12]


class BrowseView(ListView):
    template_name = 'materials/browse.html'
    context_object_name = 'materials'
    paginate_by = settings.MATERIALS_PER_PAGE

    def get_queryset(self):
        self.filter_form = MaterialFilterForm(self.request.GET or None)
        self.qs, _ = get_filtered_materials(self.request)
        return self.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = self.filter_form
        ctx['categories'] = Category.objects.all()
        ctx['subjects'] = Subject.objects.all()
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class MaterialDetailView(DetailView):
    model = StudyMaterial
    template_name = 'materials/detail.html'
    context_object_name = 'material'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        qs = StudyMaterial.objects.select_related('uploaded_by', 'subject', 'category')
        if not self.request.user.is_staff:
            qs = qs.filter(Q(status='approved') | Q(uploaded_by=self.request.user))
        return qs

    def get_object(self):
        obj = super().get_object()
        if obj.status != 'approved' and obj.uploaded_by != self.request.user and not self.request.user.is_staff:
            raise Http404()
        StudyMaterial.objects.filter(pk=obj.pk).update(view_count=obj.view_count + 1)
        self._track_view(obj)
        return obj

    def _track_view(self, material):
        user = self.request.user if self.request.user.is_authenticated else None
        session_key = getattr(self.request, 'studyhub_session_key', '')
        if user:
            MaterialView.objects.filter(user=user, material=material).delete()
            MaterialView.objects.create(user=user, material=material)
        elif session_key:
            MaterialView.objects.filter(session_key=session_key, material=material, user=None).delete()
            MaterialView.objects.create(session_key=session_key, material=material)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        material = self.object
        user = self.request.user

        comments = material.comments.filter(parent=None, is_active=True).select_related('user')[:20]
        ctx['comments'] = comments
        ctx['comment_form'] = CommentForm()
        ctx['related'] = StudyMaterial.objects.filter(
            status='approved'
        ).filter(
            Q(subject=material.subject) | Q(category=material.category)
        ).exclude(pk=material.pk)[:6]

        if user.is_authenticated:
            ctx['user_liked'] = Like.objects.filter(material=material, user=user).exists()
            ctx['user_bookmarked'] = Bookmark.objects.filter(material=material, user=user).exists()
            ctx['user_rating'] = Rating.objects.filter(material=material, user=user).first()
        else:
            ctx['user_liked'] = False
            ctx['user_bookmarked'] = False
            ctx['user_rating'] = None

        return ctx


class UploadMaterialView(LoginRequiredMixin, CreateView):
    model = StudyMaterial
    form_class = StudyMaterialForm
    template_name = 'materials/upload.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Material uploaded successfully!')
        response = super().form_valid(form)
        try:
            generate_thumbnail(self.object)
            if self.object.thumbnail:
                self.object.save(update_fields=['thumbnail'])
        except Exception:
            pass  # Thumbnail is optional; upload still succeeds
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


@login_required
def download_material(request, slug):
    material = get_object_or_404(StudyMaterial, slug=slug, status='approved')
    if not material.file or not material.file.name:
        messages.error(request, 'This material has no file attached.')
        return redirect(material.get_absolute_url())
    try:
        if not material.file.storage.exists(material.file.name):
            messages.error(request, 'File not found on server. Please re-upload.')
            return redirect(material.get_absolute_url())
    except Exception:
        pass
    material.download_count += 1
    material.save(update_fields=['download_count'])

    DownloadHistory.objects.create(
        material=material,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    from core.utils import notify_user
    if material.uploaded_by != request.user:
        notify_user(
            material.uploaded_by,
            'New Download',
            f'{request.user.username} downloaded your material "{material.title}"',
            'download',
            material.get_absolute_url(),
        )

    response = FileResponse(material.file.open('rb'), as_attachment=True, filename=material.file.name.split('/')[-1])
    return response


@require_GET
def search_suggestions(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'suggestions': []})

    materials = StudyMaterial.objects.filter(
        status='approved', title__icontains=q
    ).values('title', 'slug')[:8]
    tags = StudyMaterial.objects.filter(
        status='approved', tags__name__icontains=q
    ).values_list('tags__name', flat=True).distinct()[:5]

    suggestions = []
    for m in materials:
        suggestions.append({'type': 'material', 'label': m['title'], 'url': f"/materials/{m['slug']}/"})
    subject_objs = Subject.objects.filter(name__icontains=q)[:5]
    for s in subject_objs:
        suggestions.append({'type': 'subject', 'label': s.name, 'url': f"/materials/browse/?subject={s.pk}"})
    for t in tags:
        if t:
            suggestions.append({'type': 'tag', 'label': f'#{t}', 'url': f"/materials/?q={t}"})

    return JsonResponse({'suggestions': suggestions[:15]})


@require_GET
def ajax_search(request):
    """AJAX partial for browse results."""
    qs, form = get_filtered_materials(request)
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, settings.MATERIALS_PER_PAGE)
    page_obj = paginator.get_page(page)
    return render(request, 'materials/partials/material_grid.html', {
        'materials': page_obj.object_list,
        'page_obj': page_obj,
    })


@require_GET
def infinite_scroll(request):
    """Load more materials for infinite scroll."""
    return ajax_search(request)
