from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


FactType = Literal["position", "aspect", "unaspected"]


@dataclass(frozen=True)
class Fact:
    fact_id: str
    fact_type: FactType
    text_display: str
    level: Optional[str] = None
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SelectionResult:
    selected_facts: List[Fact]
    overflow_facts: List[Fact]
    coverage_report: Dict[str, Any]


@dataclass(frozen=True)
class RetrievalQuery:
    query_id: str
    text_query: str
    source_fact_id: str
    score: float

