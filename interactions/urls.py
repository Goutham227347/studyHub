from django.urls import path

from . import views

app_name = 'interactions'

urlpatterns = [
    path('<slug:slug>/like/', views.toggle_like, name='like'),
    path('<slug:slug>/bookmark/', views.toggle_bookmark, name='bookmark'),
    path('<slug:slug>/comment/', views.add_comment, name='comment'),
    path('<slug:slug>/rate/', views.rate_material, name='rate'),
    path('<slug:slug>/report/', views.report_material, name='report'),
]
