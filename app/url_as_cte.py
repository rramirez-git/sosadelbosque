from django.urls import path

import app.vw_as_cte as views

object_name = 'as_cte'

urlpatterns = [
    path('mis_documentos/', views.mis_documentos,
         name="{}_mis_documentos".format(object_name)),
    path('mi_salario_promedio/', views.mi_salario_promedio,
         name="{}_mi_salario_promedio".format(object_name)),
    path('mi_historial_laboral/', views.mi_historial_laboral,
         name="{}_mi_historial_laboral".format(object_name)),
    path('mis_opciones_de_pension/', views.mis_opciones_pension,
         name="{}_mis_opciones_de_pension".format(object_name)),
]
