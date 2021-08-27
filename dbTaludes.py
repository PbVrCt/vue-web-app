from os import path, remove
import json
import math
import copy

DATAFOLDER = "data/"

PASOANALISIS = 11


def iniciaFicheroTaludes(fiche):
    # Obtien el contenido de 'data.*.json'
    # Si el fichero no existe lo crea
    ficData = DATAFOLDER + fiche
    if path.exists(ficData):
        with open(ficData, 'r') as f:
            data = json.load(f)
    else:
        data = {}
        guardaDatos(fiche, data)
    return data


def borraFicheroTaludes(fiche):
    # Elimina el fichero de datos de taludes
    ficData = DATAFOLDER + fiche
    ok = False
    if path.exists(ficData):
        remove(ficData)
        ok = True
    return ok


def getDatos(fiche):
    # Obtiene el contenido del fichero
    ficData = DATAFOLDER + fiche
    with open(ficData, 'r') as f:
        data = json.load(f)
    return data


def guardaDatos(fiche, data):
    # Guarda el contenido de 'data.json'
    ficData = DATAFOLDER + fiche
    with open(ficData, 'w') as f:
        json.dump(data, f, indent=True)


def getTaludes(data):
    # Devuelve una lista con los nombres y códigos de los taludes
    proy = []
    for p in data.values():
        proy.append(
            {'codigo': p['codigo'], 'nombre': p['nombre'], 'avance': p['avance'],
             'sinCargas': p['sinCargas']})
    taludes = sorted(proy, key=lambda p: p['nombre'])
    return taludes


def getIdTalud(data, nombre):
    # Busca un talud por su nombre y obtiene su codigo
    # Si no encuentra el nombre devuelve 0
    id = 0
    for p in data.values():
        if p['nombre'] == nombre:
            id = p['codigo']
            break
    return id


def testTalud(data, id):
    # Comprueba si existe un talud dado id
    return str(id) in data


def getTalud(data, id):
    # Busca un talud por su id y obtiene sus datos
    # Si no encuentra el id devuelve {}
    return data.get(str(id), {})


def getIdLibre(data):
    # Devuelve un numero mayor o igual a 1 no utilizado en data[i]['codigo']
    codes = []
    for p in data.values():
        codes.append(p['codigo'])
    i = 1
    found = True
    while found:
        found = i in codes
        if found:
            i += 1
    return i


def nuevoTalud(fiche, data, nombre):
    # Crea un talud dado el nombre
    # Devuelve un código de talud mayor o igual a 1
    # Si el nombre ya existe devuelve 0
    id = getIdTalud(data, nombre.strip().lower())
    if id != 0:
        return 0
    else:
        id = getIdLibre(data)
        data[id] = {'codigo': id, 'nombre': nombre.strip().lower(),
                    'avance': 0, 'sinCargas': False}
        guardaDatos(fiche, data)
        return id


def copiaTalud(fiche, data, nombre, idCopiar):
    # Copia un talud dado el nombre y el id (como texto) del talud a copiar
    # Devuelve un código de talud mayor o igual a 1
    # Si el nombre ya existe devuelve 0
    # Si el talud a copiar no existe devuelve -1
    id = getIdTalud(data, nombre.strip().lower())
    if id != 0:
        return 0
    elif idCopiar not in data:
        return -1
    else:
        id = getIdLibre(data)
        data[id] = copy.deepcopy(data[idCopiar])
        data[id]['codigo'] = id
        data[id]['nombre'] = nombre
        guardaDatos(fiche, data)
        return id


def importaTalud(fiche, data, textoTaludImportado):
    # Importa un talud dado el texto en formato JSON
    # Devuelve un código de talud mayor o igual a 1
    # Si hay un error de contenido en el fichero devuelve 0
    ok = True
    taludImportado = ''
    try:
        taludImportado = json.loads(textoTaludImportado)
    except:
        ok = False
    if not ok:
        return 0
    else:
        id = getIdLibre(data)
        nombre = taludImportado['nombre']
        num = 1
        nuevoNombre = nombre
        while getIdTalud(data, nuevoNombre) != 0:
            num = num + 1
            nuevoNombre = nombre + '-' + str(num)
        data[id] = taludImportado
        data[id]['codigo'] = id
        data[id]['nombre'] = nuevoNombre
        guardaDatos(fiche, data)
        return id


def exportaTalud(talud):
    # Exporta un talud como texto en formato JSON
    return json.dumps(talud, indent=True)


def borraTalud(data, idEliminar):
    # Borra un talud dado el id (como texto) del talud a eliminar
    # Devuelve un código de talud mayor o igual a 1
    # Si el id no existe devuelve 0; si existe devuelve 1
    if str(idEliminar) not in data:
        return 0
    else:
        del data[str(idEliminar)]
        return 1


def modificaPaso1(data, id, form):
    # Modificaciones de paso 1 dado el id y el formulario con datos
    proy = data[str(id)]
    if proy['avance'] < 1:
        proy['avance'] = 1
    proy['nombre'] = form['nombre'].strip().lower()
    izq = form['dimensiones']['izquierda']
    der = form['dimensiones']['derecha']
    aba = form['dimensiones']['abajo']
    arr = form['dimensiones']['arriba']
    if proy['avance'] >= 2:
        for p in proy['contorno']:
            if p['x'] < izq:
                izq = p['x']
            if p['x'] > der:
                der = p['x']
            if p['y'] < aba:
                aba = p['y']
            if p['y'] > arr:
                arr = p['y']
    if proy['avance'] >= 3:
        for c in proy['capas']:
            for q in c['contorno']:
                if q['x'] < izq:
                    izq = q['x']
                if q['x'] > der:
                    der = q['x']
                if q['y'] < aba:
                    aba = q['y']
                if q['y'] > arr:
                    arr = q['y']
    if proy['avance'] >= 5:
        for p in proy['nivelFreatico']:
            if p['x'] < izq:
                izq = p['x']
            if p['x'] > der:
                der = p['x']
            if p['y'] < aba:
                aba = p['y']
            if p['y'] > arr:
                arr = p['y']
    proy['dimensiones'] = {'izquierda': izq, 'derecha': der, 'abajo': aba, 'arriba': arr,
                           'gridx': form['dimensiones']['gridx'],
                           'gridy': form['dimensiones']['gridy'],
                           'intervalosx': form['dimensiones']['intervalosx'],
                           'intervalosy': form['dimensiones']['intervalosy']}
    return data


def modificaPaso2(data, id, contorno):
    # Modificaciones de paso 2 dado el id y el contorno
    proy = data[str(id)]
    proy['avance'] = 2
    proy['nombreMaterial'] = "exterior"
    proy['contorno'] = contorno
    return data


def eliminaPaso2(data, id):
    # Elimina el paso 2 dado su id
    proy = data[str(id)]
    proy['avance'] = 1
    del proy['contorno']
    return data


def sinCapasPaso3(data, id):
    # Indica que no hay capas en paso 3 dado su id
    proy = data[str(id)]
    proy['avance'] = 3
    proy['sinCapas'] = True
    proy['capas'] = []
    return data


def modificaPaso3(data, id, nombre, contorno):
    # Añade capa en paso 3 dado el id, el nombre y el contorno
    proy = data[str(id)]
    proy['avance'] = 3
    if 'capas' not in proy:
        proy['sinCapas'] = False
        proy['capas'] = []
    proy['capas'].append(
        {'nombre': nombre.strip().lower(), 'contorno': contorno})
    return data


def eliminaPaso3(data, id):
    # Elimina ultima capa en paso 3 dado su id
    proy = data[str(id)]
    n = len(proy['capas'])
    if n <= 1:
        del proy['sinCapas']
        del proy['capas']
        proy['avance'] = 2
    else:
        proy['capas'].pop()
    return data


def modificaPaso4(data, id, form):
    # Modificaciones de paso 4 dado el id y el formulario con datos
    proy = data[str(id)]
    if proy['avance'] < 4:
        proy['avance'] = 4
    elif proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    proy['nombreMaterial'] = form['nombreMaterial'].strip().lower()
    proy['material'] = form['material']
    for i, capa in enumerate(proy['capas']):
        capa['nombre'] = form['nombresMaterialesCapas'][i].strip().lower()
        capa['material'] = form['materialesCapas'][i]
    return data


def eliminaPaso4(data, id):
    # Elimina materiales en paso 4 dado el id
    proy = data[str(id)]
    proy['avance'] = 3
    del proy['material']
    for capa in proy['capas']:
        del capa['material']
    return data


def sinNivelFreaticoPaso5(data, id):
    # Indica que no hay nivel freatico en paso 5 dado su id
    proy = data[str(id)]
    if proy['avance'] < 5:
        proy['avance'] = 5
    elif proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    proy['sinNivelFreatico'] = True
    proy['nivelFreatico'] = []
    return data


def modificaPaso5(data, id, contorno):
    # Añade nivel freatico en paso 5 dado el id y el contorno
    proy = data[str(id)]
    if proy['avance'] < 5:
        proy['avance'] = 5
    elif proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    proy['sinNivelFreatico'] = False
    proy['nivelFreatico'] = contorno
    return data


def eliminaPaso5(data, id):
    # Elimina ultima capa en paso 3 dado su id
    proy = data[str(id)]
    proy['avance'] = 4
    del proy['sinNivelFreatico']
    del proy['nivelFreatico']
    return data


def sinCargasPaso6(data, id):
    # Indica que no hay cargas en paso 6 dado su id
    proy = data[str(id)]
    proy['avance'] = 6
    proy['sinCargas'] = True
    proy['cargas'] = []
    return data


def modificaPaso6(data, id, nombre, xInicial, xFinal):
    # Añade capa en paso 6 dado el id, el nombre y las X inicial y final
    proy = data[str(id)]
    proy['avance'] = 6
    if 'cargas' not in proy:
        proy['sinCargas'] = False
        proy['cargas'] = []
    proy['cargas'].append(
        {'nombre': nombre.strip().lower(), 'xInicial': xInicial, 'xFinal': xFinal})
    return data


def eliminaPaso6(data, id):
    # Elimina ultima capa en paso 6 dado su id
    proy = data[str(id)]
    n = len(proy['cargas'])
    if n <= 1:
        proy['sinCargas'] = False
        del proy['cargas']
        proy['avance'] = 5
    else:
        proy['cargas'].pop()
    return data


def expresionSegura(expr, x):
    # Dada una expresión y la posible variable 'x' devuelve True o False si la expresión es segura
    listaSegura = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
                   'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',
                   'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
    nombresValidos = dict([(k, locals().get(k, None)) for k in listaSegura])
    nombresValidos['x'] = x
    ok = True
    code = ''
    try:
        code = compile(expr, "<string>", "eval")
    except:
        ok = False
    if ok:
        for nombre in code.co_names:
            if nombre not in nombresValidos:
                ok = False
                break
    return ok


def evalSeguro(expr, x):
    # Evalua la expresión con la posible variable 'x' y devuelve el resultado
    listaSegura = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
                   'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',
                   'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
    nombresValidos = dict([(k, locals().get(k, None)) for k in listaSegura])
    nombresValidos['x'] = x
    code = compile(expr, "<string>", "eval")
    return eval(code, {"__builtins__": {}}, nombresValidos)


def isNumber(str):
    # Devuelve True si el texto representa un número
    ok = True
    try:
        float(str)
    except ValueError:
        ok = False
    return ok


def testFuerzas(fuerzasX, fuerzasY):
    # Comprueba si el formato de los textos de Fuerzas X e Y es correcto
    error = ""
    for i in range(len(fuerzasX)):
        if ";" in fuerzasX[i]:
            f2 = fuerzasX[i].split(';')
            if not (isNumber(f2[0].strip()) and isNumber(f2[1].strip())):
                error = "La FX de la carga " + \
                    str(i + 1) + " contiene ';' pero no contiene 2 números válidos"
                break
        elif not expresionSegura(fuerzasX[i], 1):
            error = "La FX de la carga " + \
                str(i + 1) + " no contiene una expresión segura de Python"
    if(len(error) == 0):
        for i in range(len(fuerzasY)):
            if ";" in fuerzasY[i]:
                f2 = fuerzasY[i].split(';')
                if not (isNumber(f2[0].strip()) and isNumber(f2[1].strip())):
                    error = "La FY de la carga " + \
                        str(i + 1) + \
                        " contiene ';' pero no contiene 2 números válidos"
                    break
            elif not expresionSegura(fuerzasY[i], 1):
                error = "La FY de la carga " + \
                    str(i + 1) + " no contiene una expresión segura de Python"
    return error


def modificaPaso7(data, id, nombres, fuerzasX, fuerzasY):
    # Modifica nombre y añade fx, fy a la carga en paso 7 dado el id
    proy = data[str(id)]
    if proy['avance'] < 7:
        proy['avance'] = 7
    elif proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    for i, carga in enumerate(proy['cargas']):
        carga['nombre'] = nombres[i].strip().lower()
        carga['fX'] = fuerzasX[i]
        carga['fY'] = fuerzasY[i]
    return data


def eliminaPaso7(data, id):
    # Elimina datos de fx, fy en cargas
    proy = data[str(id)]
    proy['avance'] = 6
    for carga in proy['cargas']:
        del carga['fX']
        del carga['fY']
    return data


def modificaPaso8(data, id, centros):
    # Modifica centros de circulos en paso 8 dado el id
    proy = data[str(id)]
    if proy['avance'] < 8:
        proy['avance'] = 8
    elif proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    proy['centros'] = centros
    return data


def deletePaso8(data, id):
    # Elimina datos de centros
    proy = data[str(id)]
    proy['avance'] = 7
    del proy['centros']
    return data


def modificaPaso9(data, id, radios):
    # Modifica radios de circulos en paso 9 dado el id
    proy = data[str(id)]
    if proy['avance'] < 9:
        proy['avance'] = 9
    elif proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    proy['radios'] = radios
    return data


def deletePaso9(data, id):
    # Elimina datos de radios
    proy = data[str(id)]
    proy['avance'] = 8
    del proy['radios']
    return data


def avanzaPaso10(data, id, analisis):
    # Avanza paso tras ejecutar analisis
    proy = data[str(id)]
    if proy['avance'] < 11:
        proy['avance'] = 11
    proy['analisis'] = analisis
    return data


def modificaPaso10(data, id, dovelasX, dovelasAnchoMax, metodo):
    # Modifica dovelas y metodo en paso 10 dado el id
    proy = data[str(id)]
    if proy['avance'] < 10:
        proy['avance'] = 10
    if proy['avance'] == PASOANALISIS:
        proy['avance'] = PASOANALISIS - 1
        del proy['analisis']
    proy['dovelasX'] = dovelasX
    proy['dovelasAnchoMax'] = dovelasAnchoMax
    proy['metodo'] = metodo
    return data


def eliminaPaso10(data, id):
    # Elimina datos de dovelas y metodo
    proy = data[str(id)]
    proy['avance'] = 9
    del proy['dovelasX']
    del proy['dovelasAnchoMax']
    del proy['metodo']
    return data


def eliminaPaso11(data, id):
    # Elimina datos de dovelas y metodo
    proy = data[str(id)]
    proy['avance'] = 10
    del proy['analisis']
    return data
