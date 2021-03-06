import glfw
from OpenGL.GL import *
from shader import Shader
from textures import loadBMP,loadDDS
from controls import Controls
from objloader import loadOBJ
import numpy as np
import struct

def main():

    # Initialize the library
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True) # To make MacOS happy; should not be needed
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(1024, 768, "Tutorial 08 - Basic Shading", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to open GLFW window.")

    # Make the window's context current
    glfw.make_context_current(window)

    # Ensure we can capture the escape key being pressed below
    glfw.set_input_mode(window, glfw.STICKY_KEYS, True)

    # Hide the mouse and enable unlimited mouvement
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Set the mouse at the center of the screen
    glfw.poll_events()
    glfw.set_cursor_pos(window, 1024/2, 768/2)

    # Dark blue background
    glClearColor(0.0, 0.0, 0.4, 0.0)

    # Enable depth test
    glEnable(GL_DEPTH_TEST)
    # Accept fragment if it closer to the camera than the former one
    glDepthFunc(GL_LESS)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Create and compile our GLSL program from the shaders
    shader = Shader("StandardShading.vertexshader", "StandardShading.fragmentshader")
    shader.compile()

    # Create Controls object
    controls = Controls(window)
    
    # Load the texture using any two methods
    Texture = loadDDS("uvmap2.DDS")

    # Read our .obj file
    vertices, uvs, normals = loadOBJ("suzanne.obj",invert_v=True)

    # Create the vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Create the uv buffer object
    uvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, uvbo)
    glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)

    # Create normal buffer object
    nbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, nbo)
    glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)

    # Loop until the user closes the window
    while( glfw.get_key(window, glfw.KEY_ESCAPE ) != glfw.PRESS and
            glfw.window_should_close(window) == 0 ):
        
        # Clear the screen
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # Use our shader
        shader.enable()

        # Compute the MVP matrix from keyboard and mouse input
        controls.update()

        # Send our transformation to the currently bound shader, 
        # in the "MVP" uniform
        shader.setUniform("V", "mat4", np.array(controls.ViewMatrix,dtype=np.float32))
        shader.setUniform("M", "mat4", np.array(controls.ModelMatrix,dtype=np.float32))
        shader.setUniform("MVP", "mat4", controls.MVP)

        shader.setUniform("LightPosition_worldspace", "vec3", 
                np.array([4,4,4],dtype=np.float32))

        # Bind our texture in Texture Unit 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, Texture)

        # Set our "myTextureSampler" sampler to user Texture Unit 0
        shader.setUniform("myTextureSampler","sampler2D",0)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexAttribPointer(
                0,         # attribute 0.
                3,         # size
                GL_FLOAT,  # type
                GL_FALSE,  # normalized?
                0,         # stride
                None       # array buffer offset
        )

        # 2nd attribute buffer : UVs
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, uvbo)
        glVertexAttribPointer(
                1,         # attribute.
                2,         # size
                GL_FLOAT,  # type
                GL_FALSE,  # normalized?
                0,         # stride
                None       # array buffer offset
        )

        # 3rd attribute buffer : UVs
        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, nbo)
        glVertexAttribPointer(
                2,         # attribute.
                3,         # size
                GL_FLOAT,  # type
                GL_FALSE,  # normalized?
                0,         # stride
                None       # array buffer offset
        )
        
        # Draw the triangle !
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
    
        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":

    main()
