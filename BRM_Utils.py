import sys
from mathutils import Vector


def get_face_uv_axis(face, uv_layer, world_matrix, view_up_vector, view_right_vector):
    """
    Find the UV translation axis by matching the face edges to view up and right vectors
    :param face:
    :param uv_layer:
    :param world_matrix:
    :param view_up_vector:
    :param view_right_vector:
    :return:
    """
    uv_x = None
    uv_y = None
    closest_up = sys.float_info.max
    closest_right = sys.float_info.max
    closest_dot_up = None
    closest_dot_right = None

    # Start from index 1, so we can can just
    # go to previous loop to get an edge
    for o, loop in enumerate(face.loops, 1):
        prev_loop = loop.link_loop_prev

        # Calculate the edge in world space, so matches view up and right vectors
        edge_vec = (world_matrix * loop.vert.co) - (world_matrix * prev_loop.vert.co)
        edge_vec.normalize()
        # Calculate the UV vector back to previous vertex
        uv_vec = loop[uv_layer].uv - prev_loop[uv_layer].uv
        # Calculate dot against view vectors, to get similarity
        dot_up = edge_vec.dot(view_up_vector)
        dot_right = edge_vec.dot(view_right_vector)
        # Restrict dot to 0-1 space for convenience
        flat_up = 1.0 - abs(dot_up)
        flat_right = 1.0 - abs(dot_right)

        if flat_up < closest_up:
            # If dot up is negative, reverse UV vector
            # if dot_up < 0:
            #     uv_vec *= -1
            # Bigger axis is chosen as the vector
            if abs(uv_vec.y) > abs(uv_vec.x):
                # Lazy normalization, basically
                uv_y = Vector((0, 1 if uv_vec.y > 0 else -1))
            else:
                uv_y = Vector((1 if uv_vec.x > 0 else -1, 0))

            closest_up = flat_up
            closest_dot_up = dot_up

        if flat_right < closest_right:
            # if dot_right < 0:
            #     uv_vec *= -1
            # Bigger axis is chosen as the vector
            if abs(uv_vec.y) > abs(uv_vec.x):
                uv_x = Vector((0, 1 if uv_vec.y > 0 else -1))
            else:
                uv_x = Vector((1 if uv_vec.x > 0 else -1, 0))

            closest_right = flat_right
            closest_dot_right = dot_right

    if uv_x is None or uv_y is None:
        return None
    # Fail safe, to make sure a weird parallel axis wasn't constructed
    if abs(uv_x.dot(uv_y)) > 0.7:
        return None
    # Normalize the dots, so value of 1 is the
    # closest axis to both view up and view right
    normalized_dot = abs(closest_dot_right + closest_dot_up) / 2
    return uv_x, uv_y, normalized_dot


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
