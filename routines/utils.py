from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from datetime import date, timedelta, datetime
from os import path, mkdir
from unicodedata import normalize
from email.mime.image import MIMEImage

import pandas as pd


def print_error(message, level="Warning"):
    """
    Imprime un mensaje como valor de error.

    (string/var) message                mensaje / var a mostrar
        (string) level      = Warning   string del nivel a mostrar

    return None
    """
    print("=======================", level, message)


def print_list(lista):
    """
    Imprime una lista de valores junto con el indice correspondiente.

    return None
    """
    for indice, elemento in enumerate(lista):
        print("{:04d}: {}".format(indice, elemento))


def requires_jquery_ui(request):
    """
    Indica si el navegador del usuario requiere el uso de jQueryUI basado
    en el USER_AGENT del navegador.

    (request) request   Objeto request sobre el que se realizará la
                            verificación.

    return boolean
    """
    ua = request.META["HTTP_USER_AGENT"].lower()
    if "chrome" in ua \
            or "chromium" in ua \
            or "edge" in ua \
            or "mobi" in ua \
            or "phone" in ua:
        return False
    return True


def month_name(month):
    """
    Devuelve en cadena de 3 letras el mes.

    Si el numero del mes no esta entre 1 y 12 se devuelve una cadena vacia.

    (int) month mes a convertir

    return string
    """
    if 1 == int(month):
        return "Ene"
    if 2 == int(month):
        return "Feb"
    if 3 == int(month):
        return "Mar"
    if 4 == int(month):
        return "Abr"
    if 5 == int(month):
        return "May"
    if 6 == int(month):
        return "Jun"
    if 7 == int(month):
        return "Jul"
    if 8 == int(month):
        return "Ago"
    if 9 == int(month):
        return "Sep"
    if 10 == int(month):
        return "Oct"
    if 11 == int(month):
        return "Nov"
    if 12 == int(month):
        return "Dic"
    return ""


def unaccent(name):
    name = name.replace("ñ", "n")
    name = name.replace("Ñ", "N")
    name = name.replace("á", "a")
    name = name.replace("Á", "A")
    name = name.replace("é", "e")
    name = name.replace("É", "E")
    name = name.replace("í", "i")
    name = name.replace("Í", "I")
    name = name.replace("ó", "o")
    name = name.replace("Ó", "O")
    name = name.replace("ú", "u")
    name = name.replace("U", "U")
    name = name.replace("ä", "a")
    name = name.replace("Ä", "A")
    name = name.replace("ë", "e")
    name = name.replace("ë", "E")
    name = name.replace("ï", "i")
    name = name.replace("Ï", "I")
    name = name.replace("ö", "o")
    name = name.replace("ö", "O")
    name = name.replace("ü", "u")
    name = name.replace("Ü", "U")
    return name


def clean_name(name, to_lower=True):
    """
    Limpia un nombre para generar un nombre inglés y sustituye los
    espacios por _

    (string) name               nombre a limpiar
    (boolean) to_lower = True   convertir a minusculas

    return string
    """
    name = name.replace(" ", "_")
    name = unaccent(name)
    if to_lower is True:
        name = name.lower()
    return name


def move_uploaded_file(file, upload_to):
    """
    Mueve un archivo a la ruta especificada.

    (UploadedFile) file archivo a mover
    (string) upload_to  path relativo a settings.MEDIA_ROOT donde se
                        almacenará el archivo

    return string
    """
    filename = file.name.replace(" ", "_")
    newfilename = path.join(settings.MEDIA_ROOT, upload_to, filename)
    cont = 0
    if not path.exists(path.join(settings.MEDIA_ROOT, upload_to)):
        mkdir(path.join(settings.MEDIA_ROOT, upload_to))
    while path.isfile(newfilename):
        cont += 1
        fname, fext = path.splitext(filename)
        newfilename = path.join(
            settings.MEDIA_ROOT,
            upload_to,
            "{}_{:04d}{}".format(fname, cont, fext))
    with open(newfilename, 'wb+') as archivo:
        try:
            for chunk in file.chunks:
                archivo.write(chunk)
        except:
            archivo.write(file.read())
    return path.join(upload_to, path.basename(newfilename))


def is_mobile(request):
    ua = request.META["HTTP_USER_AGENT"].lower()
    if "ipod" in ua:
        return True
    if "iphone" in ua:
        return True
    if "android" in ua and "mobile" in ua:
        return True
    if "ipdad" in ua:
        return True
    if "android" in ua:
        return True
    return False


def get_setting_fn(sectionvalue, Setting):
    """
    Obtiene el valor de un setting

    (string) sectionvalue   Setting a obtener en formato section.value

    return string
    """
    section, value = sectionvalue.split(".")
    return Setting.get_value(section, value)


def as_paragraph_fn(text):
    text = text.replace('\r', '')
    text = text.strip()
    res = ""
    for p in text.split('\n'):
        res += p.strip() + "<br />"
    res = "<p>{}</p>".format(res)
    res = res.replace("<br /><br />", '</p><p>')
    res = res.replace("<br /></p>", '</p>')
    return res


def hipernormalize(text=None):
    if text is None:
        text = ''
    elif "str" != type(text).__name__:
        text = "{}".format(text)
    forma = "NFKC"
    return unaccent(normalize(forma, text).lower())


def truncate(f, n=0):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        res = '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    res = '.'.join([i, (d+'0'*n)[:n]])
    if n == 0:
        res = res[:-1]
    return res


def send_mail(
        asunto, texto_plano, email_from, email_to, texto_html, imagenes=()):
    email = EmailMultiAlternatives(
        asunto,
        texto_plano,
        email_from,
        email_to,
    )
    email.attach_alternative(texto_html, "text/html")
    for img in imagenes:
        print(img[0], img[1])
        with open(settings.MEDIA_ROOT + img[0], 'rb') as i:
            data = i.read()
        data_image = MIMEImage(data)
        data_image.add_header('Content-ID', '<' + img[1] + '>')
        email.attach(data_image)
    print(email.send())


def inter_periods_days(p1_inicio, p1_fin, p2_inicio, p2_fin):
    """
    Detecta el numero de días entre dos periodos

    Parameters
    p1_inicio : datetime.date
        Fecha inicial del primer periodo
    p1_fin : datetime.date
        Fecha final del primer periodo
    p2_inicio : datetime.date
        Fecha inicial del segundo periodo
    p2_fin : datetime.date
        Fecha final del segundo periodo
    ----------
    Returns
    -------
    integer
        numero de días entre los dos periodos
        0 si el primer periodo esta dentro del segundo
        0 si el segundo periodo esta dentro del primero
        0 si un periodo inicia dentro de otro
    """
    p1 = {'ini': p1_inicio, 'fin': p1_fin}
    p2 = {'ini': p2_inicio, 'fin': p2_fin}
    if ((p1['ini'] == p2['ini'] and p1['fin'] < p2['fin']) or
            (p1['fin'] == p2['fin'] and p1['ini'] > p2['ini']) or
            (p1['ini'] > p2['ini'])):
        t1 = p1
        p1 = p2
        p2 = t1
    if p1['fin'] < p2['ini']:
        return (p2['ini'] - p1['fin']).days
    return 0


def free_days(p1_inicio, p1_fin, p2_inicio, p2_fin):
    """
    Detecta los días del segundo período
    que no pertenecen al primero

    Parameters
    p1_inicio : datetime.date
        Fecha inicial del primer periodo
    p1_fin : datetime.date
        Fecha final del primer periodo
    p2_inicio : datetime.date
        Fecha inicial del segundo periodo
    p2_fin : datetime.date
        Fecha final del segundo periodo
    ----------
    Returns
    -------
    list
        lista de objetos datetime.date
    """
    p1 = create_date_range(p1_inicio, p1_fin)
    p2 = create_date_range(p2_inicio, p2_fin)
    res = []
    for val in p2:
        isIn = False
        for item in p1:
            if val == item:
                isIn = True
                break
        if isIn is False:
            res.append(val)
    return res


def create_date_range(inicio, fin):
    result = []
    for x in pd.date_range(inicio,fin):
        result.append(date(x.year, x.month, x.day))
    return result

BootstrapColors = (
    ('', 'Ninguno'),
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('success', 'Success'),
    ('danger', 'Danger'),
    ('warning', 'Warning'),
    ('info', 'Info'),
    ('light', 'Light'),
    ('dark', 'Dark'),
)
