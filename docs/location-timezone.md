# Resolucion de Ciudad y Timezone

## Objetivo
Resolver `birth_place` de forma local para obtener:
- `latitude`
- `longitude`
- `timezone` (IANA)

y convertir fecha/hora local a UTC para el calculo astral.

## Implementacion Actual
- Fuente local: `astrology/location/cities_test.csv`
- Logica principal: `astrology/location/place.py`
  - normalizacion de texto (minusculas, sin tildes, espacios compactados)
  - indice cacheado por `query`
  - fallback por inclusion de texto
  - conversion de hora local a UTC con `zoneinfo`

## Por Que Local-First
Decision tomada para:
- evitar dependencia de red
- facilitar pruebas reproducibles
- reducir complejidad inicial del MVP
- controlar calidad de datos de entrada

## Comportamiento de Errores
Si la ciudad no existe en el CSV, se lanza error explicito para forzar:
- expansion del dataset
- correccion de input

## Limitaciones Conocidas
- cobertura parcial de ciudades
- matching basado en texto simple
- posible ambiguedad en nombres repetidos (ej. ciudades homonimas)

## Evolucion Recomendada
- ampliar dataset local
- introducir alias por ciudad/pais
- opcion de desambiguacion por pais
- cache persistente para busquedas complejas

