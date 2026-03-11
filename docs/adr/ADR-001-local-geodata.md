# ADR-001: Geodatos Locales para MVP

## Estado
Accepted

## Contexto
El sistema necesita resolver `birth_place` a coordenadas y timezone para calcular la carta.
Se podia usar API externa o dataset local.

## Decision
Usar dataset local (`cities_test.csv`) como fuente principal.

## Motivo
- reducir complejidad inicial
- evitar dependencias de red
- asegurar reproducibilidad en pruebas
- controlar la calidad de entradas

## Consecuencias
### Positivas
- flujo estable y deterministico
- debugging simple

### Negativas
- cobertura parcial de ciudades
- necesidad de mantenimiento del dataset

