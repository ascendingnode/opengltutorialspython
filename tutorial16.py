import glfw
from OpenGL.GL import *
from shader import Shader
from textures import loadBMP,loadDDS
from controls import *
from objloader import loadOBJ
from vboindexer import indexVBO
import numpy as np

def main():

    # Initialize the library
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True) 
    # To make MacOS happy; should not be needed
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(1024, 768, "Tutorial 16 - Shadows", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to open GLFW window.")

    # Make the window's context current
    glfw.make_context_current(window)

    # We would expect width and height to be 1024 and 768
    windowWidth = 1024
    windowHeight = 768
    # But on MacOS X with a retina screen it'll be 1024*2 and 768*2, 
    # so we get the actual framebuffer size:
    windowWidth,windowHeight = glfw.get_framebuffer_size(window)

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
    depth_shader = Shader("DepthRTT.vertexshader", "DepthRTT.fragmentshader")
    depth_shader.compile()

    # Create Controls object
    controls = Controls(window)
    
    # Load the texture using any two methods
    Texture = loadDDS("uvmap3.DDS")

    # Read our .obj file
    vertices, uvs, normals = loadOBJ("room_thickwalls.obj",invert_v=True)

    indices,indexed_vertices,indexed_uvs,indexed_normals = indexVBO(vertices,uvs,normals)

    # Create the vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, indexed_vertices.nbytes, indexed_vertices, GL_STATIC_DRAW)

    # Create the uv buffer object
    uvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, uvbo)
    glBufferData(GL_ARRAY_BUFFER, indexed_uvs.nbytes, indexed_uvs, GL_STATIC_DRAW)

    # Create normal buffer object
    nbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, nbo)
    glBufferData(GL_ARRAY_BUFFER, indexed_normals.nbytes, indexed_normals, GL_STATIC_DRAW)

    # Generate a buffer for the indices as well
    ibo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, ibo)
    glBufferData(GL_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # ---------------------------------------------
    # Render to Texture - specific code begins here
    # ---------------------------------------------

    # The framebuffer, which regroups 0, 1, or more textures, and 0 or 1 depth buffer.
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)


    # Depth texture. Slower than a depth buffer, but you can sample it later in your shader
    depthTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, depthTexture)
    glTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT16,1024,1024,0,GL_DEPTH_COMPONENT,GL_FLOAT,
            np.zeros((1024,1024),dtype=np.uint16))
    #glTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT16,1024,1024,0,GL_DEPTH_COMPONENT,GL_FLOAT,0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_R_TO_TEXTURE)

    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, depthTexture, 0)

    # No color output in the bound framebuffer, only depth.
    glDrawBuffer(GL_NONE)

    # Always check that our framebuffer is ok
    if glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError("Framebuffer not OK!")

    # Create and compile our GLSL program from the shaders
    shader = Shader( "ShadowMapping.vertexshader", "ShadowMapping.fragmentshader" )
    shader.compile()

    # For speed computation
    lastTime = glfw.get_time()
    nbFrames = 0

    # Loop until the user closes the window
    while( glfw.get_key(window, glfw.KEY_ESCAPE ) != glfw.PRESS and
            glfw.window_should_close(window) == 0 ):

        # Measure speed
        currentTime = glfw.get_time()
        nbFrames += 1
        if currentTime-lastTime >= 1.0: 
            # If last prinf() was more than 1sec ago
            # printf and reset
            print("{:.5f} ms/frame".format(1000.0/float(nbFrames)))
            nbFrames = 0
            lastTime += 1.0
        
        # Render to our framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        glViewport(0,0,1024,1024)
        # Render on the whole framebuffer, complete from the lower left corner to the upper right

        # We don't use bias in the shader, but instead we draw back faces, 
        # which are already separated from the front faces by a small distance 
        # (if your geometry is made this way)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK) # Cull back-facing triangles -> draw only front-facing triangles

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use our shader
        depth_shader.enable()

        lightInvDir = np.array([0.5,2,2])

        depthProjectionMatrix = glm_ortho(-10.,10.,-10.,10.,-10.,20.)
        depthViewMatrix = glm_lookAt(lightInvDir,[0.,0.,0.],[0.,1.,0.])
        depthModelMatrix = np.eye(4)
        depthMVP = np.array(
                np.dot(np.dot(depthModelMatrix,depthViewMatrix),depthProjectionMatrix),
                dtype=np.float32)

        # Send our transformation to the currently bound shader, 
        # in the "MVP" uniform
        depth_shader.setUniform("depthMVP", "mat4", depthMVP)

        # 1rst attribute buffer : vertices
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexAttribPointer(
            0,        # The attribute we want to configure
            3,        # size
            GL_FLOAT, # type
            GL_FALSE, # normalized?
            0,        # stride
            None      # array buffer offset
            )

        # Index buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)

        # Draw the triangles !
        glDrawElements(
            GL_TRIANGLES,      # mode
            len(indices),      # count
            GL_UNSIGNED_SHORT, # type
            None               # element array buffer offset
            )

        glDisableVertexAttribArray(0)

        # Render to the screen
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        glViewport(0,0,windowWidth,windowHeight)
        # Render on the whole framebuffer, complete from the lower left corner to the upper right

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        # Cull back-facing triangles -> draw only front-facing triangles

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use our shader
        shader.enable()

        # Compute the MVP matrix from keyboard and mouse input
        controls.update()

        biasMatrix = np.array([
            [0.5, 0.0, 0.0, 0.0],
            [0.0, 0.5, 0.0, 0.0],
            [0.0, 0.0, 0.5, 0.0],
            [0.5, 0.5, 0.5, 1.0]
            ])

        depthBiasMVP = np.array(np.dot(depthMVP,biasMatrix),dtype=np.float32)

        # Send our transformation to the currently bound shader, 
        # in the "MVP" uniform
        shader.setUniform("V", "mat4", np.array(controls.ViewMatrix,dtype=np.float32))
        shader.setUniform("M", "mat4", np.array(controls.ModelMatrix,dtype=np.float32))
        shader.setUniform("MVP", "mat4", controls.MVP)
        shader.setUniform("DepthBiasMVP", "mat4", depthBiasMVP)

        shader.setUniform("LightInvDirection_worldspace", "vec3", 
                np.array(lightInvDir,dtype=np.float32))

        # Bind our texture in Texture Unit 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, Texture)

        # Set our "myTextureSampler" sampler to user Texture Unit 0
        shader.setUniform("myTextureSampler","sampler2D",0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, depthTexture)
        shader.setUniform("shadowMap", "sampler2DShadow",1)

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
        
        # Index buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)

        # Draw the triangles !
        glDrawElements(
            GL_TRIANGLES,      # mode
            len(indices),      # count
            GL_UNSIGNED_SHORT, # type
            None               # element array buffer offset
        )

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
    
        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":

    main()
