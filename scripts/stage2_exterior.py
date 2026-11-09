#!/usr/bin/env python3
"""
Stage 2 — EXTERIOR BUILDER
Le planta.json e constroi exterior da casa no Blender headless:
paredes exteriores, telhado de duas aguas, chao, porta, janelas.
Exporta: output/exterior.glb
"""
import bpy, json, os

os.makedirs("output", exist_ok=True)

with open("output/planta.json", encoding="utf-8") as f:
    H = json.load(f)

ext = H["exterior"]
W   = ext["width"]
D   = ext["depth"]
WH  = ext["wall_height"]
WT  = ext["wall_thickness"]
RH  = ext["roof_height"]

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def new_mat(name, r, g, b, alpha=1.0, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (r, g, b, alpha)
    bsdf.inputs["Roughness"].default_value  = roughness
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat

def add_box(name, x, y, z, sx, sy, sz, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x+sx/2, y+sy/2, z+sz/2))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

clear()

mat_wall  = new_mat("M_Wall",   0.85, 0.80, 0.72, roughness=0.85)
mat_roof  = new_mat("M_Roof",   0.45, 0.28, 0.18, roughness=0.9)
mat_floor = new_mat("M_Floor",  0.55, 0.50, 0.42, roughness=1.0)
mat_door  = new_mat("M_Door",   0.42, 0.26, 0.12, roughness=0.7)
mat_win   = new_mat("M_Window", 0.60, 0.80, 0.95, alpha=0.35, roughness=0.05)

# Chao exterior
add_box("Floor_Ext", -WT, -WT, -0.1, W+WT*2, D+WT*2, 0.1, mat_floor)

# 4 paredes exteriores
walls = [
    ("Wall_South", 0,    0,    0, W,  WT, WH),
    ("Wall_North", 0,    D-WT, 0, W,  WT, WH),
    ("Wall_West",  0,    0,    0, WT, D,  WH),
    ("Wall_East",  W-WT, 0,    0, WT, D,  WH),
]
for name, x, y, z, sx, sy, sz in walls:
    add_box(name, x, y, z, sx, sy, sz, mat_wall)

# Porta de entrada
door = next(d for d in H["doors"] if d["id"] == "door_entrada")
add_box("Door_Ext", door["x"], -0.05, 0, door["w"], WT+0.1, door["h"], mat_door)

# Janelas fachada sul
for i, wx_ in enumerate([1.0, W-2.5]):
    add_box(f"Win_South_{i}", wx_, -0.05, 0.9, 1.2, WT+0.1, 1.2, mat_win)

# Janelas fachada norte
add_box("Win_North_0", 1.0, D-0.05, 0.9, 1.2, WT+0.1, 1.2, mat_win)

# Telhado de duas aguas (gable)
ridge_x = W / 2
ridge_z = WH + RH
verts = [
    (0, 0, WH), (W, 0, WH), (W, D, WH), (0, D, WH),
    (ridge_x, 0, ridge_z), (ridge_x, D, ridge_z),
]
faces = [
    (0, 1, 4),
    (1, 2, 5, 4),
    (2, 3, 5),
    (3, 0, 4, 5),
]
mesh = bpy.data.meshes.new("Roof_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()
roof_obj = bpy.data.objects.new("Roof", mesh)
bpy.context.collection.objects.link(roof_obj)
roof_obj.data.materials.append(mat_roof)

# Exportar GLB
out_path = os.path.abspath("output/exterior.glb")
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_normals=True,
)
sz = os.path.getsize(out_path)
print(f"\n=== STAGE 2 EXTERIOR COMPLETO ===")
print(f"Paredes: 4 | Janelas: 3 | Porta: 1 | Telhado: gable")
print(f"Exportado: {out_path} ({sz//1024} KB)")
