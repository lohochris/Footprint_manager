import abc
from decimal import Decimal
from typing import Any, List

from backend.apps.graph.dtos import NodeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO, NodeCentralityDTO
from backend.apps.intelligence.dto.risk import RiskFactorDTO
from backend.apps.intelligence.models.enums import FactorType

class IRiskStrategy(abc.ABC):
    """Defines scoring logic pattern for risk assessment."""

    @abc.abstractmethod
    def evaluate(
        self,
        node: NodeDTO,
        metrics: NodeCentralityDTO,
        analytics: AnalyticsResultDTO,
        context: dict[str, Any],
    ) -> List[RiskFactorDTO]:
        """Return a list of risk factors to apply to the entity."""
        pass


class CentralityStrategy(IRiskStrategy):
    """Assigns risk bonus based on network centrality."""

    def evaluate(
        self,
        node: NodeDTO,
        metrics: NodeCentralityDTO,
        analytics: AnalyticsResultDTO,
        context: dict[str, Any],
    ) -> List[RiskFactorDTO]:
        factors = []
        # If degree centrality is very high, it adds a risk factor
        if metrics.degree > Decimal("0.5"):
            factors.append(
                RiskFactorDTO(
                    factor_type=FactorType.HIGH_CENTRALITY,
                    weight_applied=Decimal("0.20"),
                    description=f"Highly central node (degree: {metrics.degree})",
                )
            )
        return factors


class ConfidenceStrategy(IRiskStrategy):
    """Adjusts risk based on node confidence."""

    def evaluate(
        self,
        node: NodeDTO,
        metrics: NodeCentralityDTO,
        analytics: AnalyticsResultDTO,
        context: dict[str, Any],
    ) -> List[RiskFactorDTO]:
        factors = []
        if node.confidence < Decimal("0.5"):
            factors.append(
                RiskFactorDTO(
                    factor_type=FactorType.CONFIDENCE_ADJUSTMENT,
                    weight_applied=Decimal("-0.10"),
                    description=f"Low confidence entity (confidence: {node.confidence})",
                )
            )
        return factors


class WatchlistProximityStrategy(IRiskStrategy):
    """Checks if node is a watchlist entry or close to one."""

    def evaluate(
        self,
        node: NodeDTO,
        metrics: NodeCentralityDTO,
        analytics: AnalyticsResultDTO,
        context: dict[str, Any],
    ) -> List[RiskFactorDTO]:
        factors = []
        watchlists = context.get("watchlists", [])
        
        # Simple implementation: exact match on label
        for wl in watchlists:
            if wl.entity_value == node.label:
                factors.append(
                    RiskFactorDTO(
                        factor_type=FactorType.WATCHLIST_PROXIMITY,
                        weight_applied=Decimal("0.50"),
                        description=f"Exact watchlist match: {wl.entity_value}",
                    )
                )
                break
                
        return factors
