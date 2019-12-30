from django.urls import path

import simple_tasks.vw_tarea as views

object_name = 'tarea'

urlpatterns = [
     path('', views.index,
          name="{}_index".format(object_name)),
     path('<int:anio>/', views.index,
          name="{}_index".format(object_name)),
     path('<int:anio>/<int:mes>/', views.index,
          name="{}_index".format(object_name)),
     path('nuevo/', views.new,
          name="{}_new".format(object_name)),
     path('obtener/<int:anio>/<int:mes>/', views.get_tasks,
          name="{}_getall".format(object_name)),
]