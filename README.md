# app-astrologia

## Dependencias: Swiss Ephemeris (`swisseph`)

El código usa `import swisseph as swe`. Ese módulo lo proporciona el paquete de PyPI **`pyswisseph`** (no existe un paquete pip llamado `swisseph`).

- Local o CI: `pip install -r requirements.txt` (incluye `pyswisseph`).
- **Railway / otros hosts:** con el mismo `requirements.txt`, el build ejecuta `pip install -r requirements.txt`; tras hacer **push** del repo, el despliegue debería reconstruirse y desaparecer el error `ModuleNotFoundError: No module named 'swisseph'`.

Si el README o un tutorial decía “añade `swisseph` al requirements”, sustitúyelo por **`pyswisseph`** como en este proyecto.
