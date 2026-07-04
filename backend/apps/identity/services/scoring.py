from decimal import Decimal
from typing import Any
from backend.apps.identity.choices import MatchingStrategy
from backend.apps.identity.models.identity import Identity
from backend.apps.identity.services.matching import (
    levenshtein_similarity,
    normalize_domain,
    normalize_email,
    normalize_phone,
    normalize_username,
)


def calculate_identity_similarity(identity_a: Identity, identity_b: Identity) -> dict[str, Any]:
    """Calculate the similarity between two identities based on their attributes and labels.

    Returns:
        A dictionary containing:
        - "overall_score": Decimal
        - "components": list of dict explaining the score components
    """
    components: list[dict[str, Any]] = []
    scores: list[Decimal] = []
    weights: list[Decimal] = []

    # 1. Label Similarity (Fuzzy matching)
    label_a = identity_a.label.strip().lower()
    label_b = identity_b.label.strip().lower()
    if label_a and label_b:
        similarity = levenshtein_similarity(label_a, label_b)
        # Weight for label similarity
        weight = Decimal("0.300")
        components.append({
            "strategy": MatchingStrategy.FUZZY.value,
            "field": "label",
            "weight": str(weight),
            "similarity": str(similarity),
        })
        scores.append(similarity)
        weights.append(weight)

    # Fetch attributes for both identities
    attrs_a = identity_a.attributes.all()
    attrs_b = identity_b.attributes.all()

    # Group attributes by type for matching
    by_type_a: dict[str, list[str]] = {}
    by_type_b: dict[str, list[str]] = {}

    for attr in attrs_a:
        by_type_a.setdefault(attr.type, []).append(attr.value)
    for attr in attrs_b:
        by_type_b.setdefault(attr.type, []).append(attr.value)

    # 2. Attribute-specific matching
    all_types = set(by_type_a.keys()).union(by_type_b.keys())

    for attr_type in all_types:
        vals_a = by_type_a.get(attr_type, [])
        vals_b = by_type_b.get(attr_type, [])
        if not vals_a or not vals_b:
            continue

        best_similarity = Decimal("0.000")
        matched_pair = ("", "")
        strategy_used = MatchingStrategy.EXACT.value

        for va in vals_a:
            for vb in vals_b:
                sim = Decimal("0.000")
                if attr_type == "email":
                    sim = Decimal("1.000") if normalize_email(va) == normalize_email(vb) else Decimal("0.000")
                    strategy_used = MatchingStrategy.EMAIL_NORM.value
                elif attr_type == "phone":
                    sim = Decimal("1.000") if normalize_phone(va) == normalize_phone(vb) else Decimal("0.000")
                    strategy_used = MatchingStrategy.PHONE_NORM.value
                elif attr_type == "username":
                    sim = levenshtein_similarity(normalize_username(va), normalize_username(vb))
                    strategy_used = MatchingStrategy.USERNAME_NORM.value
                elif attr_type == "domain":
                    sim = Decimal("1.000") if normalize_domain(va) == normalize_domain(vb) else Decimal("0.000")
                    strategy_used = MatchingStrategy.DOMAIN_NORM.value
                else:
                    # General attribute matching
                    sim = Decimal("1.000") if va.strip().lower() == vb.strip().lower() else Decimal("0.000")
                    strategy_used = MatchingStrategy.EXACT.value

                if sim > best_similarity:
                    best_similarity = sim
                    matched_pair = (va, vb)

        # Apply weights based on attribute type significance
        if attr_type in ("email", "phone"):
            weight = Decimal("0.500")
        elif attr_type in ("username", "domain"):
            weight = Decimal("0.400")
        else:
            weight = Decimal("0.200")

        components.append({
            "strategy": strategy_used,
            "field": f"attribute_{attr_type}",
            "weight": str(weight),
            "similarity": str(best_similarity),
            "matched_values": matched_pair,
        })
        scores.append(best_similarity)
        weights.append(weight)

    # 3. Overall score calculation
    if not scores:
        return {
            "overall_score": Decimal("0.000"),
            "components": [],
        }

    total_weight = sum(weights)
    weighted_sum = sum(s * w for s, w in zip(scores, weights, strict=False))
    overall_score = weighted_sum / total_weight if total_weight > 0 else Decimal("0.000")
    overall_score = Decimal(str(round(overall_score, 3)))

    return {
        "overall_score": overall_score,
        "components": components,
    }
