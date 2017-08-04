import bpy
import bmesh
import math
import mathutils


class UVTranslate(bpy.types.Operator):
    """Translate UVs in the 3D Viewport"""
    bl_idname = "brm.uvtranslate"
    bl_label = "BRM UVTranslate"
    bl_options = {"GRAB_CURSOR", "UNDO", "BLOCKING"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None
    bm_orig = None

    shiftreset = False
    delta=0

    xlock=False
    ylock=False

    stateswitch = False
    mousetestx=False
    constrainttest = False

    def invoke(self, context, event):
        self.shiftreset = False
        self.xlock=False
        self.ylock=False
        self.constrainttest = False
        self.stateswitch = False
        self.mousetestx=False

        #object->edit switch seems to "lock" the data. Ugly but hey it works
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y

            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            #save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)
            self.bm_orig = bmesh.new()
            self.bm_orig.from_mesh(self.mesh)

            #have to do this for some reason
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()
            self.bm_orig.faces.ensure_lookup_table()

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

    def modal(self, context, event):
        context.area.header_text_set("BRM UVTranslate: X/Y - contrain along X/Y Axis, MMB drag - alternative axis contrain method, SHIFT - precision mode, CTRL - stepped mode, CTRL + SHIFT - stepped with smaller increments")
        context.area.tag_redraw()

        #setup constraints first
        if event.type == 'X':
            self.stateswitch=True
            self.xlock=False
            self.ylock=True
        if event.type == 'Y':
            self.stateswitch=True
            self.xlock=True
            self.ylock=False

        #test is middle mouse held down
        if event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            self.constrainttest = True
        if event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            self.constrainttest = False

        #test if mouse is in the right quadrant for X or Y movement
        if self.constrainttest:
            mouseangle=math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            mousetestx=False
            if (mouseangle < 0.785 and mouseangle > -0.785) or (mouseangle > 2.355 or mouseangle < -2.355):
               mousetestx=True
            if mousetestx:
                self.xlock=False
                self.ylock=True
            else:
                self.xlock=True
                self.ylock=False
            if mousetestx is not self.mousetestx:
                self.stateswitch=True
                self.mousetestx = not self.mousetestx

        if self.stateswitch:
            self.stateswitch=False
            #reset to start editing from start position
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        vert[self.bm.loops.layers.uv.active].uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv

        if event.type == 'MOUSEMOVE':
            self.delta=((self.first_mouse_x - event.mouse_x),(self.first_mouse_y - event.mouse_y))
            self.delta = mathutils.Vector(self.delta)*0.001

            if event.shift and not event.ctrl:
                self.delta*=.1
                #reset origin position to shift into precision mode
                if not self.shiftreset:
                    self.shiftreset=True
                    self.first_mouse_x = event.mouse_x
                    self.first_mouse_y = event.mouse_y
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                    self.delta=(0,0)
                    self.delta = mathutils.Vector(self.delta)

            else:
                #reset origin position to shift into normal mode
                if self.shiftreset:
                    self.shiftreset=False
                    self.first_mouse_x = event.mouse_x
                    self.first_mouse_y = event.mouse_y
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                    self.delta=(0,0)
                    self.delta = mathutils.Vector(self.delta)

            if event.ctrl and not event.shift:
                self.delta.x=math.floor(self.delta.x*4)/4
                self.delta.y=math.floor(self.delta.y*4)/4
            if event.ctrl and event.shift:
                self.delta.x=math.floor(self.delta.x*16)/16
                self.delta.y=math.floor(self.delta.y*16)/16

            #loop through every selected face and move the uv's using original uv as reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        if not self.xlock:
                            vert[self.bm.loops.layers.uv.active].uv.x = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x + self.delta.x
                        if not self.ylock:
                            vert[self.bm.loops.layers.uv.active].uv.y = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y + self.delta.y

            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()

            #finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set()

            #reset all uvs to reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        vert[self.bm.loops.layers.uv.active].uv = self.bm_orig.faces[i].loops[o][self.bm_orig.loops.layers.uv.active].uv
            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
