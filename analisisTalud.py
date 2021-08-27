import os
import scipy.interpolate as itp
import matplotlib.pyplot as plt
from matplotlib import cm
from random import seed, random
import sys
import math
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')

OUTFOLDER = "dist/analisis/"


def calculaCoeficiente(talud, px, py, rd):
    # ESTA FUNCION DEVUELVE DATOS ALEATORIOS. DEBE SER SUSTITUIDA.
    #
    # SOLO CALCULA LA DISTANCIA DE CADA PUNTO AL CENTRO DEL GRAFICO
    # DIVIDIDO POR EL RADIO
    # Y MULTIPLICADO POR UN VALOR ALEATORIO ENTRE 0 Y 1
    cpx = talud['dimensiones']['derecha'] - talud['dimensiones']['izquierda']
    cpy = talud['dimensiones']['arriba'] - talud['dimensiones']['abajo']
    return random() * math.sqrt((px - cpx) * (px - cpx) + (py - cpy) * (py - cpy)) / rd


def generaGraficoSimple(x, y, z, fichero):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.view_init(azim=45, elev=45)
    #
    ax.plot_trisurf(np.array(x), np.array(y), np.array(z))
    #
    fig.savefig(fichero)


def generaGraficoSuavizado(x, y, z, fichero):
    X = np.array(x)
    Y = np.array(y)
    Z = np.array(z)
    funcInterpola = itp.interp2d(X, Y, Z, kind='cubic')
    xx = np.linspace(x[0], x[len(x) - 1])
    yy = np.linspace(y[0], y[len(y) - 1])
    XX, YY = np.meshgrid(xx, yy)
    ZZ = funcInterpola(xx, yy)
    #
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.view_init(azim=45, elev=45)
    #
    ax.plot_surface(XX, YY, ZZ, rstride=1, cstride=1, cmap=cm.viridis)
    ax.plot(X.flatten(), Y.flatten(), Z.flatten(), ls='', marker='o', color='k')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z'),
    #
    fig.savefig(fichero)


def run(talud, idUsuario, idTalud, generarGrafico, suavizar):
    numeroX = talud['centros']['numeroX']
    numeroY = talud['centros']['numeroY']
    nradios = talud['centros']['nradios']
    # ASIGNAR COEFICIENTES
    seed(datetime.now())
    coefic = []
    x = []
    y = []
    z = []
    for ny in range(numeroY):
        py = talud['centros']['inicioY'] + ny * talud['centros']['distanciaY']
        for nx in range(numeroX):
            px = talud['centros']['inicioX'] + nx * \
                talud['centros']['distanciaX'] + \
                ny * talud['centros']['desplazaX']
            rdmin = talud['radios'][ny * numeroX + nx]['min']
            rdmax = talud['radios'][ny * numeroX + nx]['max']
            min = sys.float_info.max
            for nr in range(nradios):
                if nradios == 1:
                    rd = rdmin
                else:
                    rd = rdmin + nr * (rdmax - rdmin) / (nradios - 1)
                coef = calculaCoeficiente(talud, px, py, rd)
                if coef < min:
                    min = coef
                coefic.append({'centroX': px, 'centroY': py,
                              'radio': rd, 'coeficiente': coef})
            x.append(px)
            y.append(py)
            z.append(min)
    # BUSCAR LOS COEFICIENTES MINIMO Y MAXIMO PARA EL TOTAL
    min = sys.float_info.max
    max = sys.float_info.min
    nCenX = -1
    nCenY = -1
    nRad = -1
    pos = -1
    i = 0
    for ny in range(numeroY):
        for nx in range(numeroX):
            for nr in range(nradios):
                if coefic[i]['coeficiente'] > max:
                    max = coefic[i]['coeficiente']
                if coefic[i]['coeficiente'] < min:
                    min = coefic[i]['coeficiente']
                    nCenY = ny
                    nCenX = nx
                    nRad = nr
                    pos = i
                i = i + 1
    # GENERAR GRAFICO (OPCIONAL)
    if generarGrafico:
        if not os.path.exists(OUTFOLDER):
            os.makedirs(OUTFOLDER)
        fichero = OUTFOLDER + idUsuario + '.' + str(idTalud) + '.1.png'
        if os.path.isfile(fichero):
            os.remove(fichero)
        if suavizar:
            generaGraficoSuavizado(x, y, z, fichero)
        else:
            generaGraficoSimple(x, y, z, fichero)
    # DEVOLVER RESULTADO ANALISIS
    return {'numCentroY': nCenY, 'numCentroX': nCenX, 'numRradio': nRad,
            'centroX': coefic[pos]['centroX'], 'centroY': coefic[pos]['centroY'],
            'radio': coefic[pos]['radio'], 'coefMin': min, 'coefMax': max,
            'coeficientes': coefic}
