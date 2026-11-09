#!/usr/bin/env python3
"""
Stage 5 — ASSEMBLER
Importa furnished.glb, faz limpeza final, optimiza e exporta:
- output/casa_final.glb  (formato principal)
- output/casa_final.obj  (formato alternativo)
Gera tambem um relatorio JSON do resultado final.
"""
import bpy, json, os

os.makedirs("output", exist_ok=True)

with open("output/planta.json", encoding="utf-8") as f:
    H = json.load(f)

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

clear()

# Importar cena completa
bpy.ops.import_scene.gltf(filepath=os.path.abspath("output/furnished.glb"))
total_before = len(bpy.data.objects)
print(f"Cena importada: {total_before} objectos")

# Remover objectos invalidos ou de tamanho zero
removed = 0
for obj in list(bpy.data.objects):
    if obj.type == 'MESH':
        dims = obj.dimensions
        if max(dims) < 0.001:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1

print(f"Objectos removidos (invalidos): {removed}")
print(f"Objectos finais: {len(bpy.data.objects)}")

# Aplicar transformacoes a todos
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Smooth shading nos meshes
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()

# Exportar GLB final
glb_path = os.path.abspath("output/casa_final.glb")
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_normals=True,
    export_colors=True,
)
glb_sz = os.path.getsize(glb_path)

# Exportar OBJ
obj_path = os.path.abspath("output/casa_final.obj")
bpy.ops.export_mesh.obj(
    filepath=obj_path,
    use_materials=True,
    use_normals=True,
    use_uvs=True,
)
obj_sz = os.path.getsize(obj_path)

# Relatorio final
report = {
    "pipeline": "AXEV City Generator — Test 001",
    "stages_completed": ["architect", "exterior", "interior", "furnisher", "assembler"],
    "house": H["name"],
    "stats": {
        "total_objects": len(bpy.data.objects),
        "rooms": len(H["rooms"]),
        "doors": len(H["doors"]),
        "trees": len(H["garden"]["trees"]),
        "exterior_area_m2": H["exterior"]["width"] * H["exterior"]["depth"],
        "garden_area_m2": H["garden"]["width"] * H["garden"]["depth"],
    },
    "exports": {
        "glb": {"path": "output/casa_final.glb", "size_kb": round(glb_sz/1024, 1)},
        "obj": {"path": "output/casa_final.obj", "size_kb": round(obj_sz/1024, 1)},
    },
    "blender_version": bpy.app.version_string,
    "gpu_used": False,
    "paid_apis": False,
}

with open("output/pipeline_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"=== STAGE 5 ASSEMBLER — PIPELINE COMPLETA ===")
print(f"{'='*50}")
print(f"Casa: {H['name']}")
print(f"Quartos: {len(H['rooms'])} | Portas: {len(H['doors'])} | Arvores: {len(H['garden']['trees'])}")
print(f"Objectos 3D: {len(bpy.data.objects)}")
print(f"GLB: {glb_path} ({glb_sz//1024} KB)")
print(f"OBJ: {obj_path} ({obj_sz//1024} KB)")
print(f"Relatorio: output/pipeline_report.json")
print(f"{'='*50}")
