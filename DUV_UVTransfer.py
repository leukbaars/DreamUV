import bpy
import bmesh
from bpy.types import Menu
from bpy.props import EnumProperty, BoolProperty

class UVTransfer(bpy.types.Operator):
    """DUV_UVTransfer"""
    bl_idname = "uv.duv_uvtransfer"
    bl_label = "transfer"
    bl_options = {"UNDO"}
    def execute(self, context):  
        
        bpy.ops.uv.select_split()
 
        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        faces = list()

        xmin,xmax,ymin,ymax=0,0,0,0

        first = True
        for i,face in enumerate(bm.faces):
            if face.select:
                for o,vert in enumerate(face.loops):
                    if vert[bm.loops.layers.uv.active].select:
                        if first:
                            xmin=vert[bm.loops.layers.uv.active].uv.x
                            xmax=vert[bm.loops.layers.uv.active].uv.x
                            ymin=vert[bm.loops.layers.uv.active].uv.y
                            ymax=vert[bm.loops.layers.uv.active].uv.y
                            first=False
                        else:
                            if vert[bm.loops.layers.uv.active].uv.x < xmin:
                                xmin=vert[bm.loops.layers.uv.active].uv.x
                            elif vert[bm.loops.layers.uv.active].uv.x > xmax:
                                xmax=vert[bm.loops.layers.uv.active].uv.x
                            if vert[bm.loops.layers.uv.active].uv.y < ymin:
                                ymin=vert[bm.loops.layers.uv.active].uv.y
                            elif vert[bm.loops.layers.uv.active].uv.y > ymax:
                                ymax=vert[bm.loops.layers.uv.active].uv.y


        aspect = (xmax-xmin)/(ymax-ymin)
        aspecttarget = (context.scene.uvtransferxmax-context.scene.uvtransferxmin)/(context.scene.uvtransferymax-context.scene.uvtransferymin)
        print("aspects")
        print(aspect)
        print(aspecttarget)
        

        #move to 0,1

        for i,face in enumerate(bm.faces):
            if face.select:
                for o,vert in enumerate(face.loops):
                    if vert[bm.loops.layers.uv.active].select:
                        vert[bm.loops.layers.uv.active].uv.x -= xmin
                        vert[bm.loops.layers.uv.active].uv.y -= ymin
                        vert[bm.loops.layers.uv.active].uv.x /= (xmax-xmin)
                        vert[bm.loops.layers.uv.active].uv.y /= (ymax-ymin)
                        

        xmin2 = .5
        ymin2 = .5

        xmax2 = 1
        ymax2 = 1

        #move to new rect

        for i,face in enumerate(bm.faces):
            if face.select:
                for o,vert in enumerate(face.loops):
                    if vert[bm.loops.layers.uv.active].select:
                        vert[bm.loops.layers.uv.active].uv.x = (vert[bm.loops.layers.uv.active].uv.x * (context.scene.uvtransferxmax-context.scene.uvtransferxmin)) + context.scene.uvtransferxmin
                        vert[bm.loops.layers.uv.active].uv.y = (vert[bm.loops.layers.uv.active].uv.y * (context.scene.uvtransferymax-context.scene.uvtransferymin)) + context.scene.uvtransferymin

                
        bmesh.update_edit_mesh(obj.data)

        #cycle if needed:
        if (aspect >= 1 and aspecttarget < 1) or (aspect <= 1 and aspecttarget > 1):
            bpy.ops.uv.duv_uvcycle()
        return {'FINISHED'}

class UVTransferGrab(bpy.types.Operator):
    """DUV_UVTransferGrab"""
    bl_idname = "uv.duv_uvtransfergrab"
    bl_label = "transfer"
    bl_options = {"UNDO"}
    def execute(self, context):
        bpy.ops.uv.select_split()
 
        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        faces = list()

        xmin,xmax,ymin,ymax=0,0,0,0

        

        first = True
        for i,face in enumerate(bm.faces):
            if face.select:
                for o,vert in enumerate(face.loops):
                    if vert[bm.loops.layers.uv.active].select:
                        if first:
                            xmin=vert[bm.loops.layers.uv.active].uv.x
                            xmax=vert[bm.loops.layers.uv.active].uv.x
                            ymin=vert[bm.loops.layers.uv.active].uv.y
                            ymax=vert[bm.loops.layers.uv.active].uv.y
                            first=False
                        else:
                            if vert[bm.loops.layers.uv.active].uv.x < xmin:
                                xmin=vert[bm.loops.layers.uv.active].uv.x
                            elif vert[bm.loops.layers.uv.active].uv.x > xmax:
                                xmax=vert[bm.loops.layers.uv.active].uv.x
                            if vert[bm.loops.layers.uv.active].uv.y < ymin:
                                ymin=vert[bm.loops.layers.uv.active].uv.y
                            elif vert[bm.loops.layers.uv.active].uv.y > ymax:
                                ymax=vert[bm.loops.layers.uv.active].uv.y



        context.scene.uvtransferxmax = xmax
        context.scene.uvtransferxmin = xmin
        context.scene.uvtransferymax = ymax
        context.scene.uvtransferymin = ymin

        return {'FINISHED'}

        
