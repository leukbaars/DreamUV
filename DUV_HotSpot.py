import bpy
import bmesh
import math
import random
from mathutils import Vector
from . import DUV_Utils


class DREAMUV_OT_hotspotter(bpy.types.Operator):
    """Unwrap selection using the atlas object as a guide"""
    bl_idname = "view3d.dreamuv_hotspotter"
    bl_label = "HotSpot"
    bl_options = {"UNDO"}

    def execute(self, context):
        #Check if an atlas object exists
        if context.scene.subrect_atlas is None:
            self.report({'WARNING'}, "No valid atlas selected!")
            return {'FINISHED'}

        #make sure active object is actually selected in edit mode:
        if bpy.context.object.mode == 'EDIT':
            bpy.context.object.select_set(True)
        
            
        #check for object or edit mode:
        objectmode = False
        if bpy.context.object.mode == 'OBJECT':
            objectmode = True
            #switch to edit and select all
            bpy.ops.object.editmode_toggle() 
            bpy.ops.mesh.select_all(action='SELECT')

        #check if uv sync selection is used and turn off if so
        uvsync = False
        if bpy.context.scene.tool_settings.use_uv_select_sync == True:
            uvsync = True
            bpy.context.scene.tool_settings.use_uv_select_sync = False


        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)

        #ADD MATERIAL
        if context.scene.duv_hotspotmaterial is not None:
            matindex = 0
            doesmatexist = False
            for m in obj.data.materials:
                if m == context.scene.duv_hotspotmaterial:
                    doesmatexist = True
                    break
                matindex += 1
            if doesmatexist is False:
                obj.data.materials.append(context.scene.duv_hotspotmaterial)
            for face in bm.faces:
                if face.select: 
                    face.material_index = matindex
        bmesh.update_edit_mesh(obj.data)

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
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        angle = bpy.context.object.data.auto_smooth_angle
        bpy.ops.mesh.edges_select_sharp(sharpness=angle)
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

        #PREPROCESS - find islands

        #create UV islands using blender unwrap
        bpy.ops.uv.unwrap(method='CONFORMAL', margin=1.0)
        #list islands
        #iterate using select linked uv

        islands = list()        
        tempfaces = list()
        updatedfaces = list()
        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                updatedfaces.append(face)
                tempfaces.append(face)
                face.select = False
               
        while len(tempfaces) > 0:
            updatedfaces[0].select = True
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.mesh.select_linked(delimit={'UV'})

            islandfaces = list()
            for face in bm.faces:
                if face.select:
                    islandfaces.append(face)
            islands.append(islandfaces)

            #create updated list
            tempfaces.clear()
            for face in updatedfaces:
                if face.select == False:
                    tempfaces.append(face)
                else:
                    face.select = False 
            #make new list into updated list
            updatedfaces.clear()
            updatedfaces = tempfaces.copy()

        bpy.ops.uv.select_all(action='SELECT')

        #get atlas
        atlas = DUV_Utils.read_atlas(context)

        #NOW ITERATE!
        for island in islands:
            uv_layer = bm.loops.layers.uv.verify()

            for face in faces:
                face.select = False
            for face in island:
                face.select = True
                        
            HSfaces = list()
            #MAKE FACE LIST
            for face in bm.faces:
                if face.select:
                    HSfaces.append(face)    

            #get original size
            xmin2, xmax2 = HSfaces[0].loops[0][uv_layer].uv.x, HSfaces[0].loops[0][uv_layer].uv.x
            ymin2, ymax2 = HSfaces[0].loops[0][uv_layer].uv.y, HSfaces[0].loops[0][uv_layer].uv.y
            for face in HSfaces: 
                for vert in face.loops:
                    xmin2 = min(xmin2, vert[uv_layer].uv.x)
                    xmax2 = max(xmax2, vert[uv_layer].uv.x)
                    ymin2 = min(ymin2, vert[uv_layer].uv.y)
                    ymax2 = max(ymax2, vert[uv_layer].uv.y)
          
            #try fitting selection to square
            is_rect = DUV_Utils.square_fit(context)
            if is_rect is False:
                
                #return {'FINISHED'}
            
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
                uv_layer = bm.loops.layers.uv.verify()

            #rotate to world angle here:
            DUV_Utils.get_orientation(context)

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

            for face in HSfaces:
                for loop in face.loops:
                    loop[uv_layer].uv.x -= xmin
                    loop[uv_layer].uv.y -= ymin
                    loop[uv_layer].uv.x /= (xmax-xmin)
                    loop[uv_layer].uv.y /= (ymax-ymin)

            edge1 = xmax-xmin
            edge2 = ymax-ymin
            aspect = edge1/edge2
            size = area = sum(f.calc_area() for f in HSfaces if f.select)
            
            if is_rect is False:
                #calulate ratio empty vs full
                sizeratio = DUV_Utils.get_uv_ratio(context)
                #prevent divide by 0:
                if sizeratio == 0:
                    sizeratio = 1.0
                size = size / sizeratio 

            if aspect > 1:
                aspect = round(aspect)
            else:
                aspect = 1/(round(1/aspect))

            #ASPECT LOWER THAN 1.0 = TALL
            #ASPECT HIGHER THAN 1.0 = WIDE

            #find closest aspect ratio in list

            #2 variations depending on tall or wide
            
            index = 0
            templength = abs(atlas[0].posaspect-aspect)
            tempindex = 0

            worldorientation = context.scene.duv_useorientation
            
            if worldorientation:
                for number in atlas:
                        testlength = abs(number.aspect-aspect) 
                        if testlength < templength:
                            templength = testlength
                            tempindex = index
                        index += 1

            if not worldorientation:
                    
                #wide:
                if aspect >= 1.0:
                    for number in atlas:
                        testlength = abs(number.posaspect-aspect) 
                        if testlength < templength:
                            templength = testlength
                            tempindex = index
                        index += 1
                
                #tall:
                if aspect < 1.0:
                    templength = abs((atlas[0].posaspect)-(1/aspect))
                    for number in atlas:
                        testlength = abs((number.posaspect)-(1/aspect)) 
                        if testlength < templength:
                            templength = testlength
                            tempindex = index
                        index += 1

            #NOW MAKE LIST OF ASPECTS!
            flipped = False
            aspectbucket = list()
            for r in atlas:
                if r.aspect == atlas[tempindex].aspect:
                    aspectbucket.append(r)
                if worldorientation is False:
                    if r.aspect == 1/atlas[tempindex].aspect:
                        aspectbucket.append(r)

            #find closest size in bucket:
            index = 0

            templength = abs(aspectbucket[0].size-size)
            tempindex = 0

            validrects = list()
            for a in aspectbucket:
                testlength = abs(a.size-size) 
                if testlength <= templength:
                    templength = testlength
                    tempindex = index
                index += 1
            
            index = 0
            for a in aspectbucket:
                if a.size == aspectbucket[tempindex].size:
                    validrects.append(index)
                index += 1

            tempindex = random.choice(validrects)

            #test if coords are already asigned by comparing minmaxes, then try again

            #2 assign uv
            #get minmax of target rect
            xmin, xmax = aspectbucket[tempindex].uvcoord[0].x, aspectbucket[tempindex].uvcoord[0].x
            ymin, ymax = aspectbucket[tempindex].uvcoord[0].y, aspectbucket[tempindex].uvcoord[0].y

            for vert in aspectbucket[tempindex].uvcoord:
                
                xmin = min(xmin, vert.x)
                xmax = max(xmax, vert.x)
                ymin = min(ymin, vert.y)
                ymax = max(ymax, vert.y)

            #flip if aspect is inverted

            if xmin == xmin2 and ymin == ymin2 and xmax == xmax2 and ymax == ymax2 and len(validrects) > 1:
                #remove current choice
                validrects.remove(tempindex)
                #print(validrects)

                tempindex = random.choice(validrects)

                xmin, xmax = aspectbucket[tempindex].uvcoord[0].x, aspectbucket[tempindex].uvcoord[0].x
                ymin, ymax = aspectbucket[tempindex].uvcoord[0].y, aspectbucket[tempindex].uvcoord[0].y

                for vert in aspectbucket[tempindex].uvcoord:
                    xmin = min(xmin, vert.x)
                    xmax = max(xmax, vert.x)
                    ymin = min(ymin, vert.y)
                    ymax = max(ymax, vert.y)

            #flip U and V if aspect is reversed:
            #WIDE case becomes TALL
            if aspectbucket[tempindex].aspect < 1.0 and aspect >= 1.0:
                for face in HSfaces:
                    for loop in face.loops:
                        newx = loop[uv_layer].uv.y
                        newy = loop[uv_layer].uv.x
                        loop[uv_layer].uv.x = newx
                        loop[uv_layer].uv.y = newy
            
            #TALL case becomes WIDE
            if aspectbucket[tempindex].aspect > 1.0 and aspect < 1.0:
                for face in HSfaces:
                    for loop in face.loops:
                        newx = loop[uv_layer].uv.y
                        newy = loop[uv_layer].uv.x
                        loop[uv_layer].uv.x = newx
                        loop[uv_layer].uv.y = newy

            #check if uv needs to be inset
            if context.scene.duv_hotspotuseinset is True:
                pixel_inset = context.scene.hotspotinsetpixels/context.scene.hotspotinsettexsize
                xmin += pixel_inset
                xmax -= pixel_inset
                ymin += pixel_inset
                ymax -= pixel_inset

            #apply the new UV
            for face in HSfaces:
                for loop in face.loops:
                    loop[uv_layer].uv.x *= xmax-xmin
                    loop[uv_layer].uv.y *= ymax-ymin
                    loop[uv_layer].uv.x += xmin
                    loop[uv_layer].uv.y += ymin

            worldorientation = context.scene.duv_useorientation
            use_mirrorx = context.scene.duv_usemirrorx
            use_mirrory = context.scene.duv_usemirrory

            #MIRRORING:

            if worldorientation is False:
                #flip around square aspects randomly
                if aspect == 1:
                    flips = random.randint(0, 3)
                    for x in range(flips):
                        bpy.ops.view3d.dreamuv_uvcycle()
            
            #and also do randomized mirroring:
            if use_mirrorx is True:
                randomMirrorX = random.randint(0, 1)
                if randomMirrorX == 1:
                    op = bpy.ops.view3d.dreamuv_uvmirror(direction = "x")

            if use_mirrory is True:
                randomMirrorY = random.randint(0, 1)
                if randomMirrorY == 1:
                    op = bpy.ops.view3d.dreamuv_uvmirror(direction = "y")

            #apply material from index
            if context.scene.duv_hotspotmaterial is not None:
                for face in HSfaces:   
                    face.material_index = matindex

        for face in faces:
            face.select = True
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

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
        
        if uvsync == True:
            bpy.ops.object.editmode_toggle()
            bpy.context.scene.tool_settings.use_uv_select_sync = True
            bpy.ops.object.editmode_toggle()
            
        
        if objectmode is False:
            bpy.ops.object.editmode_toggle() 
        
        return {'FINISHED'}
        
        bpy.ops.object.editmode_toggle() 
