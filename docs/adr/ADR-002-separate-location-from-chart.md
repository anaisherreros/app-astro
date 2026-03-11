# ADR-002: Separar Location/Timezone del Calculo de Carta

## Estado
Accepted

## Contexto
Al principio la resolucion de ciudad y timezone estaba acoplada al calculador.
Eso mezclaba responsabilidades distintas.

## Decision
Mover la logica de lugar/hora a `astrology/location/place.py` y dejar
`astrology/charts/calculator.py` enfocado en calculo astral.

## Motivo
- separar responsabilidades
- mejorar mantenibilidad
- facilitar testing por modulo
- preparar evolucion independiente de ambas capas

## Consecuencias
### Positivas
- codigo mas claro
- menor acoplamiento

### Negativas
- mas puntos de integracion a vigilar

