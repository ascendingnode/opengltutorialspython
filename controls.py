import glfw
import numpy as np

def glm_normalize(v):
    norm = np.linalg.norm(v)
    if norm==0: return v
    return v/norm

def glm_perspective(fovy,aspect,zNear,zFar):
    assert(abs(aspect) > 0)
    tanHalfFovy = np.tan(fovy / 2.0)
    Result = np.zeros((4,4))
    Result[0][0] = 1. / (aspect * tanHalfFovy)
    Result[1][1] = 1. / (tanHalfFovy)
    Result[2][3] = -1.
    Result[2][2] = -float(zFar + zNear) / (zFar - zNear)
    Result[3][2] = -(2. * zFar * zNear) / (zFar - zNear)
    return Result

def glm_ortho(left, right, bottom, top, zNear, zFar):
    Result = np.eye(4)
    Result[0][0] = 2. / (right - left)
    Result[1][1] = 2. / (top - bottom)
    Result[3][0] = -float(right + left) / (right - left)
    Result[3][1] = -float(top + bottom) / (top - bottom)
    Result[2][2] = -2. / (zFar - zNear)
    Result[3][2] = -float(zFar + zNear) / (zFar - zNear)
    return Result

def glm_lookAt(eye, center, up):

    eye = np.asarray(eye)
    center = np.asarray(center)
    up = np.asarray(up)

    f = glm_normalize(center - eye)
    s = glm_normalize(np.cross(f, up))
    u = glm_normalize(np.cross(s, f))

    Result = np.eye(4)
    Result[:3,0] = s
    Result[:3,1] = u
    Result[:3,2] = -f
    Result[3][0] =-np.dot(s, eye)
    Result[3][1] =-np.dot(u, eye)
    Result[3][2] = np.dot(f, eye)
    return Result

class Controls:

    def __init__(self, window):

        self.window = window
    
        self.ViewMatrix = np.eye(4)
        self.ProjectionMatrix = np.eye(4)

        # Initial position : on +Z
        self.position = np.array([ 0., 0., 5. ])
        # Initial horizontal angle : toward -Z
        self.horizontalAngle = np.pi
        # Initial vertical angle : none
        self.verticalAngle = 0.0
        # Initial Field of View
        self.initialFoV = 45.0

        self.speed = 3.0 # 3 units / second
        self.mouseSpeed = 0.0005

        self.lastTime = None

    def update(self):

        # glfwGetTime is called only once, the first time this function is called
        if self.lastTime is None:
            self.lastTime = glfw.get_time()

        # Compute time difference between current and last frame
        currentTime = glfw.get_time()
        deltaTime = float(currentTime - self.lastTime)

        # Get mouse position
        xpos, ypos = glfw.get_cursor_pos(self.window)

        # Reset mouse position for next frame
        glfw.set_cursor_pos(self.window, 1024/2, 768/2);

        # Compute new orientation
        self.horizontalAngle += self.mouseSpeed * float(1024/2 - xpos )
        self.verticalAngle   += self.mouseSpeed * float( 768/2 - ypos )

        # Direction : Spherical coordinates to Cartesian coordinates conversion
        direction = np.array([
            np.cos(self.verticalAngle) * np.sin(self.horizontalAngle), 
            np.sin(self.verticalAngle),
            np.cos(self.verticalAngle) * np.cos(self.horizontalAngle)
        ])

        # Right vector
        right = np.array([
            np.sin(self.horizontalAngle - np.pi/2.0), 
            0,
            np.cos(self.horizontalAngle - np.pi/2.0)
        ])

        # Up vector
        up = np.cross( right, direction )

        # Move forward
        if glfw.get_key( self.window, glfw.KEY_UP ) == glfw.PRESS:
            self.position += direction * deltaTime * self.speed
        # Move backward
        if glfw.get_key( self.window, glfw.KEY_DOWN ) == glfw.PRESS:
            self.position -= direction * deltaTime * self.speed
        # Strafe right
        if glfw.get_key( self.window, glfw.KEY_RIGHT ) == glfw.PRESS:
            self.position += right * deltaTime * self.speed
        # Strafe left
        if glfw.get_key( self.window, glfw.KEY_LEFT ) == glfw.PRESS:
            self.position -= right * deltaTime * self.speed

        FoV = self.initialFoV #- 5 * glfwGetMouseWheel(); 
        # Now GLFW 3 requires setting up a callback for this. 
        # It's a bit too complicated for this beginner's tutorial, so it's disabled instead.

        # Projection matrix : 45 deg Field of View, 4:3 ratio, display range : 0.1 unit <-> 100 units
        self.ProjectionMatrix = glm_perspective(FoV*np.pi/180., 4.0 / 3.0, 0.1, 100.0)
        # Camera matrix
        self.ViewMatrix = glm_lookAt(
                self.position,           # Camera is here
                self.position+direction, # and looks here : at the same position, plus "direction"
                up                       # Head is up (set to 0,-1,0 to look upside-down)
        )

        # For the next frame, the "last time" will be "now"
        self.lastTime = currentTime

        self.ModelMatrix = np.eye(4)

        self.MVP = np.array( np.dot(np.dot(self.ModelMatrix, self.ViewMatrix), self.ProjectionMatrix), dtype=np.float32 )
