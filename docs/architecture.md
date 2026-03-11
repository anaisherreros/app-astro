# Arquitectura Tecnica

## Objetivo
Este proyecto implementa el backend de una app de astrologia con enfoque modular.
El objetivo actual es calcular carta natal base con:
- posiciones planetarias
- casas
- angulos
- nodos
- aspectos

## Flujo End-to-End
1. El cliente envia `birth_date`, `birth_time`, `birth_place`.
2. `astrology/services/chart_service.py` valida presencia de datos y delega el calculo.
3. `astrology/location/place.py` resuelve ciudad, coordenadas y timezone (local-first).
4. `astrology/charts/calculator.py` calcula:
   - dia juliano UTC
   - planetas, casas, nodos y angulos con Swiss Ephemeris
   - aspectos e inaspectados
5. La API devuelve JSON con todos los bloques calculados.

## Modulos Principales
- `astrology/views.py`
  - Endpoint HTTP y serializacion de respuesta/errores.
- `astrology/services/chart_service.py`
  - Capa de orquestacion y validacion minima de entrada.
- `astrology/location/place.py`
  - Resolucion de lugar y conversion horaria.
- `astrology/charts/calculator.py`
  - Calculo astronomico/astrologico base.
- `astrology/charts/aspects.py`
  - Regla de aspectos y planetas inaspectados.

## Decisiones Clave
- Separar geolocalizacion/timezone del calculo de carta.
- Usar dataset local de ciudades para evitar dependencia de APIs.
- Mantener conjunto de aspectos acotado (7) para coherencia interpretativa.
- Aplicar orbes por prioridad Huber adaptada.
- Tratar conjuncion como no suficiente para sacar un planeta de inaspectado.

## Riesgos y Limites Actuales
- `cities_test.csv` no cubre todas las ciudades del mundo.
- Sistema de casas esta fijado en Koch en el calculador.
- Falta suite de tests automatizados de regresion.

## Proximos Pasos
- Anadir tests unitarios para `place.py` y `aspects.py`.
- Versionar configuraciones astrologicas (casas/orbes) por perfil.
- Ampliar dataset de ciudades y estrategia de matching.

