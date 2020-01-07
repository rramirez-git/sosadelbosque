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
     path('obtener/<pk>/', views.get_task,
          name="{}_see".format(object_name)),
     path('obtener/', views.get_task,
          name="{}_see".format(object_name)),
     path('actualizar/', views.update,
          name=f"{object_name}_update"),
     path('comentar/', views.add_coment,
          name=f"{object_name}_add_comment"),
     path('eliminar/', views.delete_tarea,
          name=f"{object_name}_delete"),
     path('eliminar/<pk>/', views.delete_tarea,
          name=f"{object_name}_delete"),
     path('eliminar/comentario/', views.delete_comentario,
          name=f"{object_name}_delete_comment"),
     path('eliminar/comentario/<pk>/', views.delete_comentario,
          name=f"{object_name}_delete_comment"),
     path('actualizar/comentario/', views.update_comentario,
          name=f"{object_name}_update_comment"),
     path('nuevo/vinculo', views.new_link,
          name=f"{object_name}_new_link"),
     path('eliminar/vinculo', views.delete_link,
          name=f"{object_name}_delete_link"),
     path('reporte/', views.reporte_maestro,
          name=f"{object_name}_reporte_maestro"),
]