import bpy
import bmesh
from math import degrees
from math import radians
from mathutils import Vector
from . import DUV_Utils


def main(context):
    
    #Check if a box object exists
    if context.scene.uv_box is None:
        self.report({'WARNING'}, "No valid box reference assigned!")
        return {'FINISHED'}

    #make sure active object is actually selected in edit mode:
    if bpy.context.object.mode == 'EDIT':
        bpy.context.object.select_set(True)
    
        
    #check for object or edit mode:
    objectmode = False
    if bpy.context.object.mode == 'OBJECT':
        objectmode = True
        print("switch to edit mode")
        #switch to edit and select all
        bpy.ops.object.editmode_toggle() 
        bpy.ops.mesh.select_all(action='SELECT')



    obj = context.scene.uv_box
        
    mat = obj.matrix_world

    startloc = mat @ obj.bound_box.data.data.vertices[0].co

    xmin = startloc.x
    xmax = startloc.x
    ymin = startloc.y
    ymax = startloc.y
    zmin = startloc.z
    zmax = startloc.z

    for v in obj.bound_box.data.data.vertices:

        loc = mat @ v.co
        
        if loc.x < xmin:
            xmin=loc.x
        elif loc.x >= xmax:
            xmax=loc.x
            
        if loc.y < ymin:
            ymin=loc.y
        elif loc.y >= ymax:
            ymax=loc.y
            
        if loc.z < zmin:
            zmin=loc.z
        elif loc.z >= zmax:
            zmax=loc.z
            
    up = Vector((0, 0, 1)) #  -z axis.
    right = Vector((1, 0, 0)) #  -x axis.
    front = Vector((0, 1, 0)) #  -y axis.
    test_angle = radians(89) 
                    
                    
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    #uv_layer = bm.loops.layers.uv[0]
    uv_layer = bm.loops.layers.uv.verify()
    mat = obj.matrix_world         
                        
    for f in bm.faces:
        if f.select:

            #print(degrees(f.normal.angle(up)))
            
            m = obj.matrix_world.to_quaternion().to_matrix()
            
            f_world_normal = m @ f.normal
     
            #gather up, front and right angles
            
            upangle = degrees(f_world_normal.angle(up))
            if upangle > 90:
                upangle = 180 - upangle
            rightangle = degrees(f_world_normal.angle(right))
            if rightangle > 90:
                rightangle = 180 - rightangle
            frontangle = degrees(f_world_normal.angle(front))
            if frontangle > 90:
                frontangle = 180 - frontangle
            
            #pick smallest angle
            
            if upangle <= rightangle and upangle <= frontangle:
                for loop in f.loops:
                    vco = loop.vert.co        
                    # Multiply matrix by vertex (see also: https://developer.blender.org/T56276)
                    loc = mat @ vco
                    loop[uv_layer].uv.x = loc.x
                    loop[uv_layer].uv.y = loc.y
                    loop[uv_layer].uv.x -= xmin
                    loop[uv_layer].uv.y -= ymin
                    loop[uv_layer].uv.x /= (xmax-xmin)
                    loop[uv_layer].uv.y /= (ymax-ymin)
            
            elif rightangle <= upangle and rightangle <= frontangle:
                for loop in f.loops:
                    vco = loop.vert.co        
                    # Multiply matrix by vertex (see also: https://developer.blender.org/T56276)
                    loc = mat @ vco
                    loop[uv_layer].uv.x = loc.y
                    loop[uv_layer].uv.y = loc.z
                    loop[uv_layer].uv.x -= ymin
                    loop[uv_layer].uv.y -= zmin
                    loop[uv_layer].uv.x /= (ymax-ymin)
                    loop[uv_layer].uv.y /= (zmax-zmin)

            elif frontangle <= upangle and frontangle <= rightangle:
                for loop in f.loops:
                    vco = loop.vert.co        
                    # Multiply matrix by vertex (see also: https://developer.blender.org/T56276)
                    loc = mat @ vco
                    loop[uv_layer].uv.x = loc.x
                    loop[uv_layer].uv.y = loc.z
                    loop[uv_layer].uv.x -= xmin
                    loop[uv_layer].uv.y -= zmin
                    loop[uv_layer].uv.x /= (xmax-xmin)
                    loop[uv_layer].uv.y /= (zmax-zmin)
            
            #backup uv just in case
            else:
                for loop in f.loops:
                    vco = loop.vert.co        
                    # Multiply matrix by vertex (see also: https://developer.blender.org/T56276)
                    loc = mat @ vco
                    loop[uv_layer].uv.x = loc.x
                    loop[uv_layer].uv.y = loc.z
                    loop[uv_layer].uv.x -= xmin
                    loop[uv_layer].uv.y -= zmin
                    loop[uv_layer].uv.x /= (xmax-xmin)
                    loop[uv_layer].uv.y /= (zmax-zmin)


    bmesh.update_edit_mesh(obj.data)
    
    if objectmode is True:
        print("switch to object mode")
        bpy.ops.object.editmode_toggle() 

class DREAMUV_OT_uv_boxmap(bpy.types.Operator):
    """Unwrap using a box shape"""
    bl_idname = "view3d.dreamuv_uvboxmap"
    bl_label = "box map"
    
    def execute(self, context):
        #remember selected uv
        uv_index = bpy.context.view_layer.objects.active.data.uv_layers.active_index
        if context.scene.duv_boxmap_uv1 == True:
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 0
            main(context)
        if context.scene.duv_boxmap_uv2 == True:    
            bpy.context.view_layer.objects.active.data.uv_layers.active_index = 1
            main(context)
        if context.scene.duv_boxmap_uv1 == False and context.scene.duv_boxmap_uv2 == False:
            #just uv selected uv
            main(context)
        #reset selected uv
        bpy.context.view_layer.objects.active.data.uv_layers.active_index = uv_index

        return {'FINISHED'}