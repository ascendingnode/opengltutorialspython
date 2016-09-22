import glfw
from OpenGL import GL

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
    window = glfw.create_window(1024, 768, "Tutorial 01", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to open GLFW window. If you have an Intel GPU, they are not 3.3 compatible. Try the 2.1 version of the tutorials.")

    # Make the window's context current
    glfw.make_context_current(window)

    # Ensure we can capture the escape key being pressed below
    glfw.set_input_mode(window, glfw.STICKY_KEYS, True)

    # Dark blue background
    GL.glClearColor(0.0, 0.0, 0.4, 0.0)

    # Loop until the user closes the window
    while( glfw.get_key(window, glfw.KEY_ESCAPE ) != glfw.PRESS and
            glfw.window_should_close(window) == 0 ):
        
        # Render here, e.g. using pyOpenGL
        GL.glClear( GL.GL_COLOR_BUFFER_BIT )

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":

    main()
