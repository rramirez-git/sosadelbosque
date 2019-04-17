"""sosadelbosque URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from initsys import views, vw_perfil, vw_permiso, vw_settings, vw_usuario

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'elemento-no-encontrado/',
        views.item_not_found,
        name="item_no_encontrado"),
    path(
        'elemento-con-relaciones/',
        views.item_with_relations,
        name="item_con_relaciones"),
    path(
        'my-panel/',
        views.panel,
        name="panel"),
    path(
        'logout/',
        views.logout,
        name="logout"),
    path(
        '',
        views.index,
        name="index"),
    path(
        'sql/',
        views.sql,
        name='sql'),

    # Permiso
    path(
        'permiso/actualizar/<pk>/',
        vw_permiso.update,
        name='permiso_update'),
    path(
        'permiso/eliminar/<pk>/',
        vw_permiso.delete,
        name='permiso_delete'),
    path(
        'permiso/nuevo/',
        vw_permiso.new,
        name='permiso_new'),
    path(
        'permiso/<pk>/',
        vw_permiso.see,
        name='permiso_see'),
    path(
        'permisos/',
        vw_permiso.index,
        name='permiso_index'),
    path(
        'permission/',
        vw_permiso.permission_index,
        name="permission_index"),

    # Perfil
    path(
        'perfil/actualizar/<pk>/',
        vw_perfil.update,
        name='perfil_update'),
    path(
        'perfil/eliminar/<pk>/',
        vw_perfil.delete,
        name='perfil_delete'),
    path(
        'perfil/nuevo/',
        vw_perfil.new,
        name='perfil_new'),
    path(
        'perfil/<pk>/',
        vw_perfil.see,
        name='perfil_see'),
    path(
        'perfiles/',
        vw_perfil.index,
        name='perfil_index'),

    # Usuario
    path(
        'usuario/actualizar/<pk>/',
        vw_usuario.update,
        name="usuario_update"),
    path(
        'usuario/eliminar/<pk>/',
        vw_usuario.delete,
        name="usuario_delete"),
    path(
        'usuario/nuevo/',
        vw_usuario.new,
        name="usuario_new"),
    path(
        'usuario/<pk>/',
        vw_usuario.see,
        name="usuario_see"),
    path(
        'usuarios/',
        vw_usuario.index,
        name='usuario_index'),
    path(
        'user/',
        vw_usuario.user_index,
        name="user_index"),

    # Settings
    path(
        'settings/configurar/',
        vw_settings.index_adm,
        name='setting_index'),
    path(
        'settings/actualizar/<pk>/',
        vw_settings.update_adm,
        name="setting_update"),
    path(
        'settings/eliminar/<pk>/',
        vw_settings.delete_adm,
        name="setting_delete"),
    path(
        'settings/nuevo/',
        vw_settings.new_adm,
        name="setting_new"),
    path(
        'settings/<pk>/',
        vw_settings.see_adm,
        name="setting_see"),
    path(
        'settings/',
        vw_settings.index,
        name="setting_value"),

    path('cliente/', include('app.url_cliente')),
    path('taxonomia/', include('app.url_taxonomia')),
    path('tiposdocumento/', include('app.url_tipodocumento')),
    path('estatusactividad/', include('app.url_estatusactividad')),
    path('tiposactividad/', include('app.url_tipoactividad')),
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
