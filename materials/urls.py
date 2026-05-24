from django.urls import path

from . import views

app_name = 'materials'

urlpatterns = [
    path('browse/', views.BrowseView.as_view(), name='browse'),
    path('upload/', views.UploadMaterialView.as_view(), name='upload'),
    path('<slug:slug>/', views.MaterialDetailView.as_view(), name='detail'),
    path('<slug:slug>/download/', views.download_material, name='download'),
    path('api/suggestions/', views.search_suggestions, name='suggestions'),
    path('api/search/', views.ajax_search, name='ajax_search'),
    path('api/more/', views.infinite_scroll, name='infinite_scroll'),
]
