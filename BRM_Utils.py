import bpy
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
