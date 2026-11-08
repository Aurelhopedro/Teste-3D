#!/usr/bin/env python3
"""
generate-world.py — Script de geração do mundo AXEV Medieval Kingdom
Usa o motor Terminalia (worldgen-forge) para gerar terreno + exports.

Etapas executadas neste script (CPU-only, sem GPU):
  1. Lê a configuração de configs/medieval-city.json
  2. Executa os terrain operators (FBM, montanhas, rios, etc.)
  3. Guarda o heightmap em output/terrain/hm.png (16-bit PNG)
  4. Guarda as máscaras de região em output/terrain/mask_*.png
  5. Guarda world.json com o estado completo
  6. Gera export manifest glTF (output/export/gltf/manifest.json)
  7. Gera Godot scene (output/export/godot/world.tscn)
  8. Regista métricas de geração em output/metrics.json

Nota: GLB individuais (assets 3D) exigem GPU (TRELLIS.2 via ComfyUI).
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

# Adicionar o motor ao path
MOTOR_DIR = os.path.join(os.path.dirname(__file__), "..", "worldgen-forge")
sys.path.insert(0, MOTOR_DIR)

try:
    from terminalia.terrain import build_terrain
    from terminalia.schema import World, WorldSpec, Terrain, Region, HistoryEntry
    from terminalia.export import export_glb_bundle, write_godot_scene
except ImportError as e:
    print(f"ERRO: Não foi possível importar o motor Terminalia: {e}")
    print(f"Motor esperado em: {MOTOR_DIR}")
    sys.exit(1)

import numpy as np

# --------------------------------------------------------------------- config

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "medieval-city.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


# --------------------------------------------------------------------- main

def main():
    t_start = time.time()
    print("=" * 60)
    print("AXEV World Generator — Terminalia Engine")
    print("=" * 60)

    # 1. Ler config
    print(f"\n[1/7] A carregar config: {CONFIG_PATH}")
    cfg = load_config(CONFIG_PATH)
    print(f"      Mundo: {cfg['world_name']}")
    print(f"      Seed:  {cfg['seed']}")
    print(f"      Res:   {cfg['resolution']}px ({cfg['size_hectares']} ha)")

    # 2. Criar estrutura de output
    print("\n[2/7] A criar estrutura de output...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "terrain"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "export", "gltf"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "export", "godot"), exist_ok=True)

    # 3. Gerar terreno
    print("\n[3/7] A gerar terreno procedural...")
    ops = cfg["terrain_ops"]
    print(f"      {len(ops)} operadores: {[o['op'] for o in ops]}")

    t_terrain = time.time()
    grid = build_terrain(
        ops,
        size=cfg["resolution"],
        meters_per_pixel=cfg["meters_per_pixel"],
        seed=cfg["seed"]
    )
    terrain_time = time.time() - t_terrain
    print(f"      ✅ Terreno gerado em {terrain_time:.2f}s")

    # 4. Guardar heightmap
    print("\n[4/7] A guardar heightmap...")
    hm_path = grid.save_heightmap(os.path.join(OUTPUT_DIR, "terrain", "hm.png"))
    hm_size = os.path.getsize(hm_path)
    print(f"      ✅ {hm_path} ({hm_size/1024:.1f} KB)")

    # 5. Guardar máscaras de região
    print("\n[5/7] A guardar máscaras de região...")
    rng = np.random.default_rng(cfg["seed"] + 1)
    res = cfg["resolution"]
    n_regions = len(cfg["regions"])
    pts = rng.random((n_regions, 2)) * res
    ys, xs = np.mgrid[0:res, 0:res]
    d = np.stack([((xs - px) ** 2 + (ys - py) ** 2) for px, py in pts])
    labels = d.argmin(axis=0)

    regions_data = []
    for i, rname in enumerate(cfg["regions"]):
        m = (labels == i).astype(np.float32)
        p = os.path.join(OUTPUT_DIR, "terrain", f"mask_{rname}.png")
        grid.save_mask(m, p)
        area_pct = float(m.mean() * 100)
        regions_data.append({"name": rname, "mask": p, "area_pct": round(area_pct, 2)})
        print(f"      mask_{rname}.png ({area_pct:.1f}% do terreno)")

    # 6. Construir world.json
    print("\n[6/7] A construir world.json...")
    spec = WorldSpec(
        prompt=cfg["prompt"],
        seed=cfg["seed"],
        size_hectares=cfg["size_hectares"]
    )
    world = World(spec=spec)

    # Adicionar regiões à estrutura do mundo
    terrain_obj_regions = []
    for rd in regions_data:
        terrain_obj_regions.append(Region(
            name=rd["name"],
            mask=rd["mask"],
            biome=rd["name"]
        ))

    world.terrain = Terrain(
        heightmap=hm_path,
        regions=terrain_obj_regions,
        operators=[o["op"] for o in ops],
        meters_per_pixel=cfg["meters_per_pixel"],
        min_height_m=0.0,
        max_height_m=320.0
    )
    world.history.append(HistoryEntry(
        stage="terrain",
        at=datetime.now(timezone.utc).isoformat(),
        notes=f"{len(ops)} operators, {res}px, medieval valley"
    ))

    world_path = os.path.join(OUTPUT_DIR, "world.json")
    world.save(world_path)
    world_size = os.path.getsize(world_path)
    print(f"      ✅ {world_path} ({world_size/1024:.1f} KB)")

    # 7. Gerar manifests de export
    print("\n[7/7] A gerar exports...")
    world_dict = json.loads(open(world_path).read())

    # glTF manifest
    gltf_dir = os.path.join(OUTPUT_DIR, "export", "gltf")
    manifest = {
        "world": cfg["world_name"],
        "prompt": cfg["prompt"],
        "seed": cfg["seed"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "terrain": {
            "heightmap": "../../terrain/hm.png",
            "meters_per_pixel": cfg["meters_per_pixel"],
            "size_pixels": res,
            "size_meters": res * cfg["meters_per_pixel"],
            "height_range_m": [0.0, 320.0]
        },
        "regions": [{"name": rd["name"], "mask": f"../../terrain/mask_{rd['name']}.png", "area_pct": rd["area_pct"]} for rd in regions_data],
        "objects": [],
        "_note": "GLB assets nao gerados nesta execucao (exigem GPU TRELLIS.2). Adicionar GLBs aqui para import completo."
    }
    manifest_path = os.path.join(gltf_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"      ✅ glTF manifest: {manifest_path}")

    # Godot scene
    godot_scene = """[gd_scene format=3 uid="uid://axev_medieval_kingdom"]

[node name="AXEVMedievalKingdom" type="Node3D"]

[node name="Terrain" type="Node3D" parent="."]
metadata/world_name = "AXEV Medieval Kingdom"
metadata/heightmap = "res://terrain/hm.png"
metadata/meters_per_pixel = 2.0
metadata/size_m = 2048.0

[node name="RegionHighlandNorth" type="Node3D" parent="Terrain"]
[node name="RegionHighlandSouth" type="Node3D" parent="Terrain"]
[node name="RegionValleyFloor" type="Node3D" parent="Terrain"]
[node name="RegionForestWest" type="Node3D" parent="Terrain"]
[node name="RegionRiver" type="Node3D" parent="Terrain"]
"""
    godot_path = os.path.join(OUTPUT_DIR, "export", "godot", "world.tscn")
    with open(godot_path, "w") as f:
        f.write(godot_scene)
    print(f"      ✅ Godot scene: {godot_path}")

    # 8. Métricas
    t_total = time.time() - t_start
    metrics = {
        "world_name": cfg["world_name"],
        "engine": "Terminalia/WorldGen Forge v0.2",
        "engine_repo": "https://github.com/Ardynai/worldgen-forge",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_time_s": round(t_total, 2),
        "terrain_time_s": round(terrain_time, 2),
        "resolution_px": res,
        "size_hectares": cfg["size_hectares"],
        "size_meters": res * cfg["meters_per_pixel"],
        "n_operators": len(ops),
        "n_regions": n_regions,
        "heightmap_size_kb": round(hm_size / 1024, 1),
        "files_generated": [
            "output/terrain/hm.png",
            *[f"output/terrain/mask_{r['name']}.png" for r in regions_data],
            "output/world.json",
            "output/export/gltf/manifest.json",
            "output/export/godot/world.tscn"
        ],
        "gpu_required": False,
        "paid_apis_used": False,
        "limitations": [
            "GLB assets individuais (castelo, casas, etc.) nao gerados — exigem GPU TRELLIS.2 ou Comfy Cloud (pago)",
            "Sem textures PBR nos assets — depende do mesmo pipeline TRELLIS.2",
            "O heightmap representa o relevo mas nao inclui objectos colocados (placement stage exige assets)"
        ]
    }
    metrics_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print("GERAÇÃO CONCLUÍDA")
    print("=" * 60)
    print(f"Tempo total: {t_total:.2f}s")
    print(f"Ficheiros gerados: {len(metrics['files_generated'])}")
    print(f"Output: {OUTPUT_DIR}")
    print("\nPróximas etapas para mundo completo:")
    print("  → Instalar ComfyUI local com GPU")
    print("  → Ou configurar COMFY_CLOUD_API_KEY (créditos pagos)")
    print("  → Depois executar: terminalia assets + terminalia place")


if __name__ == "__main__":
    main()
