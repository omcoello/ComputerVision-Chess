# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import pygame
from checkers.constants import *
from checkers.game import Game
import cv2
import numpy as np
import os
from math import acos,atan,cos,sin,pi

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

type Square = dict[str, list[float]]

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def generateGameBoardDict(size) -> Square:
    d = dict()
    counter = 0
    for i in range(8):
        for j in range(8):
            # Crea la posicion central del cuadrado del tablero [ancho, alto]
            d["s"+str(counter)] = [j*size + size/2, i*size + size/2]
            counter += 1
    return d

# Criterio de terminación (un parámetro de función CornerSubPix)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

#inicializa los array que van a contener los puntos: (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:7].T.reshape(-1,2)

# Inicializa los parametros que almacenarán los puntos de la imagen, del mundo real, y los valóres intrínsecos y extrínsecos
# Para cada imagen creamos una lista que contiene una lista de puntos-3D de la escena del mundo real.
# coord3D contendrá la posición 3D de los puntos que representa a las esquinas internas de los cuadros del tablero en la escena 3D del mundo real.

coord3D = [] # PUNTOS 3D ESPACIALES EN EL MUNDO REAL

# Para cada imagen creamos una lista que contiene una lista de puntos-2D en la imagen
# coord2D contendrá la posición 2D de los puntos que representan a las esquinas internas de los cuadros del tablero en la imagen 2D.

coord2D = [] # PUNTOS 2D EN EL PLANO IMAGEN.

# Una vez que se tienen las posiciones 3D y las posiciones 2D de las esquinas internas del tablero se puede calcular la relación entre ambas
# NOTA: dado que usamos un tablero de ajedrez estos puntos tienen una relación definida entre ellos, esto es:
# la posición de los puntos está sobre las lineas y los cuadrados del tablero.
# entonces la relación (esperado-real) puede ser usada para corregir la distorsión de la imagen.

#Obtencion de imagen inicial para el juego de damas
cap = cv2.VideoCapture(1)

# Capturar un frame de la webcam
ret, frame = cap.read()

# Liberar la webcam
cap.release()

# Verificar si la captura fue exitosa
if ret:
    # Guardar la imagen en un archivo (por ejemplo, 'captura.jpg')
    image_path = os.path.dirname(__file__) + '\\capture.png'
    cv2.imwrite(image_path, frame)
    print("Imagen capturada y guardada como", image_path)
else:
    print("No se pudo capturar la imagen")

# Cerrar las ventanas
cv2.destroyAllWindows()

path = os.path.dirname(__file__) + "\\" + "capture.png"
img = cv2.imread(path)
exit() if not img else None  
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Encuentra las esquinas en un tablero de ajedrez
ret, corners = cv2.findChessboardCorners(gray, (7,7),None)

# If found, add object points, image points (after refining them)
if ret == True:
    
    corners_opt = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
    coord2D.append(corners_opt)

    coord3D.append(objp)

    # Draw and display the corners
    img = cv2.drawChessboardCorners(img, (7,7), corners_opt, ret)

    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('img', 800,600)
    cv2.imshow('img',img)
    cv2.waitKey(0)

cv2.destroyAllWindows()

# test = cv2.imread(os.path.dirname(__file__) + "\\" + images[-1])
test = cv2.imread(os.path.dirname(__file__) + "\\" + "capture.png")
exit(1) if not test else None

# print(tuple(np.array(corners_opt[-2][0], int)))
# print(corners_opt[-1][0])
#print("last four points", corners_opt[-4:][:])

points = corners_opt[-4:][:]
points = np.concatenate((points,corners_opt[-11:-7][:]), axis=0)

def calculateUpperLowerCorners(points, upper=True):
    finalPoints = []
    if upper:
        for i in range(1,7):
            data = points[i][0] - points[i-1][0]
            arg = data[1]/data[0]            
            radians =  acos(arg) if arg <= 1 and arg >= -1 else atan(arg)
            yLength = cos(radians)*data[0] if arg <= 1 and arg >= -1 else cos(radians)*data[1]
            xLength = sin(radians)*data[0] if arg <= 1 and arg >= -1 else sin(radians)*data[1]
            if i == 1:
                finalPoints.append([-xLength + (yLength + points[i-1][0][0]), -yLength + (-xLength + points[i-1][0][1])])
                finalPoints.append([yLength + points[i-1][0][0], -xLength + points[i-1][0][1]])
            
            finalPoints.append([yLength + points[i][0][0], -xLength + points[i][0][1]])
            if i == 6:
                finalPoints.append([xLength + (yLength + points[i][0][0]), yLength + (-xLength + points[i][0][1])])
        return np.array(finalPoints,dtype=int)
    
    for i in range(1,7):
        data = points[i][0] - points[i-1][0]
        arg = data[1]/data[0]            
        radians =  acos(arg) if arg <= 1 and arg >= -1 else atan(arg)
        yLength = cos(pi-radians)*data[0] if arg <= 1 and arg >= -1 else cos(pi-radians)*data[1]
        xLength = sin(pi-radians)*data[0] if arg <= 1 and arg >= -1 else sin(pi-radians)*data[1]            
        if i == 1:
            finalPoints.append([-xLength + (yLength + points[i-1][0][0]), yLength + (xLength + points[i-1][0][1])])
            finalPoints.append([yLength + points[i-1][0][0], xLength + points[i-1][0][1]])
        
        finalPoints.append([yLength + points[i][0][0], xLength + points[i][0][1]])
        if i == 6:
            finalPoints.append([xLength + (yLength + points[i][0][0]), -yLength + (xLength + points[i][0][1])])                
    
    return np.array(finalPoints,dtype=int)

data = []
boardRange = dict()

def addData(d,counter,times):
    if times == 1:
        for i in range(-8,-1):
            key = "s"+str(counter)
            if key not in d.keys():
                if i == -8: 
                    d[key] = [data[i-1],data[i]]
                    counter += 1
                key = "s"+str(counter)
                d[key] = [data[i], data[i+1]]
            else:
                if i == -8:
                    d[key].append(data[i-1])
                    d[key].append(data[i])
                    counter += 1
                key = "s"+str(counter)
                d[key].append(data[i])
                d[key].append(data[i+1])
                d[key] = np.array(d[key])
            counter += 1
    else:
        for i in range(-8,-1):
            key = "s"+str(counter)
            if key not in d.keys():
                if i == -8: 
                    d[key] = [data[i-1],data[i]]
                    counter += 1
                key = "s"+str(counter)
                d[key] = [data[i],data[i+1]]
            else:
                if i == -8:
                    d[key].append(data[i-1])
                    d[key].append(data[i])
                    d["s"+str(counter+8)] = [data[i-1],data[i]]
                    counter += 1
                key = "s"+str(counter)
                d[key].append(data[i])
                d[key].append(data[i+1])
                d["s"+str(counter+8)] = [data[i], data[i+1]]
                d[key] = np.array(d[key])
            counter += 1

i = 7
data = calculateUpperLowerCorners(coord2D[-1][:i][:])
addData(boardRange,0,1)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i:][:])),axis=0)
addData(boardRange,0,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+7:][:])),axis=0)
addData(boardRange,8,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+14:][:])),axis=0)
addData(boardRange,16,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+21:][:])),axis=0)
addData(boardRange,24,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+28:][:])),axis=0)
addData(boardRange,32,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+35:][:])),axis=0)
addData(boardRange,40,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+28:][:],False)),axis=0)
addData(boardRange,48,2)

data = np.concatenate((data,calculateUpperLowerCorners(coord2D[-1][i+35:][:],False)),axis=0)
addData(boardRange,56,1)


for p in data:
    cv2.circle(test, p, radius=3, color=(0, 0, 255), thickness=-1)

for p in boardRange["s56"]:
    cv2.circle(test, p, radius=3, color=(255, 0, 0), thickness=-1)

#from left to right, up to down
upperBounds = np.array([boardRange["s0"][0], boardRange["s7"][1]])
lowerBounds = np.array([boardRange["s56"][2], boardRange["s63"][3]]) 

cv2.imshow('test',test)
cv2.waitKey(0)


print(boardRange)
#Generar diccionario de cuadros de tablero de pygame
gameBoard = generateGameBoardDict(SQUARE_SIZE)

# Diccionario para almacenar los tiempos de permanencia en una posición
time_in_position = {key: 0 for key in boardRange.keys()}

cap = cv2.VideoCapture(1)

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        if game.winner() != None:
            print(game.winner())
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                        
        # Capturar un frame de la webcam
        ret, frame = cap.read()

        if not ret:
            break

        # Convertir el frame a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Definir el rango de colores rojos en HSV
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        # Crear una máscara para el color rojo
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Encontrar los contornos en la máscara
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Calcular el área del contorno
            area = cv2.contourArea(contour)

            # Ignorar contornos pequeños
            if area > 100:
                # Calcular el centroide del contorno
                M = cv2.moments(contour)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])

                # Dibujar un círculo en el centro del objeto
                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # Verificar si el centroide está dentro de algún rango de posición
                for key, p in boardRange.items():
                    if p[0][0] <= cx <= p[1][0] and p[0][1] <= cy <= p[2][1]:
                        # Incrementar el tiempo en esta posición
                        time_in_position[key] += 1

                        # Si el tiempo es >= 2 segundos (2000 ms), ejecutar función X()
                        if time_in_position[key] >= 2000 / 30:  # Usamos 30 como aproximación de los fps
                            print("Ejecutar función X() para posición:", key)
                            # Llamar a la función X() aquí
                            pos = gameBoard[key]
                            row, col = int(pos[1])//SQUARE_SIZE, int(pos[0])//SQUARE_SIZE
                            print(key)
                            print(row, "---",col)
                            game.select(row, col)
                    else:
                        time_in_position[key] = 0

                # Mostrar las coordenadas del centro
                print("Centro X:", cx, "Centro Y:", cy)

        # Mostrar el frame original con el círculo dibujado
        cv2.imshow("Object Tracking", frame)

        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        game.update()
    
    pygame.quit()

main()