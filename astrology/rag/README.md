# Submodulo RAG (Astrology)

Este submodulo esta aislado de:
- calculo de carta (`astrology/charts`)
- dibujo/render de carta (frontend)
- cliente de IA (LLM)

## Objetivo

Transformar datos tecnicos de la carta en hechos textuales y priorizarlos para retrieval.

## Flujo actual

1. `facts_builder.build_facts(chart_result)`
   - Convierte JSON de carta en hechos:
     - posiciones
     - aspectos (deduplicados A-B / B-A)
     - inaspectados
2. `scoring.score_facts(facts)`
   - Aplica score por niveles:
     - L1: Nodo Norte
     - L2: Sol, Luna, Saturno, Ascendente
     - L3: Aspectos rojos (oposicion, cuadratura)
     - L4: Aspectos azules (trigono, sextil)
     - L5: resto
3. `selector.select_facts(scored_facts)`
   - Garantiza cobertura minima:
     - posiciones clave (Nodo Norte, Sol, Luna, Saturno, Ascendente)
     - minimo de aspectos rojos
   - Luego completa por score.
4. `build_chunks.py`
   - Lee PDFs en `astrology/rag/data/pdf`
   - Genera chunks en `astrology/rag/data/chunks/chunks.jsonl`
   - Genera estadisticas en `astrology/rag/data/chunks/stats.json`
5. `build_index.py`
   - Lee `chunks.jsonl`
   - Construye indice TF-IDF local en `astrology/rag/data/index/tfidf_index.joblib`
6. `retriever.LocalTfidfRetriever`
   - Ejecuta busqueda por similitud para cada query generada.

## Notas

- El score ordena prioridad, no elimina cobertura total de carta.
- La interpretacion final puede usar `selected_facts` + `overflow_facts` segun contexto disponible.

## Chunking inicial (paso 4)

Ejecutar desde la raiz del repo:

`python -m astrology.rag.build_chunks`

Opciones utiles:
- `--chunk-size 1200`
- `--overlap 180`
- `--min-chars 220`

## Indexado vectorial local

Ejecutar desde la raiz del repo:

`python -m astrology.rag.build_index`
