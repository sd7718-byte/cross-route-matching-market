"""Reproduce all numerical results and audit key equilibrium residuals.

The script uses only Python's standard library. Assertions fail loudly if a
reported cutoff, fixed point, stability classification, or fold condition no
longer matches the manuscript.
"""

from __future__ import annotations

import math


P = 0.30
LAMBDA_0 = 2.0
LAMBDA_1 = 3.0
SUBJECTIVE_LAMBDA_0 = 1.0
SUBJECTIVE_LAMBDA_1 = 4.0
GAMMA_0 = 0.05
GAMMA_1 = 0.45
DELTA = 0.90
L_A = 1.00
L_H = 1.60
S_H = 1.10
R = 0.50

# Two-sided illustration: F(z) = logistic(SLOPE * (z - CENTER)).
SLOPE = 10.0
CENTER = 0.55
MU = 1.0
B_P = 1.0
B_R = 1.0


def poisson_pmf(n: int, rate: float) -> float:
    return math.exp(-rate) * rate**n / math.factorial(n)


def posterior(n: int, rate_0: float, rate_1: float) -> float:
    prior_odds = P / (1.0 - P)
    odds = prior_odds * math.exp(-(rate_1 - rate_0)) * (rate_1 / rate_0) ** n
    return odds / (1.0 + odds)


def conversion_probability(prob_high: float) -> float:
    return GAMMA_0 + (GAMMA_1 - GAMMA_0) * prob_high


def mixture_pmf(n: int) -> float:
    return (1.0 - P) * poisson_pmf(n, LAMBDA_0) + P * poisson_pmf(n, LAMBDA_1)


def logistic_cdf(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-SLOPE * (z - CENTER)))


def logistic_density_at_cdf_value(value: float) -> float:
    return SLOPE * value * (1.0 - value)


def bisect_root(function, lower: float, upper: float, iterations: int = 100) -> float:
    f_lower = function(lower)
    f_upper = function(upper)
    if f_lower == 0.0:
        return lower
    if f_upper == 0.0:
        return upper
    assert f_lower * f_upper < 0.0, (lower, upper, f_lower, f_upper)
    for _ in range(iterations):
        midpoint = (lower + upper) / 2.0
        f_midpoint = function(midpoint)
        if f_lower * f_midpoint <= 0.0:
            upper = midpoint
            f_upper = f_midpoint
        else:
            lower = midpoint
            f_lower = f_midpoint
    return (lower + upper) / 2.0


def symmetric_fixed_points(alpha: float, grid_size: int = 100_000) -> list[float]:
    """Find every root of x = F(alpha*x) on [0,1] by bracketed bisection."""
    gap = lambda x: logistic_cdf(alpha * x) - x
    roots: list[float] = []
    left = 0.0
    f_left = gap(left)
    for index in range(1, grid_size + 1):
        right = index / grid_size
        f_right = gap(right)
        if f_left == 0.0:
            root = left
        elif f_left * f_right < 0.0:
            root = bisect_root(gap, left, right)
        else:
            root = None
        if root is not None and (not roots or abs(root - roots[-1]) > 1e-7):
            roots.append(root)
        left, f_left = right, f_right
    return roots


def high_fold() -> tuple[float, float]:
    """Solve the symmetric fold conditions x=F(alpha*x), alpha*F'=1."""
    def fold_gap(x: float) -> float:
        alpha = 1.0 / (SLOPE * x * (1.0 - x))
        return math.log(x / (1.0 - x)) - SLOPE * (alpha * x - CENTER)

    x_star = bisect_root(fold_gap, 0.80, 0.95)
    alpha_star = 1.0 / (SLOPE * x_star * (1.0 - x_star))
    return x_star, alpha_star


def main() -> None:
    gamma_star = (
        (1.0 + DELTA) * L_A - S_H - DELTA * R * L_A
    ) / (DELTA * (L_H - R * L_A))
    pi_star = (gamma_star - GAMMA_0) / (GAMMA_1 - GAMMA_0)

    rows: list[tuple[int, float, float, float, float]] = []
    true_threshold = None
    subjective_threshold = None
    for n in range(100):
        pi = posterior(n, LAMBDA_0, LAMBDA_1)
        pi_subjective = posterior(n, SUBJECTIVE_LAMBDA_0, SUBJECTIVE_LAMBDA_1)
        gamma = conversion_probability(pi)
        gamma_subjective = conversion_probability(pi_subjective)
        rows.append((n, pi, pi_subjective, gamma, gamma_subjective))
        if true_threshold is None and gamma >= gamma_star:
            true_threshold = n
        if subjective_threshold is None and gamma_subjective >= gamma_star:
            subjective_threshold = n

    assert true_threshold == 8
    assert subjective_threshold == 4
    distortion_counts = range(subjective_threshold, true_threshold)
    distortion_mass = sum(mixture_pmf(n) for n in distortion_counts)
    expected_loss = sum(
        mixture_pmf(n)
        * DELTA
        * (L_H - R * L_A)
        * (gamma_star - rows[n][3])
        for n in distortion_counts
    )
    calibrated_acceptance = sum(mixture_pmf(n) for n in range(true_threshold))
    subjective_acceptance = sum(mixture_pmf(n) for n in range(subjective_threshold))

    # Posterior log-odds identities and monotonicity checks.
    # Restrict the numerical logit check away from floating-point saturation.
    for n, pi, pi_subjective, _, _ in rows[:15]:
        true_log_odds = math.log(pi / (1.0 - pi))
        subjective_log_odds = math.log(pi_subjective / (1.0 - pi_subjective))
        analytic_wedge = n * math.log(
            (SUBJECTIVE_LAMBDA_1 / SUBJECTIVE_LAMBDA_0)
            / (LAMBDA_1 / LAMBDA_0)
        ) - (
            (SUBJECTIVE_LAMBDA_1 - SUBJECTIVE_LAMBDA_0)
            - (LAMBDA_1 - LAMBDA_0)
        )
        assert abs((subjective_log_odds - true_log_odds) - analytic_wedge) < 1e-9

    x_star, alpha_star = high_fold()
    calibrated_roots = symmetric_fixed_points(calibrated_acceptance)
    subjective_roots = symmetric_fixed_points(subjective_acceptance)
    assert len(calibrated_roots) == 3
    assert len(subjective_roots) == 1
    assert subjective_acceptance < alpha_star < calibrated_acceptance

    # Residual and local-stability audit. H'(x)=[alpha*F'(alpha*x)]^2.
    def composed_slope(alpha: float, root: float) -> float:
        density = logistic_density_at_cdf_value(root)
        return (alpha * density) ** 2

    for alpha, roots in (
        (calibrated_acceptance, calibrated_roots),
        (subjective_acceptance, subjective_roots),
    ):
        for root in roots:
            assert abs(logistic_cdf(alpha * root) - root) < 1e-11
    assert composed_slope(calibrated_acceptance, calibrated_roots[0]) < 1.0
    assert composed_slope(calibrated_acceptance, calibrated_roots[1]) > 1.0
    assert composed_slope(calibrated_acceptance, calibrated_roots[2]) < 1.0
    assert composed_slope(subjective_acceptance, subjective_roots[0]) < 1.0

    # Numerical instance of all four fold conditions in Proposition 5.
    fold_density = logistic_density_at_cdf_value(x_star)
    fold_second_density = SLOPE**2 * x_star * (1.0 - x_star) * (1.0 - 2.0 * x_star)
    h_x = (alpha_star * fold_density) ** 2
    h_xx = 2.0 * alpha_star**2 * fold_second_density
    h_alpha = 2.0 * fold_density * x_star
    assert abs(logistic_cdf(alpha_star * x_star) - x_star) < 1e-11
    assert abs(h_x - 1.0) < 1e-10
    assert h_xx < 0.0
    assert h_alpha > 0.0

    calibrated_high = calibrated_roots[-1]
    subjective_low = subjective_roots[0]
    calibrated_high_volume = MU * calibrated_acceptance * calibrated_high**2
    subjective_low_volume = MU * subjective_acceptance * subjective_low**2

    print(f"gamma_star={gamma_star:.10f}")
    print(f"pi_star={pi_star:.10f}")
    print(f"true_threshold={true_threshold}")
    print(f"subjective_threshold={subjective_threshold}")
    print(f"distortion_mass={distortion_mass:.10f}")
    print(f"expected_loss={expected_loss:.10f}")
    print(f"calibrated_acceptance={calibrated_acceptance:.10f}")
    print(f"subjective_acceptance={subjective_acceptance:.10f}")
    print(f"fold_x={x_star:.10f}")
    print(f"fold_alpha={alpha_star:.10f}")
    print("calibrated_roots=" + ",".join(f"{root:.10f}" for root in calibrated_roots))
    print("subjective_roots=" + ",".join(f"{root:.10f}" for root in subjective_roots))
    print(f"calibrated_high_volume={calibrated_high_volume:.10f}")
    print(f"subjective_low_volume={subjective_low_volume:.10f}")
    print("all_residual_checks=PASS")
    print("\n n   pi(n)  pi_tilde(n)  gamma(n)  gamma_tilde(n)")
    for n, pi, pi_subjective, gamma, gamma_subjective in rows[3:9]:
        print(
            f"{n:2d}  {pi:6.3f}      {pi_subjective:6.3f}"
            f"      {gamma:6.3f}          {gamma_subjective:6.3f}"
        )


if __name__ == "__main__":
    main()
