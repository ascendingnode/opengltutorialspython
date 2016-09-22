from OpenGL.GL import *
from OpenGL.GL.EXT.texture_compression_s3tc import *
import numpy as np
import struct

def loadBMP(imagepath,trilinear=True):

    print("Reading image {:}".format(imagepath))

    # Open the file
    try: file = open(imagepath,'rb')
    except:
        raise RuntimeError(
                "{:} could not be opened. Are you in the right directory? Don't forget to read the FAQ!"
                .format(imagepath))

    # Read the header, i.e. the 54 first bytes
    header = file.read(54)

    # If less than 54 bytes are read, problem
    assert len(header)==54, "Not a correct BMP file"
    # A BMP files always begins with "BM"
    assert struct.unpack('2s',header[:2])[0]==b'BM', "Not a correct BMP file"
    # Make sure this is a 24bpp file
    assert struct.unpack('i',header[0x1E:0x22])[0]==0 , "Not a correct BMP file"
    assert struct.unpack('i',header[0x1C:0x20])[0]==24, "Not a correct BMP file"

    # Read the information about the image
    dataPos    = struct.unpack('i',header[0x0A:0x0E])[0]
    imageSize  = struct.unpack('i',header[0x22:0x26])[0]
    width      = struct.unpack('i',header[0x12:0x16])[0]
    height     = struct.unpack('i',header[0x16:0x1A])[0]

    # Some BMP files are misformatted, guess missing information
    if imageSize==0: imageSize = width*height*3 # 3 : one byte for each Red, Green and Blue component
    if dataPos==0:   dataPos = 54 # The BMP header is done that way

    # Read the actual data from the file into the buffer
    data = file.read(imageSize)

    # Everything is in memory now, the file wan be closed
    file.close()

    # Create one OpenGL texture
    textureID = glGenTextures(1)

    # "Bind" the newly created texture : all future texture functions will modify this texture
    glBindTexture(GL_TEXTURE_2D, textureID)

    # Give the image to OpenGL
    glTexImage2D(GL_TEXTURE_2D, 0,GL_RGB, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, data);

    # OpenGL has now copied the data. Free our own version
    del data

    if not trilinear:
        # Poor filtering, or ...
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    else:
        # ... nice trilinear filtering.
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)

    # Return the ID of the texture we just created
    return textureID

def loadDDS(imagepath):

    # try to open the file
    try: fp = open(imagepath,'rb')
    except:
        raise RuntimeError(
                "{:} could not be opened. Are you in the right directory? Don't forget to read the FAQ!"
                .format(imagepath))

    # verify the type of file
    filecode = fp.read(4)
    if filecode!=b"DDS ":
        fp.close()
        raise RuntimeError("{:} appears not to be a DDS file".format(imagepath))

    # get the surface desc 
    header = fp.read(124)

    height      = struct.unpack( 'I',header[ 8:12])[0]
    width       = struct.unpack( 'I',header[12:16])[0]
    linearSize  = struct.unpack( 'I',header[16:20])[0]
    mipMapCount = struct.unpack( 'I',header[24:28])[0]
    fourCC      = struct.unpack('4s',header[80:84])[0]

    # how big is it going to be including all mipmaps?
    if mipMapCount>1: bufsize = linearSize*2
    else: bufsize = linearSize
    data = fp.read(bufsize)

    # close the file pointer
    fp.close()

    if fourCC=='DXT1': components = 3
    else: components = 4
    try: dxformat = {
        b'DXT1' : GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
        b'DXT3' : GL_COMPRESSED_RGBA_S3TC_DXT3_EXT,
        b'DXT5' : GL_COMPRESSED_RGBA_S3TC_DXT5_EXT,
        }[fourCC]
    except:
        raise RuntimeError("Didn't understand format code: {:}".format(fourCC))

    # Create one OpenGL texture
    textureID = glGenTextures(1)

    # "Bind" the newly created texture : all future texture functions will modify this texture
    glBindTexture(GL_TEXTURE_2D, textureID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)

    if dxformat==GL_COMPRESSED_RGBA_S3TC_DXT1_EXT: blockSize = 8
    else: blockSize = 16
    offset = 0

    # load the mipmaps
    for level in range(mipMapCount):
        size = ((width+3)//4)*((height+3)//4)*blockSize
        glCompressedTexImage2D(GL_TEXTURE_2D, level, dxformat, width, height, 0, size, data[offset:offset+size])
        
        offset += size
        width  /= 2
        height /= 2
        
        # Deal with Non-Power-Of-Two textures. This code is not included in the webpage to reduce clutter.
        if width<1: width = 1
        if height<1: height = 1

    return textureID
