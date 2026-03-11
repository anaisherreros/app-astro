# Motor Astrologico

## Alcance Actual
El motor calcula:
- planetas (Sun a Pluto)
- casas
- ascendente y MC
- nodo norte y nodo sur
- aspectos
- planetas inaspectados

## Calculo Base de Carta
Archivo: `astrology/charts/calculator.py`

Pasos principales:
1. Recibir contexto resuelto (ciudad/timezone/UTC) desde `place.py`.
2. Convertir a dia juliano UTC.
3. Calcular casas y angulos con Swiss Ephemeris.
4. Calcular posiciones planetarias y nodos.
5. Calcular aspectos e inaspectados.

## Aspectos Activos
Archivo: `astrology/charts/aspects.py`

Set final:
- conjunction
- sextile (blue)
- trine (blue)
- semi_sextile (green)
- quincunx (green)
- square (red)
- opposition (red)

## Regla de Orbes (Huber Adaptada)
Se aplica el orbe del punto con mayor prioridad en la pareja:

`north_node > personality_planets > major_planets > minor_planets`

### Grupos
- `personality_planets`: sun, moon, saturn
- `major_planets`: jupiter, uranus, neptune, pluto
- `minor_planets`: mercury, venus, mars
- `north_node`: prioridad maxima

## Regla de Inaspectados
Un planeta se considera inaspectado si no tiene ningun aspecto distinto de conjuncion.

Es decir:
- tener solo conjunciones no basta para "estar aspectado"
- necesita al menos un aspecto no-conjuncion

## Decisiones Relevantes
- Mantener conjunto de aspectos reducido para claridad interpretativa.
- Priorizar coherencia de metodo sobre cantidad de tecnicas activas.
- Añadir trazabilidad por aspecto (`allowed_orb`, `priority_group`) para auditar decisiones.

