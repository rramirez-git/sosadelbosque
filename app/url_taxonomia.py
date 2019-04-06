from django.urls import path

import app.vw_taxonomia as views

object_name = 'taxonomia'

urlpatterns = [
    path('', views.index, name="{}_index".format(object_name)),
    path('nueva/', views.new, name="{}_new".format(object_name)),
    path('<pk>/', views.see, name="{}_see".format(object_name)),
    path('actualizar/<pk>/', views.update, name="{}_update".format(
        object_name)),
    path('eliminar/<pk>/', views.delete, name="{}_delete".format(
        object_name)),
]