from __future__ import annotations

import hashlib
import itertools
import logging
from collections import Counter

from ..core.config import settings
from ..core.schemas import AssetState, ScoredCOA, ScoredCOAPackage
from .plan_packages import build_plan_package

logger = logging.getLogger("coa_engine.engine.portfolio")


def _asset_pool(
    asset_states: list[AssetState] | None,
    asset_inventory: dict[str, int] | None,
) -> dict[str, int]:
    if asset_states:
        return {
            asset.asset_id: max(int(asset.quantity_available), 0)
            for asset in asset_states
        }
    if asset_inventory:
        return {asset_id: max(int(qty), 0) for asset_id, qty in asset_inventory.items()}
    return {}


def _is_globally_feasible(
    combo: tuple[ScoredCOA, ...],
    pool: dict[str, int],
) -> tuple[bool, Counter[str]]:
    usage: Counter[str] = Counter()
    for scored in combo:
        usage.update(scored.coa.assigned_assets)
    if not pool:
        return True, usage
    return all(usage[asset_id] <= pool.get(asset_id, 0) for asset_id in usage), usage


def _package_score(combo: tuple[ScoredCOA, ...], usage: Counter[str]) -> tuple[float, float, str]:
    members = list(combo)
    mean_score = sum(item.total_score for item in members) / len(members)
    mean_feasibility = sum(item.coa.feasibility_score for item in members) / len(members)
    unique_targets = {target for item in members for target in item.coa.target_entities}
    unique_templates = {item.coa.template_id for item in members}
    member_assets = [asset for item in members for asset in item.coa.assigned_assets]

    coordination_bonus = min(8.0, 1.5 * len(unique_targets))
    diversity_bonus = min(5.0, 2.0 * max(len(unique_templates) - 1, 0))
    logistics_penalty = min(
        8.0,
        8.0 * (sum(item.coa.logistics_burden for item in members) / len(members)),
    )
    duplicate_asset_penalty = max(sum(max(count - 1, 0) for count in usage.values()) * 1.5, 0.0)

    total = mean_score + coordination_bonus + diversity_bonus - logistics_penalty - duplicate_asset_penalty
    total *= 0.4 + 0.6 * mean_feasibility
    total = round(max(0.0, min(total, 100.0)), 1)

    notes: list[str] = [
        f"{len(members)}-COA package",
        f"{len(unique_targets)} target entity coverage",
    ]
    if len(unique_templates) > 1:
        notes.append(f"{len(unique_templates)} complementary templates")
    if duplicate_asset_penalty > 0:
        notes.append("Shared asset contention inside package")
    if member_assets:
        notes.append(f"{len(set(member_assets))} distinct assigned assets")

    return total, round(mean_feasibility, 3), "; ".join(notes)


def build_portfolios(
    scored: list[ScoredCOA],
    asset_states: list[AssetState] | None = None,
    asset_inventory: dict[str, int] | None = None,
    max_package_size: int | None = None,
    candidate_pool: int | None = None,
    max_packages: int | None = None,
) -> list[ScoredCOAPackage]:
    """Build globally feasible multi-COA packages over the scored alternatives."""
    if len(scored) < 2:
        return []

    pool = _asset_pool(asset_states, asset_inventory)
    max_package_size = max(2, max_package_size or settings.portfolio_max_coas)
    candidate_pool = max(2, candidate_pool or settings.portfolio_candidate_pool)
    max_packages = max(1, max_packages or settings.portfolio_max_packages)

    candidates = scored[:candidate_pool]
    packages: list[ScoredCOAPackage] = []
    seen_signatures: set[tuple[str, ...]] = set()

    for size in range(2, min(max_package_size, len(candidates)) + 1):
        for combo in itertools.combinations(candidates, size):
            signature = tuple(sorted(item.coa.coa_id for item in combo))
            if signature in seen_signatures:
                continue
            feasible, usage = _is_globally_feasible(combo, pool)
            if not feasible:
                continue

            targets = {target for item in combo for target in item.coa.target_entities}
            if len(targets) < len(combo):
                # Avoid packaging COAs that mostly pile onto the same entity.
                continue

            total_score, feasibility_score, tradeoff = _package_score(combo, usage)
            package_id = "PKG-" + hashlib.sha256("|".join(signature).encode("utf-8")).hexdigest()[:10]
            package = ScoredCOAPackage(
                package_id=package_id,
                coas=list(combo),
                combined_assets=sorted(usage.keys()),
                feasibility_score=feasibility_score,
                total_score=total_score,
                rank=0,
                tradeoff_explanation=tradeoff,
            )
            package.plan = build_plan_package(package)
            packages.append(package)
            seen_signatures.add(signature)

    packages.sort(key=lambda item: item.total_score, reverse=True)
    packages = packages[:max_packages]
    for index, package in enumerate(packages, start=1):
        package.rank = index

    if packages:
        logger.info(
            "Portfolio allocator built %d feasible package(s), top=%s (%.1f)",
            len(packages),
            packages[0].package_id,
            packages[0].total_score,
        )
    return packages
