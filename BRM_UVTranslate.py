import bpy
import bmesh
import math
import sys
from mathutils import Vector
from . import BRM_Utils


class UVTranslate(bpy.types.Operator):
    """Translate UVs in the 3D Viewport"""
    bl_idname = "uv.brm_uvtranslate"
    bl_label = "BRM UVTranslate"
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

    face_axis = None
    uv_axis_default = None

    def invoke(self, context, event):

        if context.object is None:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

        self.shiftreset = False
        self.xlock = False
        self.ylock = False
        self.constrainttest = False
        self.stateswitch = False
        self.mousetestx = False

        self.pixel_steps = None
        self.do_pixel_snap = False

        self.face_axis = None

        # object->edit switch seems to "lock" the data. Ugly but hey it works
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        print("UV Translate")

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

        # Get reference to addon preference to get snap setting
        module_name = __name__.split('.')[0]
        addon_prefs = context.user_preferences.addons[module_name].preferences
        self.do_pixel_snap = addon_prefs.pixel_snap

        # Precalculate data before going into modal
        self.pixel_steps = {}
        self.uv_axis_default = (
            Vector((1.0, 0.0)),
            Vector((0.0, 1.0))
        )

        # Won't translate if didn't pass any selected faces
        will_translate = False

        # Variables for calculating UV axis
        world_matrix = context.object.matrix_world
        rv3d = context.region_data
        view_up_vector = rv3d.view_rotation * Vector((0.0, 1.0, 0.0))
        view_right_vector = rv3d.view_rotation * Vector((1.0, 0.0, 0.0))
        face_view_dot_max = sys.float_info.min
        face_view_dist = sys.float_info.max
        uv_layer = self.bm.loops.layers.uv.active
        for i, face in enumerate(self.bm.faces):
            # Don't process unselected faces
            if face.select is False:
                continue
            will_translate = True
            # Find pixel steps per face to look up for pixel snap.
            # Doing this per face in case faces have different textures applied
            if self.do_pixel_snap:
                pixel_step = BRM_Utils.get_face_pixel_step(context, face)
                if pixel_step is not None:
                    self.pixel_steps[face.index] = pixel_step

            # Find the UV directions for this face in relation to viewport
            face_axis = BRM_Utils.get_face_uv_axis(
                                        face, uv_layer, world_matrix,
                                        view_up_vector, view_right_vector
                                    )
            # Able to find UV directions for this face...
            if face_axis is not None:
                face_uv_axis = face_axis[0:2]

                # Find the face closest to view direction
                normalized_dot = face_axis[2]
                face_pos = world_matrix * face.calc_center_bounds()
                dist_to_view = (face_pos - Vector(rv3d.view_location)).magnitude
                if normalized_dot > face_view_dot_max and dist_to_view < face_view_dist:
                    face_view_dot_max = normalized_dot
                    face_view_dist = dist_to_view
                    # Make this face UV axis the default
                    self.uv_axis_default = face_uv_axis

        # No faces selected while looping
        if will_translate is False:
            self.report({'WARNING'}, "No selected faces to transform")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.header_text_set(
            "BRM UVTranslate: X/Y - contrain along X/Y Axis, MMB drag - alternative axis contrain method, SHIFT - precision mode, CTRL - stepped mode, CTRL + SHIFT - stepped with smaller increments")
        context.area.tag_redraw()

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
                self.delta.x = math.floor(self.delta.x * 4) / 4
                self.delta.y = math.floor(self.delta.y * 4) / 4
            if event.ctrl and event.shift:
                self.delta.x = math.floor(self.delta.x * 16) / 16
                self.delta.y = math.floor(self.delta.y * 16) / 16

            # loop through every selected face and move the uv's using original uv as reference
            for i, face in enumerate(self.bm.faces):
                if face.select is False:
                    continue

                local_delta = self.delta.copy()
                if self.do_pixel_snap and face.index in self.pixel_steps.keys():
                    pixel_step = self.pixel_steps[face.index]
                    local_delta.x *= pixel_step.x
                    local_delta.y *= pixel_step.y

                uv_x_axis = self.uv_axis_default[0]
                uv_y_axis = self.uv_axis_default[1]

                if self.xlock:
                    uv_x_axis = Vector((0, 0))
                if self.ylock:
                    uv_y_axis = Vector((0, 0))

                for o, vert in enumerate(face.loops):
                    origin_uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv
                    uv_offset = local_delta.x * uv_x_axis + local_delta.y * uv_y_axis
                    vert[self.bm.loops.layers.uv.active].uv = origin_uv + uv_offset

            # update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()

            # finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set()

            # reset all uvs to reference
            for i, face in enumerate(self.bm.faces):
                if face.select:
                    for o, vert in enumerate(face.loops):
                        reset_uv = self.bm_orig.faces[i].loops[o][self.bm_orig.loops.layers.uv.active].uv
                        vert[self.bm.loops.layers.uv.active].uv = reset_uv
            # update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
