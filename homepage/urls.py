from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('getdata/', views.get_data),
    path('download/', views.download_file),
    path('download_excel/', views.download_excel_file),
    path('playlist_download/', views.playlist_download_file),
    path('playlist_download_excel/', views.playlist_download_excel_file)


]