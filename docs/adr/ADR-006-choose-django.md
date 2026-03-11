# ADR-006: Elegir Django como Base del Backend

## Estado
Accepted

## Contexto
Para el backend de la app astrologica se necesitaba:
- rapidez de desarrollo
- estructura clara para crecer a MVP
- ecosistema estable en Python
- facilidad para exponer endpoints y evolucionar reglas de negocio

Se evaluo construir con stack mas minimalista, pero tambien se considero
el valor de una base madura para escalar con menos friccion.

## Decision
Usar Django como framework base del backend.

## Motivo
- framework maduro y muy estable en produccion
- estructura "baterias incluidas" (routing, apps, admin, ORM, seguridad)
- facilita evolucionar desde prototipo a producto sin reescritura grande
- muy buen encaje con logica de dominio en Python (astrologia + IA)
- comunidad amplia y documentacion robusta

## Consecuencias
### Positivas
- base solida para escalar funcionalidades
- organizacion clara por apps/modulos
- herramientas integradas para operaciones y mantenimiento

### Negativas
- algo mas de peso inicial que un microframework
- requiere disciplina para mantener separadas capas (view/service/domain)

## Notas
La decision de Django no impide integrar componentes IA modernos
(RAG, LLM, workers, colas, APIs externas). El motor astrologico sigue
aislado por modulos para mantener flexibilidad tecnica.

