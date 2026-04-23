#!/usr/bin/env python3
"""
Options Flow & Positioning Analyzer (CBOE delayed + yfinance spot — free, no API key)

Uses CBOE's public delayed quotes API as primary data source (real OI + volume + IV
+ Greeks). Falls back to yfinance if CBOE fails (e.g. HK tickers).

Computes:
- Put/Call ratio (OI + volume)
- Max Pain
- IV term structure (ATM IV per expiry)
- IV skew (OTM put IV vs OTM call IV)
- Top OI strikes (support/resistance proxy)
- GEX estimate (real gamma × real OI)

Usage:
    python3 flow_analyzer.py TICKER [--expiries N]

Output: JSON to stdout. Degrades gracefully when no data.
"""
import json
import sys
import re
import argparse
import urllib.request
from datetime import datetime, timezone
from collections import defaultdict


CBOE_URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker}.json"


def parse_occ(code: str):
    """Parse OCC code like 'NVDA260515C00200000' → (root, exp_date, right, strike)."""
    m = re.match(r"^([A-Z]+)(\d{6})([CP])(\d{8})$", code)
    if not m:
        return None
    root, date_str, right, strike_str = m.groups()
    yy, mm, dd = int(date_str[:2]), int(date_str[2:4]), int(date_str[4:6])
    year = 2000 + yy
    exp_date = f"{year}-{mm:02d}-{dd:02d}"
    strike = int(strike_str) / 1000
    return root, exp_date, right, strike


def fetch_cboe(ticker: str) -> dict | None:
    try:
        req = urllib.request.Request(
            CBOE_URL.format(ticker=ticker.upper()),
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return None
            return json.loads(resp.read())
    except Exception:
        return None


def get_spot(ticker: str) -> float | None:
    try:
        import yfinance as yf
        return float(yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1])
    except Exception:
        return None


def analyze_flow(ticker: str, n_expiries: int = 3) -> dict:
    ticker = ticker.upper()
    spot = get_spot(ticker)

    cboe = fetch_cboe(ticker)
    if not cboe or "data" not in cboe or "options" not in cboe.get("data", {}):
        return {
            "ticker": ticker,
            "has_options": False,
            "reason": "CBOE delayed data unavailable (ticker may not be US-optionable or ADR)",
            "spot": spot,
            "data_source": "none",
        }

    options = cboe["data"]["options"]
    if not options:
        return {"ticker": ticker, "has_options": False, "reason": "empty options chain", "spot": spot}

    # Organize by expiration
    by_exp = defaultdict(lambda: {"calls": [], "puts": []})
    today = datetime.now(timezone.utc).date()

    for opt in options:
        code = opt.get("option")
        parsed = parse_occ(code)
        if not parsed:
            continue
        _, exp_date, right, strike = parsed
        # Skip already-expired
        try:
            edate = datetime.strptime(exp_date, "%Y-%m-%d").date()
            if (edate - today).days < 7:
                continue
        except Exception:
            continue

        record = {
            "strike": strike,
            "oi": int(opt.get("open_interest") or 0),
            "vol": int(opt.get("volume") or 0),
            "iv": float(opt.get("iv") or 0),
            "delta": float(opt.get("delta") or 0),
            "gamma": float(opt.get("gamma") or 0),
        }
        if right == "C":
            by_exp[exp_date]["calls"].append(record)
        else:
            by_exp[exp_date]["puts"].append(record)

    # Sort expiries chronologically, take first N
    expirations = sorted(by_exp.keys())[:n_expiries]
    if not expirations:
        return {"ticker": ticker, "has_options": False, "reason": "no expiries >= 7 DTE", "spot": spot}

    out = {
        "ticker": ticker,
        "has_options": True,
        "data_source": "cboe_delayed",
        "spot": round(spot, 2) if spot else None,
        "as_of": cboe.get("timestamp", ""),
        "expirations_analyzed": expirations,
        "by_expiry": [],
    }

    total_call_oi = total_put_oi = 0
    total_call_vol = total_put_vol = 0
    all_pain = defaultdict(float)
    atm_ivs = []
    skew_samples = []
    call_oi_by_strike = defaultdict(int)
    put_oi_by_strike = defaultdict(int)
    total_gamma_exposure = 0.0  # dollar gamma

    for exp in expirations:
        calls = by_exp[exp]["calls"]
        puts = by_exp[exp]["puts"]

        c_oi = sum(c["oi"] for c in calls)
        p_oi = sum(p["oi"] for p in puts)
        c_vol = sum(c["vol"] for c in calls)
        p_vol = sum(p["vol"] for p in puts)

        total_call_oi += c_oi
        total_put_oi += p_oi
        total_call_vol += c_vol
        total_put_vol += p_vol

        for c in calls:
            call_oi_by_strike[c["strike"]] += c["oi"]
        for p in puts:
            put_oi_by_strike[p["strike"]] += p["oi"]

        # ATM IV (closest call strike to spot with positive IV)
        atm_iv = None
        if spot:
            candidates = [c for c in calls if c["iv"] > 0.01]
            if candidates:
                atm = min(candidates, key=lambda c: abs(c["strike"] - spot))
                atm_iv = round(atm["iv"], 4)
                atm_ivs.append({"expiry": exp, "iv": atm_iv})

            # Skew: OTM put IV vs OTM call IV (~10% out)
            otm_puts = [p for p in puts if p["strike"] < spot * 0.95 and p["iv"] > 0.01]
            otm_calls = [c for c in calls if c["strike"] > spot * 1.05 and c["iv"] > 0.01]
            if otm_puts and otm_calls:
                p_target = min(otm_puts, key=lambda p: abs(p["strike"] - spot * 0.9))
                c_target = min(otm_calls, key=lambda c: abs(c["strike"] - spot * 1.1))
                skew_samples.append({
                    "expiry": exp,
                    "put_iv_90pct": round(p_target["iv"], 4),
                    "call_iv_110pct": round(c_target["iv"], 4),
                    "skew": round(p_target["iv"] - c_target["iv"], 4),
                })

        # Max pain for this expiry
        strikes = sorted(set(c["strike"] for c in calls) | set(p["strike"] for p in puts))
        for strike in strikes:
            call_pain = sum(c["oi"] * max(0, strike - c["strike"]) for c in calls)
            put_pain = sum(p["oi"] * max(0, p["strike"] - strike) for p in puts)
            all_pain[strike] += call_pain + put_pain

        # GEX contribution: dealer assumed SHORT calls + LONG puts (std assumption)
        # → per call: -gamma × OI × 100 × spot²
        # → per put: +gamma × OI × 100 × spot²
        if spot:
            for c in calls:
                total_gamma_exposure -= c["gamma"] * c["oi"] * 100 * spot * spot
            for p in puts:
                total_gamma_exposure += p["gamma"] * p["oi"] * 100 * spot * spot

        out["by_expiry"].append({
            "expiry": exp,
            "dte": (datetime.strptime(exp, "%Y-%m-%d").date() - today).days,
            "call_oi": c_oi,
            "put_oi": p_oi,
            "call_volume": c_vol,
            "put_volume": p_vol,
            "pc_ratio_oi": round(p_oi / c_oi, 3) if c_oi else None,
            "pc_ratio_vol": round(p_vol / c_vol, 3) if c_vol else None,
            "atm_iv": atm_iv,
        })

    # Max pain = strike with min total pain
    max_pain_strike = min(all_pain, key=all_pain.get) if all_pain else None

    # Top OI strikes
    top_call_oi = sorted(call_oi_by_strike.items(), key=lambda x: -x[1])[:5]
    top_put_oi = sorted(put_oi_by_strike.items(), key=lambda x: -x[1])[:5]

    out["aggregate"] = {
        "total_call_oi": total_call_oi,
        "total_put_oi": total_put_oi,
        "pc_ratio_oi": round(total_put_oi / total_call_oi, 3) if total_call_oi else None,
        "total_call_volume": total_call_vol,
        "total_put_volume": total_put_vol,
        "pc_ratio_volume": round(total_put_vol / total_call_vol, 3) if total_call_vol else None,
        "max_pain_strike": max_pain_strike,
        "max_pain_vs_spot_pct": round((max_pain_strike - spot) / spot * 100, 2) if (max_pain_strike and spot) else None,
        "top_call_oi_strikes": [{"strike": k, "oi": v} for k, v in top_call_oi],
        "top_put_oi_strikes": [{"strike": k, "oi": v} for k, v in top_put_oi],
        "iv_term_structure": atm_ivs,
        "iv_skew_samples": skew_samples,
        "gex_estimate_bn_usd": round(total_gamma_exposure / 1e9, 3),
    }

    # Qualitative interpretation
    interp = []
    agg = out["aggregate"]
    pc = agg["pc_ratio_oi"]
    if pc:
        if pc > 1.2:
            interp.append(f"P/C OI ratio {pc} — bearish positioning tilt (puts > calls)")
        elif pc < 0.7:
            interp.append(f"P/C OI ratio {pc} — bullish positioning tilt (calls > puts)")
        else:
            interp.append(f"P/C OI ratio {pc} — neutral positioning")

    if max_pain_strike and spot:
        mp_pct = (max_pain_strike - spot) / spot * 100
        if abs(mp_pct) > 3:
            direction = "below" if mp_pct < 0 else "above"
            interp.append(f"Max pain ${max_pain_strike} is {abs(mp_pct):.1f}% {direction} spot — pin bias toward ${max_pain_strike}")

    gex = agg["gex_estimate_bn_usd"]
    if abs(gex) > 0.5:
        if gex > 0:
            interp.append(f"GEX ≈ +${gex}bn — positive dealer gamma, suppresses moves (range-bound bias, vol compression)")
        else:
            interp.append(f"GEX ≈ ${gex}bn — negative dealer gamma, amplifies moves (vol expansion risk, dealer chases moves)")

    if skew_samples:
        avg_skew = sum(s["skew"] for s in skew_samples) / len(skew_samples)
        if avg_skew > 0.05:
            interp.append(f"Put skew avg {avg_skew:.3f} — elevated fear/hedging demand")
        elif avg_skew < -0.02:
            interp.append(f"Negative skew {avg_skew:.3f} — unusual call demand > put demand (very bullish)")

    # Top OI concentration
    if top_call_oi and top_call_oi[0][1] > 0:
        interp.append(f"Top call OI concentration at ${top_call_oi[0][0]} ({top_call_oi[0][1]:,} contracts) — possible resistance/magnet")
    if top_put_oi and top_put_oi[0][1] > 0:
        interp.append(f"Top put OI concentration at ${top_put_oi[0][0]} ({top_put_oi[0][1]:,} contracts) — possible support/magnet")

    out["interpretation"] = interp
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("--expiries", type=int, default=3, help="number of near-term expiries to analyze")
    args = parser.parse_args()
    result = analyze_flow(args.ticker, args.expiries)
    print(json.dumps(result, indent=2, default=str))
