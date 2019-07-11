import pandas as pd
import zipfile as zf
import sys
from os import path, mkdir, remove
from datetime import timedelta

from django.conf import settings

from routines.utils import inter_periods_days, free_days

BASE_PATH = path.join(settings.BASE_DIR,'managed/files')


def get_directory(usr_pk):
    directory = path.join(BASE_PATH, "{:04}".format(usr_pk))
    if not path.exists(directory):
        mkdir(directory)
    return directory


def df_struct_HLRDDay():
    return pd.DataFrame(columns=[
        'historialaboralregistrodetalle_pk',
        'historialaboralregistro_pk',
        'historialaboral_pk',
        'fecha',
        'salario_base',
    ])


def df_struct_HLRDDay_agg():
    return pd.DataFrame(columns=[
        'fecha',
        'salario',
    ])


def df_struct_HLRD_periodo_continuo_laborado():
    return pd.DataFrame(columns=[
        'historialaboralregistro_pk',
        'historialaboral_pk',
        'fecha_inicio',
        'fecha_fin',
        'dias',
        'semanas',
        'anios',
        'dias_cotiz',
        'semanas_cotiz',
        'anios_cotiz',
        'dias_inact',
        'semanas_inact',
        'anios_inact',
    ])


def df_struct_HLRD_periodo_continuo_laborado_levelhl():
    return pf.DataFrame(columns=[
        'historialaboral_pk',
        'fecha_inicio',
        'fecha_fin',
        'dias',
        'semanas',
    ])


def df_data_generate_HLRDDay(histLabRegDet):
    df = df_struct_HLRDDay()
    reg = histLabRegDet.historia_laboral_registro
    for dt in pd.date_range(histLabRegDet.inicio, histLabRegDet.fin):
        df = df.append({
            'historialaboralregistrodetalle_pk': histLabRegDet.pk,
            'historialaboralregistro_pk': reg.pk,
            'historialaboral_pk': reg.historia_laboral.pk,
            'fecha': dt,
            'salario_base': histLabRegDet.salario_base,
        }, ignore_index=True)
    return df


def df_load_HLRDDay(cte_pk):
    file = path.join(get_directory(cte_pk),'hldr_day.csv')
    zfile = file + ".zip"
    if path.exists(zfile):
        with zf.ZipFile(zfile, 'r') as zipf:
            with zipf.open(path.basename(file)) as f:
                return pd.read_csv(
                    filepath_or_buffer=f,
                    header=0,
                    parse_dates=['fecha'],
                    encoding='utf_8')
    return df_struct_HLRDDay()


def df_save_HLRDDay(cte_pk, df):
    file = path.join(get_directory(cte_pk),'hldr_day.csv')
    df.sort_values(by='fecha', inplace=True)
    df.to_csv(path_or_buf=file, encoding='utf_8', index=False)
    with zf.ZipFile(file + ".zip", "w") as zipf:
        zipf.write(file,path.basename(file), zf.ZIP_BZIP2)
    remove(file)
    df_save_HLRDDay_agg(cte_pk)
    return True


def df_save_HLRDDay_agg(cte_pk):
    df = df_load_HLRDDay(cte_pk)
    file = path.join(get_directory(cte_pk),'hldr_day_agg.csv')
    df_agg = df.groupby('fecha').agg(['sum']).salario_base
    df_agg.index.names=['f']
    df_agg['fecha'] = df_agg.index
    df_agg.columns = ['salario','fecha']
    df_agg = df_agg[['fecha','salario']]
    df_agg.sort_index(ascending=False, inplace=True)
    df_agg.to_csv(path_or_buf=file, encoding='utf_8', index=False)
    with zf.ZipFile(file + ".zip", "w") as zipf:
        zipf.write(file,path.basename(file), zf.ZIP_BZIP2)
    remove(file)
    return True


def df_load_HLRDDay_agg(cte_pk):
    file = path.join(get_directory(cte_pk),'hldr_day_agg.csv')
    zfile = file + ".zip"
    if path.exists(zfile):
        with zf.ZipFile(zfile, 'r') as zipf:
            with zipf.open(path.basename(file)) as f:
                return pd.read_csv(
                    filepath_or_buffer=f,
                    header=0,
                    parse_dates=['fecha'],
                    encoding='utf_8')
    return df_struct_HLRDDay_agg()


def df_update(df, df2, hl=None, reg=None, det=None):
    if not hl is None:
        df = df[df.historialaboral_pk != hl]
    if not reg is None:
        df = df[df.historialaboralregistro_pk != reg]
    if not det is None:
        df = df[df.historialaboralregistrodetalle_pk != det]
    df = df = df.append(df2, ignore_index=True)
    return df


def df_load_HLRD_periodo_continuo_laborado(cte_pk):
    file = path.join(get_directory(cte_pk),'hldr_per_cont_lab.csv')
    zfile = file + ".zip"
    if path.exists(zfile):
        with zf.ZipFile(zfile, 'r') as zipf:
            with zipf.open(path.basename(file)) as f:
                return pd.read_csv(
                    filepath_or_buffer=f,
                    header=0,
                    parse_dates=['fecha_inicio', 'fecha_fin'],
                    encoding='utf_8')
    return df_struct_HLRD_periodo_continuo_laborado()

def df_generate_HLRD_periodo_continuo_laborado(cte_pk, histLabReg):
    df_day = df_load_HLRDDay(cte_pk)
    df_per = df_struct_HLRD_periodo_continuo_laborado()
    df_day = df_day[df_day.historialaboralregistro_pk == histLabReg.pk]
    if 0 == len(df_day):
        return df_per
    fecha_ini = None
    fecha_ant = None
    for r in df_day.itertuples():
        reg = {
            'historialaboral_pk': r[3],
            'fecha': r[4],
            'salario_base': r[5]}
        if fecha_ini is None:
            fecha_ini = reg['fecha']
        if fecha_ant is None:
            fecha_ant = reg['fecha']
        if reg['fecha'] > fecha_ant + timedelta(days=1):
            d = (fecha_ant - fecha_ini).days + 1
            s = round(d / 7)
            a = s / 52
            df_per = df_per.append({
                'historialaboralregistro_pk': histLabReg.pk,
                'historialaboral_pk': reg['historialaboral_pk'],
                'fecha_inicio': fecha_ini,
                'fecha_fin': fecha_ant,
                'dias': d,
                'semanas': s,
                'anios': a,
                'dias_cotiz': 0,
                'semanas_cotiz': 0,
                'anios_cotiz': 0.00,
                'dias_inact': 0,
                'semanas_inact': 0,
                'anios_inact': 0.00,
            }, ignore_index=True)
            fecha_ini = reg['fecha']
        fecha_ant = reg['fecha']
    d = (fecha_ant - fecha_ini).days + 1
    s = round(d / 7)
    a = s / 52
    df_per = df_per.append({
        'historialaboralregistro_pk': histLabReg.pk,
        'historialaboral_pk': reg['historialaboral_pk'],
        'fecha_inicio': fecha_ini,
        'fecha_fin': fecha_ant,
        'dias': d,
        'semanas': s,
        'anios': a,
        'dias_cotiz': 0,
        'semanas_cotiz': 0,
        'anios_cotiz': 0.00,
        'dias_inact': 0,
        'semanas_inact': 0,
        'anios_inact': 0.00,
    }, ignore_index=True)
    return df_per

def df_generate_data_cotiz_HLRD_periodo_continuo_laborado(cte_pk, df_pers=None):
    if df_pers is None:
        df_pers = df_load_HLRD_periodo_continuo_laborado(cte_pk)
    for x in range(len(df_pers)):
        dias_cotizados = df_pers.dias[x]
        dias_inactivos = sys.maxsize
        if 0 == x:
            dias_inactivos = 0
        else:
            for y in range(len(df_pers)):
                if y < x:
                    dias_c = len(free_days(
                        df_pers.fecha_inicio[y],
                        df_pers.fecha_fin[y],
                        df_pers.fecha_inicio[x],
                        df_pers.fecha_fin[x]))
                    if dias_cotizados > dias_c:
                        dias_cotizados = dias_c
                    dias_i = inter_periods_days(
                        df_pers.fecha_inicio[y],
                        df_pers.fecha_fin[y],
                        df_pers.fecha_inicio[x],
                        df_pers.fecha_fin[x])
                    if dias_inactivos > dias_i:
                        dias_inactivos = dias_i
        sc = round(int(dias_cotizados) / 7)
        si = round(int(dias_inactivos) / 7)
        df_pers.at[x, 'dias_cotiz'] = dias_cotizados
        df_pers.at[x, 'semanas_cotiz'] = sc
        df_pers.at[x, 'anios_cotiz'] = sc / 52
        df_pers.at[x, 'dias_inact'] = dias_inactivos
        df_pers.at[x, 'semanas_inact'] = si
        df_pers.at[x, 'anios_inact'] = si / 52
    return df_pers

def df_save_HLRD_periodo_continuo_laborado(cte_pk, df):
    file = path.join(get_directory(cte_pk),'hldr_per_cont_lab.csv')
    df.sort_values(by=['fecha_inicio', 'fecha_fin'], inplace=True)
    df.to_csv(path_or_buf=file, encoding='utf_8', index=False)
    with zf.ZipFile(file + ".zip", "w") as zipf:
        zipf.write(file,path.basename(file), zf.ZIP_BZIP2)
    remove(file)
    return True
