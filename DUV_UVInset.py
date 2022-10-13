import bpy
import bmesh
import math


class DREAMUV_OT_uv_inset(bpy.types.Operator):
    """Inset UVs in the 3D Viewport"""
    bl_idname = "view3d.dreamuv_uvinset"
    bl_label = "UV Inset"
    bl_options = {"GRAB_CURSOR", "UNDO", "BLOCKING"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None

    xcenter=0
    ycenter=0

    shiftreset = False

    xlock=False
    ylock=False
    constrainttest = False

    s1=3
    s2=.5

    move_snap = 2

    def invoke(self, context, event):

        #object->edit switch seems to "lock" the data. Ugly but hey it works
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        self.shiftreset = False
        self.xlock=False
        self.ylock=False
        self.constrainttest = False

        self.scale_snap = 2
        module_name = __name__.split('.')[0]
        addon_prefs = bpy.context.preferences.addons[module_name].preferences
        self.scale_snap = addon_prefs.scale_snap

        if context.object:
            self.first_mouse_x = event.mouse_x+1000/self.s1
            self.first_mouse_y = event.mouse_y+1000/self.s1

            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            #save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)

            #have to do this for some reason
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()

            #find "center"
            #loop through every selected face and move the uv's using original uv as reference
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
        
        if event.type == 'X':
            self.xlock=False
            self.ylock=True
        if event.type == 'Y':
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
                self.xlock=True
                self.ylock=False
            else:
                self.xlock=False
                self.ylock=True


        if event.type == 'MOUSEMOVE':

            deltax = self.first_mouse_x - event.mouse_x
            deltay = self.first_mouse_y - event.mouse_y


            if event.shift and not event.ctrl:
                #self.delta*=.1
                #reset origin position to shift into precision mode

                if not self.shiftreset:
                    self.shiftreset=True
                    self.first_mouse_x = event.mouse_x+1000/self.s2
                    self.first_mouse_y = event.mouse_y+1000/self.s2
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                deltax = self.first_mouse_x - event.mouse_x
                deltay = self.first_mouse_y - event.mouse_y
                deltax*=0.001*self.s2
                deltay*=0.001*self.s2

            else:
                #reset origin position to shift into normal mode
                if self.shiftreset:
                    self.shiftreset=False
                    self.first_mouse_x = event.mouse_x+1000/self.s1
                    self.first_mouse_y = event.mouse_y+1000/self.s1
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                deltax = self.first_mouse_x - event.mouse_x
                deltay = self.first_mouse_y - event.mouse_y
                deltax*=0.001*self.s1
                deltay*=0.001*self.s1

            if not self.xlock and not self.ylock:
                delta=(deltax+deltay)*.5
                deltax=delta
                deltay=delta

            if self.xlock:
                deltax=1

            if self.ylock:
                deltay=1

            if event.ctrl and not event.shift:
                deltax=math.floor(deltax*self.scale_snap)/self.scale_snap
                deltay=math.floor(deltay*self.scale_snap)/self.scale_snap
            if event.ctrl and event.shift:
                deltax=math.floor(deltax*self.scale_snap*self.scale_snap)/(self.scale_snap*self.scale_snap)
                deltay=math.floor(deltay*self.scale_snap*self.scale_snap)/(self.scale_snap*self.scale_snap)

            #loop through every selected face and move the uv's using original uv as reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):

                        vert[self.bm.loops.layers.uv.active].uv.x=((deltax)*self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x)+((1-(deltax))*self.xcenter)
                        vert[self.bm.loops.layers.uv.active].uv.y=((deltay)*self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y)+((1-(deltay))*self.ycenter)

            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)

        elif event.type == 'LEFTMOUSE':
            
            #finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            
            #reset all uvs to reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        vert[self.bm.loops.layers.uv.active].uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv
            #update mesh
            bmesh.update_edit_mesh(self.mesh, loop_triangles=False, destructive=False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

class DREAMUV_OT_uv_inset_step(bpy.types.Operator):
    """Inset UVs using pixel size"""
    bl_idname = "view3d.dreamuv_uvinsetstep"
    bl_label = "inset"
    bl_options = {"UNDO"}

    direction : bpy.props.StringProperty()

    def execute(self, context): 
        mesh = bpy.context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.active

        faces = list()
        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                faces.append(face)  

        #get original size
        xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
        ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y
        
        for face in faces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)
        
        print(xmin)
        print(xmax)
        print(ymin)
        print(ymax)

        for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x-= xmin
                    loop[uv_layer].uv.y -= ymin
                    loop[uv_layer].uv.x /= (xmax-xmin)
                    loop[uv_layer].uv.y /= (ymax-ymin)

        pixel_inset = context.scene.uvinsetpixels/context.scene.uvinsettexsize

        if self.direction == "in":
            xmin += pixel_inset
            xmax -= pixel_inset
            ymin += pixel_inset
            ymax -= pixel_inset
        if self.direction == "out":
            xmin -= pixel_inset
            xmax += pixel_inset
            ymin -= pixel_inset
            ymax += pixel_inset

        #move into new quad
        for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x *= xmax-xmin
                    loop[uv_layer].uv.y *= ymax-ymin
                    loop[uv_layer].uv.x += xmin
                    loop[uv_layer].uv.y += ymin

        #update mesh
        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)



        return {'FINISHED'}