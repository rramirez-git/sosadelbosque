from django.urls import path

import app.vw_cliente as views

object_name = 'cliente'

urlpatterns = [
     path('', views.index,
          name="{}_index".format(object_name)),
     path('nuevo/', views.new,
          name="{}_new".format(object_name)),
     path('<pk>/', views.see,
          name="{}_see".format(object_name)),
     path('actualizar/<pk>/', views.update,
          name="{}_update".format(object_name)),
     path('eliminar/<pk>/', views.delete,
          name="{}_delete".format(object_name)),
     path('historial_laboral/<pk>/', views.historia_laboral,
          name="{}_historia_laboral".format(object_name)),
     path('reporte/maestro/', views.reporte_maestro,
          name="{}_reporte_maestro".format(object_name)),
     path('eliminar_registro/<pk>/', views.delete_registro,
          name="{}_delete_registro".format(object_name)),
     path('eliminar_detalle/<pk>/', views.delete_detalle,
          name="{}_delete_detalle".format(object_name)),
     path('vista_tabular/<pk>/', views.historia_laboral_vista_tabular,
          name="{}_vista_tabular".format(object_name)),
     path('vista_grafica/<pk>/', views.historia_laboral_vista_grafica,
          name="{}_vista_grafica".format(object_name)),
]
