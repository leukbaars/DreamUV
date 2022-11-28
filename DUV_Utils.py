import bpy
import bmesh
import math
import random
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






def get_orientation(context):
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    faces = list()
    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            faces.append(face)
    
    for face in faces:
        xmin, xmax = face.loops[0][uv_layer].uv.x, face.loops[0][uv_layer].uv.x
        ymin, ymax = face.loops[0][uv_layer].uv.y, face.loops[0][uv_layer].uv.y

    for vert in face.loops:
        xmin = min(xmin, vert[uv_layer].uv.x)
        xmax = max(xmax, vert[uv_layer].uv.x)
        ymin = min(ymin, vert[uv_layer].uv.y)
        ymax = max(ymax, vert[uv_layer].uv.y)

    # corners:
    # 3 2
    # 0 1

    bound0 = Vector((xmin,ymin))
    bound1 = Vector((xmax,ymin))
    bound2 = Vector((xmax,ymax))
    bound3 = Vector((xmin,ymax))
    middle = Vector(( ((xmax+xmin)/2)- bound0.x,((ymax+ymin)/2)-bound0.y ))

    distance = middle.length
    corner0 = faces[0].loops[0]
    for f in faces:
        for loop in f.loops:
            loop_uv = loop[uv_layer]
            vertuv = Vector((loop_uv.uv.x - bound0.x,loop_uv.uv.y - bound0.y))
            tempdistance = vertuv.length
            if tempdistance <= distance:
                distance = tempdistance
                corner0 = loop

    distance = middle.length
    corner1 = faces[0].loops[0]
    for f in faces:
        for loop in f.loops:
            loop_uv = loop[uv_layer]
            vertuv = Vector((loop_uv.uv.x - bound1.x,loop_uv.uv.y - bound1.y))
            tempdistance = vertuv.length
            if tempdistance <= distance:
                distance = tempdistance
                corner1 = loop

    distance = middle.length
    corner2 = faces[0].loops[0]
    for f in faces:
        for loop in f.loops:
            loop_uv = loop[uv_layer]
            vertuv = Vector((loop_uv.uv.x - bound2.x,loop_uv.uv.y - bound2.y))
            tempdistance = vertuv.length
            if tempdistance <= distance:
                distance = tempdistance
                corner2 = loop

    distance = middle.length
    corner3 = faces[0].loops[0]
    for f in faces:
        for loop in f.loops:
            loop_uv = loop[uv_layer]
            vertuv = Vector((loop_uv.uv.x - bound3.x,loop_uv.uv.y - bound3.y))
            tempdistance = vertuv.length
            if tempdistance <= distance:
                distance = tempdistance
                corner3 = loop


    #orientations:
    # 3 2   0 3   1 0   2 1
    # 0 1   1 2   2 3   3 0  

    #1st case:
    #if corner3.vert.co.z >= corner0.vert.co.z and corner2.vert.co.z >= corner1.vert.co.z and corner3.vert.co.z >= corner1.vert.co.z and corner2.vert.co.z >= corner0.vert.co.z:
        #print("case1")
    
    if corner0.vert.co.z >= corner1.vert.co.z and corner3.vert.co.z >= corner2.vert.co.z and corner0.vert.co.z >= corner2.vert.co.z and corner3.vert.co.z >= corner1.vert.co.z:
        #print("case2")
        for face in faces:
            for loop in face.loops:
                newx = loop[uv_layer].uv.y
                newy = -loop[uv_layer].uv.x 
                loop[uv_layer].uv.x = newx
                loop[uv_layer].uv.y = newy

    if corner1.vert.co.z >= corner2.vert.co.z and corner0.vert.co.z >= corner3.vert.co.z and corner1.vert.co.z >= corner3.vert.co.z and corner0.vert.co.z >= corner2.vert.co.z:
        #print("case3")
        for face in faces:
            for loop in face.loops:
                newx = -loop[uv_layer].uv.x
                newy = -loop[uv_layer].uv.y 
                loop[uv_layer].uv.x = newx
                loop[uv_layer].uv.y = newy

    if corner2.vert.co.z >= corner3.vert.co.z and corner1.vert.co.z >= corner0.vert.co.z and corner2.vert.co.z >= corner0.vert.co.z and corner1.vert.co.z >= corner3.vert.co.z:
        #print("case4")
        for face in faces:
            for loop in face.loops:
                newx = -loop[uv_layer].uv.y
                newy = loop[uv_layer].uv.x 
                loop[uv_layer].uv.x = newx
                loop[uv_layer].uv.y = newy

    return None
    





def get_uv_ratio(context):
    #figure out uv size to then compare against subrect size
    #to do this I project the mesh using uv coords so i can calculate the area using sum(f.calc_area(). Because I am too lazy to figure out the math

    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    faces = list()
    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            faces.append(face)
    backupfaces = list()
    for f in faces:
        backupface = list()
        for loop in f.loops:
            loop_uv = loop[uv_layer]
            backupvert = list()
            backupvert.append(loop.vert.co.x)
            backupvert.append(loop.vert.co.y)
            backupvert.append(loop.vert.co.z)
            backupface.append(backupvert)
        backupfaces.append(backupface)
    for f in faces:
        for loop in f.loops:
            loop_uv = loop[uv_layer]
            loop.vert.co.xy = loop_uv.uv
            loop.vert.co.z = 0 
    size = area = sum(f.calc_area() for f in faces if f.select)

    #return shape:
    for f, backupface in zip(faces, backupfaces):
        for loop, backupvert in zip(f.loops, backupface):
            loop.vert.co.x = backupvert[0]
            loop.vert.co.y = backupvert[1]
            loop.vert.co.z = backupvert[2]
    #bmesh.update_edit_mesh(obj.data)
    return size






def read_atlas(context):
    atlas = list()
    obj = context.scene.subrect_atlas
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
        if edge1 > 0 and edge2 > 0:

            aspect = edge1/edge2
            if aspect > 1:
                aspect = round(aspect)
            else:
                aspect = 1/(round(1/aspect))
                #aspect = 1/aspect
            posaspect = aspect
            if posaspect < 1.0:
                posaspect = 1/posaspect
            #calculate size
            size = face.calc_area()

            #adjust scale
            size /= context.scene.duvhotspotscale*context.scene.duvhotspotscale

            size = float('%.2g' % size) #round to 2 significant digits

            


            new_subrect.aspect = aspect
            new_subrect.posaspect = posaspect
            new_subrect.size = size
            atlas.append(new_subrect)   

    return atlas






def donut_uv_fixer(context):
    obj = bpy.context.view_layer.objects.active
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()

    faces = list()

    #MAKE FACE LIST
    for face in bm.faces:
        if face.select:
            faces.append(face)

    #Unwrap and get the edge verts
    bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
    bpy.ops.mesh.region_to_loop()

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
    
    #print("CHECKING DOUNt!!!!")
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

    #reselect faces:
    for f in faces:
        f.select = True

    return True
    






def square_fit(context):

       
    #return {'FINISHED'}

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
        if len(face.loops) != 4 :
            quadmethod = False
    
    #FIRST FIX DONUT SHAPES:
    noDonut = True
    noDonut = donut_uv_fixer(context)
    if noDonut is False:
        #select boundary edges
        bpy.ops.mesh.region_to_loop()
        boundary_edge_list = list()
        for e in bm.edges:
            if e.select is True:
                boundary_edge_list.append(e)
        
        #pick a random edge for where the topology cut will start
        #active_edge = boundary_edge_list[0]
        active_edge = boundary_edge_list[random.randint(0, len(boundary_edge_list)-1)]      
        bm.select_history.add(active_edge)
        
        #if its all quads, we can probably just cut it straight
        if quadmethod:
            for l in active_edge.verts[0].link_edges:
                if l.select == False:
                    l.select = True
                    bm.select_history.add(l)
                    break
            
            bpy.ops.mesh.loop_multi_select(ring=False)
            
        
        else:
            #walk through the boundary where the active edge exists to deselect them without deselecting the other boundary
            currentvert = active_edge.verts[0]       
            foundedge = True   
            while foundedge == True:
                foundedge = False
                for le in currentvert.link_edges:
                    if le.select == True:
                        currentvert = le.other_vert(currentvert)
                        le.select = False
                        foundedge = True
                        break
            
            
            #Dijkstra version
            #1)make list of all verts for distance values:
            Dverts = list()
            for v in bm.verts:
                Dverts.append(0)
            
            #set first index
            active_edge.select=False
            Dverts[active_edge.verts[0].index] = 1
            startvert = active_edge.verts[0].index
            
            #this will be a loop
            endvert = 0
            currentStep = 1
            iterating = True
            while iterating == True:
                for v in bm.verts:
                    if Dverts[v.index] == currentStep:
                        for l in v.link_edges:
                            if Dverts[l.other_vert(v).index] == 0:
                                Dverts[l.other_vert(v).index] = currentStep + 1
                            if l.other_vert(v).select == True:
                                iterating = False
                                endvert = l.other_vert(v).index
                                break
                currentStep += 1  
            
            #now we have a start and end vert, just run shortest path between them for quick selection
            for v in bm.verts:
                v.select = False
            for e in boundary_edge_list:
                e.select = False
            bm.verts.ensure_lookup_table()    
            bm.verts[startvert].select=True
            bm.verts[endvert].select=True
            
            bpy.ops.mesh.select_mode(type="VERT")
            
            #if shortest path is more than one edge use:
            shortconnection = False
            for l in bm.verts[startvert].link_edges:
                if l.select == True:
                    shortconnection = True
            if shortconnection == False:
                bpy.ops.mesh.shortest_path_select(edge_mode='SELECT')
            
            bpy.ops.mesh.select_mode(type="EDGE")
                    
        #turn into seam and split
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.edge_split()
        

        #reset selection
        for f in faces:
            f.select = True 
    
    

    #SLOW HERE, find faster way to test if selection is ring shaped

    #Unwrap and get the edge verts
    bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
    bpy.ops.mesh.region_to_loop()

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
        #print("weird! - means no mesh was sent?")
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
        #catch again if a patch is donut shaped:
        if i >= len(sorted_vert_list):
            for f in faces:
                f.select = True
            bmesh.update_edit_mesh(obj.data)
            #print("DONUT PATCH!!!!")
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
        if sorted_angle_list[i] > 230:
            distorted = True
            bmesh.update_edit_mesh(obj.data)
            return False

    #angle test:
    #test if more than 4 90 degrees:
    NCount = 0
    for i in range(len(sorted_angle_list)):
        if sorted_angle_list[i] < 100:
            NCount += 1
    if NCount > 4:
        distorted = True

    #now find top 4 angles
    topangles = list()
    for o in range(4):
        top = 360
        topindex = -1
        for i in range(len(sorted_angle_list)):
            if sorted_angle_list[i] < top:
                top = sorted_angle_list[i]
                topindex = i
        if o == 3:
            if sorted_angle_list[topindex] > 125:
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

    #create coord list:
    cornerz = list()

    for i in range(len(sorted_vert_list)):
        if sorted_corner_list[i] is True:
            cornerz.append(sorted_vert_list[i].co.z)

    sorted_edge_ratios = list()

    #get edge lenghts
    edge = list()
    for i in range(len(sorted_vert_list)):
        if sorted_corner_list[i] is True:
            sorted_edge_ratios.append(0)
            if i != 0:
                l = (sorted_vert_list[i-1].co.xyz - sorted_vert_list[i].co.xyz).length
                edge.append(sorted_edge_ratios[i-1] + l)
            
        if sorted_corner_list[i] is False:
            l = (sorted_vert_list[i-1].co.xyz - sorted_vert_list[i].co.xyz).length
            sorted_edge_ratios.append(sorted_edge_ratios[i-1] + l)
        if i is (len(sorted_vert_list)-1):
            l = (sorted_vert_list[i].co.xyz - sorted_vert_list[0].co.xyz).length
            edge.append(sorted_edge_ratios[i] + l)

    
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
        bpy.ops.uv.follow_active_quads()
        uv_layer = bm.loops.layers.uv.verify()

        #return
        edge1 = (edge[0]+edge[2])*.5
        edge2 = (edge[1]+edge[3])*.5

        #FIT TO 0-1 range
        xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
        ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y

        for face in faces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)

        #return

        #prevent divide by 0:
        if (xmax - xmin) == 0:
            xmin = .1
        if (ymax - ymin) == 0:
            ymin = .1

        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x -= xmin
                loop[uv_layer].uv.y -= ymin
                loop[uv_layer].uv.x /= (xmax-xmin)
                loop[uv_layer].uv.y /= (ymax-ymin)
        
        #shift extents to be positive only:
        xmax = xmax - xmin
        ymax = ymax - ymin

        #now fit to correct edge lengths:
        if (edge1 < edge2):
            #flip them:
            tedge = edge1
            edge1 = edge2
            edge2 = tedge
        
        if xmax >= ymax:
            for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x *= edge1
                    loop[uv_layer].uv.y *= edge2
        if xmax < ymax:
            for face in faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x *= edge2
                    loop[uv_layer].uv.y *= edge1

    if quadmethod is False:
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

        
        #newmethod:
        #select boundary and pin
        bpy.ops.uv.select_all(action='DESELECT')
        for v in sorted_vert_list:
            for l in v.link_loops:
                l[uv_layer].select = True
        bpy.ops.uv.pin(clear=False)
        
        #select all and unwrap (and unpin?)
        bpy.ops.uv.select_all(action='SELECT')  
        bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
        bpy.ops.uv.pin(clear=True)
        
        #return False
        #select boundary and unpin

        #bpy.ops.uv.select_all(action='SELECT')
        #expand middle verts
        #bpy.ops.uv.minimize_stretch(iterations=50)   
        #return true if rect fit was succesful
        
        return not distorted     






class subrect:
    aspect = int()
    posaspect = int()
    size = float()
    uvcoord = list()

class trim:
    uvcoord = list()


