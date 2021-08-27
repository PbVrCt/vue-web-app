from os import path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import dateutil.parser
import copy
import json
import random
import string

DATAFOLDER = "data/"
DATAUSERS = DATAFOLDER + "usuarios.json"


def iniciaFicheroUsuarios(usr, pwd):
    # Obtiene el contenido de 'usuarios.json'
    # Si el fichero no existe lo crea
    if not path.exists(DATAUSERS):
        now = datetime.now()
        password = generate_password_hash(pwd)
        data = {}
        data[usr] = {'password': password, 'admin': True,
                     'data': getNombreFicheroAleatorio(), 'createDate': now, 'accessDate': now}
        guardaUsuarios(data)
    return None


def CodificaFechaHora(obj):
    # Para usar en JSON.DUMP: Convierte Fecha y Hora a texto en formato ISO
    if isinstance(obj, datetime):
        return obj.isoformat()


def DecodificaFechaHora(dct):
    # Para usar en JSON.LOAD: Obtiene Fecha y Hora a partir de un texto en formato ISO
    for k, v in dct.items():
        if isinstance(v, str) and len(v) == 26:
            try:
                dct[k] = dateutil.parser.isoparse(v)
            except:
                pass
    return dct


def getUsuarios():
    # Obtiene el contenido de 'usuarios.json'
    with open(DATAUSERS, 'r') as f:
        data = json.load(f, object_hook=DecodificaFechaHora)
    return data


def getUsuariosParcial():
    # Obtiene el contenido de 'usuarios.json'
    with open(DATAUSERS, 'r') as f:
        data = json.load(f, object_hook=DecodificaFechaHora)
    # Copia los datos de usuarios omitiendo datos confidenciales y cambiando tipos de Fecha a Texto
    usrs = []
    for k, v in data.items():
        usrs.append({'username': k, 'admin': v['admin'], 'createDate': v['createDate'].strftime(
            "%Y-%m-%d %H:%M"), 'accessDate': v['accessDate'].strftime("%Y-%m-%d %H:%M")})
    usuarios = sorted(usrs, key=lambda p: p['username'])
    return usuarios


def guardaUsuarios(data):
    # Guarda el contenido de 'usuarios.json'
    with open(DATAUSERS, 'w') as f:
        json.dump(data, f, indent=True, default=CodificaFechaHora)


def getNombreFicheroAleatorio():
    # Obtiene un nombre de fichero con 12 letras aleatorias
    letras = string.ascii_lowercase
    while True:
        txt = ''.join(random.choice(letras) for i in range(12))
        txt = 'data.' + txt + '.json'
        if not path.exists(DATAFOLDER + txt):
            break
    return txt


def getDatosUsuario(usr):
    # Obtiene los datos de un usuario
    data = getUsuarios()
    user = usr.strip().lower()
    usuario = copy.deepcopy(data[user])
    del usuario['password']
    return usuario


def getFicheroUsuario(usr):
    # Obtiene el nombre del fichero de datos de un usuario
    data = getUsuarios()
    user = usr.strip().lower()
    return data[user]['data']


def login(user, pwd):
    # Comprueba si existe un usuario con su contraseña y hace login
    data = getUsuarios()
    ok = user in data
    if ok:
        ok = check_password_hash(data[user]['password'], pwd)
    if ok:
        data[user]['accessDate'] = datetime.now()
        guardaUsuarios(data)
    if ok:
        usuario = copy.deepcopy(data[user])
        del usuario['password']
        return usuario
    else:
        return None


def register(user, pwd):
    # Registra un nuevo usuario
    data = getUsuarios()
    ok = user not in data
    if ok and len(user) > 4 and len(pwd) > 4:
        now = datetime.now()
        password = generate_password_hash(pwd)
        data[user] = {'password': password, 'admin': False,
                      'data': getNombreFicheroAleatorio(), 'createDate': now, 'accessDate': now}
        guardaUsuarios(data)
        usuario = copy.deepcopy(data[user])
        del usuario['password']
        return usuario
    else:
        return None


def check(user, pwd):
    # Comprueba si existe un usuario con su contraseña
    data = getUsuarios()
    ok = user in data
    if ok:
        ok = check_password_hash(data[user]['password'], pwd)
    return ok


def putPassword(user, pwd):
    # Cambia contraseña
    data = getUsuarios()
    ok = user in data
    if ok and len(pwd) > 4:
        data[user]['password'] = generate_password_hash(pwd)
        guardaUsuarios(data)
        return True
    else:
        return False


def deleteUsuario(user):
    # Eliminar usuario
    data = getUsuarios()
    ok = user in data
    if ok and not data[user]['admin']:
        del data[user]
        guardaUsuarios(data)
        return True
    else:
        return False
