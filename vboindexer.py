import numpy as np
import pickle

def indexVBO(in_vertices,in_uvs,in_normals):
    VertexToOutIndex = {}
    out_vertices,out_uvs,out_normals,out_indices = [],[],[],[]

    # For each input vertex
    for i in range(len(in_vertices)):

        packed = pickle.dumps([in_vertices[i], in_uvs[i], in_normals[i]])
		
        # Try to find a similar vertex in out_XXXX
        if packed in VertexToOutIndex.keys():
	    
            # A similar vertex is already in the VBO, use it instead !
	    out_indices.append( VertexToOutIndex[packed] )
	
        else:
            
            # If not, it needs to be added in the output data.
	    out_vertices.append( in_vertices[i] )
	    out_uvs     .append( in_uvs[i] )
	    out_normals .append( in_normals[i] )
	    newindex = np.uint16( len(out_vertices) - 1 )
	    out_indices .append( newindex )
	    VertexToOutIndex[ packed ] = newindex
    
    return np.array(out_indices),np.array(out_vertices),np.array(out_uvs),np.array(out_normals)
