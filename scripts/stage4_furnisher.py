#!/usr/bin/env python3
"""
Stage 4 — FURNISHER
Importa interior.glb e adiciona:
- mobilia basica por quarto (cama, mesa, sofa, sanita, bancada)
- 2 arvores no quintal (tronco cilindrico + copa esferica)
- caminho no jardim
Exporta: output/furnished.glb
"""
import bpy, json, os, math

os.makedirs("output", exist_ok=True)

with open("output/planta.json", encoding="utf-8") as f:
    H = json.load(f)

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def new_mat(name, r, g, b, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value  = roughness
    bsdf.inputs["Metallic"].default_value   = metallic
    return mat

def add_box(name, x, y, z, sx, sy, sz, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x+sx/2, y+sy/2, z+sz/2))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

def add_cylinder(name, x, y, z, r, h, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z+h/2))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def add_sphere(name, x, y, z, r, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

clear()

# Importar interior
bpy.ops.import_scene.gltf(filepath=os.path.abspath("output/interior.glb"))
print(f"Interior importado: {len(bpy.data.objects)} objectos")

# Materiais de mobilia
mat_wood   = new_mat("M_Wood",   0.45, 0.28, 0.14, roughness=0.8)
mat_fabric = new_mat("M_Fabric", 0.30, 0.45, 0.65, roughness=0.95)
mat_white  = new_mat("M_White",  0.95, 0.95, 0.95, roughness=0.9)
mat_metal  = new_mat("M_Metal",  0.70, 0.70, 0.72, roughness=0.3, metallic=0.9)
mat_trunk  = new_mat("M_Trunk",  0.35, 0.22, 0.10, roughness=0.95)
mat_leaf_oak  = new_mat("M_LeafOak",  0.20, 0.52, 0.18, roughness=1.0)
mat_leaf_pine = new_mat("M_LeafPine", 0.12, 0.40, 0.14, roughness=1.0)
mat_grass  = new_mat("M_Grass",  0.28, 0.58, 0.20, roughness=1.0)
mat_path   = new_mat("M_Path",   0.70, 0.62, 0.48, roughness=0.95)

# ── SALA: sofa + mesa de centro ──────────────────────────────
sala = next(r for r in H["rooms"] if r["id"] == "sala")
sx, sy = sala["x"], sala["y"]
add_box("Sofa_Base",  sx+0.4, sy+0.5, 0.05, 2.2, 0.9, 0.45, mat_fabric)
add_box("Sofa_Back",  sx+0.4, sy+0.5, 0.05, 2.2, 0.15, 0.80, mat_fabric)
add_box("Coffee_Table", sx+1.2, sy+1.8, 0.05, 1.0, 0.6, 0.40, mat_wood)

# ── COZINHA: bancada + fogao ──────────────────────────────────
coz = next(r for r in H["rooms"] if r["id"] == "cozinha")
cx, cy = coz["x"], coz["y"]
add_box("Kitchen_Counter", cx+0.1, cy+0.1, 0.0, coz["w"]-0.2, 0.6, 0.90, mat_wood)
add_box("Kitchen_Top",     cx+0.1, cy+0.1, 0.9, coz["w"]-0.2, 0.6, 0.05, mat_white)
add_box("Stove",           cx+0.2, cy+0.15, 0.9, 0.7, 0.55, 0.05, mat_metal)

# ── QUARTO: cama + mesinha ────────────────────────────────────
qto = next(r for r in H["rooms"] if r["id"] == "quarto")
qx, qy = qto["x"], qto["y"]
add_box("Bed_Frame",   qx+0.3, qy+0.3, 0.0, 2.0, 1.4, 0.30, mat_wood)
add_box("Mattress",    qx+0.3, qy+0.3, 0.3, 2.0, 1.4, 0.25, mat_white)
add_box("Pillow",      qx+0.4, qy+0.4, 0.55, 0.6, 0.5, 0.12, mat_white)
add_box("Nightstand",  qx+2.5, qy+0.3, 0.0, 0.5, 0.5, 0.55, mat_wood)

# ── WC: sanita + lavatorio ────────────────────────────────────
wc = next(r for r in H["rooms"] if r["id"] == "wc")
wx, wy = wc["x"], wc["y"]
add_box("Toilet_Base", wx+0.2, wy+0.2, 0.0, 0.45, 0.65, 0.40, mat_white)
add_box("Toilet_Tank", wx+0.2, wy+0.65, 0.40, 0.45, 0.18, 0.30, mat_white)
add_box("Sink",        wx+1.2, wy+0.1, 0.0, 0.55, 0.45, 0.85, mat_white)
add_box("Sink_Basin",  wx+1.2, wy+0.1, 0.85, 0.55, 0.45, 0.08, mat_white)

# ── JARDIM: relva + caminho + 2 arvores ──────────────────────
garden = H["garden"]
gx, gy_raw = garden["position"]
gy = gy_raw - garden["depth"]

# Relva
add_box("Grass", gx, gy, -0.05, garden["width"], garden["depth"], 0.05, mat_grass)

# Caminho
path = garden["path"]
px1, py1 = path["from"]
px2, py2 = path["to"]
add_box("Garden_Path",
    px1 - path["width"]/2, py2, -0.04,
    path["width"], py1 - py2, 0.04,
    mat_path)

# Arvores
for tree in garden["trees"]:
    tx_ = tree["x"]
    ty_ = tree["y"]
    r   = tree["radius"]
    th_ = tree["height"]
    is_oak = tree["type"] == "oak"
    mat_leaf = mat_leaf_oak if is_oak else mat_leaf_pine

    # Tronco
    add_cylinder(f"Trunk_{tree['id']}", tx_, ty_, 0, r*0.18, th_*0.5, mat_trunk)

    if is_ok := is_oak:
        # Copa arredondada (esfera)
        add_sphere(f"Crown_{tree['id']}", tx_, ty_, th_*0.5 + r*0.9, r*1.1, mat_leaf)
    else:
        # Copa conica (pine — empilhar 3 cones com cubos escalonados)
        for i, (cw, cz) in enumerate([(r*1.4, th_*0.35), (r*1.0, th_*0.55), (r*0.6, th_*0.72)]):
            add_box(f"Pine_{tree['id']}_{i}", tx_-cw, ty_-cw, cz, cw*2, cw*2, th_*0.18, mat_leaf)

out_path = os.path.abspath("output/furnished.glb")
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_normals=True,
)
sz = os.path.getsize(out_path)
print(f"\n=== STAGE 4 FURNISHER COMPLETO ===")
print(f"Mobilia adicionada: sala, cozinha, quarto, WC")
print(f"Jardim: relva + caminho + 2 arvores ({len(garden['trees'])})")
print(f"Exportado: {out_path} ({sz//1024} KB)")
