import bpy
import bmesh
import math


class UVRotate(bpy.types.Operator):
    """Rotate UVs in the 3D Viewport"""
    bl_idname = "brm.uvrotate"
    bl_label = "BRM UVRotate"
    bl_options = {"GRAB_CURSOR", "UNDO", "BLOCKING"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None

    xcenter=0
    ycenter=0

    startdelta=0

    def invoke(self, context, event):

        #object->edit switch seems to "lock" the data. Ugly but hey it works
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        if context.object:
            #self.first_mouse_x = event.mouse_x
            #self.first_mouse_y = event.mouse_y

            #test: set rotation center to viewport center for now
            #test: possibly change this to selection center?
            self.first_mouse_x = (bpy.context.region.width/2)+bpy.context.region.x
            self.first_mouse_y = (bpy.context.region.height/2)+bpy.context.region.y

            #get neutral angle from start location
            self.startdelta=math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)

            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            #save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)

            #have to do this for some reason
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()

            #find "center"
            xmin=0
            xmax=0
            ymin=0
            ymax=0
            first = True
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        if first:
                            xmin=vert[self.bm.loops.layers.uv.active].uv.x
                            xmax=vert[self.bm.loops.layers.uv.active].uv.x
                            ymin=vert[self.bm.loops.layers.uv.active].uv.y
                            ymax=vert[self.bm.loops.layers.uv.active].uv.y
                            first=False
                        else:
                            if vert[self.bm.loops.layers.uv.active].uv.x < xmin:
                                xmin=vert[self.bm.loops.layers.uv.active].uv.x
                            elif vert[self.bm.loops.layers.uv.active].uv.x > xmax:
                                xmax=vert[self.bm.loops.layers.uv.active].uv.x

                            if vert[self.bm.loops.layers.uv.active].uv.y < ymin:
                                ymin=vert[self.bm.loops.layers.uv.active].uv.y
                            elif vert[self.bm.loops.layers.uv.active].uv.y > ymax:
                                ymax=vert[self.bm.loops.layers.uv.active].uv.y

            self.xcenter=(xmin+xmax)/2
            self.ycenter=(ymin+ymax)/2

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

    def modal(self, context, event):
        context.area.header_text_set("BRM UVRotate: CTRL - stepped mode")
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':

            #get angle of cursor from start pos in radians
            delta = -math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            #neutralize angle for mouse start position
            delta+=self.startdelta

            print(event.mouse_x)
            vcenterx = (bpy.context.region.width/2)+bpy.context.region.x
            print(vcenterx)
            #step rotation
            if event.ctrl and not event.shift:
                #PI/4=0.78539816339
                PIdiv=0.78539816339
                delta=math.floor(delta/PIdiv)*PIdiv
            if event.ctrl and event.shift:
                #PI/16=0.19634954084
                PIdiv=0.19634954084
                delta=math.floor(delta/PIdiv)*PIdiv

            #loop through every selected face and scale the uv's using original uv as reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):

                        px=self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x
                        py=self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y

                        vert[self.bm.loops.layers.uv.active].uv.x = math.cos(delta) * (px-self.xcenter) - math.sin(delta) * (py-self.ycenter) + self.xcenter
                        vert[self.bm.loops.layers.uv.active].uv.y = math.sin(delta) * (px-self.xcenter) +  math.cos(delta) * (py-self.ycenter) + self.ycenter

            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()

            #finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
