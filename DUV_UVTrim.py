import bpy
import bmesh
import math
from mathutils import Vector
from . import DUV_Utils

def read_trim_atlas(context):
    atlas = list()
    obj = context.scene.trim_atlas
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    #lets read coords

    faces = list()

    print("gettin atlas")

    #MAKE FACE LIST
    for face in bm.faces:
        faces.append(face)

    for face in faces:
        xmin, xmax = face.loops[0][uv_layer].uv.x, face.loops[0][uv_layer].uv.x
        ymin, ymax = face.loops[0][uv_layer].uv.y, face.loops[0][uv_layer].uv.y

        for vert in face.loops:
            xmin = min(xmin, vert[uv_layer].uv.x)
            xmax = max(xmax, vert[uv_layer].uv.x)
            ymin = min(ymin, vert[uv_layer].uv.y)
            ymax = max(ymax, vert[uv_layer].uv.y)

        print(face)



        #new_subrect = subrect()
        #edge1 = xmax - xmin
        #edge2 = ymax - ymin

        
        #rect = list()
        
        #for loop in face.loops:
        #    loop_uv = loop[uv_layer]
            #make sure to create new uv vector here, dont reference
        #    uvcoord = Vector((loop_uv.uv.x,loop_uv.uv.y))
        #    rect.append(uvcoord)
        
        #new_subrect.uvcoord = rect
        
        #calculate aspect ratio
        #if edge1 > 0 and edge2 > 0:

            #aspect = edge1/edge2
            #if aspect > 1:
            #    aspect = round(aspect)
            #else:
            #    aspect = 1/(round(1/aspect))
                #aspect = 1/aspect
            #posaspect = aspect
            #if posaspect < 1.0:
            #    posaspect = 1/posaspect
            #calculate size
            #size = face.calc_area()

            #adjust scale
            #size /= context.scene.duvhotspotscale*context.scene.duvhotspotscale

            #size = float('%.2g' % size) #round to 2 significant digits

            


            #new_subrect.aspect = aspect
            #new_subrect.posaspect = posaspect
            #new_subrect.size = size
            #atlas.append(new_subrect)   

    #print("atlas")
    #print(atlas)
    #for a in atlas:
    #    print(a.posaspect)
    return faces

class DREAMUV_OT_uv_trim(bpy.types.Operator):
    """Unwrap selection using the atlas object as a guide"""
    bl_idname = "view3d.dreamuv_uvtrim"
    bl_label = "Trim"
    bl_options = {"UNDO"}
    
    def execute(self, context):

        #get atlas first
        atlas = read_trim_atlas(context)
        print("atlas:")
        print(atlas)
        #check if horizontal or vertical, and make trimsheet

        #temp: assuming it's horizontal:
        trimsheet = list()
        

        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        HSfaces = list()
        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                HSfaces.append(face)

        
        is_rect = DUV_Utils.square_fit(context)

        #V1: assume horizontal layout
        
        xmin, xmax = HSfaces[0].loops[0][uv_layer].uv.x, HSfaces[0].loops[0][uv_layer].uv.x
        ymin, ymax = HSfaces[0].loops[0][uv_layer].uv.y, HSfaces[0].loops[0][uv_layer].uv.y
        
        for face in HSfaces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)

        #test if tall or wide:
        width = xmax - xmin
        height = ymax - ymin

        horizontal = True

        if width > height:
            print("horizontal!")

        if width <= height:
            print("vertical!")
            horizontal = False
            
        #flip it!
        if horizontal == False:
            #flip width and height values:
            width = ymax - ymin
            height = xmax - xmin
            #rotate
            for face in HSfaces:
                for loop in face.loops:
                    tempx = loop[uv_layer].uv.x
                    loop[uv_layer].uv.x = loop[uv_layer].uv.y
                    loop[uv_layer].uv.y = tempx

        #temporary trim sheet:
        uvcoord = Vector(( 1.0 , 0.75 ))
        trimsheet.append(uvcoord)

        print(trimsheet[0].y)

        #map trim to trimsheet index

        scale = (trimsheet[0].x-trimsheet[0].y)/height
        print(scale)

        #scale the uvs to sheet and move:
        for face in HSfaces:
            for loop in face.loops:
                loop[uv_layer].uv.x *= scale
                loop[uv_layer].uv.y *= scale
                #move
                loop[uv_layer].uv.y += trimsheet[0].y
        

        #prevent divide by 0:
        #if (xmax - xmin) == 0:
        #    xmin = .1
        #if (ymax - ymin) == 0:
        #    ymin = .1

        #for face in HSfaces:
        #    for loop in face.loops:
        #        loop[uv_layer].uv.x -= xmin
        #        loop[uv_layer].uv.y -= ymin
        #        loop[uv_layer].uv.x /= (xmax-xmin)
        #        loop[uv_layer].uv.y /= (ymax-ymin)

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        return {'FINISHED'}