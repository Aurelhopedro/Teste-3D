#!/usr/bin/env python3
"""
generate-viewer.py - Cria o visualizador 3D interactivo em HTML usando Three.js
Lê o terrain_data.json gerado pelo pipeline e cria index.html interactivo.
"""
import json, os

cfg = json.load(open("configs/medieval-city.json"))
world_name = cfg["world_name"]
seed = cfg["seed"]
regions = cfg["regions"]
regions_tags = "".join(f'    <span class="tag">{r.replace("_"," ")}</span>\n' for r in regions)

html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{world_name} — AXEV 3D Viewer</title>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:#0a0a12; color:#e0e0e0; font-family:'Segoe UI',sans-serif; overflow:hidden; }}
    #c {{ width:100vw; height:100vh; }}
    #ui {{
      position:fixed; top:16px; left:16px; z-index:10;
      background:rgba(0,0,0,0.78); border:1px solid #2a3a4a;
      border-radius:10px; padding:14px 18px; min-width:230px;
      backdrop-filter:blur(10px);
    }}
    #ui h2 {{ font-size:13px; color:#7eb8f7; margin-bottom:8px; letter-spacing:1px; text-transform:uppercase; }}
    #ui p {{ font-size:11px; color:#aaa; margin:3px 0; }}
    .tag {{ display:inline-block; background:#1a2f4a; color:#7eb8f7; border-radius:4px; padding:2px 7px; font-size:10px; margin:2px 2px 0 0; }}
    #legend {{
      position:fixed; top:16px; right:16px; z-index:10;
      background:rgba(0,0,0,0.78); border:1px solid #2a3a4a;
      border-radius:10px; padding:12px 16px; min-width:150px;
      backdrop-filter:blur(10px);
    }}
    #legend h3 {{ color:#7eb8f7; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
    .li {{ display:flex; align-items:center; gap:8px; margin:5px 0; font-size:11px; color:#bbb; }}
    .lc {{ width:14px; height:14px; border-radius:3px; flex-shrink:0; }}
    #controls {{
      position:fixed; bottom:16px; left:50%; transform:translateX(-50%);
      background:rgba(0,0,0,0.7); border:1px solid #2a3a4a;
      border-radius:8px; padding:9px 20px; font-size:11px; color:#666;
      backdrop-filter:blur(6px); white-space:nowrap;
    }}
    #loading {{
      position:fixed; inset:0; background:#0a0a12;
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      z-index:100; gap:14px;
    }}
    #loading h1 {{ font-size:20px; color:#7eb8f7; letter-spacing:3px; font-weight:300; }}
    #loading p {{ color:#555; font-size:12px; }}
    .bar-wrap {{ width:240px; height:3px; background:#1a1a2e; border-radius:2px; overflow:hidden; }}
    .bar {{ height:100%; background:linear-gradient(90deg,#2a5faa,#7eb8f7); animation:ld 1.4s ease-in-out infinite; }}
    @keyframes ld {{ 0%{{width:0%}} 60%{{width:85%}} 100%{{width:100%}} }}
  </style>
</head>
<body>
<div id="loading">
  <h1>AXEV 3D VIEWER</h1>
  <p>A carregar terreno procedural...</p>
  <div class="bar-wrap"><div class="bar"></div></div>
  <p style="font-size:10px;color:#333;margin-top:4px">Terminalia/WorldGen Forge v0.2 · Seed {seed}</p>
</div>

<div id="c"></div>

<div id="ui">
  <h2>🌍 {world_name}</h2>
  <p>Seed: <strong style="color:#fff">{seed}</strong></p>
  <p>Motor: Terminalia v0.2 · CPU-only</p>
  <p>Gerado via GitHub Actions</p>
  <div style="margin-top:8px">
{regions_tags}  </div>
</div>

<div id="legend">
  <h3>Altitude</h3>
  <div class="li"><div class="lc" style="background:#1a4a8a"></div>Água</div>
  <div class="li"><div class="lc" style="background:#a89060"></div>Praia</div>
  <div class="li"><div class="lc" style="background:#2d6e2d"></div>Planície</div>
  <div class="li"><div class="lc" style="background:#4a6e28"></div>Colina</div>
  <div class="li"><div class="lc" style="background:#7a6040"></div>Montanha</div>
  <div class="li"><div class="lc" style="background:#eeeeee"></div>Neve</div>
</div>

<div id="controls">
  🖱 Arrastar — rodar &nbsp;|&nbsp; Scroll — zoom &nbsp;|&nbsp; Btn dir — mover &nbsp;|&nbsp; Duplo clique — reset
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(async function() {{
  let td;
  try {{
    const r = await fetch('terrain_data.json');
    td = await r.json();
  }} catch(e) {{
    td = fallback();
  }}
  document.getElementById('loading').style.display = 'none';

  const container = document.getElementById('c');
  const W = container.clientWidth, H = container.clientHeight;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060810);
  scene.fog = new THREE.FogExp2(0x060810, 0.0006);

  const camera = new THREE.PerspectiveCamera(52, W/H, 0.1, 10000);

  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(W, H);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0x334466, 0.5));
  const sun = new THREE.DirectionalLight(0xfff4e0, 1.3);
  sun.position.set(300, 500, 200);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  const sc = sun.shadow.camera;
  sc.left = sc.bottom = -600; sc.right = sc.top = 600;
  sc.near = 10; sc.far = 2000;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x446688, 0.25);
  fill.position.set(-300, 150, -400);
  scene.add(fill);

  const tw = td.width, th = td.height;
  const sc2 = 800 / Math.max(tw, th);
  const hScale = 180;
  const geo = new THREE.PlaneGeometry(tw*sc2, th*sc2, tw-1, th-1);
  geo.rotateX(-Math.PI/2);
  const pos = geo.attributes.position;
  const cols = [];
  const hs = td.heights;
  for (let i = 0; i < pos.count; i++) {{
    const h = hs[i] || 0;
    pos.setY(i, h * hScale);
    let r,g,b;
    if      (h < 0.07) {{ r=0.07; g=0.20; b=0.50; }}
    else if (h < 0.15) {{ r=0.68; g=0.58; b=0.40; }}
    else if (h < 0.35) {{ r=0.20; g=0.46; b=0.20; }}
    else if (h < 0.55) {{ r=0.36; g=0.50; b=0.20; }}
    else if (h < 0.72) {{ r=0.50; g=0.40; b=0.28; }}
    else if (h < 0.88) {{ r=0.54; g=0.50; b=0.46; }}
    else               {{ r=0.92; g=0.94; b=0.98; }}
    cols.push(r,g,b);
  }}
  geo.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
  geo.computeVertexNormals();

  const mesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({{ vertexColors: true }}));
  mesh.castShadow = mesh.receiveShadow = true;
  scene.add(mesh);
  scene.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({{ color: 0x1a2a3a, wireframe: true, transparent: true, opacity: 0.05 }})));

  const waterGeo = new THREE.PlaneGeometry(tw*sc2, th*sc2);
  waterGeo.rotateX(-Math.PI/2);
  const waterMesh = new THREE.Mesh(waterGeo, new THREE.MeshLambertMaterial({{ color: 0x1a4a8a, transparent: true, opacity: 0.72 }}));
  waterMesh.position.y = 0.07 * hScale;
  scene.add(waterMesh);

  const sv = [];
  for (let i = 0; i < 2500; i++) sv.push((Math.random()-.5)*9000, 300+Math.random()*3500, (Math.random()-.5)*9000);
  const sg = new THREE.BufferGeometry();
  sg.setAttribute('position', new THREE.Float32BufferAttribute(sv, 3));
  scene.add(new THREE.Points(sg, new THREE.PointsMaterial({{ color: 0xffffff, size: 1.0, transparent: true, opacity: 0.55 }})));

  let drag=false, rDrag=false, lx=0, ly=0;
  let theta=0.3, phi=0.55, rad=750, tx=0, tz=0;

  function upCam() {{
    camera.position.set(
      tx + rad * Math.sin(theta) * Math.cos(phi),
      rad * Math.sin(phi),
      tz + rad * Math.cos(theta) * Math.cos(phi)
    );
    camera.lookAt(tx, 0, tz);
  }}
  upCam();

  const el = renderer.domElement;
  el.addEventListener('mousedown', e => {{ drag=true; rDrag=e.button===2; lx=e.clientX; ly=e.clientY; }});
  el.addEventListener('contextmenu', e => e.preventDefault());
  window.addEventListener('mouseup', () => drag=false);
  window.addEventListener('mousemove', e => {{
    if (!drag) return;
    const dx=e.clientX-lx, dy=e.clientY-ly; lx=e.clientX; ly=e.clientY;
    if (rDrag) {{ tx-=dx*.5; tz-=dy*.5; }}
    else {{ theta-=dx*.005; phi=Math.max(.06,Math.min(1.45,phi-dy*.005)); }}
    upCam();
  }});
  el.addEventListener('wheel', e => {{ rad=Math.max(80,Math.min(2200,rad+e.deltaY*.5)); upCam(); }});
  el.addEventListener('dblclick', () => {{ theta=.3; phi=.55; rad=750; tx=0; tz=0; upCam(); }});

  let lt=null;
  el.addEventListener('touchstart', e => {{ lt=e.touches[0]; }});
  el.addEventListener('touchmove', e => {{
    e.preventDefault();
    const t=e.touches[0], dx=t.clientX-lt.clientX, dy=t.clientY-lt.clientY;
    theta-=dx*.005; phi=Math.max(.06,Math.min(1.45,phi-dy*.005)); lt=t; upCam();
  }}, {{ passive:false }});

  window.addEventListener('resize', () => {{
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }});

  let t=0;
  function anim() {{
    requestAnimationFrame(anim);
    t+=.001;
    sun.position.set(300*Math.cos(t*.08), 500, 300*Math.sin(t*.08));
    sun.intensity = .9 + .4*Math.sin(t*.05);
    waterMesh.material.opacity = .68 + .04*Math.sin(t*.3);
    renderer.render(scene, camera);
  }}
  anim();

  function fallback() {{
    const W=128, H=128, h=[];
    for (let y=0;y<H;y++) for (let x=0;x<W;x++) {{
      const nx=x/W-.5, ny=y/H-.5;
      let v=0, amp=1, freq=2;
      for (let o=0;o<6;o++) {{ v+=amp*(Math.sin(freq*nx*Math.PI*4+1337)*Math.cos(freq*ny*Math.PI*4+42)); amp*=.5; freq*=2.1; }}
      v=(v+1.5)/3;
      v*=Math.max(0,1-Math.sqrt(nx*nx+ny*ny)*1.8);
      h.push(Math.max(0,Math.min(1,v)));
    }}
    return {{ world_name:'{world_name}', seed:{seed}, width:W, height:H, heights:h }};
  }}
}})();
</script>
</body>
</html>"""

os.makedirs("output/viewer", exist_ok=True)
with open("output/viewer/index.html", "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize("output/viewer/index.html") / 1024
print(f"Visualizador criado: output/viewer/index.html ({size_kb:.1f} KB)")
