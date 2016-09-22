import glfw
from OpenGL.GL import *
from shader import Shader
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
    window = glfw.create_window(1024, 768, "Tutorial 02 - Red triangle", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to open GLFW window.")

    # Make the window's context current
    glfw.make_context_current(window)

    # Ensure we can capture the escape key being pressed below
    glfw.set_input_mode(window, glfw.STICKY_KEYS, True)

    # Dark blue background
    glClearColor(0.0, 0.0, 0.4, 0.0)

    # Create and compile our GLSL program from the shaders
    shader = Shader("SimpleVertexShader.vertexshader","SimpleFragmentShader.fragmentshader")
    shader.compile()

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Define the verticies
    v = np.array([
            -1.0, -1.0, 0.0,
             1.0, -1.0, 0.0,
             0.0,  1.0, 0.0,
             ], dtype=np.float32)

    # Create the vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, v.nbytes, v, GL_STATIC_DRAW)

    # Loop until the user closes the window
    while( glfw.get_key(window, glfw.KEY_ESCAPE ) != glfw.PRESS and
            glfw.window_should_close(window) == 0 ):
        
        # Clear the screen
        glClear( GL_COLOR_BUFFER_BIT )

        # Use our shader
        shader.enable()

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
        
        # Draw the triangle !
        glDrawArrays(GL_TRIANGLES, 0, 3) # 3 indices starting at 0 -> 1 triangle

        glDisableVertexAttribArray(0)
    
        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    del vao,vbo,shader
    glfw.terminate()

if __name__ == "__main__":

    main()
