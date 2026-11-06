# VectorizadorSVG

> Convierte imágenes PNG, JPEG, WebP, GIF y BMP a vectores SVG de alta calidad.  
> Alternativa open source a vectorizer.ai · FastAPI + React + OpenCV + vtracer

[![CI/CD](https://github.com/pameeesd/vectorizador-svg/actions/workflows/ci.yml/badge.svg)](https://github.com/pameeesd/vectorizador-svg/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Características

| Feature | Detalle |
|---------|---------|
| 🎨 Vectorización en color | Colores reales → capas SVG apiladas |
| ◑ Modo binario | B&W con umbralización Otsu |
| 🔧 Parámetros ajustables | 8 controles en tiempo real |
| 🔒 Validación segura | Magic bytes, rate limiting, CSP, non-root Docker |
| 🐳 Docker Compose | Un comando para levantar todo |
| ⚡ CI/CD | Lint, tests, Trivy scan, npm audit en cada push |
| 📦 Sin dependencias externas de pago | 100% open source |

---

## 🚀 Inicio rápido

### Con Docker (recomendado)

```bash
git clone https://github.com/pameeesd/vectorizador-svg.git
cd vectorizador-svg

# Configurar variables de entorno del backend
cp backend/.env.example backend/.env
# Edita backend/.env y cambia SECRET_KEY

docker compose up --build
```

Abre **http://localhost** en tu navegador.

### Desarrollo local

#### Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env              # Edita SECRET_KEY

uvicorn app.main:app --reload --port 8000
```

#### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Abre **http://localhost:5173**

---

## 🏗️ Arquitectura

```
vectorizador-svg/
├── backend/
│   ├── app/
│   │   ├── api/        # Rutas FastAPI
│   │   ├── core/       # Config + Security
│   │   └── services/   # Lógica de vectorización (OpenCV + vtracer)
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/ # React UI
│   │   ├── hooks/      # useVectorizer
│   │   ├── types/      # TypeScript types
│   │   └── utils/      # API client
│   └── Dockerfile
├── .github/workflows/  # CI/CD + Security audit
├── docker-compose.yml
└── SECURITY.md
```

---

## 🔒 Seguridad

Ver [SECURITY.md](SECURITY.md) para reportar vulnerabilidades.

Medidas implementadas:

- ✅ Validación por **magic bytes** (no solo Content-Type)
- ✅ **Rate limiting** 20 req/min por IP
- ✅ CORS restringido a orígenes configurados
- ✅ **Archivos temporales** eliminados automáticamente tras cada request
- ✅ Docker con usuario **non-root**
- ✅ **Content-Security-Policy** en el frontend
- ✅ Auditoría de dependencias semanal (`pip-audit` + `npm audit` + Trivy)

---

## ⚙️ Parámetros de vectorización

| Parámetro | Descripción | Rango |
|-----------|-------------|-------|
| `color_mode` | `color` o `binary` | — |
| `filter_speckle` | Área mínima de caminos (px²) | 0–100 |
| `color_precision` | Bits por canal (solo color) | 1–8 |
| `layer_difference` | Luminancia mínima entre capas | 1–256 |
| `corner_threshold` | Ángulo de detección de esquinas | 1–180° |
| `length_threshold` | Longitud mínima de segmento | 0.1–10 |
| `max_iterations` | Iteraciones de simplificación | 1–50 |
| `splice_threshold` | Ángulo para fusionar segmentos | 1–180° |

---

## 🧪 Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Haz tus cambios y tests
4. Abre un Pull Request

---

## 📄 Licencia

MIT © 2026 [pameeesd](https://github.com/pameeesd)
