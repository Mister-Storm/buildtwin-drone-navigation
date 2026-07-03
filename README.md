# BuildTwin Drone Navigation Service 🚁

Serviço de planejamento de missões autônomas para drones. Calcula rotas de cobertura boustrophedon (zigue-zague) a partir de um polígono do terreno, com cálculo automático de altitude, densidade de fotos e waypoints.

---

## Arquitetura

```
Frontend (Next.js)        Kotlin Backend              Python Service
       │                       │                           │
       │  POST /drone-mission  │                           │
       ├──────────────────────►│  POST /plan-mission       │
       │                       ├──────────────────────────►│
       │                       │                           │
       │                       │  Boustrophedon + Camera   │
       │                       │◄──────────────────────────│
       │◄──────────────────────┤                           │
       │    Waypoints + Stats  │                           │
```

## API

### POST `/plan-mission`

Planeja uma missão a partir de um polígono da área.

**Request:**

```json
{
  "boundary": [
    {"lat": -23.5505, "lon": -46.6333},
    {"lat": -23.5505, "lon": -46.6300},
    {"lat": -23.5480, "lon": -46.6300},
    {"lat": -23.5480, "lon": -46.6333}
  ],
  "photos_per_m2": 0.01,
  "altitude_m": null,
  "overlap_front": 0.75,
  "overlap_side": 0.60,
  "speed_mps": 10.0,
  "margin_m": 0.0
}
```

| Campo | Tipo | Default | Descrição |
|---|---|---|---|
| `boundary` | `[GeoPoint]` | — | Vértices do polígono (mín. 3) |
| `photos_per_m2` | `float` | 0.5 | Densidade desejada (fotos/m²) |
| `altitude_m` | `float?` | `null` | Altitude fixa (null = calculada autom.) |
| `overlap_front` | `float` | 0.75 | Sobreposição frontal entre fotos |
| `overlap_side` | `float` | 0.60 | Sobreposição lateral entre passes |
| `speed_mps` | `float` | 10.0 | Velocidade de voo (m/s) |
| `margin_m` | `float` | 0.0 | Margem de segurança da borda |

**Response:**

```json
{
  "waypoints": [
    {
      "lat": -23.5480,
      "lon": -46.6333,
      "altitudeMeters": 80.0,
      "headingDeg": 90.0,
      "triggerCamera": false,
      "speedMps": 10.0
    }
  ],
  "stats": {
    "areaSquareMeters": 93510.24,
    "altitudeMeters": 80.0,
    "totalDistanceMeters": 23964.9,
    "estimatedTimeSeconds": 2396.0,
    "photoCount": 6374,
    "photosPerM2": 0.068,
    "gsdCmPerPixel": 0.27
  },
  "camera": {
    "model": "DJI Phantom 4 Pro",
    "sensorWidthMm": 13.2,
    "sensorHeightMm": 8.8,
    "focalLengthMm": 8.8,
    "imageWidthPx": 5472,
    "imageHeightPx": 3648
  },
  "parameters": {
    "overlapFront": 0.75,
    "overlapSide": 0.60,
    "flightSpeedMps": 10.0,
    "marginMeters": 0.0
  }
}
```

### GET `/health`

```json
{"status": "ok"}
```

---

## Como rodar

### Local (dev)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8091 --reload
```

### Docker

```bash
docker build -t buildtwin-drone-navigation .
docker run -p 8091:8091 buildtwin-drone-navigation
```

---

## Stack

- **Python** 3.12 com **FastAPI**
- **Shapely** para geometria de polígonos
- **Modelo de câmera**: DJI Phantom 4 Pro (padrão)

## Algoritmos

### Boustrophedon (cobertura em zigue-zague)

Gera passes paralelos no eixo de menor largura do polígono, alternando direção a cada linha — padrão clássico de voo de mapeamento aéreo.

### Cálculo de câmera

```
GSD = (altitude × sensor_width) / (focal_length × image_width)
Footprint = GSD × resolução (largura × altura)
```

### Projeção geoespacial

- Coordenadas geográficas → plano cartesiano local (projeção ao redor do centroide)
- Distância Haversine para precisão sub-métrica
- Rotação do polígono para alinhar passes com o eixo dominante

## Próximos passos

- [ ] Suporte a MAVLink para comunicação com drone real
- [ ] Simulador de voo com mapa interativo
- [ ] No-fly zones e evitamento de obstáculos
- [ ] Exportação de missão no formato DJI (KMZ)
- [ ] Cálculo de overlap real com relevo (SRTM)
