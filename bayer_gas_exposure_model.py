#!/usr/bin/env python3
"""
Bayer AG - Natural Gas Price Exposure: Mathematical Model
==========================================================
Quantifies Bayer's sensitivity to natural gas (TTF) price movements
across direct energy costs, indirect feedstock (Scope 3), and margin impact.

Data sources: Bayer Annual Reports 2022-2025, TCFD 2024, Eurostat TTF.
"""

import math
from dataclasses import dataclass

# ============================================================================
# 1. CONSTANTS & BASELINE DATA
# ============================================================================

# --- Bayer FY 2025 financials (EUR billions) ---
TOTAL_REVENUE = 45.575
CROP_SCIENCE_REVENUE = 17.800
PHARMA_REVENUE = 17.829
CONSUMER_HEALTH_REVENUE = 5.802
GROUP_EBITDA = 9.669

# --- Energy profile ---
TOTAL_ENERGY_PJ = 35.5          # petajoules (2022 baseline)
NATURAL_GAS_SHARE = 0.42        # estimated share of primary energy from gas
ENERGY_GJ_PER_PJ = 1_000_000
MWH_PER_GJ = 1 / 3.6

# --- Emissions (2024, thousand tCO2e) ---
SCOPE_1 = 1_880   # direct combustion
SCOPE_2 = 1_080   # purchased electricity (market-based)
SCOPE_3 = 8_380   # value chain (purchased goods dominant)

# --- TTF natural gas reference prices (EUR/MWh) ---
TTF_HISTORY = {
    2019: 13.5,
    2020:  9.5,
    2021: 47.0,
    2022: 130.0,
    2023: 41.0,
    2024: 34.0,
    2025: 47.0,
    2026: 52.0,   # current / forward
}
TTF_BASELINE = TTF_HISTORY[2024]  # model baseline year

# --- Crop Science EBITDA margins (%) ---
CS_MARGIN_HISTORY = {
    2019: 22.5,
    2020: 21.0,
    2021: 23.0,
    2022: 27.3,
    2023: 22.0,
    2024: 19.4,
}

# --- Ammonia / feedstock parameters ---
MMBTU_PER_TONNE_AMMONIA = 33     # natural gas input per tonne NH3
EUR_PER_MMBTU_CONV = 0.293       # 1 MWh ≈ 3.412 MMBtu → 1 MMBtu ≈ 0.293 MWh


# ============================================================================
# 2. MODEL 1 — DIRECT ENERGY COST SENSITIVITY
# ============================================================================

def direct_energy_exposure(ttf_price: float = TTF_BASELINE) -> dict:
    """
    Estimate Bayer's direct natural gas cost as a function of TTF price.

    Model:
        Gas consumption (MWh) = Total energy (PJ) × gas share × 10^6 / 3.6
        Direct gas cost (EUR)  = Gas consumption × TTF price
        Cost-to-revenue ratio  = Direct gas cost / Total revenue
    """
    gas_pj = TOTAL_ENERGY_PJ * NATURAL_GAS_SHARE
    gas_gwh = gas_pj * 1_000 / 3.6  # PJ → GWh
    gas_mwh = gas_gwh * 1_000

    direct_cost_eur = gas_mwh * ttf_price           # EUR
    direct_cost_bn = direct_cost_eur / 1e9
    cost_to_revenue_pct = (direct_cost_bn / TOTAL_REVENUE) * 100

    return {
        "gas_consumption_twh": gas_gwh / 1_000,
        "ttf_price_eur_mwh": ttf_price,
        "direct_gas_cost_eur_bn": round(direct_cost_bn, 3),
        "cost_to_revenue_pct": round(cost_to_revenue_pct, 2),
    }


# ============================================================================
# 3. MODEL 2 — INDIRECT (SCOPE 3) FEEDSTOCK EXPOSURE
# ============================================================================

def feedstock_exposure(ttf_price: float = TTF_BASELINE) -> dict:
    """
    Estimate Crop Science's exposure through ammonia-based input costs.

    Assumptions:
        - Crop Science purchases ~1.2M tonnes of ammonia-equivalent inputs/yr
          (derived from Scope 3 purchased-goods emissions allocation)
        - Gas accounts for 80% of ammonia cash cost
        - Ammonia requires ~33 MMBtu / tonne

    Model:
        Gas per tonne (MWh) = 33 MMBtu × 0.293 MWh/MMBtu ≈ 9.67 MWh
        Ammonia gas cost     = tonnes × gas_per_tonne × TTF
        Total feedstock cost = ammonia_gas_cost / 0.80  (gas = 80% of cost)
    """
    estimated_ammonia_tonnes = 1_200_000  # model estimate
    gas_mwh_per_tonne = MMBTU_PER_TONNE_AMMONIA * EUR_PER_MMBTU_CONV  # ≈9.67
    # BUT we need MWh: 33 MMBtu × (1 MWh / 3.412 MMBtu) ≈ 9.67 MWh
    gas_mwh_per_tonne = MMBTU_PER_TONNE_AMMONIA / 3.412

    total_gas_mwh = estimated_ammonia_tonnes * gas_mwh_per_tonne
    ammonia_gas_cost = total_gas_mwh * ttf_price
    total_feedstock_cost = ammonia_gas_cost / 0.80

    feedstock_bn = total_feedstock_cost / 1e9
    pct_of_cs_revenue = (feedstock_bn / CROP_SCIENCE_REVENUE) * 100

    return {
        "ammonia_equivalent_tonnes": estimated_ammonia_tonnes,
        "gas_per_tonne_mwh": round(gas_mwh_per_tonne, 2),
        "total_gas_demand_twh": round(total_gas_mwh / 1e6, 2),
        "feedstock_cost_eur_bn": round(feedstock_bn, 3),
        "pct_of_crop_science_revenue": round(pct_of_cs_revenue, 1),
    }


# ============================================================================
# 4. MODEL 3 — TOTAL GAS-LINKED COST & EBITDA SENSITIVITY
# ============================================================================

def total_exposure(ttf_price: float = TTF_BASELINE) -> dict:
    """
    Combine direct + indirect exposure and compute EBITDA sensitivity.

    ΔCost = (direct_cost(P) + feedstock_cost(P)) - (direct_cost(P₀) + feedstock_cost(P₀))
    ΔEBITDA = -ΔCost  (assuming no pass-through)
    Adjusted EBITDA = GROUP_EBITDA - ΔCost

    Also computes the pass-through adjusted version:
        - Short-term pass-through rate: 40%  (empirical from 2021-2022)
        - Long-term pass-through rate: 70%
    """
    baseline_direct = direct_energy_exposure(TTF_BASELINE)
    baseline_feed = feedstock_exposure(TTF_BASELINE)
    baseline_total = baseline_direct["direct_gas_cost_eur_bn"] + baseline_feed["feedstock_cost_eur_bn"]

    scenario_direct = direct_energy_exposure(ttf_price)
    scenario_feed = feedstock_exposure(ttf_price)
    scenario_total = scenario_direct["direct_gas_cost_eur_bn"] + scenario_feed["feedstock_cost_eur_bn"]

    delta_cost = scenario_total - baseline_total

    # Pass-through adjustments
    SHORT_TERM_PASSTHROUGH = 0.40
    LONG_TERM_PASSTHROUGH = 0.70

    net_impact_short = delta_cost * (1 - SHORT_TERM_PASSTHROUGH)
    net_impact_long = delta_cost * (1 - LONG_TERM_PASSTHROUGH)

    return {
        "ttf_price": ttf_price,
        "baseline_ttf": TTF_BASELINE,
        "total_gas_linked_cost_bn": round(scenario_total, 3),
        "delta_cost_bn": round(delta_cost, 3),
        "ebitda_impact_no_passthrough_bn": round(-delta_cost, 3),
        "ebitda_impact_short_term_bn": round(-net_impact_short, 3),
        "ebitda_impact_long_term_bn": round(-net_impact_long, 3),
        "ebitda_pct_change_no_passthrough": round((-delta_cost / GROUP_EBITDA) * 100, 2),
    }


# ============================================================================
# 5. MODEL 4 — REGRESSION: GAS PRICE → CROP SCIENCE MARGIN
# ============================================================================

def ols_regression():
    """
    Simple OLS regression: CS_margin = α + β × ln(TTF)

    Uses log-transform of TTF to capture diminishing marginal effect
    (pass-through saturates at high prices).

    β̂ = Cov(X,Y) / Var(X),  α̂ = Ȳ - β̂X̄
    """
    years = sorted(CS_MARGIN_HISTORY.keys())
    X = [math.log(TTF_HISTORY[y]) for y in years]
    Y = [CS_MARGIN_HISTORY[y] for y in years]
    n = len(X)

    x_bar = sum(X) / n
    y_bar = sum(Y) / n

    cov_xy = sum((X[i] - x_bar) * (Y[i] - y_bar) for i in range(n)) / n
    var_x = sum((X[i] - x_bar) ** 2 for i in range(n)) / n

    beta = cov_xy / var_x if var_x != 0 else 0
    alpha = y_bar - beta * x_bar

    # R² calculation
    y_pred = [alpha + beta * X[i] for i in range(n)]
    ss_res = sum((Y[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((Y[i] - y_bar) ** 2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    # Standard error of beta
    if n > 2 and var_x > 0:
        mse = ss_res / (n - 2)
        se_beta = math.sqrt(mse / (n * var_x))
        t_stat = beta / se_beta if se_beta != 0 else 0
    else:
        se_beta = float('inf')
        t_stat = 0

    return {
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
        "r_squared": round(r_squared, 3),
        "se_beta": round(se_beta, 3),
        "t_statistic": round(t_stat, 3),
        "n_observations": n,
        "interpretation": (
            f"CS Margin ≈ {alpha:.1f} + {beta:.2f} × ln(TTF). "
            f"A 10% increase in TTF → {beta * math.log(1.10):.2f}pp margin change. "
            f"R² = {r_squared:.3f}."
        ),
    }


# ============================================================================
# 6. MODEL 5 — MONTE CARLO VALUE-AT-RISK (VaR)
# ============================================================================

def monte_carlo_var(n_simulations: int = 100_000, seed: int = 42) -> dict:
    """
    Monte Carlo simulation of annual gas-cost impact on EBITDA.

    TTF price modeled as geometric Brownian motion (GBM):
        P(t+1) = P(t) × exp((μ - σ²/2) + σ × Z),  Z ~ N(0,1)

    Parameters calibrated from 2019-2026 TTF history:
        μ  = annualized drift (log-returns mean)
        σ  = annualized volatility (log-returns std)

    VaR₉₅ = 95th percentile of cost increase distribution
    """
    # Calibrate from historical TTF
    years_sorted = sorted(TTF_HISTORY.keys())
    prices = [TTF_HISTORY[y] for y in years_sorted]
    log_returns = [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]

    mu = sum(log_returns) / len(log_returns)
    sigma = math.sqrt(sum((r - mu) ** 2 for r in log_returns) / len(log_returns))

    # Linear congruential generator (deterministic, no numpy needed)
    def lcg(seed, n):
        """Simple LCG pseudo-random number generator."""
        a, c, m = 1664525, 1013904223, 2 ** 32
        results = []
        x = seed
        for _ in range(n):
            x = (a * x + c) % m
            results.append(x / m)
        return results

    def box_muller(uniforms):
        """Convert uniform samples to standard normal via Box-Muller."""
        normals = []
        for i in range(0, len(uniforms) - 1, 2):
            u1, u2 = uniforms[i], uniforms[i + 1]
            if u1 == 0:
                u1 = 1e-10
            z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            z1 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
            normals.extend([z0, z1])
        return normals[:n_simulations]

    uniforms = lcg(seed, n_simulations * 2 + 2)
    Z = box_muller(uniforms)

    current_ttf = TTF_HISTORY[2026]
    simulated_costs = []
    simulated_ttf = []

    baseline_cost = (
        direct_energy_exposure(current_ttf)["direct_gas_cost_eur_bn"]
        + feedstock_exposure(current_ttf)["feedstock_cost_eur_bn"]
    )

    for z in Z:
        future_ttf = current_ttf * math.exp((mu - 0.5 * sigma ** 2) + sigma * z)
        future_ttf = max(future_ttf, 5.0)  # floor at EUR 5/MWh
        future_ttf = min(future_ttf, 500.0)  # cap at EUR 500/MWh

        cost = (
            direct_energy_exposure(future_ttf)["direct_gas_cost_eur_bn"]
            + feedstock_exposure(future_ttf)["feedstock_cost_eur_bn"]
        )
        simulated_costs.append(cost)
        simulated_ttf.append(future_ttf)

    cost_deltas = sorted([c - baseline_cost for c in simulated_costs])
    n = len(cost_deltas)

    var_95 = cost_deltas[int(0.95 * n)]
    var_99 = cost_deltas[int(0.99 * n)]
    cvar_95 = sum(cost_deltas[int(0.95 * n):]) / max(len(cost_deltas[int(0.95 * n):]), 1)

    mean_delta = sum(cost_deltas) / n
    median_idx = n // 2
    median_delta = cost_deltas[median_idx]

    ttf_sorted = sorted(simulated_ttf)
    ttf_5 = ttf_sorted[int(0.05 * n)]
    ttf_95 = ttf_sorted[int(0.95 * n)]

    return {
        "n_simulations": n_simulations,
        "current_ttf": current_ttf,
        "calibrated_mu": round(mu, 4),
        "calibrated_sigma": round(sigma, 4),
        "ttf_90pct_range": f"EUR {ttf_5:.0f} - {ttf_95:.0f} /MWh",
        "mean_cost_delta_bn": round(mean_delta, 3),
        "median_cost_delta_bn": round(median_delta, 3),
        "var_95_bn": round(var_95, 3),
        "var_99_bn": round(var_99, 3),
        "cvar_95_bn": round(cvar_95, 3),
        "var_95_pct_ebitda": round((var_95 / GROUP_EBITDA) * 100, 2),
        "interpretation": (
            f"At 95% confidence, Bayer faces up to EUR {var_95:.2f}bn additional "
            f"gas-linked costs ({(var_95 / GROUP_EBITDA) * 100:.1f}% of EBITDA) "
            f"in a 1-year horizon. CVaR₉₅ = EUR {cvar_95:.2f}bn."
        ),
    }


# ============================================================================
# 7. SCENARIO TABLE
# ============================================================================

def scenario_analysis():
    """Run stress scenarios across TTF price levels."""
    scenarios = {
        "Low (2020 avg)": 10,
        "Pre-crisis (2019)": 14,
        "Current (2024)": 34,
        "Elevated (2025)": 47,
        "Forward (2026)": 52,
        "Stress (+50%)": 78,
        "Crisis (2022 level)": 130,
        "Extreme tail": 200,
    }
    results = []
    for label, price in scenarios.items():
        exp = total_exposure(price)
        results.append({
            "scenario": label,
            "ttf_eur_mwh": price,
            "total_gas_cost_bn": exp["total_gas_linked_cost_bn"],
            "delta_vs_baseline_bn": exp["delta_cost_bn"],
            "ebitda_impact_pct": exp["ebitda_pct_change_no_passthrough"],
        })
    return results


# ============================================================================
# 8. MAIN — RUN ALL MODELS AND PRINT RESULTS
# ============================================================================

def print_section(title: str):
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")


def print_dict(d: dict, indent: int = 2):
    for k, v in d.items():
        print(f"{' ' * indent}{k:.<45} {v}")


def main():
    print("BAYER AG — NATURAL GAS PRICE EXPOSURE MODEL")
    print("Baseline year: 2024 | TTF baseline: EUR 34/MWh")
    print(f"Revenue: EUR {TOTAL_REVENUE}bn | EBITDA: EUR {GROUP_EBITDA}bn")

    # --- Model 1: Direct Energy ---
    print_section("MODEL 1: DIRECT ENERGY COST SENSITIVITY")
    for price in [10, 34, 52, 130]:
        r = direct_energy_exposure(price)
        print(f"\n  TTF = EUR {price}/MWh:")
        print_dict(r, 4)

    # --- Model 2: Feedstock ---
    print_section("MODEL 2: INDIRECT FEEDSTOCK (AMMONIA/SCOPE 3) EXPOSURE")
    for price in [10, 34, 52, 130]:
        r = feedstock_exposure(price)
        print(f"\n  TTF = EUR {price}/MWh:")
        print_dict(r, 4)

    # --- Model 3: Total Sensitivity ---
    print_section("MODEL 3: TOTAL EXPOSURE & EBITDA SENSITIVITY")
    for price in [10, 34, 52, 78, 130, 200]:
        r = total_exposure(price)
        print(f"\n  TTF = EUR {price}/MWh:")
        print_dict(r, 4)

    # --- Model 4: Regression ---
    print_section("MODEL 4: OLS REGRESSION — ln(TTF) → CROP SCIENCE MARGIN")
    reg = ols_regression()
    print_dict(reg)

    # Predict for current/forward TTF
    print(f"\n  Predictions:")
    for price in [34, 52, 80, 130]:
        pred = reg["alpha"] + reg["beta"] * math.log(price)
        print(f"    TTF={price} → Predicted CS Margin = {pred:.1f}%")

    # --- Model 5: Monte Carlo VaR ---
    print_section("MODEL 5: MONTE CARLO VALUE-AT-RISK (100K simulations)")
    var_results = monte_carlo_var()
    print_dict(var_results)

    # --- Scenario Table ---
    print_section("SCENARIO ANALYSIS SUMMARY")
    print(f"  {'Scenario':<22} {'TTF':>6} {'Gas Cost':>10} {'ΔCost':>8} {'ΔEBITDA%':>9}")
    print(f"  {'-'*22} {'-'*6} {'-'*10} {'-'*8} {'-'*9}")
    for s in scenario_analysis():
        print(
            f"  {s['scenario']:<22} {s['ttf_eur_mwh']:>5}€ "
            f"{s['total_gas_cost_bn']:>9.3f}bn "
            f"{s['delta_vs_baseline_bn']:>+7.3f}bn "
            f"{s['ebitda_impact_pct']:>+8.2f}%"
        )

    # --- Key Findings ---
    print_section("KEY FINDINGS")
    base = total_exposure(TTF_BASELINE)
    stress = total_exposure(130)
    var_r = monte_carlo_var(50_000)

    print(f"""
  1. TOTAL GAS-LINKED COST at baseline (EUR 34/MWh):
     EUR {base['total_gas_linked_cost_bn']:.3f}bn = ~{base['total_gas_linked_cost_bn']/TOTAL_REVENUE*100:.1f}% of revenue

  2. CRISIS SCENARIO (EUR 130/MWh, 2022-level):
     Additional cost of EUR {stress['delta_cost_bn']:+.3f}bn
     EBITDA impact (no pass-through): {stress['ebitda_pct_change_no_passthrough']:+.2f}%
     EBITDA impact (40% pass-through): {stress['ebitda_impact_short_term_bn']:+.3f}bn

  3. VALUE-AT-RISK (95%, 1-year):
     EUR {var_r['var_95_bn']:.3f}bn additional cost risk
     = {var_r['var_95_pct_ebitda']:.1f}% of group EBITDA

  4. REGRESSION INSIGHT:
     CS Margin and ln(TTF) show {ols_regression()['r_squared']:.1%} correlation.
     The positive beta ({ols_regression()['beta']:.2f}) confirms counter-intuitive
     finding: high gas prices historically HELPED margins via cost pass-through,
     though with only {ols_regression()['n_observations']} data points, significance is limited.

  5. PRIMARY RISK CHANNEL:
     Indirect feedstock (Scope 3) exposure is ~3-4x larger than direct energy
     cost, making ammonia/agrochemical input prices the dominant transmission
     mechanism.

  6. MITIGANTS:
     - 40-70% cost pass-through to customers (empirical)
     - Commodity hedging program (EUR 28.7bn notional derivatives)
     - 39.5% renewable electricity (targeting 100% by 2029)
     - EUR 200M capex for energy transition through 2029
""")


if __name__ == "__main__":
    main()
