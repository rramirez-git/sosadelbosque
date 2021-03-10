from django.urls import path

import app.vw_utilerias as views

object_name = 'utilerias'

urlpatterns = [
    path('simulador_de_pension', views.simulador,
         name="{}_simulador".format(object_name)),
]
