import glfw
from OpenGL.GL import *
from shader import Shader
from controls import glm_perspective,glm_lookAt
import numpy as np

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
    window = glfw.create_window(1024, 768, "Tutorial 04 - Colored Cube", None, None)
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
    shader = Shader( "TransformVertexShader.vertexshader", "ColorFragmentShader.fragmentshader")
    shader.compile()

    # Projection matrix : 45 deg Field of View, 4:3 ratio, display range : 0.1 unit <-> 100 units
    Projection = glm_perspective(45.0*np.pi/180., 4.0 / 3.0, 0.1, 100.0)

    # Camera matrix
    View = glm_lookAt(
            [4,3,-3], # Camera is at (4,3,-3), in World Space
            [0,0,0], # and looks at the origin
            [0,1,0]  # Head is up (set to 0,-1,0 to look upside-down)
            )

    # Model matrix : an identity matrix (model will be at the origin)
    Model = np.eye(4)

    # Our ModelViewProjection : multiplication of our 3 matrices
    # (convert to 32-bit now that computations are done)
    MVP = np.array( np.dot(np.dot(Model, View), Projection), dtype=np.float32 )

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

    # One color for each vertex. They were generated randomly.
    g_color_buffer_data = np.array([
                0.583,  0.771,  0.014,
                0.609,  0.115,  0.436,
                0.327,  0.483,  0.844,
                0.822,  0.569,  0.201,
                0.435,  0.602,  0.223,
                0.310,  0.747,  0.185,
                0.597,  0.770,  0.761,
                0.559,  0.436,  0.730,
                0.359,  0.583,  0.152,
                0.483,  0.596,  0.789,
                0.559,  0.861,  0.639,
                0.195,  0.548,  0.859,
                0.014,  0.184,  0.576,
                0.771,  0.328,  0.970,
                0.406,  0.615,  0.116,
                0.676,  0.977,  0.133,
                0.971,  0.572,  0.833,
                0.140,  0.616,  0.489,
                0.997,  0.513,  0.064,
                0.945,  0.719,  0.592,
                0.543,  0.021,  0.978,
                0.279,  0.317,  0.505,
                0.167,  0.620,  0.077,
                0.347,  0.857,  0.137,
                0.055,  0.953,  0.042,
                0.714,  0.505,  0.345,
                0.783,  0.290,  0.734,
                0.722,  0.645,  0.174,
                0.302,  0.455,  0.848,
                0.225,  0.587,  0.040,
                0.517,  0.713,  0.338,
                0.053,  0.959,  0.120,
                0.393,  0.621,  0.362,
                0.673,  0.211,  0.457,
                0.820,  0.883,  0.371,
                0.982,  0.099,  0.879
    ],dtype=np.float32)

    # Create the vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)

    # Create the vertex color buffer object
    cbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, cbo)
    glBufferData(GL_ARRAY_BUFFER, g_color_buffer_data.nbytes, g_color_buffer_data, GL_STATIC_DRAW)

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
        glBindBuffer(GL_ARRAY_BUFFER, cbo)
        glVertexAttribPointer(
                1,         # attribute. No particular reason for 1, but must match the layout in the shader.
                3,         # size
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

    del vao,vbo,shader
    glfw.terminate()

if __name__ == "__main__":

    main()
