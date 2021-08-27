from flask import Flask, redirect, request, jsonify, make_response, send_file
from flask_restful import Resource, Api, abort
from flask_jwt_extended import (JWTManager, jwt_required, jwt_optional, create_access_token,
                                create_refresh_token, verify_jwt_in_request, unset_jwt_cookies,
                                get_jwt_identity, get_jwt_claims, set_access_cookies,
                                set_refresh_cookies, jwt_refresh_token_required)
from functools import wraps
import dbUsuarios
import dbTaludes
import analisisTalud
import datetime
import os
import re

OUTFOLDER = "dist/analisis/"

app = Flask(__name__, static_url_path='', static_folder='dist')
app.debug = True
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = 'dfkk347dfgkr4jdfs8734herrheewr834'

jwt = JWTManager(app)

api = Api(app)

DEFAULTADMIN = "admin"
DEFAULTPASSWORD = "admin"

# ---------------------------------------------------
# FUNCION NECESARIA PARA HABILITAR 'CORS'
#
# PERMITE ACCEDER UTILIZANDO UN DOMINIO Y/O PUERTO DIFERENTE
# ---------------------------------------------------


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# ---------------------------------------------------
# FUNCIONES NECESARIAS PARA FLASK-JWT-EXTENDED
#
# PERMITE PROTEGER EL ACCESO POR USUARIOS REGISTRADOS
# ---------------------------------------------------


class UserObject:
    # Esta 'clase' contiene un 'constructor' con la información que se guarda en los 'token'
    def __init__(self, username, admin, data, createDate, accessDate):
        self.username = username
        self.admin = admin
        self.data = data
        self.createDate = createDate
        self.accessDate = accessDate


@jwt.user_identity_loader
def user_identity_lookup(user):
    # Función necesaria para que 'get_jwt_identity()' devuelva el 'username' existente en el 'token'
    return user.username


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    # Función necesaria para que 'get_jwt_claims()' devuelva otros datos que hay en el 'token'
    return {'admin': user.admin, 'data': user.data,
            'createDate': user.createDate, 'accessDate': user.accessDate}


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Esta función permite utilizar el 'decorador' 'admin_required'
        # para permitir solo el acceso del administrador
        verify_jwt_in_request()
        if not get_jwt_claims()['admin']:
            abort(403, message="Solo Administradores!")
        else:
            return fn(*args, **kwargs)
    return wrapper


# -----------------------------------------------------
# FUNCIONES NECESARIAS PARA DEVOLVER EL FICHERO INDEX.HTML
#
# UNA VEZ QUE NAVEGADOR DESCARGA EL .HTML SOLICITA TAMBIEN EL .JS CORRESPONDIENTE
# -----------------------------------------------------


@app.route('/')
@app.route('/login')
@app.route('/register')
@app.route('/pwduser')
@app.route('/usuarios')
@app.route('/nuevo')
@app.route('/copia')
@app.route('/exporta')
@app.route('/importa')
@app.route('/borra')
def index1():
    return app.send_static_file('index.html')


@app.route('/pwdadmin/<user>/')
@app.route('/userborra/<user>/')
def index2(user):
    return app.send_static_file('index.html')


@app.route('/paso1/<int:id>')
@app.route('/paso2/<int:id>')
@app.route('/paso3/<int:id>')
@app.route('/paso4/<int:id>')
@app.route('/paso5/<int:id>')
@app.route('/paso6/<int:id>')
@app.route('/paso7/<int:id>')
@app.route('/paso8/<int:id>')
@app.route('/paso9/<int:id>')
@app.route('/paso10/<int:id>')
@app.route('/paso11/<int:id>')
def index3(id):
    return app.send_static_file('index.html')


@app.route('/grafico/<int:id>')
def grafico(id):
    return app.send_static_file('grafico.html')

# -----------------------------------------------------
# FUNCIONES NECESARIAS PARA LA AUTENTICACION
#
# PATH: /token/
# -----------------------------------------------------


@app.route('/token/login', methods=['POST'])
def loginAuth():
    dbUsuarios.iniciaFicheroUsuarios(DEFAULTADMIN, DEFAULTPASSWORD)
    form = request.get_json()
    username = form['username'].strip().lower()
    password = form['password']
    usr = dbUsuarios.login(username, password)
    if usr is None:
        return {'login': False, 'message': 'Error en el usuario y/o contraseña'}, 401
    else:
        user = UserObject(username=username, admin=usr['admin'], data=usr['data'],
                          createDate=usr['createDate'].isoformat(),
                          accessDate=usr['accessDate'].isoformat())
        expires = datetime.timedelta(hours=4)
        access_token = create_access_token(
            identity=user, expires_delta=expires)
        refresh_token = create_refresh_token(identity=user)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        resp.status_code = 200
        return resp


@app.route('/token/register', methods=['POST'])
def registerAuth():
    form = request.get_json()
    username = form['username'].strip().lower()
    password = form['password']
    usr = dbUsuarios.register(username, password)
    if usr is None:
        return {'register': False,
                'message': 'El usuario ya existe o no se cumplen los requisitos'}, 401
    else:
        user = UserObject(username=username, admin=usr['admin'], data=usr['data'],
                          createDate=usr['createDate'].isoformat(),
                          accessDate=usr['accessDate'].isoformat())
        expires = datetime.timedelta(hours=4)
        access_token = create_access_token(
            identity=user, expires_delta=expires)
        refresh_token = create_refresh_token(identity=user)
        resp = jsonify({'register': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        resp.status_code = 200
        return resp


@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    resp.status_code = 200
    return resp


@app.route('/token/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    resp.status_code = 200
    return resp


# ------------------------------------------------------
# FUNCIONES NECESARIAS PARA LA GESTION DE USUARIOS
#
# PATH: /api/
# ------------------------------------------------------


class AuthR(Resource):
    method_decorators = {'get': [jwt_optional]}

    def get(self):
        # Obtiene datos de autenticación
        admin = False
        current_user = get_jwt_identity()
        if current_user is not None:
            admin = get_jwt_claims()['admin']
        return {'auth': bool(current_user), 'username': current_user, 'admin': admin}


api.add_resource(AuthR, '/api/auth')


class PwdUserR(Resource):
    method_decorators = {'put': [jwt_required]}

    def put(self):
        # Permite a cualquier usuario cambiar su propia contraseña
        form = request.get_json()
        oldPassword = form['oldPassword']
        newPassword = form['newPassword']
        current_user = get_jwt_identity()
        if not dbUsuarios.check(current_user, oldPassword):
            return {'password': False, 'message': 'La contraseña actual no es correcta'}, 401
        if not dbUsuarios.putPassword(current_user, newPassword):
            return {'password': False, 'message': 'No se pudo cambiar la contraseña'}, 401
        return {'password': True}


api.add_resource(PwdUserR, '/api/pwduser')


class PwdAdminR(Resource):
    method_decorators = {'put': [admin_required]}

    def put(self):
        # Permite al administrador cambiar la contraseña de cualquier usuario
        form = request.get_json()
        username = form['username']
        newPassword = form['newPassword']
        if not dbUsuarios.putPassword(username, newPassword):
            return {'password': False, 'message': 'No se pudo cambiar la contraseña'}, 401
        return {'password': True}


api.add_resource(PwdAdminR, '/api/pwdadmin')


class BorraUsuarioR(Resource):
    method_decorators = {'delete': [admin_required]}

    def delete(self, user):
        # Permite al administrador eliminar a cualquier usuario
        fichero = dbUsuarios.getFicheroUsuario(user)
        if not dbUsuarios.deleteUsuario(user):
            return {'deleteuser': False, 'message': 'No se pudo eliminar el usuario'}, 401
        if not dbTaludes.borraFicheroTaludes(fichero):
            return {'deleteuser': False,
                    'message': 'No se pudo eliminar el fichero de datos del usuario'}, 401
        return {'deleteuser': True}


api.add_resource(BorraUsuarioR, '/api/deleteuser/<user>')


class UsuariosR(Resource):
    method_decorators = {'get': [admin_required]}

    def get(self):
        # Obtiene la lista de usuarios sin datos confidenciales
        usuarios = dbUsuarios.getUsuariosParcial()
        return usuarios


api.add_resource(UsuariosR, '/api/usuarios')


# ------------------------------------------------------
# FUNCIONES NECESARIAS PARA LA GESTION DE DATOS DE TALUD
#
# PATH: /api/
# ------------------------------------------------------


class TaludesR(Resource):
    method_decorators = {'get': [jwt_required]}

    def get(self):
        # Obtiene la lista de taludes
        ficData = get_jwt_claims()['data']
        data = dbTaludes.iniciaFicheroTaludes(ficData)
        taludes = dbTaludes.getTaludes(data)
        return taludes


api.add_resource(TaludesR, '/api/taludes')


class NuevoR(Resource):
    method_decorators = {'post': [jwt_required]}

    def post(self):
        # Crea un nuevo talud con el nombre indicado
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        form = request.get_json()
        nombre = form['nombre']
        id = dbTaludes.nuevoTalud(ficData, data, nombre)
        return {'codigo': id}


api.add_resource(NuevoR, '/api/nuevo')


class CopiaR(Resource):
    method_decorators = {'post': [jwt_required]}

    def post(self):
        # Copia un talud con el nombre indicado
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        form = request.get_json()
        nombre = form['nombre']
        idCopiar = form['idCopiar']
        id = dbTaludes.copiaTalud(ficData, data, nombre, str(idCopiar))
        return {'codigo': id}


api.add_resource(CopiaR, '/api/copia')


class ExportaR(Resource):
    method_decorators = {'get': [jwt_required]}

    def get(self, id):
        # Exporta un talud dado su 'id'
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        talud = dbTaludes.getTalud(data, id)
        if not bool(talud):
            abort(400, message="Talud no encontrado")
        else:
            fic = 'talud-' + str(id) + '-' + \
                re.sub(r"[^A-Za-z0-9]+", '', talud['nombre'])
            dataExportar = dbTaludes.exportaTalud(talud)
            response = make_response(dataExportar)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = 'attachment; filename="' + fic + '.json"'
            return response


api.add_resource(ExportaR, '/api/exporta/<int:id>')


class ImportaR(Resource):
    method_decorators = {'post': [jwt_required]}

    def post(self):
        # Importa un talud
        if 'file' not in request.files:
            abort(400, message="Fichero no encontrado")
        else:
            ficData = get_jwt_claims()['data']
            data = dbTaludes.getDatos(ficData)
            textoTaludImportado = request.files['file'].read()
            id = dbTaludes.importaTalud(ficData, data, textoTaludImportado)
            return {'codigo': id}


api.add_resource(ImportaR, '/api/importa')


class BorraR(Resource):
    method_decorators = {'delete': [jwt_required]}

    def delete(self, id):
        # Elimina un talud dado su 'id'
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        cod = dbTaludes.borraTalud(data, str(id))
        if cod == 0:
            return {'codigo': cod, 'message': 'No se pudo eliminar el talud'}, 401
        dbTaludes.guardaDatos(ficData, data)
        return {'codigo': cod}


api.add_resource(BorraR, '/api/borra/<int:id>')


class TaludR(Resource):
    method_decorators = {'get': [jwt_required]}

    def get(self, id):
        # obtiene los datos de un talud dado su 'id'
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        talud = dbTaludes.getTalud(data, id)
        if not bool(talud):
            abort(400, message="Talud no encontrado")
        else:
            return talud


api.add_resource(TaludR, '/api/talud/<int:id>')


class Graf1R(Resource):
    method_decorators = {'get': [jwt_required]}

    def get(self, id):
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        talud = dbTaludes.getTalud(data, id)
        idUsuario = ficData.split('.')[1]
        fichero = idUsuario + '.' + str(id) + '.1.png'
        path = OUTFOLDER + fichero
        if not os.path.isfile(path):
            analisis = analisisTalud.run(talud, idUsuario, id, True, True)
        return send_file(path, as_attachment=True, attachment_filename=fichero, cache_timeout=0)


api.add_resource(Graf1R, '/api/graf1/<int:id>')


class Paso1R(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    def put(self, id):
        # Modifica Paso 1
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        nombre = form['nombre']
        existeId = dbTaludes.getIdTalud(data, nombre)
        if existeId != 0 and existeId != id:
            abort(500, message="El nombre de Talud ya existe")
        data = dbTaludes.modificaPaso1(data, id, form)
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 1 y por tanto elimina el talud
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.borraTalud(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso1R, '/api/paso1/<int:id>')


class Paso2R(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    def put(self, id):
        # Modifica Paso 2
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso2(data, id, form['contorno'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 2
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso2(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso2R, '/api/paso2/<int:id>')


class Paso3R(Resource):
    method_decorators = {'post': [jwt_required],
                         'put': [jwt_required], 'delete': [jwt_required]}

    def post(self, id):
        # ESTABLECE QUE EL TALUD NO TIENE CAPAS
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.sinCapasPaso3(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def put(self, id):
        # Modifica Paso 3
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso3(
            data, id, form['nombre'], form['contorno'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 3
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso3(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso3R, '/api/paso3/<int:id>')


class Paso4R(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    def put(self, id):
        # Modifica Paso 4
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso4(data, id, form)
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 4
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso4(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso4R, '/api/paso4/<int:id>')


class Paso5R(Resource):
    method_decorators = {'post': [jwt_required],
                         'put': [jwt_required], 'delete': [jwt_required]}

    def post(self, id):
        # ESTABLECE QUE EL TALUD NO TIENE NIVEL FREATICO
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.sinNivelFreaticoPaso5(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def put(self, id):
        # Modifica Paso 5
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso5(
            data, id, form['nivelFreatico'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 5
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso5(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso5R, '/api/paso5/<int:id>')


class Paso6R(Resource):
    method_decorators = {'post': [jwt_required],
                         'put': [jwt_required], 'delete': [jwt_required]}

    def post(self, id):
        # ESTABLECE QUE EL TALUD NO TIENE CARGAS
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.sinCargasPaso6(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def put(self, id):
        # Modifica Paso 6
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso6(
            data, id, form['nombre'], form['xInicial'], form['xFinal'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 6
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso6(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso6R, '/api/paso6/<int:id>')


class Paso7R(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    def put(self, id):
        # Modifica Paso 7
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        error = dbTaludes.testFuerzas(form['fuerzasX'], form['fuerzasY'])
        if len(error) > 0:
            abort(500, message=error)
        data = dbTaludes.modificaPaso7(
            data, id, form['nombres'], form['fuerzasX'], form['fuerzasY'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 7
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso7(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso7R, '/api/paso7/<int:id>')


class Paso8R(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    def put(self, id):
        # Modifica Paso 8
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso8(data, id, form['centros'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 8
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.deletePaso8(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso8R, '/api/paso8/<int:id>')


class Paso9R(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    def put(self, id):
        # Modifica Paso 9
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso9(data, id, form['radios'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 9
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.deletePaso9(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso9R, '/api/paso9/<int:id>')


class Paso10R(Resource):
    method_decorators = {'post': [jwt_required],
                         'put': [jwt_required], 'delete': [jwt_required]}

    def post(self, id):
        # MODIFICA Y EJECUTA ANALISIS
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso10(
            data, id, form['dovelasX'], form['dovelasAnchoMax'], form['metodo'])
        # ANALISIS
        talud = dbTaludes.getTalud(data, id)
        idUsuario = ficData.split('.')[1]
        analisis = analisisTalud.run(talud, idUsuario, id, True, True)
        dbTaludes.avanzaPaso10(data, id, analisis)
        # ---
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def put(self, id):
        # Modifica Paso 10
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        form = request.get_json()
        data = dbTaludes.modificaPaso10(
            data, id, form['dovelasX'], form['dovelasAnchoMax'], form['metodo'])
        dbTaludes.guardaDatos(ficData, data)
        return {}

    def delete(self, id):
        # Elimina Paso 10
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso10(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso10R, '/api/paso10/<int:id>')


class Paso11R(Resource):
    method_decorators = {'delete': [jwt_required]}

    def delete(self, id):
        # Elimina Paso 10
        ficData = get_jwt_claims()['data']
        data = dbTaludes.getDatos(ficData)
        if not dbTaludes.testTalud(data, id):
            abort(400, message="Talud no encontrado")
        dbTaludes.eliminaPaso11(data, id)
        dbTaludes.guardaDatos(ficData, data)
        return {}


api.add_resource(Paso11R, '/api/paso11/<int:id>')
