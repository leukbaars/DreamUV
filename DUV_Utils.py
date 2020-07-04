import bpy
import bmesh
import math
from mathutils import Vector


def get_face_pixel_step(context, face):
    """
    Finds the UV space amount for one pixel of a face, if it is textured
    :param context:
    :param face:
    :return: Vector of the pixel translation, None if face is not textured
    """
    # Try to get the material being applied to the face
    slot_len = len(context.object.material_slots)
    if face.material_index < 0 or face.material_index >= slot_len:
        return None
    material = context.object.material_slots[face.material_index].material
    if material is None:
        return None
    # Try to get the texture the material is using
    target_img = None
    for texture_slot in material.texture_slots:
        if texture_slot is None:
            continue
        if texture_slot.texture is None:
            continue
        if texture_slot.texture.type == 'NONE':
            continue
        if texture_slot.texture.image is None:
            continue
        if texture_slot.texture.type == 'IMAGE':
            target_img = texture_slot.texture.image
            break
    if target_img is None:
        return None
    # With the texture in hand, save the UV step for one pixel movement
    pixel_step = Vector((1 / target_img.size[0], 1 / target_img.size[1]))
    return pixel_step



def read_atlas(context):
    atlas = list()
    obj = bpy.data.objects.get(context.scene.subrect_atlas)
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    #lets read coords

    faces = list()

    #MAKE FACE LIST
    for face in bm.faces:
        faces.append(face)

    for face in faces:
        xmin, xmax = face.loops[0][uv_layer].uv.x, face.loops[0][uv_layer].uv.x
        ymin, ymax = face.loops[0][uv_layer].uv.y, face.loops[0][uv_layer].uv.y

        for vert in face.loops:
            xmin = min(xmin, vert[uv_layer].uv.x)
            xmax = max(xmax, vert[uv_layer].uv.x)
            ymin = min(ymin, vert[uv_layer].uv.y)
            ymax = max(ymax, vert[uv_layer].uv.y)

        new_subrect = subrect()
        edge1 = xmax - xmin
        edge2 = ymax - ymin

        rect = list()
        
        for loop in face.loops:
            loop_uv = loop[uv_layer]
            #make sure to create new uv vector here, dont reference
            uvcoord = Vector((loop_uv.uv.x,loop_uv.uv.y))
            rect.append(uvcoord)
        
        new_subrect.uvcoord = rect
        
        #calculate aspect ratio
        aspect = edge1/edge2
        if aspect > 1:
            aspect = round(aspect)
        else:
            aspect = 1/(round(1/aspect))
        #calculate size
        size = face.calc_area()
        size = float('%.2g' % size) #round to 2 significant digits


        new_subrect.aspect = aspect
        new_subrect.size = size
        atlas.append(new_subrect)   
    return atlas



def square_fit(context):
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)

    uv_layer = bm.loops.layers.uv.verify()

    faces = list()

    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            faces.append(face)

    #TEST IF QUADS OR NOT

    quadmethod = True
    #EXPERIMENTAL! TO MUCH SKEWING TEST:
    distorted = False

    for face in faces: 
        if len(face.loops) is not 4 :
            quadmethod = False
            #print('no quad!')

    #SLOW HERE, find faster way to test if selection is ring shaped

    #Unwrap and get the edge verts
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
    bpy.ops.mesh.region_to_loop()

    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    edge_list = list()
    for e in bm.edges:
        if e.select is True:
            edge_list.append(e)
            #print(e)
            
    #select faces again
    for f in faces:
        f.select = True      
    #get start loop (this makes sure we loop in the right direction)
    startloop = None

    if(len(edge_list) == 0):
        print("weird! - means no mesh was sent?")
        return distorted 

    for l in edge_list[0].link_loops:
        if l.face.select is True:
            startloop = l
    #create sorted verts from start loop
    sorted_vert_list = list()
    for f in faces:
        f.select = False
    for e in edge_list:
        e.select = True

    sorted_vert_list.append(startloop.vert)
    startloop.edge.select = False
    sorted_vert_list.append(startloop.link_loop_next.vert)

    for i in range(1,len(edge_list)-1):
        #catch if a patch is donut shaped:
        if i >= len(sorted_vert_list):
            for f in faces:
                f.select = True
            bmesh.update_edit_mesh(obj.data)
            return False

        for e in sorted_vert_list[i].link_edges:
            if e.select is True:
                sorted_vert_list.append(e.other_vert(sorted_vert_list[i]))
                e.select = False

    #select faces again
    for f in faces:
        f.select = True

    #get UV
    sorted_uv_list = list()
    uv_layer = bm.loops.layers.uv.active
    for v in sorted_vert_list:
        for l in v.link_loops:
            if l.face.select is True:
                sorted_uv_list.append(l[uv_layer])
                break

    #get all angles
    sorted_angle_list = list()

    for i in range(len(sorted_uv_list)):
        prev = (i-1)%len(sorted_uv_list)
        next = (i+1)%len(sorted_uv_list)
        vector1 = Vector((sorted_uv_list[prev].uv.y-sorted_uv_list[i].uv.y,sorted_uv_list[prev].uv.x-sorted_uv_list[i].uv.x))
        vector2 = Vector((sorted_uv_list[next].uv.y-sorted_uv_list[i].uv.y,sorted_uv_list[next].uv.x-sorted_uv_list[i].uv.x))
        #check failcase of zero length vector:
        if vector1.length == 0 or vector2.length == 0:
            bmesh.update_edit_mesh(obj.data)
            return False
        angle = -math.degrees(vector1.angle_signed(vector2))
        if angle < 0:
            angle += 360
        sorted_angle_list.append(angle)

    
    #find concaves:
    for i in range(len(sorted_angle_list)):
        #print(sorted_angle_list[i])
        if sorted_angle_list[i] > 230:
            distorted = True
            bmesh.update_edit_mesh(obj.data)
            return False

    #angle test:
    #print("angles")
    #test if more than 4 90 degrees:
    NCount = 0
    for i in range(len(sorted_angle_list)):
        #print(sorted_angle_list[i])
        if sorted_angle_list[i] < 100:
            NCount += 1
    if NCount > 4:
        distorted = True

    
    if quadmethod: 
    #MAP FIRST QUAD
        edge1 = (faces[0].loops[0].vert.co.xyz - faces[0].loops[1].vert.co.xyz).length
        edge2 = (faces[0].loops[1].vert.co.xyz - faces[0].loops[2].vert.co.xyz).length

        faces[0].loops[0][uv_layer].uv.x = 0
        faces[0].loops[0][uv_layer].uv.y = 0
        faces[0].loops[1][uv_layer].uv.x = edge1
        faces[0].loops[1][uv_layer].uv.y = 0
        faces[0].loops[2][uv_layer].uv.x = edge1
        faces[0].loops[2][uv_layer].uv.y = edge2
        faces[0].loops[3][uv_layer].uv.x = 0
        faces[0].loops[3][uv_layer].uv.y = edge2

        bm.faces.active = faces[0]

        #UNWRAP ADJACENT
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.uv.follow_active_quads()
        #print("quading it")


    if quadmethod is False:

        #now find top 4 angles
        topangles = list()
        for o in range(4):
            top = 360
            topindex = -1
            for i in range(len(sorted_angle_list)):
                if sorted_angle_list[i] < top:
                    top = sorted_angle_list[i]
                    topindex = i
            #print(sorted_angle_list[topindex])
            
            if o is 3:
                if sorted_angle_list[topindex] > 120:
                    distorted = True

            topangles.append(topindex)
            sorted_angle_list[topindex] = 999 #lol

        sorted_corner_list = list()
        for i in range(len(sorted_uv_list)):
            sorted_corner_list.append(False)
        sorted_corner_list[topangles[0]] = True
        sorted_corner_list[topangles[1]] = True
        sorted_corner_list[topangles[2]] = True
        sorted_corner_list[topangles[3]] = True

        #find bottom left corner (using distance method seems to work well)
        distance = 2
        closest = 0
        for t in topangles:
            l = sorted_uv_list[t].uv.length
            if l < distance:
                distance = l
                closest = t

        #rotate lists to get clostest corner at start:
        for i in range(closest):
            sorted_corner_list.append(sorted_corner_list.pop(0))
            sorted_uv_list.append(sorted_uv_list.pop(0))
            sorted_vert_list.append(sorted_vert_list.pop(0))

        sorted_edge_ratios = list()

        #get edge lenghts
        edge = list()
        for i in range(len(sorted_vert_list)):
            if sorted_corner_list[i] is True:
                sorted_edge_ratios.append(0)
                if i is not 0:
                    l = (sorted_vert_list[i-1].co.xyz - sorted_vert_list[i].co.xyz).length
                    edge.append(sorted_edge_ratios[i-1] + l)
                
            if sorted_corner_list[i] is False:
                l = (sorted_vert_list[i-1].co.xyz - sorted_vert_list[i].co.xyz).length
                sorted_edge_ratios.append(sorted_edge_ratios[i-1] + l)
            if i is (len(sorted_vert_list)-1):
                l = (sorted_vert_list[i].co.xyz - sorted_vert_list[0].co.xyz).length
                edge.append(sorted_edge_ratios[i] + l)

        if distorted is False:
            #NOW LAY OUT ALL EDGE UVs
            i = 0
            #EDGE 1
            for l in sorted_vert_list[i].link_loops:
                if l.face.select is True:
                    l[uv_layer].uv = Vector((0,0))
            i += 1
            while sorted_corner_list[i] is False:
                for l in sorted_vert_list[i].link_loops:
                    if l.face.select is True:
                        l[uv_layer].uv = Vector((sorted_edge_ratios[i]/edge[0],0)) 
                i += 1 
            #EDGE 2
            for l in sorted_vert_list[i].link_loops:
                if l.face.select is True:
                    l[uv_layer].uv = Vector((1,0))        
            i += 1
            while sorted_corner_list[i] is False:
                for l in sorted_vert_list[i].link_loops:
                    if l.face.select is True:
                        l[uv_layer].uv = Vector((1,sorted_edge_ratios[i]/edge[1])) 
                i += 1     
            #EDGE 3
            for l in sorted_vert_list[i].link_loops:
                if l.face.select is True:
                    l[uv_layer].uv = Vector((1,1))         
            i += 1
            while sorted_corner_list[i] is False:
                for l in sorted_vert_list[i].link_loops:
                    if l.face.select is True:
                        l[uv_layer].uv = Vector((1-(sorted_edge_ratios[i]/edge[2]),1)) 
                i += 1
            #EDGE 4
            for l in sorted_vert_list[i].link_loops:
                if l.face.select is True:
                    l[uv_layer].uv = Vector((0,1))
            i += 1
            for o in range(i,len(sorted_vert_list)):
                for l in sorted_vert_list[o].link_loops:
                    if l.face.select is True:
                        l[uv_layer].uv = Vector((0,1-(sorted_edge_ratios[o]/edge[3])))

            #set proper aspect ratio
        
            for f in bm.faces:
                if f.select is True:
                    for loop in f.loops:
                        loop_uv = loop[uv_layer]
                        loop_uv.uv.x *= edge[0]
                        loop_uv.uv.y *= edge[1]

        bmesh.update_edit_mesh(me, True)
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.minimize_stretch(iterations=100)   
        #return true if rect fit was succesful
        return not distorted     


class subrect:
    aspect = int()
    size = float()
    uvcoord = list()


