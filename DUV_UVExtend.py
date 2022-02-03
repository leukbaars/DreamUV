import bpy
import bmesh
import math
from mathutils import Vector

class DREAMUV_OT_uv_extend(bpy.types.Operator):
    """Extend UVs on selected faces from active face"""
    bl_idname = "view3d.dreamuv_uvextend"
    bl_label = "3D View UV Extend"
    bl_options = {"UNDO"}

    def execute(self, context):  
        mesh = bpy.context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active #active uv layer!

        facecounter = 0

        face0=[]
        face1=[]

        #count to make sure only 2 faces selected
        for f in bm.faces:
            if f.select:
                facecounter += 1
        if facecounter < 2:
            self.report({'INFO'}, "only one face selected, aborting")
            return {'FINISHED'}
        

        #save active face!
        for l in bm.faces.active.loops:
            face1.append(l)

        #save other face
        for f in bm.faces:
            if f.select:
                if f is not bm.faces.active:
                    for l in f.loops:
                        face0.append(l)
                else:
                    f.select=False

        bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)


        #find first 2 shared vertices

        vert1 = None    
        vert1uv0 = None
        vert1uv1 = None
        vert2 = None
        vert2uv0 = None
        vert2uv1 = None

        for l in face0:
            for l2 in face1:
                if l.vert.index == l2.vert.index and vert1 == None:
                    vert1 = l.vert.index
                    vert1uv0 = l[uv_layer].uv
                    vert1uv1 = l2[uv_layer].uv
        for l in face0:
            for l2 in face1:
                if l.vert.index is not vert1:            
                    if l.vert.index == l2.vert.index and vert2 == None:
                        vert2 = l.vert.index
                        vert2uv0 = l[uv_layer].uv
                        vert2uv1 = l2[uv_layer].uv

        if vert1 is None or vert2 is None:
            self.report({'INFO'}, "no shared edge found, aborting")
            return {'FINISHED'}

        #calculate angle
        TWOPI = 6.2831853071795865
        RAD2DEG = 57.2957795130823209
        a1,a2 = vert1uv0.x,vert1uv0.y
        b1,b2 = vert2uv0.x,vert2uv0.y
        theta = math.atan2(b1 - a1, a2 - b2)-(TWOPI/4)
        if theta < 0.0:
            theta += TWOPI
        angle1 = theta

        a1,a2 = vert1uv1.x,vert1uv1.y
        b1,b2 = vert2uv1.x,vert2uv1.y
        theta = math.atan2(b1 - a1, a2 - b2)-(TWOPI/4)
        if theta < 0.0:
            theta += TWOPI
        angle2 = theta

        angle=angle2-angle1
        if angle < 0.0:
            angle += TWOPI

        #move face0 to face1
        xdist = vert1uv0.x - vert1uv1.x 
        ydist = vert1uv0.y - vert1uv1.y

        for l in face0:
            l[uv_layer].uv.x -= xdist
            l[uv_layer].uv.y -= ydist

        #rotate face0
        for l in face0:
            px = l[uv_layer].uv.x
            py = l[uv_layer].uv.y
            l[uv_layer].uv.x = math.cos(angle) * (px- vert1uv0.x) - math.sin(angle) * (py- vert1uv0.y) + vert1uv0.x
            l[uv_layer].uv.y = math.sin(angle) * (px - vert1uv0.x) + math.cos(angle) * (py- vert1uv0.y) + vert1uv0.y

        #find scale
        p1 = (vert2uv0.x+vert2uv0.y)-(vert1uv0.x+vert1uv0.y)
        p2 = (vert2uv1.x+vert2uv1.y)-(vert1uv0.x+vert1uv0.y)

        if p1 == 0.0:
            p1=0.01
        scaledelta = p2/p1


        ox=vert1uv0.x
        oy=vert1uv0.y

        #scale face0
        for l in face0:    
            l[uv_layer].uv.x -= ox
            l[uv_layer].uv.y -= oy
            l[uv_layer].uv.x *= scaledelta
            l[uv_layer].uv.y *= scaledelta
            l[uv_layer].uv.x += ox
            l[uv_layer].uv.y += oy
            
        #bm.to_mesh(me)           
        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)

        return {'FINISHED'}