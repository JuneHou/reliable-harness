"""The verdict estimator of exp-2026-10-23-v. Pure functions over pass counts, no file access.

A side is a list of (cell, y, enacted) tuples, one per run. y is 1 for a pass. enacted is True, False or None
(not observable). Every probability is computed from Jeffreys Beta posteriors, Beta(k + 0.5, n - k + 0.5),
by one dimensional numerical integration. No random draws.
"""

from collections import Counter, defaultdict

from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import beta, fisher_exact

LEVEL = 0.95
DELTAS = (0.1, 0.2)


def posterior(k: int, n: int):
    return beta(k + 0.5, n - k + 0.5)


def jeffreys(k: int, n: int, level: float = LEVEL) -> tuple[float, float]:
    """Equal tailed interval of the pass probability."""
    d = posterior(k, n)
    return float(d.ppf((1 - level) / 2)), float(d.ppf(1 - (1 - level) / 2))


def _expect_over_without(d0, g) -> float:
    """E[g(p0)] under the without side posterior, by the substitution u = F0(p0), which removes the end point
    singularities of a Beta density with a shape parameter below one."""
    return float(quad(lambda u: g(float(d0.ppf(u))), 0.0, 1.0, limit=200)[0])


def prob_delta_below(k1, n1, k0, n0, t: float) -> float:
    """P(p1 - p0 < t) for independent posteriors."""
    d1, d0 = posterior(k1, n1), posterior(k0, n0)
    return _expect_over_without(d0, lambda p0: d1.cdf(min(1.0, max(0.0, p0 + t))))


def prob_delta_close(k1, n1, k0, n0, delta: float) -> float:
    """P(|p1 - p0| < delta)."""
    d1, d0 = posterior(k1, n1), posterior(k0, n0)
    return _expect_over_without(d0, lambda p0: d1.cdf(min(1.0, p0 + delta)) - d1.cdf(max(0.0, p0 - delta)))


def delta_quantile(k1, n1, k0, n0, q: float) -> float:
    return float(brentq(lambda t: prob_delta_below(k1, n1, k0, n0, t) - q, -1.0, 1.0, xtol=1e-6))


def contrast(k1, n1, k0, n0, level: float = LEVEL, deltas=DELTAS) -> dict:
    """Posterior quantities of Delta = p_with - p_without."""
    lo, hi = delta_quantile(k1, n1, k0, n0, (1 - level) / 2), delta_quantile(k1, n1, k0, n0, 1 - (1 - level) / 2)
    below = prob_delta_below(k1, n1, k0, n0, 0.0)
    return {"p_with_mean": (k1 + 0.5) / (n1 + 1), "p_without_mean": (k0 + 0.5) / (n0 + 1),
            "delta_mean": (k1 + 0.5) / (n1 + 1) - (k0 + 0.5) / (n0 + 1), "delta_interval": [lo, hi],
            "p_delta_positive": 1.0 - below, "p_delta_negative": below,
            "p_delta_close": {str(d): prob_delta_close(k1, n1, k0, n0, d) for d in deltas}}


def pn_ps(p_with: float, p_without: float) -> dict:
    """Probability of necessity and of sufficiency at the given probabilities, under monotonicity, with the
    Tian and Pearl bounds for PN without it. None when a denominator is zero."""
    d = p_with - p_without
    out = {"pn": None, "ps": None, "pn_bounds": None}
    if p_with > 0:
        out["pn"] = d / p_with
        out["pn_bounds"] = [max(0.0, d / p_with), min(1.0, (1 - p_without) / p_with)]
    if p_without < 1:
        out["ps"] = d / (1 - p_without)
    return out


def fisher_p(k1, n1, k0, n0) -> float:
    return float(fisher_exact([[k1, n1 - k1], [k0, n0 - k0]])[1])


def cells_of(side: list[tuple]) -> dict:
    counts = defaultdict(lambda: [0, 0])
    for cell, y, _ in side:
        counts[cell][0] += int(bool(y))
        counts[cell][1] += 1
    return {cell: {"k": k, "n": n, "mean": (k + 0.5) / (n + 1), "interval": list(jeffreys(k, n))} for cell, (k, n) in counts.items()}


def enactment(side: list[tuple]) -> dict:
    """Enactment rate of the with side. rate is None when enactment is not observable for any run."""
    states = Counter("null" if e is None else ("yes" if e else "no") for _, _, e in side)
    if states["null"]:
        return {"enacted": states["yes"], "runs": len(side), "rate": None, "state": "not_observable"}
    rate = states["yes"] / len(side) if side else None
    return {"enacted": states["yes"], "runs": len(side), "rate": rate,
            "state": "never_enacted" if rate == 0 else ("observed" if rate is not None else "no_runs")}


def survives(verdict: str, c: dict, delta: float, level: float = LEVEL):
    """The survival rule per recorded verdict value. None when the verdict carries no survival label."""
    if verdict == "required_in_context":
        return c["p_delta_positive"] >= level
    if verdict == "removable_in_context":
        return c["p_delta_close"][str(delta)] >= level
    return None


def summarise_comparison(with_side: list[tuple], without_side: list[tuple], verdict: str, delta: float = 0.2,
                         required_cells=None) -> dict:
    """Every quantity of one comparison row. The contrast pools the cells present on both sides, restricted to
    required_cells when given (the checks the recorded verdict was computed on)."""
    cw, cwo = cells_of(with_side), cells_of(without_side)
    shared = sorted(set(cw) & set(cwo), key=str)
    if required_cells is not None:
        shared = [c for c in shared if c in set(required_cells)]
    k1, n1 = sum(cw[c]["k"] for c in shared), sum(cw[c]["n"] for c in shared)
    k0, n0 = sum(cwo[c]["k"] for c in shared), sum(cwo[c]["n"] for c in shared)
    row = {"recorded_verdict": verdict, "shared_cells": [list(c) if isinstance(c, tuple) else c for c in shared],
           "with_only_cells": sorted((set(cw) - set(cwo)), key=str), "without_only_cells": sorted((set(cwo) - set(cw)), key=str),
           "with": {"k": k1, "n": n1, "interval": list(jeffreys(k1, n1)) if n1 else None},
           "without": {"k": k0, "n": n0, "interval": list(jeffreys(k0, n0)) if n0 else None},
           "enactment": enactment(with_side), "delta_margin": delta}
    if n1 and n0:
        c = contrast(k1, n1, k0, n0)
        row["contrast"] = c
        row.update(pn_ps(c["p_with_mean"], c["p_without_mean"]))
        row["fisher_p"] = fisher_p(k1, n1, k0, n0)
        en = row["enactment"]
        row["cace"] = (c["delta_mean"] / en["rate"]) if en["rate"] else None
        row["survives"] = survives(verdict, c, delta)
    else:
        row.update({"contrast": None, "pn": None, "ps": None, "pn_bounds": None, "fisher_p": None, "cace": None, "survives": None})
    return row
