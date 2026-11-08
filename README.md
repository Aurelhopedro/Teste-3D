# Teste-3D — Gerador Experimental de Mundos 3D

Repositório independente para testar a geração de mundos 3D com o motor
**Terminalia / WorldGen Forge** via GitHub Actions gratuitos.

## Motor
- **Repositório:** [Ardynai/worldgen-forge](https://github.com/Ardynai/worldgen-forge)
- **Nome oficial:** Terminalia v0.2
- **Licença:** MIT
- **Dependências base:** Python 3.11+, numpy, pillow, pydantic

## Capacidades no runner gratuito (sem GPU)

| Capacidade | Estado |
|---|---|
| Terreno procedural (heightmap PNG 16-bit) | ✅ CPU-only |
| Operadores: FBM, montanhas, rios, costa | ✅ CPU-only |
| Regiões Voronoi e biomas | ✅ CPU-only |
| world.json (estado completo) | ✅ CPU-only |
| Export Godot (.tscn) | ✅ CPU-only |
| Export glTF manifest (.json) | ✅ CPU-only |
| Meshes 3D individuais (GLB via TRELLIS.2) | ⚠️ Exige GPU ou API key paga |

## Primeiro mundo: AXEV Medieval Kingdom

```json
{
  "world_name": "AXEV Medieval Kingdom",
  "prompt": "fortified medieval city in a mountain valley",
  "seed": 1337,
  "size_hectares": 400,
  "resolution": 1024
}
```

## Como executar

1. Vai a **Actions** → **AXEV World Generator**
2. Clica em **Run workflow**
3. Aguarda ~3-5 minutos
4. Descarrega o artefacto **AXEV-MEDIEVAL-WORLD-TEST-001**

## Estrutura

```
Teste-3D/
├── .github/workflows/axev-world-generator.yml
├── configs/medieval-city.json
├── scripts/generate-world.py
├── scripts/generate-report.py
├── docs/WORLD_GENERATION_REPORT.md
└── README.md
```

## Licença

MIT
