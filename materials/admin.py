from django.contrib import admin

from .models import Category, Subject, StudyMaterial, MaterialView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'color')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category')


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'status', 'file_type', 'download_count', 'created_at')
    list_filter = ('status', 'file_type', 'category', 'is_featured')
    search_fields = ('title', 'description', 'uploaded_by__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('file_size', 'download_count', 'view_count')


admin.site.register(MaterialView)
