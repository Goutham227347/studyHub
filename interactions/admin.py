from django.contrib import admin

from .models import Bookmark, Comment, DownloadHistory, Like, Rating, Report


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'material', 'created_at', 'is_active')
    list_filter = ('is_active',)


admin.site.register(Rating)
admin.site.register(Like)
admin.site.register(DownloadHistory)
admin.site.register(Bookmark)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('material', 'reported_by', 'reason', 'resolved', 'created_at')
    list_filter = ('resolved', 'reason')
