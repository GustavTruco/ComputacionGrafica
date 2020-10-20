import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import time
import random
from pygame import mixer

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import lighting_shaders as ls 


maze = np.load(sys.argv[1])

PROJECTION_ORTHOGRAPHIC = 0
PROJECTION_FRUSTUM = 1
PROJECTION_PERSPECTIVE = 2

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.projection = PROJECTION_PERSPECTIVE
        self.mousePosX=0
        self.mousePosY=0
        self.noche= False

controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_N:
        controller.noche = not controller.noche

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

def cursor_pos_callback(window, x, y): 
    global camera_theta

    controller.mousePosX,controller.mousePosY = (x,y)

def createWall(modo, var=1):
    if modo == True and var ==1:
        gpuSquare=  es.toGPUShape(bs.createTextureNormalsCube("paredS.jpg"), GL_REPEAT, GL_LINEAR)
    elif modo == True and var ==2:
        gpuSquare=  es.toGPUShape(bs.createTextureNormalsCube("pared.jpg"), GL_REPEAT, GL_LINEAR)
    else:
        gpuSquare=  es.toGPUShape(bs.createTextureCube("pared.jpg"), GL_REPEAT, GL_LINEAR)
    wall= sg.SceneGraphNode("wall")
    wall.transform = tr.scale(10,10,200)
    wall.childs += [gpuSquare]
    return wall

def createFloor(modo):
    global dim_x,dim_y,lado
    if modo == True:
        gpuFloor= es.toGPUShape(bs.createTextureNormalsCube("suelo.jpg"), GL_REPEAT, GL_LINEAR)
    else:
        gpuFloor= es.toGPUShape(bs.createTextureCube("suelo.jpg"), GL_REPEAT, GL_LINEAR)
    floor= sg.SceneGraphNode("floor")
    floor.transform = tr.scale(dim_x*lado,dim_y*lado,0.0001)
    floor.childs += [gpuFloor]
    return floor

def createCube(modo):
    if modo == True:
        gpuPersonaje= es.toGPUShape(bs.createTextureNormalsCube("personaje.jpg"), GL_REPEAT, GL_LINEAR)
    else: 
        gpuPersonaje= es.toGPUShape(bs.createTextureCube("personaje.jpg"), GL_REPEAT, GL_LINEAR)
    personaje= sg.SceneGraphNode("personaje")
    personaje.transform = tr.scale(1,1,1)
    personaje.childs += [gpuPersonaje]
    return personaje

def createTreasure(modo,var=1): 

    indices = [
        0, 1, 2, 2, 3, 0, # Z+
        7, 6, 5, 5, 4, 7, # Z-
        8, 9,10,10,11, 8, # X+
        15,14,13,13,12,15, # X-
        19,18,17,17,16,19, # Y+
        20,21,22,22,23,20] # Y-

    if modo == True:
        vertices = [

            -0.5, -0.5,  0.5,    1/2 , 1,        0,0,1,
            0.5, -0.5,  0.5,    1, 1,        0,0,1,
            0.5,  0.5,  0.5,    1, 0,        0,0,1,
            -0.5,  0.5,  0.5,    1/2, 0,        0,0,1,   
                
            -0.5, -0.5, -0.5,    0, 1,        0,0,-1,
            0.5, -0.5, -0.5,    1/2, 1,        0,0,-1,
            0.5,  0.5, -0.5,    1/2, 0,        0,0,-1,
            -0.5,  0.5, -0.5,    0, 0,        0,0,-1,
                    
            0.5, -0.5, -0.5,    0, 1,        1,0,0,
            0.5,  0.5, -0.5,    1/2, 1,        1,0,0,
            0.5,  0.5,  0.5,    1/2, 0,        1,0,0,
            0.5, -0.5,  0.5,    0, 0,        1,0,0,   
                    
            -0.5, -0.5, -0.5,    0, 1,        -1,0,0,
            -0.5,  0.5, -0.5,    1/2, 1,        -1,0,0,
            -0.5,  0.5,  0.5,    1/2, 0,        -1,0,0,
            -0.5, -0.5,  0.5,    0, 0,        -1,0,0,   
                
            -0.5,  0.5, -0.5,    0, 1,        0,1,0,
            0.5,  0.5, -0.5,    1/2, 1,        0,1,0,
            0.5,  0.5,  0.5,    1/2, 0,        0,1,0,
            -0.5,  0.5,  0.5,    0, 0,        0,1,0,   
                
            -0.5, -0.5, -0.5,    0, 1,        0,-1,0,
            0.5, -0.5, -0.5,    1/2, 1,        0,-1,0,
            0.5, -0.5,  0.5,    1/2, 0,        0,-1,0,
            -0.5, -0.5,  0.5,    0, 0,        0,-1,0
            ]  

        if var==1:
            gpuTreasure= es.toGPUShape(Shape(vertices, indices, "Cofre.png"), GL_REPEAT, GL_LINEAR)
        else:
           gpuTreasure= es.toGPUShape(Shape(vertices, indices, "CofreS.png"), GL_REPEAT, GL_LINEAR) 

    else:
        vertices = [

            -0.5, -0.5,  0.5,    1/2 , 1,        
            0.5, -0.5,  0.5,    1, 1,        
            0.5,  0.5,  0.5,    1, 0,        
            -0.5,  0.5,  0.5,    1/2, 0,           
                
            -0.5, -0.5, -0.5,    0, 1,        
            0.5, -0.5, -0.5,    1/2, 1,        
            0.5,  0.5, -0.5,    1/2, 0,        
            -0.5,  0.5, -0.5,    0, 0,        

            0.5, -0.5, -0.5,    0, 1,       
            0.5,  0.5, -0.5,    1/2, 1,        
            0.5,  0.5,  0.5,    1/2, 0,        
            0.5, -0.5,  0.5,    0, 0,          
                
            -0.5, -0.5, -0.5,    0, 1,        
            -0.5,  0.5, -0.5,    1/2, 1,        
            -0.5,  0.5,  0.5,    1/2, 0,        
            -0.5, -0.5,  0.5,    0, 0,           
                
            -0.5,  0.5, -0.5,    0, 1,        
            0.5,  0.5, -0.5,    1/2, 1,       
            0.5,  0.5,  0.5,    1/2, 0,    
            -0.5,  0.5,  0.5,    0, 0,          
            
            -0.5, -0.5, -0.5,    0, 1,        
            0.5, -0.5, -0.5,    1/2, 1,        
            0.5, -0.5,  0.5,    1/2, 0,       
            -0.5, -0.5,  0.5,    0, 0,        
            ]  

        gpuTreasure= es.toGPUShape(Shape(vertices, indices, "Cofre.png"), GL_REPEAT, GL_LINEAR)

    treasure= sg.SceneGraphNode("treasure")
    treasure.transform = tr.scale(1,1,1)
    treasure.childs += [gpuTreasure]
    return treasure

if not (2  in maze):
    raise Exception("Error: No se encontro posición inicial")
elif not (3  in maze):
    raise Exception("Error: No se encontraron tesoros")
else:
    print("Bienvenido al Laberinto:")
    dim_x, dim_y = maze.shape
    xi,yi= np.unravel_index(np.argmax(np.isin(maze,2), axis=None), maze.shape)
    
if __name__ == "__main__":

    if not glfw.init():
        sys.exit()

    width = 1000
    height = 800

    window = glfw.create_window(width, height, "Maze Play 3D", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    glfw.set_key_callback(window, on_key)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos(window,width/2,height/2)

    glEnable(GL_DEPTH_TEST)

    lado= 1
    x0,y0=-xi,-yi

    wallNode= createWall(0) 
    floorNode= createFloor(0)
    personajeNode= createCube(0)
    treasureNode = createTreasure(0)

    wallDarkNode= createWall(1,2) 
    floorDarkNode= createFloor(1)
    personajeDarkNode= createCube(1)
    treasureDarkNode = createTreasure(1)
    wallBloodNode= createWall(1,1) 
    treasureBloodNode= createTreasure(1,2)


    #----Musica-------------
    mixer.init()

    mixer.music.load('juego.wav')
    pick= mixer.Sound('pick.wav')
    fin= mixer.Sound('win.wav')
    fin2= mixer.Sound('bad.wav')
    growl = mixer.Sound("growl.wav")
    growl.set_volume(0.5)
    scream = mixer.Sound("scream.wav")
    scream.set_volume(0.2)
    mixer.music.play(-1)

    #------------------------

    t0 = glfw.get_time()
    t_i= t0
    camera_theta =0
    cam =0
    z0=0
    c= np.count_nonzero(maze ==3)
    

    while not glfw.window_should_close(window):
        glfw.poll_events()

        dx,dy=0,0
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        ver= random.randint(0,20)
        if controller.noche == True:
            mvcPipeline = ls.SimpleTexturePhongShaderProgram()
            glClearColor(0.1,0,0.1, 1.0)
            z0 = np.sin(glfw.get_time())*0.006
            mixer.music.pause()
            
        else:
            mvcPipeline= es.SimpleTextureModelViewProjectionShaderProgram()
            glClearColor(0.3,0.5,0.8, 1.0)
            mixer.music.unpause()

        glUseProgram(mvcPipeline.shaderProgram)
        
        if 3 not in maze:
            break

        if  c > np.count_nonzero(maze ==3):
            c=np.count_nonzero(maze ==3)
            if controller.noche:
                scream.stop()
                growling = growl.play()
            else:
                pickup = pick.play()

        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):

            dy =  2 * dt* np.sin(camera_theta) 
            dx = -2 * dt* np.cos(camera_theta)


        elif (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):

            dy = -2 * dt* np.sin(camera_theta)
            dx = 2 * dt* np.cos(camera_theta)


        elif (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):

            dy = -2 * dt* np.cos(camera_theta)
            dx = -2 * dt* np.sin(camera_theta)

        elif (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):

            dy = 2*dt* np.cos(camera_theta)
            dx = 2*dt* np.sin(camera_theta)
            
        if int(np.around(-x0-10*dx))>= dim_x or int(np.around(-y0-10*dy))>= dim_y:
            pass

        elif maze[int(np.around(-x0-10*dx))][int(np.around(-y0))]==1 or maze[int(np.around(-x0))][int(np.around(-y0-10*dy))]==1 or maze[int(np.around(-x0-10*dx))][int(np.around(-y0-10*dy))]==1 :
            pass

        elif maze[int(np.around(-x0-3*dx))][int(np.around(-y0-3*dy))]==3:
            maze[int(np.around(-x0-3*dx))][int(np.around(-y0-3*dy))]=0

        else:
            y0 += dy
            x0 += dx

        camera_theta= 0.009*controller.mousePosX
        camX = 0.00000000000001* np.sin(camera_theta)
        camY = 0.00000000000001 * np.cos(camera_theta)
        
        viewPos = np.array([camX, camY, cam])
        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
            )
        model = tr.identity()

        if controller.noche:

            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "La"), 0.0001, 0, 0)
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "Ld"), 0.5, 0.4, 0.45)
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "Ls"), 0.5, 0.4, 0.45)

            # Object is barely visible at only ambient. Bright white for diffuse and specular components.
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "Ka"), 0.3, 0.3, 0.3)
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "Kd"), 0.3, 0.3, 0.3)
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "Ks"), 0.3, 0.3, 0.3)

            # TO DO: Explore different parameter combinations to understand their effect!
            
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "lightPosition"), camX, camY, cam-0.25)
            glUniform3f(glGetUniformLocation(mvcPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
            glUniform1ui(glGetUniformLocation(mvcPipeline.shaderProgram, "shininess"), 5)

            glUniform1f(glGetUniformLocation(mvcPipeline.shaderProgram, "constantAttenuation"), 0.1)
            glUniform1f(glGetUniformLocation(mvcPipeline.shaderProgram, "linearAttenuation"), 0.1)
            glUniform1f(glGetUniformLocation(mvcPipeline.shaderProgram, "quadraticAttenuation"), 0.15)
            glUniformMatrix4fv(glGetUniformLocation(mvcPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        glUniformMatrix4fv(glGetUniformLocation(mvcPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        
        glUniformMatrix4fv(glGetUniformLocation(mvcPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
        if controller.noche:
            personajeDarkNode.transform= tr.matmul([
                                            tr.uniformScale(0.5),
                                            tr.translate(camX,camY,3)
                                            ])

            sg.drawSceneGraphNode(personajeDarkNode,mvcPipeline,"model")
        else:
            personajeNode.transform= tr.matmul([
                                                tr.uniformScale(0.5),
                                                tr.translate(camX,camY,3)
                                                ])

            sg.drawSceneGraphNode(personajeNode,mvcPipeline,"model")

        
        for i in range(dim_x):

            for j in range(dim_y):
                

                if maze[i][j]==1:
                    
                    if controller.noche:
                        if glfw.get_time() %7 <=0.5:
                            screaming=scream.play()
                            wallBloodNode.transform= tr.translate(x0+lado*i, y0+lado*j, z0)
                            sg.drawSceneGraphNode(wallBloodNode, mvcPipeline, "model")
                        else:
                            wallDarkNode.transform= tr.translate(x0+lado*i, y0+lado*j, z0)
                            sg.drawSceneGraphNode(wallDarkNode, mvcPipeline, "model")

                    else:    
                        wallNode.transform= tr.translate(x0+lado*i, y0+lado*j, z0)
                        sg.drawSceneGraphNode(wallNode, mvcPipeline, "model")
                else:   

                    if controller.noche:

                        floorDarkNode.transform= np.matmul(tr.translate(x0+lado*i, y0+lado*j,-0.5),tr.scale(1,1,0.01))
                        sg.drawSceneGraphNode(floorDarkNode,mvcPipeline,"model")

                    else:
                        floorNode.transform= np.matmul(tr.translate(x0+lado*i, y0+lado*j,-0.5),tr.scale(1,1,0.01))
                        sg.drawSceneGraphNode(floorNode,mvcPipeline,"model")

                    if maze[i][j]==3:
                        if controller.noche:
                            if glfw.get_time() %7 <=0.5:
                                treasureBloodNode.transform= np.matmul(tr.translate(x0+lado*i, y0+lado*j,-0.3),tr.uniformScale(0.3))
                                sg.drawSceneGraphNode(treasureBloodNode,mvcPipeline,"model")
                            else:
                                treasureDarkNode.transform= np.matmul(tr.translate(x0+lado*i, y0+lado*j,-0.3),tr.uniformScale(0.3))
                                sg.drawSceneGraphNode(treasureDarkNode,mvcPipeline,"model")
                        else:
                            treasureNode.transform= np.matmul(tr.translate(x0+lado*i, y0+lado*j,-0.3),tr.uniformScale(0.3))
                            sg.drawSceneGraphNode(treasureNode,mvcPipeline,"model")

        glfw.swap_buffers(window)

    if 3 not in maze:
        t_f= glfw.get_time()
        print ("Te demoraste %s segundos en completarlo. Felicidades." % (int(t_f-t_i)))
        glfw.terminate()
        mixer.music.stop()
        fin.play()
        time.sleep(2)

    else:
        glfw.terminate()
        mixer.music.stop()
        fin2.play()
        time.sleep(0.25)