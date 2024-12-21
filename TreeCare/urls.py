from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),

    path('import/', views.import_csv, name='import'),

    path('export/', views.export_csv, name='export'),

    path('add-tree/', views.add_tree, name='add_tree'),

]