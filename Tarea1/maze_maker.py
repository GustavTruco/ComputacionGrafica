#!/usr/bin/python3.7
# coding=utf-8

# import modules used here -- sys is a very standard one
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from pygame import mixer #Musica
import sys 
import os
import time 

import basic_shapes as bs
import easy_shaders as es
import transformations as tr



INT_BYTES = 4

grid= sys.argv[1]

class Controller:
    fillPolygon = True
    mousePos=(0,0)

controller = Controller()

def on_key(window, key,  scancode, action, mods):
         
    if action != glfw.PRESS:
        return
    
    global controller

    if key ==glfw.KEY_1:
        global xi,yi
        if 2 in maze:
            if maze[xi][yi]==2:
                maze[xi][yi]=0

        j= int(np.around((controller.mousePos[0]-xo)/lado2))
        i= int(np.around((controller.mousePos[1]-yo)/lado2))
        if j < dim_x and i < dim_y and j >=0 and i>=0: 

            if maze[j][dim_y-1-i]==0: 
                maze[j][dim_y-1-i]= 2
                xi,yi= (j,dim_y-1-i)
                
            else:
                maze[j][dim_y-1-i]= 0

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

    else:
        print('Unknown key')

    


def mouse_button_callback(window, button, action, mods): 

    if action == glfw.PRESS:
        if button == glfw.MOUSE_BUTTON_LEFT:
            j= int(np.around((controller.mousePos[0]-xo)/lado2))
            i= int(np.around((controller.mousePos[1]-yo)/lado2))
            if j < dim_x and i < dim_y and j >=0 and i>=0: 

                if maze[j][dim_y-1-i]==0:maze[j][dim_y-1-i]= 1
                else:
                    maze[j][dim_y-1-i]= 0

        if button == glfw.MOUSE_BUTTON_RIGHT:
            j= int(np.around((controller.mousePos[0]-xo)/lado2))
            i= int(np.around((controller.mousePos[1]-yo)/lado2))
            if j < dim_x and i < dim_y and j >=0 and i>=0: 

                if maze[j][dim_y-1-i]==0: maze[j][dim_y-1-i]= 3
                else:
                    maze[j][dim_y-1-i]= 0

        if button == glfw.MOUSE_BUTTON_MIDDLE:
            global xi,yi
            if 2 in maze:
                if maze[xi][yi]==2:
                    maze[xi][yi]=0

            j= int(np.around((controller.mousePos[0]-xo)/lado2))
            i= int(np.around((controller.mousePos[1]-yo)/lado2))
            if j < dim_x and i < dim_y and j >=0 and i>=0: 

                if maze[j][dim_y-1-i]==0: 
                    maze[j][dim_y-1-i]= 2
                    xi,yi= (j,dim_y-1-i)
                    
                else:
                    maze[j][dim_y-1-i]= 0
        
        

    elif action == glfw.RELEASE:
        pass
           

def cursor_pos_callback(window, x, y): 
    controller.mousePos = (x,y)


class GPUShape:
    vao = 0
    vbo = 0
    ebo = 0
    size = 0


def drawShape(shaderProgram, shape):

    glBindVertexArray(shape.vao)
    glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

    position = glGetAttribLocation(shaderProgram, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
    
    color = glGetAttribLocation(shaderProgram, "color")
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    glDrawElements(GL_TRIANGLES, shape.size, GL_UNSIGNED_INT, None)


def createSquare(image_filename):
    vertices = [
        0.0, 0.0,  0,  0, 1/3,
         1.0, 0.0,  0,  1/2, 1/3,
         1.0,  1.0,  0,  1/2, 0,
        0.0,  1.0,  0,  0, 0, 
        ]
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
         ] # Y-

    return bs.Shape(vertices, indices, image_filename)


if not os.path.exists(sys.argv[1]):
    try:
        dim = sys.argv[2].split('x')
        dim_y, dim_x = int(dim[0]), int(dim[1])
        maze = np.zeros((dim_x, dim_y), dtype=np.int32)
        xi,yi=(0,0)
    except:
        raise Exception('Error de Especificación: No se especifica Dimensión.')

elif len(sys.argv) == 2:
    print("Bienvenido al Editor:")
    maze = np.load(grid)
    dim_x, dim_y = maze.shape
    xi,yi= np.unravel_index(np.argmax(np.isin(maze,2), axis=None), maze.shape)
         
    
    # editor

else:
    raise Exception('Error de Archivo: El archivo ya existe, para editar no especifique dimensíon')

if __name__ == "__main__":

    if not glfw.init():
        sys.exit()

    width = 800
    height = 800
    
    

    window = glfw.create_window(width, height, "MAZE-MAKER: Editor de Laberintos", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    glfw.set_key_callback(window, on_key)
    
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()
    
    glClearColor(0.0, 0.0, 0.0, 1.0)

    gpuPared = es.toGPUShape(createSquare("pared.jpg"), GL_REPEAT, GL_LINEAR)
    gpuSuelo = es.toGPUShape(createSquare("suelo.jpg"), GL_REPEAT, GL_LINEAR)
    gpuPersonaje = es.toGPUShape(createSquare("personaje.jpg"), GL_REPEAT, GL_LINEAR)
    gpuTesoro = es.toGPUShape(createSquare("tesoro.jpg"), GL_REPEAT, GL_LINEAR)

     #----Musica-------------
    mixer.init()
    juego= mixer.Sound('editor.wav')
    fin2= mixer.Sound('bad.wav')
    juego.play(-1)
    #------------------------

    while not glfw.window_should_close(window):

        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)

        view = tr.lookAt(
            np.array([0,0,100]),
            np.array([0,0,0]),
            np.array([0,1,0])
        )
        lado= 2/ max(dim_x,dim_y)
        x0=-1+ (1-lado*dim_x/2)
        y0=-1+ (1-lado*dim_y/2)
        lado2 = 800/max(dim_x,dim_y)
        xo= (lado2/2 + 400 - lado2*dim_x/2)
        yo= (lado2/2 + 400 - lado2*dim_y/2)
        

        for i in range(dim_x):

                    for j in range(dim_y):

                        quadTransform = tr.matmul([
                            tr.translate(x0+lado*i, y0+lado*j, 0),
                            tr.uniformScale(lado)
                        ])
                        glUseProgram(textureShaderProgram.shaderProgram)
                        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
                        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
                        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, quadTransform)

                        if maze[i][j]==1:
                            textureShaderProgram.drawShape(gpuPared)

                        elif maze[i][j]==2:
                            textureShaderProgram.drawShape(gpuPersonaje)

                        elif maze[i][j]==3:
                            textureShaderProgram.drawShape(gpuTesoro)

                        else:
                            textureShaderProgram.drawShape(gpuSuelo)
        glfw.swap_buffers(window)
    np.save(grid,maze)
    glfw.terminate()
    juego.stop()
    fin2.play()
    time.sleep(0.25)