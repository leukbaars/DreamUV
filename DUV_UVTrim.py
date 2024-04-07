import bpy
import bmesh
import math
import random
from mathutils import Vector
from . import DUV_Utils

def getymin(trim):
    return trim.ymin
def getxmin(trim):
    return trim.xmin

def read_trim_atlas(context, trimtype):
    atlas = list()
    obj = context.scene.trim_atlas
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    #lets read coords

    faces = list()

    print("gettin atlas")

    for face in bm.faces:
        xmin, xmax = face.loops[0][uv_layer].uv.x, face.loops[0][uv_layer].uv.x
        ymin, ymax = face.loops[0][uv_layer].uv.y, face.loops[0][uv_layer].uv.y

        for vert in face.loops:
            xmin = min(xmin, vert[uv_layer].uv.x)
            xmax = max(xmax, vert[uv_layer].uv.x)
            ymin = min(ymin, vert[uv_layer].uv.y)
            ymax = max(ymax, vert[uv_layer].uv.y)
        
        horizontal = False
        vertical = False
        if xmin <= 0.01 and xmax >= 0.99:
            horizontal = True
        if ymin <= 0.01 and ymax >= 0.99:
            vertical = True
        
        facerect = trim()
        facerect.xmin = xmin
        facerect.ymin = ymin
        facerect.xmax = xmax
        facerect.ymax = ymax
        
        #print(trimtype)
        
        if (horizontal or vertical) and trimtype == "trim":
            print("adding trim")
            atlas.append(facerect)
        
        if trimtype == "cap" and not horizontal and not vertical:
            print("adding cap")
            #print(facerect.xmin)
            #print(facerect.xmax)
            atlas.append(facerect) 
        
        if horizontal:
            atlas.sort(key=getymin, reverse=True)
        if vertical:
            atlas.sort(key=getxmin, reverse=False)
        if trimtype == "cap":
            atlas.sort(key=getxmin, reverse=False)
            

    #print(atlas)

    return atlas
    
def uv_trim(context):
    #get atlas first
    atlas = read_trim_atlas(context, "trim")
    print("atlas:")
    print(atlas)
    #check if horizontal or vertical, and make trimsheet

    if context.scene.trim_index > ( len(atlas) - 1.0 ):
        context.scene.trim_index = 0.0


    #MAKE DUPLICATE AND SPLIT EDGES
    #CREATE WORKING DUPLICATE!
    object_original = bpy.context.view_layer.objects.active
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.duplicate()
    bpy.ops.object.editmode_toggle()
    bpy.context.view_layer.objects.active.name = "dreamuv_temp"
    object_temporary = bpy.context.view_layer.objects.active

    #PREPROCESS - save seams and hard edges
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)

    faces = list()
    for face in bm.faces:
        if face.select:
            faces.append(face)

    bmesh.update_edit_mesh(obj.data)
    
    #mark seams on selection edge:
    bpy.ops.mesh.region_to_loop()
    bpy.ops.mesh.mark_seam(clear=False)
    
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
    
    #don't do angle
    #angle = bpy.context.object.data.auto_smooth_angle
    #bpy.ops.mesh.edges_select_sharp(sharpness=angle)
    #bpy.ops.mesh.mark_seam(clear=False)
    #bpy.ops.mesh.select_all(action='DESELECT')
    

    bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.mesh.select_all(action='DESELECT')

    for edge in bm.edges:
        if edge.seam or edge.smooth == False:
            edge.select = True

    bpy.ops.mesh.edge_split(type='EDGE')
    bpy.ops.mesh.select_all(action='DESELECT')



    #select all faces to be hotspotted again:

    for face in faces:
        face.select = True


    trimsheet = list()
    #for face in atlas:
        

    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()

    HSfaces = list()
    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            HSfaces.append(face)


    is_rect = DUV_Utils.square_fit(context)


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
    if width <= height:
        horizontal = False
        
    #V1: assume horizontal layout
    if atlas[0].xmin <= 0.01 and atlas[0].xmax >= 0.99:
        print("HORIZONTAL MODE")
        
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

        #map trim to trimsheet index
        trimindex = int(context.scene.trim_index)
        scale = (atlas[trimindex].ymax-atlas[trimindex].ymin)/height

        #scale the uvs to sheet and move:
        for face in HSfaces:
            for loop in face.loops:
                loop[uv_layer].uv.x *= scale
                loop[uv_layer].uv.y *= scale
                #move
                loop[uv_layer].uv.y += atlas[trimindex].ymin
                
        #map to bounds:
        #first, get current bounds:
        bmin = 0
        bmax = 0
        for face in HSfaces:
            for loop in face.loops:
                if loop[uv_layer].uv.x > bmax:
                    bmax = loop[uv_layer].uv.x
        
        #shift randomly
        random_shift = random.random()
        if context.scene.duv_uvtrim_randomshift == True:
            for face in HSfaces:
                for loop in face.loops:
                    loop[uv_layer].uv.x += random_shift
        
        #else now scale to bounds:
        elif context.scene.duv_uvtrim_bounds == True:
            for face in HSfaces:
                for loop in face.loops:
                    loop[uv_layer].uv.x /= bmax
                    loop[uv_layer].uv.x *= (context.scene.duv_uvtrim_max - context.scene.duv_uvtrim_min)
                    loop[uv_layer].uv.x += context.scene.duv_uvtrim_min

    if atlas[0].ymin <= 0.01 and atlas[0].ymax >= 0.99:
        print("VERTICAL MODE")
        #flip it!
        if not horizontal:
            print("this one is wrong")
            width = ymax - ymin
            height = xmax - xmin
        
        if horizontal:
            
            print("vertical mode and horizontal")
            
            #rotate 
            for face in HSfaces:
                for loop in face.loops:
                    tempx = loop[uv_layer].uv.x
                    loop[uv_layer].uv.x = loop[uv_layer].uv.y
                    loop[uv_layer].uv.y = tempx

        #map trim to trimsheet index
        trimindex = int(context.scene.trim_index)
        scale = (atlas[trimindex].xmax-atlas[trimindex].xmin)/height

        #scale the uvs to sheet and move:
        
        for face in HSfaces:
            for loop in face.loops:
                loop[uv_layer].uv.x *= scale
                loop[uv_layer].uv.y *= scale
                #loop[uv_layer].uv.y /= (xmax-xmin)
                
                #move
                loop[uv_layer].uv.x += atlas[trimindex].xmin
                
        #map to bounds:
        #first, get current bounds:
        bmin = 0
        bmax = 0
        for face in HSfaces:
            for loop in face.loops:
                if loop[uv_layer].uv.y > bmax:
                    bmax = loop[uv_layer].uv.y

        #shift randomly
        random_shift = random.random()
        if context.scene.duv_uvtrim_randomshift == True:
            for face in HSfaces:
                for loop in face.loops:
                    loop[uv_layer].uv.y += random_shift
        
        #else now scale to bounds:
        elif context.scene.duv_uvtrim_bounds == True:
            for face in HSfaces:
                for loop in face.loops:
                    loop[uv_layer].uv.y /= bmax
                    loop[uv_layer].uv.y *= (context.scene.duv_uvtrim_max - context.scene.duv_uvtrim_min)
                    loop[uv_layer].uv.y += context.scene.duv_uvtrim_min




    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

    #NOW RETURN OLD UVS
    #transfer UV maps back to original mesh

    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data) 
    uv_layer = bm.loops.layers.uv.verify()
    uv_backup = list();
    #print("new UV:")
    for face in bm.faces:
        backupface = list()
        for vert in face.loops:
            backupuv = list()
            backupuv.append(vert[uv_layer].uv.x)
            backupuv.append(vert[uv_layer].uv.y)
            backupface.append(backupuv)
            #print(backupuv)
        uv_backup.append(backupface)
        
    #now apply to original mesh
    bpy.ops.object.editmode_toggle()
    object_temporary.select_set(False)
    object_original.select_set(True)
    bpy.ops.object.editmode_toggle()

    obj = object_original
    bm = bmesh.from_edit_mesh(obj.data) 
    uv_layer = bm.loops.layers.uv.verify()
    #uv_backup = list();
    #print("new UV:")
    for face, backupface in zip(bm.faces, uv_backup):
        for vert, backupuv in zip(face.loops, backupface):
            vert[uv_layer].uv.x = backupuv[0]
            vert[uv_layer].uv.y = backupuv[1]
    bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.editmode_toggle() 

    object_original.select_set(False)
    object_temporary.select_set(True)
    bpy.ops.object.delete(use_global=False)
    object_original.select_set(True)
    context.view_layer.objects.active=bpy.context.selected_objects[0]

    #toggle back to edit mode
    bpy.ops.object.editmode_toggle() 

class DREAMUV_OT_uv_trim(bpy.types.Operator):
    """Unwrap selection as tiling trim using the trim atlas as a guide"""
    bl_idname = "view3d.dreamuv_uvtrim"
    bl_label = "Trim"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        
        #remember selected uv
        uv_index = bpy.context.view_layer.objects.active.data.uv_layers.active_index
        if context.scene.duv_trimcap_uv1 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 0
            uv_trim(context)
        if context.scene.duv_trimcap_uv2 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 1
            uv_trim(context)
        if context.scene.duv_trimcap_uv1 == False and context.scene.duv_trimcap_uv2 == False:
            #just uv selected uv
            uv_trim(context)
        #reset selected uv
        bpy.context.view_layer.objects.active.data.uv_layers.active_index = uv_index
        
        if context.scene.duv_autoboxmaptrim == True:
            bpy.ops.view3d.dreamuv_uvboxmap()
        
        return {'FINISHED'}
        
def uv_cap(context):  
    #get atlas first
    atlas = read_trim_atlas(context, "cap")
    print("atlas:")
    print(atlas)
    
    if context.scene.cap_index > ( len(atlas) - 1.0 ):
        context.scene.cap_index = 0.0
    
    #check if horizontal or vertical, and make trimsheet

    #temp: assuming it's horizontal:
    
    trimsheet = list()
    #for face in atlas:
        

    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()

    HSfaces = list()
    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            HSfaces.append(face)
   
    is_rect = DUV_Utils.square_fit(context)

    #FIT TO 0-1 range
    xmin, xmax = HSfaces[0].loops[0][uv_layer].uv.x, HSfaces[0].loops[0][uv_layer].uv.x
    ymin, ymax = HSfaces[0].loops[0][uv_layer].uv.y, HSfaces[0].loops[0][uv_layer].uv.y
    
    for face in HSfaces: 
        for vert in face.loops:
            xmin = min(xmin, vert[uv_layer].uv.x)
            xmax = max(xmax, vert[uv_layer].uv.x)
            ymin = min(ymin, vert[uv_layer].uv.y)
            ymax = max(ymax, vert[uv_layer].uv.y)

    #prevent divide by 0:
    if (xmax - xmin) == 0:
        xmin = .1
    if (ymax - ymin) == 0:
        ymin = .1
    
    trimindex = int(context.scene.cap_index)        
    print("move uv to this:")
    print(atlas[trimindex].xmin)
    print(atlas[trimindex].ymin)
    print(atlas[trimindex].xmax)
    print(atlas[trimindex].ymax)
    
    for face in HSfaces:
        for loop in face.loops:
            loop[uv_layer].uv.x -= xmin
            loop[uv_layer].uv.y -= ymin
            loop[uv_layer].uv.x /= (xmax-xmin)
            loop[uv_layer].uv.y /= (ymax-ymin)

    #apply the new UV
    for face in HSfaces:
        for loop in face.loops:
            loop[uv_layer].uv.x *= atlas[trimindex].xmax-atlas[trimindex].xmin
            loop[uv_layer].uv.y *= atlas[trimindex].ymax-atlas[trimindex].ymin
            loop[uv_layer].uv.x += atlas[trimindex].xmin
            loop[uv_layer].uv.y += atlas[trimindex].ymin


    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')


class DREAMUV_OT_uv_cap(bpy.types.Operator):
    """Unwrap selection as single cap using the trim atlas as a guide"""
    bl_idname = "view3d.dreamuv_uvcap"
    bl_label = "Cap"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        #remember selected uv
        uv_index = bpy.context.view_layer.objects.active.data.uv_layers.active_index
        if context.scene.duv_trimcap_uv1 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 0
            uv_cap(context)
        if context.scene.duv_trimcap_uv2 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 1
            uv_cap(context)
        if context.scene.duv_trimcap_uv1 == False and context.scene.duv_trimcap_uv2 == False:
            #just uv selected uv
            uv_cap(context)
        #reset selected uv
        bpy.context.view_layer.objects.active.data.uv_layers.active_index = uv_index
        
        if context.scene.duv_autoboxmaptrim == True:
            bpy.ops.view3d.dreamuv_uvboxmap()
        
        return {'FINISHED'}

def uv_trimnext(self, context):  
    atlas = read_trim_atlas(context, "trim")
    trimindex = int(context.scene.trim_index)

    if self.trimswitched == False:
        if self.reverse == False:
            context.scene.trim_index += 1
            if context.scene.trim_index > ( len(atlas) - 1 ):
                context.scene.trim_index = 0
        if self.reverse == True:
            context.scene.trim_index -= 1
            if context.scene.trim_index < 0:
                context.scene.trim_index = len(atlas) - 1

        trimindex = int(context.scene.trim_index)
    
    if bpy.context.object.mode == 'OBJECT':
        return {'FINISHED'}
               
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()

    selected_faces = list()
    for face in bm.faces:
        if face.select:
            selected_faces.append(face)


    if len(selected_faces) == 0:
        return {'FINISHED'}

    #select linked uvs
    bpy.ops.mesh.select_linked(delimit={'UV'})
    

    faces = list()
    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            faces.append(face)
            
    

    xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
    ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y

    for face in faces: 
        for vert in face.loops:
            xmin = min(xmin, vert[uv_layer].uv.x)
            xmax = max(xmax, vert[uv_layer].uv.x)
            ymin = min(ymin, vert[uv_layer].uv.y)
            ymax = max(ymax, vert[uv_layer].uv.y)

    

    width = xmax - xmin
    height = ymax - ymin
    

    #FIT TO 0-1 range

    #prevent divide by 0:
    if (xmax - xmin) == 0:
        xmin = .1
    if (ymax - ymin) == 0:
        ymin = .1
    if atlas[0].xmin <= 0.01 and atlas[0].xmax >= 0.99:
        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x -= xmin
                loop[uv_layer].uv.y -= ymin
                loop[uv_layer].uv.x /= height
                loop[uv_layer].uv.y /= height
    if atlas[0].ymin <= 0.01 and atlas[0].ymax >= 0.99:
        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x -= xmin
                loop[uv_layer].uv.y -= ymin
                loop[uv_layer].uv.x /= width
                loop[uv_layer].uv.y /= width

    

    if atlas[0].xmin <= 0.01 and atlas[0].xmax >= 0.99:
        scale = (atlas[trimindex].ymax-atlas[trimindex].ymin)
        #scale the uvs to sheet and move:
        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x *= scale
                loop[uv_layer].uv.y *= scale
                #move
                loop[uv_layer].uv.y += atlas[trimindex].ymin
                
        #map to bounds:
        #first, get current bounds:
        bmin = 0
        bmax = 0
        for face in faces:
            for loop in face.loops:
                if loop[uv_layer].uv.x > bmax:
                    bmax = loop[uv_layer].uv.x
        
        #shift randomly
        random_shift = random.random()
        if context.scene.duv_uvtrim_randomshift == True:
            for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x += random_shift
        
        #else now scale to bounds:
        elif context.scene.duv_uvtrim_bounds == True:
            for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x /= bmax
                    loop[uv_layer].uv.x *= (context.scene.duv_uvtrim_max - context.scene.duv_uvtrim_min)
                    loop[uv_layer].uv.x += context.scene.duv_uvtrim_min
        
    if atlas[0].ymin <= 0.01 and atlas[0].ymax >= 0.99:
        scale = (atlas[trimindex].xmax-atlas[trimindex].xmin)
        #scale the uvs to sheet and move:
        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x *= scale
                loop[uv_layer].uv.y *= scale
                #move
                loop[uv_layer].uv.x += atlas[trimindex].xmin
                
        #map to bounds:
        #first, get current bounds:
        bmin = 0
        bmax = 0
        for face in faces:
            for loop in face.loops:
                if loop[uv_layer].uv.y > bmax:
                    bmax = loop[uv_layer].uv.y
        
        #shift randomly
        random_shift = random.random()
        if context.scene.duv_uvtrim_randomshift == True:
            for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.y += random_shift
        
        #else now scale to bounds:
        elif context.scene.duv_uvtrim_bounds == True:
            for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.y /= bmax
                    loop[uv_layer].uv.y *= (context.scene.duv_uvtrim_max - context.scene.duv_uvtrim_min)
                    loop[uv_layer].uv.y += context.scene.duv_uvtrim_min

    #deselect
    for face in faces:
        face.select = False
    #reselect original selected faces
    for face in selected_faces:
        face.select = True
    
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')


class DREAMUV_OT_uv_trimnext(bpy.types.Operator):
    """Switch selected trim to next one on the atlas sheet"""
    bl_idname = "view3d.dreamuv_uvtrimnext"
    bl_label = "TrimNext"
    bl_options = {"UNDO"}

    reverse : bpy.props.BoolProperty()
    trimswitched = False
    
    def execute(self, context):
        
        
        #remember selected uv
        uv_index = bpy.context.view_layer.objects.active.data.uv_layers.active_index
        if context.scene.duv_trimcap_uv1 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 0
            uv_trimnext(self, context)
            self.trimswitched = True
        if context.scene.duv_trimcap_uv2 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 1
            uv_trimnext(self, context)
        if context.scene.duv_trimcap_uv1 == False and context.scene.duv_trimcap_uv2 == False:
            #just uv selected uv
            uv_trimnext(self, context)
        #reset selected uv
        bpy.context.view_layer.objects.active.data.uv_layers.active_index = uv_index

        return {'FINISHED'}

def uv_capnext(self, context): 
    atlas = read_trim_atlas(context, "cap")
    trimindex = int(context.scene.cap_index)
    
    if self.trimswitched == False:
        if self.reverse == False:
            context.scene.cap_index += 1
            if context.scene.cap_index > ( len(atlas) - 1 ):
                context.scene.cap_index = 0
        if self.reverse == True:
            context.scene.cap_index -= 1
            if context.scene.cap_index < 0:
                context.scene.cap_index = len(atlas) - 1

        trimindex = int(context.scene.cap_index)
    
    if bpy.context.object.mode == 'OBJECT':
        return {'FINISHED'}
    
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    
    selected_faces = list()
    for face in bm.faces:
        if face.select:
            selected_faces.append(face)


    if len(selected_faces) == 0:
        return {'FINISHED'}

    #select linked uvs
    bpy.ops.mesh.select_linked(delimit={'UV'})

    faces = list()
    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            faces.append(face)

    xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
    ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y

    for face in faces: 
        for vert in face.loops:
            xmin = min(xmin, vert[uv_layer].uv.x)
            xmax = max(xmax, vert[uv_layer].uv.x)
            ymin = min(ymin, vert[uv_layer].uv.y)
            ymax = max(ymax, vert[uv_layer].uv.y)

    

    width = xmax - xmin
    height = ymax - ymin
    

    #FIT TO 0-1 range

    #prevent divide by 0:
    if (xmax - xmin) == 0:
        xmin = .1
    if (ymax - ymin) == 0:
        ymin = .1

    for face in faces:
        for loop in face.loops:
            loop[uv_layer].uv.x -= xmin
            loop[uv_layer].uv.y -= ymin
            loop[uv_layer].uv.x /= width
            loop[uv_layer].uv.y /= height

    

    xscale = (atlas[trimindex].xmax-atlas[trimindex].xmin)
    yscale = (atlas[trimindex].ymax-atlas[trimindex].ymin)
    
    
    #scale the uvs to sheet and move:
    for face in faces:
        for loop in face.loops:
            loop[uv_layer].uv.x *= xscale
            loop[uv_layer].uv.y *= yscale
            #move
            loop[uv_layer].uv.x += atlas[trimindex].xmin
            loop[uv_layer].uv.y += atlas[trimindex].ymin

       
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

class DREAMUV_OT_uv_capnext(bpy.types.Operator):
    """Switch selected cap to next one on the atlas sheet"""
    bl_idname = "view3d.dreamuv_uvcapnext"
    bl_label = "CapNext"
    bl_options = {"UNDO"}

    reverse : bpy.props.BoolProperty()
    trimswitched = False
    
    def execute(self, context):
    
    
        #remember selected uv
        uv_index = bpy.context.view_layer.objects.active.data.uv_layers.active_index
        if context.scene.duv_trimcap_uv1 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 0
            uv_capnext(self, context)
            self.trimswitched = True
        if context.scene.duv_trimcap_uv2 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 1
            uv_capnext(self, context)
        if context.scene.duv_trimcap_uv1 == False and context.scene.duv_trimcap_uv2 == False:
            #just uv selected uv
            uv_capnext(self, context)
        #reset selected uv
        bpy.context.view_layer.objects.active.data.uv_layers.active_index = uv_index
        

        return {'FINISHED'}


class trim:
    xmin = float()
    ymin = float()
    xmax = float()
    ymax = float()
    #rect = list()
    horizontal = bool()

    