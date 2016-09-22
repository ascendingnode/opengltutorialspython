import numpy as np

# Very, VERY simple OBJ loader.
# Here is a short list of features a real function would provide : 
# - Binary files. Reading a model should be just a few memcpy's away, not parsing a file at runtime. In short : OBJ is not very great.
# - Animations & bones (includes bones weights)
# - Multiple UVs
# - All attributes should be optional, not "forced"
# - More stable. Change a line in the OBJ file and it crashes.
# - More secure. Change another line and you can inject code.
# - Loading from memory, stream, etc

def loadOBJ(path, invert_v=False):
    
    print("Loading OBJ file {:}...".format(path))

    try: f = open(path,'r')
    except:
        raise RuntimeError("Impossible to open the file! Are you in the right path?"
        " See Tutorial 1 for details")
    
    temp_vertices,temp_uvs,temp_normals,indices = [],[],[],[]

    for l in f:

	# read the first word of the line
        ls = l.split()
        if len(ls)==0 or l[0]=='#': continue
        lineHeader = ls[0] 
		
	if lineHeader=="v":
            temp_vertices.append([float(i) for i in ls[1:4]])
	elif lineHeader=="vt":
            temp_uvs.append([float(i) for i in ls[1:3]])
            # Invert V coordinate since we will only use DDS texture, which are inverted. 
            if invert_v: temp_uvs[-1][1] *= -1.
	elif lineHeader=="vn":
            temp_normals.append([float(i) for i in ls[1:4]])
	elif lineHeader=="f":
            ll = [[int(i) for i in ll.split('/')] for ll in ls[1:]]
            for ll in ls[1:]:
                indices.append([int(i) for i in ll.split('/')])
    
    out_vertices,out_uvs,out_normals = [],[],[]

    # For each vertex of each triangle
    for i in indices:
	# Get the indices of its attributes
	# Get the attributes thanks to the index
	# Put the attributes in buffers
	out_vertices.append( temp_vertices[ i[0]-1 ] )
	out_uvs     .append( temp_uvs[ i[1]-1 ] )
	out_normals .append( temp_normals[ i[2]-1 ] )
	
    return (
            np.array(out_vertices,dtype=np.float32),
            np.array(out_uvs,dtype=np.float32),
            np.array(out_normals,dtype=np.float32)
            )
