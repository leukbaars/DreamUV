import bpy
import bmesh
import math
from mathutils import Vector
from . import DUV_Utils


class DREAMUV_OT_uv_translate(bpy.types.Operator):
    """Translate UVs in the 3D Viewport"""
    bl_idname = "view3d.dreamuv_uvtranslate"
    bl_label = "UV Translate"
    bl_options = {"GRAB_CURSOR", "UNDO", "BLOCKING"}

    first_mouse_x = None
    first_mouse_y = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None
    bm_orig = None

    shiftreset = False
    delta = 0

    xlock = False
    ylock = False

    stateswitch = False
    mousetestx = False
    constrainttest = False

    pixel_steps = None
    do_pixel_snap = False

    move_snap = 4

    def invoke(self, context, event):

        self.shiftreset = False
        self.xlock = False
        self.ylock = False
        self.constrainttest = False
        self.stateswitch = False
        self.mousetestx = False

        self.pixel_steps = None
        self.do_pixel_snap = False

        self.move_snap = 0.25

        # object->edit switch seems to "lock" the data. Ugly but hey it works
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y

            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            # save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)
            self.bm_orig = bmesh.new()
            self.bm_orig.from_mesh(self.mesh)

            # have to do this for some reason
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()
            self.bm_orig.faces.ensure_lookup_table()

            # Get refrerence to addon preference to get snap and scale setting
            module_name = __name__.split('.')[0]
            addon_prefs = bpy.context.preferences.addons[module_name].preferences
            self.do_pixel_snap = addon_prefs.pixel_snap
            self.move_snap = addon_prefs.move_snap
            self.move_snap = 1/self.move_snap

            print(self.move_snap)
            # Precalculate data before going into modal
            self.pixel_steps = {}
            for i, face in enumerate(self.bm.faces):
                if face.select is False:
                    continue
                # Find pixel steps per face here to look up in future translations
                if self.do_pixel_snap:
                    pixel_step = DUV_Utils.get_face_pixel_step(context, face)
                    if pixel_step is not None:
                        self.pixel_steps[face.index] = pixel_step

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

    def modal(self, context, event):
        #context.area.header_text_set(
        #    "DUV UVTranslate: X/Y - contrain along X/Y Axis, MMB drag - alternative axis contrain method, SHIFT - precision mode, CTRL - stepped mode, CTRL + SHIFT - stepped with smaller increments")
        #context.area.tag_redraw()

        # setup constraints first
        if event.type == 'X':
            self.stateswitch = True
            self.xlock = False
            self.ylock = True
        if event.type == 'Y':
            self.stateswitch = True
            self.xlock = True
            self.ylock = False

        # test is middle mouse held down
        if event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            self.constrainttest = True
        if event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            self.constrainttest = False

        # test if mouse is in the right quadrant for X or Y movement
        if self.constrainttest:
            mouseangle = math.atan2(event.mouse_y - self.first_mouse_y, event.mouse_x - self.first_mouse_x)
            mousetestx = False
            if (mouseangle < 0.785 and mouseangle > -0.785) or (mouseangle > 2.355 or mouseangle < -2.355):
                mousetestx = True
            if mousetestx:
                self.xlock = False
                self.ylock = True
            else:
                self.xlock = True
                self.ylock = False
            if mousetestx is not self.mousetestx:
                self.stateswitch = True
                self.mousetestx = not self.mousetestx

        if self.stateswitch:
            self.stateswitch = False
            # reset to start editing from start position
            for i, face in enumerate(self.bm.faces):
                if face.select:
                    for o, vert in enumerate(face.loops):
                        reset_uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv
                        vert[self.bm.loops.layers.uv.active].uv = reset_uv

        if event.type == 'MOUSEMOVE':
            self.delta = (
                (self.first_mouse_x - event.mouse_x),
                (self.first_mouse_y - event.mouse_y)
            )

            sensitivity = 0.001 if not self.do_pixel_snap else 0.1

            self.delta = Vector(self.delta) * sensitivity

            if self.do_pixel_snap:
                self.delta.x = int(round(self.delta.x))
                self.delta.y = int(round(self.delta.y))

            if event.shift and not event.ctrl:
                self.delta *= .1
                # reset origin position to shift into precision mode
                if not self.shiftreset:
                    self.shiftreset = True
                    self.first_mouse_x = event.mouse_x
                    self.first_mouse_y = event.mouse_y
                    for i, face in enumerate(self.bm.faces):
                        if face.select:
                            for o, vert in enumerate(face.loops):
                                reset_uv = vert[self.bm.loops.layers.uv.active].uv
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = reset_uv
                    self.delta = (0, 0)
                    self.delta = Vector(self.delta)

            else:
                # reset origin position to shift into normal mode
                if self.shiftreset:
                    self.shiftreset = False
                    self.first_mouse_x = event.mouse_x
                    self.first_mouse_y = event.mouse_y
                    for i, face in enumerate(self.bm.faces):
                        if face.select:
                            for o, vert in enumerate(face.loops):
                                reset_uv = vert[self.bm.loops.layers.uv.active].uv
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = reset_uv
                    self.delta = (0, 0)
                    self.delta = Vector(self.delta)

            if event.ctrl and not event.shift:
                self.delta.x = math.floor(self.delta.x * self.move_snap) / self.move_snap
                self.delta.y = math.floor(self.delta.y * self.move_snap) / self.move_snap
            if event.ctrl and event.shift:
                self.delta.x = math.floor(self.delta.x * (self.move_snap*self.move_snap)) / (self.move_snap*self.move_snap)
                self.delta.y = math.floor(self.delta.y * (self.move_snap*self.move_snap)) / (self.move_snap*self.move_snap)

            # loop through every selected face and move the uv's using original uv as reference
            for i, face in enumerate(self.bm.faces):
                if face.select is False:
                    continue

                local_delta = self.delta.copy()
                if self.do_pixel_snap and face.index in self.pixel_steps.keys():
                    pixel_step = self.pixel_steps[face.index]
                    local_delta.x *= pixel_step.x
                    local_delta.y *= pixel_step.y

                uv_x_axis = Vector((1.0, 0.0))
                uv_y_axis = Vector((0.0, 1.0))

                if self.xlock:
                    uv_x_axis = Vector((0, 0))
                if self.ylock:
                    uv_y_axis = Vector((0, 0))

                for o, vert in enumerate(face.loops):
                    origin_uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv
                    uv_offset = local_delta.x * uv_x_axis + local_delta.y * uv_y_axis
                    vert[self.bm.loops.layers.uv.active].uv = origin_uv + uv_offset

            # update mesh
            bmesh.update_edit_mesh(self.mesh, loop_triangles=False, destructive=False)

        elif event.type == 'LEFTMOUSE':
            # finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            
            # reset all uvs to reference
            for i, face in enumerate(self.bm.faces):
                if face.select:
                    for o, vert in enumerate(face.loops):
                        reset_uv = self.bm_orig.faces[i].loops[o][self.bm_orig.loops.layers.uv.active].uv
                        vert[self.bm.loops.layers.uv.active].uv = reset_uv
            # update mesh
            bmesh.update_edit_mesh(self.mesh, loop_triangles=False, destructive=False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

class DREAMUV_OT_uv_translate_step(bpy.types.Operator):
    """Move UVs using snap size"""
    bl_idname = "view3d.dreamuv_uvtranslatestep"
    bl_label = "UV Translate Step"
    bl_options = {"UNDO"}

    direction : bpy.props.StringProperty()

    def execute(self, context): 
        mesh = bpy.context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.active

        module_name = __name__.split('.')[0]
        addon_prefs = bpy.context.preferences.addons[module_name].preferences
        move_snap = addon_prefs.move_snap

        xmove = 0
        ymove = 0

        if self.direction == "left":
            xmove = move_snap
        if self.direction == "right":
            xmove = -move_snap
        if self.direction == "up":
            ymove = -move_snap
        if self.direction == "down":
            ymove =  move_snap
        
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop[uv_layer].uv.x += xmove
                    loop[uv_layer].uv.y += ymove

        #update mesh
        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)



        return {'FINISHED'}