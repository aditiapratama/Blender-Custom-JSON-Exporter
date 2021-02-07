import bpy


# #####################################################
# Utils
# #####################################################

def write_file( fname, content ):
    out = open( fname, "w" )
    out.write( content )
    out.close()

def ensure_folder_exist( foldername ):
    if not os.access( foldername, os.R_OK|os.W_OK|os.X_OK ):
        os.makedirs( foldername )

def ensure_extension( filepath, extension ):
    if not filepath.lower().endswith( extension ):
        filepath += extension
    return filepath


# #####################################################
# Templates - mesh
# #####################################################

TEMPLATE_FILE = """\
{
    "colours" : {
        %(colours)s
    },

    "bspTreeRoot" : "%(objname)s",

    "vertices": [
        %(vertices)s
    ],

    "faces" : {
%(faces)s
    },
}
"""

TEMPLATE_FACE = """\
        "%(name)s" : {
            "colour" : "%(colour)s",
            "vertices" : [%(index)s]
        }"""

def flat_array( array ):
    
    return ", ".join( str( round( x, 6 ) ) for x in array )

def to_srgb(val):
    if (val <= 0.0031308):
        return (val * 12.92)
    else:
        return (1.055*(val**(1.0/2.4))-0.055)

def get_mesh_string( context, global_scale ):
    import bpy
    import bmesh

    vertices = []
    objfaces = []
    colors = []

    obj = context.active_object
    
    # Get material names and srgb values
    for matcolor in bpy.context.active_object.data.materials:
        Rcolor =  str(int(to_srgb(matcolor.diffuse_color[0]) * 15))
        Gcolor =  str(int(to_srgb(matcolor.diffuse_color[1]) * 15))
        Bcolor =  str(int(to_srgb(matcolor.diffuse_color[2]) * 15))

        rgb12col = "["+Rcolor+", "+Gcolor+", "+Bcolor+"]"
        colors.append(str('"'+matcolor.name+'" : '+rgb12col))

    # Get vertices of selected object
    for verts in obj.data.vertices:
        vertices.append("[" +str(int(verts.co.x*global_scale))+", " 
                        +str(int(verts.co.y*global_scale))+", "
                        +str(int(verts.co.z*global_scale))+"]")

    # Get faces of selected object
    for faces in obj.data.polygons:
        facename = "face"+str(faces.index)
        matindex = faces.material_index
        facecolor = obj.data.materials[matindex].name
        
        objfaces.append(TEMPLATE_FACE % {
            "name" : facename,
            "colour" : facecolor,
            "index" : flat_array( faces.vertices[:] ),
        })
        
    return TEMPLATE_FILE % {
        "colours" : ",\n        ".join( colors ),
        "objname" : obj.name,
        "vertices": ",\n        ".join(map(str, vertices )), #flat_array( vertices ),
        "faces": ",\n".join( objfaces ),
    }


def export_mesh( obj, filepath, global_scale ):
    
    text = get_mesh_string( obj, global_scale )
    write_file( filepath, text )
    
    print("writing", filepath, "done")


# #####################################################
# Main
# #####################################################

def save( operator, context, filepath = "", use_selection=False, use_mesh_modifiers=True, global_matrix=None, global_scale=1000):
    filepath = ensure_extension( filepath, ".json")
    
    export_mesh( context, filepath, global_scale)
    
    return {"FINISHED"}