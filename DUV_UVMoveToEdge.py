import bpy
import math
import bmesh
from mathutils import Vector

class DREAMUV_OT_uv_move_to_edge(bpy.types.Operator):
    """Move Selected faces to edge of texture"""
    bl_idname = "view3d.dreamuv_uvmovetoedge"
    bl_label = "3D View UV Move to UV Edge"
    bl_options = {"UNDO"}

    direction : bpy.props.StringProperty()

    def execute(self, context):

        mesh = bpy.context.object.data
        mesh = bpy.context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        bpy.ops.uv.select_all(action='SELECT')

        xmin,xmax,ymin,ymax=0,0,0,0

        first = True
        for face in bm.faces:
            if face.select:
                for l in face.loops:
                    if l[bm.loops.layers.uv.active].select:
                        if first:
                            xmin = l[bm.loops.layers.uv.active].uv.x
                            xmax = l[bm.loops.layers.uv.active].uv.x
                            ymin = l[bm.loops.layers.uv.active].uv.y
                            ymax = l[bm.loops.layers.uv.active].uv.y
                            first=False
                        else:
                            if l[bm.loops.layers.uv.active].uv.x < xmin:
                                xmin = l[bm.loops.layers.uv.active].uv.x
                            elif l[bm.loops.layers.uv.active].uv.x > xmax:
                                xmax = l[bm.loops.layers.uv.active].uv.x
                            if l[bm.loops.layers.uv.active].uv.y < ymin:
                                ymin = l[bm.loops.layers.uv.active].uv.y
                            elif l[bm.loops.layers.uv.active].uv.y > ymax:
                                ymax = l[bm.loops.layers.uv.active].uv.y
                                
        xdist = 0
        ydist = 0

        if self.direction == "up":
            ydist = 1-ymax
        if self.direction == "down":
            ydist = -ymin
        if self.direction == "right":
            xdist = 1-xmax
        if self.direction == "left":
            xdist = -xmin


        for face in bm.faces:
                if face.select:
                    for l in face.loops:
                        if l[bm.loops.layers.uv.active].select:
                            l[bm.loops.layers.uv.active].uv.x += xdist
                            l[bm.loops.layers.uv.active].uv.y += ydist

        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
        return {'FINISHED'}