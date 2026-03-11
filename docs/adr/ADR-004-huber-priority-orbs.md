# ADR-004: Orbes por Prioridad (Huber Adaptada)

## Estado
Accepted

## Contexto
El sistema tenia orbe fijo global, pero se definio una regla mas precisa
por tipo de punto y jerarquia.

## Decision
Aplicar orbes segun el punto de mayor prioridad del par:

`north_node > personality_planets > major_planets > minor_planets`

Con definicion de `personality_planets` como:
- sun
- moon
- saturn

## Motivo
- alineacion metodologica con enfoque Huber elegido
- mayor control interpretativo
- decisiones de aspecto auditables por regla explicita

## Consecuencias
### Positivas
- mayor fidelidad al metodo definido
- trazabilidad (`allowed_orb`, `priority_group`)

### Negativas
- logica mas compleja que orbe global

