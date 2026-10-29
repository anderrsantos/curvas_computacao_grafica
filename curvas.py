import math
import glfw
import numpy as np
from OpenGL.GL import *

R = 3.0  # raio da esfera

rng = np.random.default_rng(42)
_v = rng.normal(size=(900, 3))
_v /= np.linalg.norm(_v, axis=1, keepdims=True)   # projeta na esfera
NUVEM_PONTOS = R * _v


def desenhar_pontos_discretos():
    glColor3f(0.1, 1.0, 0.1)  # verde
    glPointSize(2.5)
    glBegin(GL_POINTS)
    for x, y, z in NUVEM_PONTOS:
        glVertex3f(x, y, z)
    glEnd()



#  EXPLÍCITA: z = ± sqrt(r² - x² - y²)
def esfera_explicita(x, y):
    """Retorna z (hemisfério positivo) ou None se (x,y) estiver fora do disco."""
    d = R**2 - x**2 - y**2
    if d < 0:
        return None
    return math.sqrt(d)


PONTOS_EXPLICITA = []
for x in np.arange(-R, R + 0.001, 0.2):
    for y in np.arange(-R, R + 0.001, 0.2):
        z = esfera_explicita(x, y)
        if z is not None:
            PONTOS_EXPLICITA.append((x, y, z))     # hemisfério norte
            PONTOS_EXPLICITA.append((x, y, -z))    # hemisfério sul (o "-")


def desenhar_explicita():
    glColor3f(1.0, 0.5, 0.0)  # laranja
    glPointSize(2.5)
    glBegin(GL_POINTS)
    for p in PONTOS_EXPLICITA:
        glVertex3f(*p)
    glEnd()


# 3) IMPLÍCITA: x² + y² + z² - r² = 0
def pertence_esfera(x, y, z, tolerancia):
    return abs(x**2 + y**2 + z**2 - R**2) < tolerancia


def gerar_implicita(passo=0.25):
    tolerancia = R * passo  # espessura da "casca" aceita
    pts = []
    grade = np.arange(-R - 0.5, R + 0.5, passo)
    for x in grade:
        for y in grade:
            for z in grade:
                if pertence_esfera(x, y, z, tolerancia):
                    pts.append((x, y, z))
    return pts


PONTOS_IMPLICITA = gerar_implicita()


def desenhar_implicita():
    glColor3f(1.0, 0.1, 0.1)  # vermelho
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for p in PONTOS_IMPLICITA:
        glVertex3f(*p)
    glEnd()


#  PARAMÉTRICA: x(u,v), y(u,v), z(u,v) com longitude u e latitude v
#    x = r·cos(v)·cos(u)
#    y = r·sin(v)
#    z = r·cos(v)·sin(u)
#    0 <= u <= 2π   e   -π/2 <= v <= π/2
def esfera_parametrica(u, v):
    x = R * math.cos(v) * math.cos(u)
    y = R * math.sin(v)
    z = R * math.cos(v) * math.sin(u)
    return x, y, z


def desenhar_parametrica(meridianos=16, paralelos=12, segmentos=60):
    glColor3f(0.0, 0.8, 1.0)  # ciano
    glLineWidth(1.0)

    # Meridianos: u fixo, v varrendo de -π/2 a π/2
    for i in range(meridianos):
        u = 2 * math.pi * i / meridianos
        glBegin(GL_LINE_STRIP)
        for j in range(segmentos + 1):
            v = -math.pi / 2 + math.pi * j / segmentos
            glVertex3f(*esfera_parametrica(u, v))
        glEnd()

    # Paralelos: v fixo, u varrendo de 0 a 2π
    for j in range(1, paralelos):
        v = -math.pi / 2 + math.pi * j / paralelos
        glBegin(GL_LINE_STRIP)
        for i in range(segmentos + 1):
            u = 2 * math.pi * i / segmentos
            glVertex3f(*esfera_parametrica(u, v))
        glEnd()


# Cena
def desenhar_eixos():
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    glVertex2f(-10, 0); glVertex2f(10, 0)
    glVertex2f(0, -10); glVertex2f(0, 10)
    glEnd()


def desenhar(tx, ty, funcao):
    glPushMatrix()
    glTranslatef(tx, ty, 0.0)
    # Inclinação FIXA (sem animação), só para dar noção de profundidade
    glRotatef(20, 1, 0, 0)
    glRotatef(30, 0, 1, 0)
    funcao()
    glPopMatrix()


def main():
    if not glfw.init():
        return
    janela = glfw.create_window(800, 800, "Esfera - Representacoes de Curvas", None, None)
    if not janela:
        glfw.terminate()
        return
    glfw.make_context_current(janela)
    glfw.swap_interval(1)

    print("Gerando... (a implícita é pré-calculada uma vez)")
    print("ESC para sair")

    while not glfw.window_should_close(janela):
        glfw.poll_events()
        if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
            break

        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10, 10, -10, 10, -20, 20)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        desenhar_eixos()

        # Topo esquerdo: pontos discretos
        desenhar(-5.0, 5.0, desenhar_pontos_discretos)
        # Topo direito: paramétrica
        desenhar(5.0, 5.0, desenhar_parametrica)
        # Inferior esquerdo: implícita
        desenhar(-5.0, -5.0, desenhar_implicita)
        # Inferior direito: explícita
        desenhar(5.0, -5.0, desenhar_explicita)

        glfw.swap_buffers(janela)

    glfw.terminate()


if __name__ == "__main__":
    main()