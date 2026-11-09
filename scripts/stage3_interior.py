#!/usr/bin/env python3
"""
Stage 3 — INTERIOR BUILDER
Importa exterior.glb e constroi interiores:
chao por quarto, tecto, paredes internas, portas internas.
Exporta: output/interior.glb
"""
import bpy, json, os

os.makedirs("output", exist_ok=True)

with open("output/planta.json", encoding="utf-8") as f:
    H = json.load(f)

ext = H["exterior"]
WH  = ext["wall_height"]
WT  = ext["wall_thickness"]

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def new_mat(name, r, g, b, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value  = roughness
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

# Importar exterior
bpy.ops.import_scene.gltf(filepath=os.path.abspath("output/exterior.glb"))
print(f"Exterior importado: {len(bpy.data.objects)} objectos")

room_mats = {
    "sala":     new_mat("M_Sala",    0.96, 0.93, 0.86),
    "cozinha":  new_mat("M_Coz",     0.98, 0.95, 0.88),
    "corredor": new_mat("M_Corr",    0.90, 0.88, 0.83),
    "quarto":   new_mat("M_Quarto",  0.88, 0.92, 0.98),
    "wc":       new_mat("M_WC",      0.92, 0.88, 0.96),
}
mat_ceil  = new_mat("M_Ceil",  0.98, 0.98, 0.97)
mat_iwall = new_mat("M_IWall", 0.93, 0.91, 0.87)
mat_door  = new_mat("M_IDoor", 0.55, 0.38, 0.22, roughness=0.6)

EW = ext["width"]
ED = ext["depth"]

for room in H["rooms"]:
    rid = room["id"]
    rx, ry, rw, rd = room["x"], room["y"], room["w"], room["d"]
    rh = room.get("height", WH)
    mat = room_mats.get(rid, mat_iwall)

    # Chao do quarto
    add_box(f"Floor_{rid}", rx, ry, 0.0, rw, rd, 0.05, mat)

    # Tecto
    add_box(f"Ceil_{rid}", rx, ry, rh-0.05, rw, rd, 0.05, mat_ceil)

    # Paredes internas (apenas as nao-exteriores)
    if ry + rd < ED - WT - 0.05:
        add_box(f"IW_N_{rid}", rx, ry+rd-WT, 0, rw, WT, rh, mat_iwall)
    if ry > WT + 0.05:
        add_box(f"IW_S_{rid}", rx, ry, 0, rw, WT, rh, mat_iwall)
    if rx + rw < EW - WT - 0.05:
        add_box(f"IW_E_{rid}", rx+rw-WT, ry, 0, WT, rd, rh, mat_iwall)
    if rx > WT + 0.05:
        add_box(f"IW_W_{rid}", rx, ry, 0, WT, rd, rh, mat_iwall)

# Portas internas
for door in H["doors"]:
    if door["id"] == "door_entrada":
        continue
    dx_, dy_ = door["x"], door["y"]
    dw, dh   = door["w"], door["h"]
    face     = door["face"]
    did      = door["id"]
    if face in ("south", "north"):
        add_box(f"Door_{did}", dx_, dy_-WT/2, 0, dw, WT+0.05, dh, mat_door)
    else:
        add_box(f"Door_{did}", dx_-WT/2, dy_, 0, WT+0.05, dw, dh, mat_door)

out_path = os.path.abspath("output/interior.glb")
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_normals=True,
)
sz = os.path.getsize(out_path)
print(f"\n=== STAGE 3 INTERIOR COMPLETO ===")
print(f"Quartos: {len(H['rooms'])} | Portas internas: {len(H['doors'])-1}")
print(f"Exportado: {out_path} ({sz//1024} KB)")
