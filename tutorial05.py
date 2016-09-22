import glfw
from OpenGL.GL import *
from shader import Shader
from textures import loadBMP,loadDDS
from controls import glm_perspective,glm_lookAt
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
    window = glfw.create_window(1024, 768, "Tutorial 05 - Textured Cube", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to open GLFW window.")

    # Make the window's context current
    glfw.make_context_current(window)

    # Ensure we can capture the escape key being pressed below
    glfw.set_input_mode(window, glfw.STICKY_KEYS, True)

    # Dark blue background
    glClearColor(0.0, 0.0, 0.4, 0.0)

    # Enable depth test
    glEnable(GL_DEPTH_TEST)
    # Accept fragment if it closer to the camera than the former one
    glDepthFunc(GL_LESS)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Create and compile our GLSL program from the shaders
    shader = Shader( "TransformVertexShader2.vertexshader", "TextureFragmentShader.fragmentshader")
    shader.compile()

    # Projection matrix : 45 deg Field of View, 4:3 ratio, display range : 0.1 unit <-> 100 units
    Projection = glm_perspective(45.0*np.pi/180., 4.0 / 3.0, 0.1, 100.0)

    # Camera matrix
    View = glm_lookAt(
            [4,3,3], # Camera is at (4,3,3), in World Space
            [0,0,0], # and looks at the origin
            [0,1,0]  # Head is up (set to 0,-1,0 to look upside-down)
            )

    # Model matrix : an identity matrix (model will be at the origin)
    Model = np.eye(4)

    # Our ModelViewProjection : multiplication of our 3 matrices
    # (convert to 32-bit now that computations are done)
    MVP = np.array( np.dot(np.dot(Model, View), Projection), dtype=np.float32 )

    # Load the texture using any two methods
    #Texture = loadBMP("uvtemplate.bmp")
    Texture = loadDDS("uvtemplate.DDS")

    # Our vertices. Tree consecutive floats give a 3D vertex; Three consecutive vertices give a triangle.
    # A cube has 6 faces with 2 triangles each, so this makes 6*2=12 triangles, and 12*3 vertices
    g_vertex_buffer_data = np.array([
                -1.0,-1.0,-1.0,
                -1.0,-1.0, 1.0,
                -1.0, 1.0, 1.0,
                 1.0, 1.0,-1.0,
                -1.0,-1.0,-1.0,
                -1.0, 1.0,-1.0,
                 1.0,-1.0, 1.0,
                -1.0,-1.0,-1.0,
                 1.0,-1.0,-1.0,
                 1.0, 1.0,-1.0,
                 1.0,-1.0,-1.0,
                -1.0,-1.0,-1.0,
                -1.0,-1.0,-1.0,
                -1.0, 1.0, 1.0,
                -1.0, 1.0,-1.0,
                 1.0,-1.0, 1.0,
                -1.0,-1.0, 1.0,
                -1.0,-1.0,-1.0,
                -1.0, 1.0, 1.0,
                -1.0,-1.0, 1.0,
                 1.0,-1.0, 1.0,
                 1.0, 1.0, 1.0,
                 1.0,-1.0,-1.0,
                 1.0, 1.0,-1.0,
                 1.0,-1.0,-1.0,
                 1.0, 1.0, 1.0,
                 1.0,-1.0, 1.0,
                 1.0, 1.0, 1.0,
                 1.0, 1.0,-1.0,
                -1.0, 1.0,-1.0,
                 1.0, 1.0, 1.0,
                -1.0, 1.0,-1.0,
                -1.0, 1.0, 1.0,
                 1.0, 1.0, 1.0,
                -1.0, 1.0, 1.0,
                 1.0,-1.0, 1.0
            ],dtype=np.float32)

    g_uv_buffer_data = np.array([
                0.000059, 1.0-0.000004,
                0.000103, 1.0-0.336048,
                0.335973, 1.0-0.335903,
                1.000023, 1.0-0.000013,
                0.667979, 1.0-0.335851,
                0.999958, 1.0-0.336064,
                0.667979, 1.0-0.335851,
                0.336024, 1.0-0.671877,
                0.667969, 1.0-0.671889,
                1.000023, 1.0-0.000013,
                0.668104, 1.0-0.000013,
                0.667979, 1.0-0.335851,
                0.000059, 1.0-0.000004,
                0.335973, 1.0-0.335903,
                0.336098, 1.0-0.000071,
                0.667979, 1.0-0.335851,
                0.335973, 1.0-0.335903,
                0.336024, 1.0-0.671877,
                1.000004, 1.0-0.671847,
                0.999958, 1.0-0.336064,
                0.667979, 1.0-0.335851,
                0.668104, 1.0-0.000013,
                0.335973, 1.0-0.335903,
                0.667979, 1.0-0.335851,
                0.335973, 1.0-0.335903,
                0.668104, 1.0-0.000013,
                0.336098, 1.0-0.000071,
                0.000103, 1.0-0.336048,
                0.000004, 1.0-0.671870,
                0.336024, 1.0-0.671877,
                0.000103, 1.0-0.336048,
                0.336024, 1.0-0.671877,
                0.335973, 1.0-0.335903,
                0.667969, 1.0-0.671889,
                1.000004, 1.0-0.671847,
                0.667979, 1.0-0.335851
            ],dtype=np.float32)

    # Create the vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)

    # Create the vertex uv buffer object
    uvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, uvbo)
    glBufferData(GL_ARRAY_BUFFER, g_uv_buffer_data.nbytes, g_uv_buffer_data, GL_STATIC_DRAW)

    # Loop until the user closes the window
    while( glfw.get_key(window, glfw.KEY_ESCAPE ) != glfw.PRESS and
            glfw.window_should_close(window) == 0 ):
        
        # Clear the screen
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # Use our shader
        shader.enable()

        # Send our transformation to the currently bound shader, 
        # in the "MVP" uniform
        shader.setUniform("MVP", "mat4", MVP)

        # Bind our texture in Texture Unit 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, Texture)

        # Set our "myTextureSampler" sampler to user Texture Unit 0
        shader.setUniform("myTextureSampler","sampler2D",0)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexAttribPointer(
                0,         # attribute 0. No particular reason for 0, but must match the layout in the shader.
                3,         # size
                GL_FLOAT,  # type
                GL_FALSE,  # normalized?
                0,         # stride
                None       # array buffer offset
        )

        # 2nd attribute buffer : colors
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, uvbo)
        glVertexAttribPointer(
                1,         # attribute. No particular reason for 1, but must match the layout in the shader.
                2,         # size
                GL_FLOAT,  # type
                GL_FALSE,  # normalized?
                0,         # stride
                None       # array buffer offset
        )
        
        # Draw the triangle !
        glDrawArrays(GL_TRIANGLES, 0, 12*3) # 3 indices starting at 0 -> 1 triangle

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
    
        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":

    main()
