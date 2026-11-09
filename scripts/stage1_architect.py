#!/usr/bin/env python3
"""
Stage 1 — ARCHITECT
Gera a planta da casa em JSON estruturado e SVG visual.
Saida: output/planta.json, output/planta.svg
"""
import json, os

os.makedirs("output", exist_ok=True)

HOUSE = {
    "name": "Casa AXEV Test-001",
    "style": "low_poly_game_ready",
    "unit": "meters",
    "exterior": {
        "width": 10.0,
        "depth": 8.0,
        "wall_height": 3.0,
        "wall_thickness": 0.3,
        "roof_type": "gable",
        "roof_height": 2.5,
        "position": [0, 0]
    },
    "rooms": [
        {"id": "sala",     "name": "Sala",          "x": 0.3, "y": 0.3, "w": 5.5, "d": 4.5, "height": 3.0, "door_to": ["corredor"], "windows": 2},
        {"id": "cozinha",  "name": "Cozinha",        "x": 6.1, "y": 0.3, "w": 3.6, "d": 4.5, "height": 3.0, "door_to": ["corredor"], "windows": 1},
        {"id": "corredor", "name": "Corredor",       "x": 0.3, "y": 5.1, "w": 9.4, "d": 1.4, "height": 3.0, "door_to": ["sala","cozinha","quarto","wc"], "windows": 0},
        {"id": "quarto",   "name": "Quarto",         "x": 0.3, "y": 6.8, "w": 6.0, "d": 2.9, "height": 3.0, "door_to": ["corredor"], "windows": 2},
        {"id": "wc",       "name": "Casa de Banho",  "x": 6.6, "y": 6.8, "w": 3.1, "d": 2.9, "height": 3.0, "door_to": ["corredor"], "windows": 1},
    ],
    "doors": [
        {"id": "door_entrada", "room": "exterior", "target": "sala",     "x": 2.5, "y": 0.0, "w": 1.0, "h": 2.2, "face": "south"},
        {"id": "door_sala",    "room": "sala",     "target": "corredor", "x": 2.0, "y": 4.8, "w": 0.9, "h": 2.1, "face": "north"},
        {"id": "door_cozinha", "room": "cozinha",  "target": "corredor", "x": 7.0, "y": 4.8, "w": 0.9, "h": 2.1, "face": "north"},
        {"id": "door_quarto",  "room": "quarto",   "target": "corredor", "x": 2.0, "y": 6.8, "w": 0.9, "h": 2.1, "face": "south"},
        {"id": "door_wc",      "room": "wc",       "target": "corredor", "x": 7.5, "y": 6.8, "w": 0.8, "h": 2.1, "face": "south"},
    ],
    "garden": {
        "width": 14.0,
        "depth": 6.0,
        "position": [0, -6.5],
        "open": True,
        "trees": [
            {"id": "tree_01", "type": "oak",  "x": 1.5,  "y": -4.5, "radius": 1.2, "height": 5.0},
            {"id": "tree_02", "type": "pine", "x": 11.5, "y": -3.0, "radius": 0.8, "height": 6.5},
        ],
        "grass": True,
        "path": {"from": [5.0, -0.5], "to": [5.0, -6.5], "width": 1.2}
    },
    "metadata": {
        "total_area_m2": 80.0,
        "rooms_count": 5,
        "trees_count": 2,
        "generated_by": "AXEV Architect Stage 1",
        "pipeline_stage": 1
    }
}

with open("output/planta.json", "w", encoding="utf-8") as f:
    json.dump(HOUSE, f, indent=2, ensure_ascii=False)
print(f"planta.json guardada ({os.path.getsize('output/planta.json')} bytes)")

# SVG
SCALE = 50
PAD   = 60
HW    = HOUSE["exterior"]["width"]
HD    = HOUSE["exterior"]["depth"]
GW    = HOUSE["garden"]["width"]
GD    = HOUSE["garden"]["depth"]
SVG_W = int((max(HW, GW) + 2) * SCALE + PAD * 2)
SVG_H = int((HD + GD + 3) * SCALE + PAD * 2)

COLORS = {
    "sala": "#d4e8c2", "cozinha": "#fde8c2", "corredor": "#e8e2d4",
    "quarto": "#c2d4e8", "wc": "#e8c2d4", "garden": "#c8e8b0",
    "path": "#e0d4b0", "wall": "#5a4a3a", "door": "#a07040",
    "tree_oak": "#4a8a30", "tree_pine": "#2a6a20",
}

def tx(x): return PAD + (x + 1) * SCALE
def ty(y): return PAD + (GD + 1 + y) * SCALE

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" style="background:#f5f0e8;font-family:Arial,sans-serif">')
svg.append(f'<text x="{SVG_W//2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#3a2a1a">{HOUSE["name"]}</text>')
svg.append(f'<text x="{SVG_W//2}" y="44" text-anchor="middle" font-size="10" fill="#888">Stage 1 — Architect · {HW}m x {HD}m · {HOUSE["metadata"]["total_area_m2"]}m2</text>')

# Jardim
gx, gy = HOUSE["garden"]["position"]
svg.append(f'<rect x="{tx(gx)}" y="{ty(gy-GD)}" width="{GW*SCALE}" height="{GD*SCALE}" fill="{COLORS["garden"]}" stroke="#6a9a50" stroke-width="2" rx="4"/>')
svg.append(f'<text x="{tx(gx+GW/2)}" y="{ty(gy-GD/2)+5}" text-anchor="middle" font-size="11" fill="#4a7a30">Quintal</text>')

# Caminho
path = HOUSE["garden"]["path"]
px1, py1 = path["from"]
px2, py2 = path["to"]
svg.append(f'<rect x="{tx(px1-path["width"]/2)}" y="{ty(py2)}" width="{path["width"]*SCALE}" height="{(py1-py2)*SCALE}" fill="{COLORS["path"]}" stroke="#c0a870" stroke-width="1"/>')

# Arvores
for tree in HOUSE["garden"]["trees"]:
    cx_ = tx(tree["x"])
    cy_ = ty(tree["y"])
    r   = int(tree["radius"] * SCALE)
    col = COLORS["tree_oak"] if tree["type"] == "oak" else COLORS["tree_pine"]
    svg.append(f'<circle cx="{cx_}" cy="{cy_}" r="{r}" fill="{col}" opacity="0.85" stroke="#2a5a10" stroke-width="1.5"/>')
    svg.append(f'<text x="{cx_}" y="{cy_+r+12}" text-anchor="middle" font-size="8" fill="#2a5a10">{tree["type"]}</text>')

# Casa exterior
svg.append(f'<rect x="{tx(0)}" y="{ty(HD)}" width="{HW*SCALE}" height="{HD*SCALE}" fill="#e8e0d4" stroke="{COLORS["wall"]}" stroke-width="3"/>')

# Quartos
room_colors = {"sala":"#d4e8c2","cozinha":"#fde8c2","corredor":"#e8e2d4","quarto":"#c2d4e8","wc":"#e8c2d4"}
for room in HOUSE["rooms"]:
    rx_, ry_, rw, rd = room["x"], room["y"], room["w"], room["d"]
    col = room_colors.get(room["id"], "#eee")
    svg.append(f'<rect x="{tx(rx_)}" y="{ty(ry_+rd)}" width="{rw*SCALE}" height="{rd*SCALE}" fill="{col}" stroke="{COLORS["wall"]}" stroke-width="2"/>')
    svg.append(f'<text x="{tx(rx_+rw/2)}" y="{ty(ry_+rd/2)+4}" text-anchor="middle" font-size="10" fill="#3a2a1a" font-weight="bold">{room["name"]}</text>')
    svg.append(f'<text x="{tx(rx_+rw/2)}" y="{ty(ry_+rd/2)+16}" text-anchor="middle" font-size="8" fill="#6a5a4a">{rw}x{rd}m</text>')

# Portas
for door in HOUSE["doors"]:
    dx_, dy_ = door["x"], door["y"]
    dw = door["w"] * SCALE
    face = door["face"]
    if face in ("south", "north"):
        svg.append(f'<rect x="{tx(dx_)}" y="{ty(dy_)-4}" width="{dw}" height="8" fill="{COLORS["door"]}" stroke="#704020" stroke-width="1.5"/>')
    else:
        svg.append(f'<rect x="{tx(dx_)-4}" y="{ty(dy_)}" width="8" height="{dw}" fill="{COLORS["door"]}" stroke="#704020" stroke-width="1.5"/>')

# Norte
svg.append(f'<text x="{PAD+10}" y="{SVG_H-20}" font-size="18" fill="#3a2a1a">N</text>')
svg.append(f'<line x1="{PAD+18}" y1="{SVG_H-40}" x2="{PAD+18}" y2="{SVG_H-26}" stroke="#3a2a1a" stroke-width="2" marker-end="url(#arr)"/>')
svg.append('</svg>')

with open("output/planta.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print(f"planta.svg gerada ({os.path.getsize('output/planta.svg')} bytes)")
print("\n=== STAGE 1 ARCHITECT COMPLETO ===")
