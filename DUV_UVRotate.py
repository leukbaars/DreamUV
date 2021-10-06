import bpy
import bmesh
import math


class DREAMUV_OT_uv_rotate(bpy.types.Operator):
    """Rotate UVs in the 3D Viewport"""
    bl_idname = "view3d.dreamuv_uvrotate"
    bl_label = "UV Rotate"
    bl_options = {"GRAB_CURSOR", "UNDO", "BLOCKING"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None

    xcenter=0
    ycenter=0

    startdelta=0

    rotate_snap = 45

    def invoke(self, context, event):

        #object->edit switch seems to "lock" the data. Ugly but hey it works
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        self.rotate_snap = 45
        module_name = __name__.split('.')[0]
        addon_prefs = bpy.context.preferences.addons[module_name].preferences
        self.rotate_snap = addon_prefs.rotate_snap

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
        
        if event.type == 'MOUSEMOVE':

            #get angle of cursor from start pos in radians
            delta = -math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            #neutralize angle for mouse start position
            delta+=self.startdelta


            vcenterx = (bpy.context.region.width/2)+bpy.context.region.x

            #step rotation
            if event.ctrl and not event.shift:

                #PI/4=0.78539816339
                PIdiv=3.14159265359/(180/self.rotate_snap)
                delta=math.floor(delta/PIdiv)*PIdiv
            if event.ctrl and event.shift:
                PIdiv=3.14159265359/(180/self.rotate_snap)/2
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
            bmesh.update_edit_mesh(self.mesh, loop_triangles=False, destructive=False)

        elif event.type == 'LEFTMOUSE':
            
            #finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            
            # reset all uvs to reference
            delta=0
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):

                        px=self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x
                        py=self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y

                        vert[self.bm.loops.layers.uv.active].uv.x = math.cos(delta) * (px-self.xcenter) - math.sin(delta) * (py-self.ycenter) + self.xcenter
                        vert[self.bm.loops.layers.uv.active].uv.y = math.sin(delta) * (px-self.xcenter) +  math.cos(delta) * (py-self.ycenter) + self.ycenter

            #update mesh
            bmesh.update_edit_mesh(self.mesh, loop_triangles=False, destructive=False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

class DREAMUV_OT_uv_rotate_step(bpy.types.Operator):
    """Rotate UVs using snap size"""
    bl_idname = "view3d.dreamuv_uvrotatestep"
    bl_label = "rotate"
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

        mirrored = False
        #check if mirrored:
        for face in faces:
            sum_edges = 0
            # Only loop 3 verts ignore others: faster!
            for i in range(3):
                uv_A = face.loops[i][uv_layer].uv
                uv_B = face.loops[(i+1)%3][uv_layer].uv
                sum_edges += (uv_B.x - uv_A.x) * (uv_B.y + uv_A.y)

            if sum_edges > 0:
                mirrored = True

        #get original size
        xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
        ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y
        
        for face in faces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)
        
        xcenter=(xmin+xmax)/2
        ycenter=(ymin+ymax)/2

        #step rotation
        module_name = __name__.split('.')[0]
        addon_prefs = bpy.context.preferences.addons[module_name].preferences
        rotate_snap = addon_prefs.rotate_snap
        print(rotate_snap)

        #PI/4=0.78539816339
        PIdiv=3.14159265359/(180/rotate_snap)
        delta = (3.14159265359/180)*rotate_snap
        #delta = math.floor(delta/PIdiv)*PIdiv
        if self.direction == "reverse":
            print("reverse")
            #delta = (3.14159265359/180)-delta
            delta = -delta
        if mirrored:
            delta = -delta

        #loop through every selected face and scale the uv's using original uv as reference
        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x -= xcenter
                loop[uv_layer].uv.y -= ycenter

                oldx = loop[uv_layer].uv.x
                oldy = loop[uv_layer].uv.y

                loop[uv_layer].uv.x = oldx * math.cos(delta) - oldy * math.sin(delta)
                loop[uv_layer].uv.y = oldy * math.cos(delta) + oldx * math.sin(delta)

                loop[uv_layer].uv.x += xcenter
                loop[uv_layer].uv.y += ycenter


        #update mesh
        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)



        return {'FINISHED'}