#!/usr/bin/env python3
"""Симуляция модели Курамото: как рой светлячков приходит к синхронизации.

Каждый светлячок — осциллятор со своей фазой θ и своей частотой ω.
Правило одно: светлячок слегка подстраивает свою фазу под соседей.

    dθi/dt = ωi + (K/N) * Σ sin(θj - θi)

K — сила связи. При малом K каждый мигает в своём ритме (r ≈ 0).
При большом K рой мигает вместе (r → 1). Между — фазовый переход.

Параметр порядка r ∈ [0, 1] измеряет, насколько фазы согласованы:
    r * e^(iψ) = (1/N) * Σ e^(iθj)
r = 0 — полная неупорядоченность, r = 1 — полная синхронизация.

Без зависимостей. Только стандартная библиотека Python.

Запуск:
    python3 fireflies.py            # 200 светлячков, K = 1.0
    python3 fireflies.py --K 0.5    # слабая связь — хаос
    python3 fireflies.py --K 2.0    # сильная связь — синхрон
    python3 fireflies.py --plot     # сохранить график r(t) в fireflies.png
"""

import argparse
import math
import random


def kuramoto_step(phases, freqs, K, dt):
    """Один шаг Эйлера для модели Курамото (полная связь).

    Использует mean-field: сумма sin(θj - θi) по j выражается через
    sin_sum и cos_sum, которые считаются один раз за шаг.
    """
    n = len(phases)
    sin_sum = 0.0
    cos_sum = 0.0
    for th in phases:
        sin_sum += math.sin(th)
        cos_sum += math.cos(th)
    new_phases = []
    for i in range(n):
        th = phases[i]
        dtheta = freqs[i] + (K / n) * (sin_sum * math.cos(th) - cos_sum * math.sin(th))
        new_phases.append(th + dtheta * dt)
    return new_phases


def order_parameter(phases):
    """Возвращает (r, psi) — параметр порядка и средний угол."""
    n = len(phases)
    re = 0.0
    im = 0.0
    for th in phases:
        re += math.cos(th)
        im += math.sin(th)
    re /= n
    im /= n
    return math.hypot(re, im), math.atan2(im, re)


def simulate(N, K, T, dt, freq_spread, seed=0):
    """Прогон модели. Возвращает историю r(t), финальные фазы и частоты."""
    rng = random.Random(seed)
    phases = [rng.uniform(0.0, 2.0 * math.pi) for _ in range(N)]
    freqs = [1.0 + freq_spread * rng.gauss(0.0, 1.0) for _ in range(N)]

    steps = int(T / dt)
    r_history = []
    for _ in range(steps):
        r, _ = order_parameter(phases)
        r_history.append(r)
        phases = kuramoto_step(phases, freqs, K, dt)
    r, _ = order_parameter(phases)
    r_history.append(r)
    return r_history, phases, freqs


def main():
    ap = argparse.ArgumentParser(description="Модель Курамото: синхронизация роя")
    ap.add_argument("--N", type=int, default=200, help="число светлячков (по умолч. 200)")
    ap.add_argument("--K", type=float, default=1.0, help="сила связи (по умолч. 1.0)")
    ap.add_argument("--T", type=float, default=50.0, help="длительность (по умолч. 50)")
    ap.add_argument("--dt", type=float, default=0.01, help="шаг времени (по умолч. 0.01)")
    ap.add_argument("--spread", type=float, default=0.3, help="разброс частот (по умолч. 0.3)")
    ap.add_argument("--seed", type=int, default=0, help="зерно ГСЧ (по умолч. 0)")
    ap.add_argument("--plot", action="store_true", help="сохранить график r(t) в fireflies.png")
    args = ap.parse_args()

    r_hist, phases, freqs = simulate(
        args.N, args.K, args.T, args.dt, args.spread, args.seed
    )

    g0 = 1.0 / (args.spread * math.sqrt(2.0 * math.pi))
    Kc = 2.0 / (math.pi * g0)

    r_final = r_hist[-1]
    tail = r_hist[-max(1, len(r_hist) // 10):]
    r_mean_last = sum(tail) / len(tail)

    print(f"Светлячков: {args.N}")
    print(f"Связь K:     {args.K:.3f}")
    print(f"Kc (оценка): {Kc:.3f}")
    print(f"r в конце:   {r_final:.3f}")
    print(f"r (среднее, последняя 10%): {r_mean_last:.3f}")
    if r_mean_last > 0.5:
        print("Результат:  синхронизация (рой мигает вместе)")
    elif r_mean_last > 0.1:
        print("Результат:  частичная синхронизация")
    else:
        print("Результат:  неупорядоченность (каждый в своём ритме)")

    # ASCII-график r(t): 20 строк, каждая — 50 временных точек
    rows, cols = 20, 50
    step = max(1, len(r_hist) // cols)
    sampled = r_hist[::step][:cols]
    while len(sampled) < cols:
        sampled.append(sampled[-1])
    print("\nr(t):")
    for row in range(rows - 1, -1, -1):
        threshold = row / rows
        line = ""
        for r in sampled:
            line += "█" if r >= threshold else " "
        print(f"  {threshold:.1f} │{line}")
    print(f"      └{'─' * cols}")

    if args.plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            t = [i * args.dt for i in range(len(r_hist))]
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.plot(t, r_hist, color="#1a1a2e", lw=1.2)
            ax.set_xlabel("время")
            ax.set_ylabel("параметр порядка r")
            ax.set_title(f"Курамото: N={args.N}, K={args.K:.2f}, Kc≈{Kc:.2f}")
            ax.set_ylim(0.0, 1.05)
            ax.grid(alpha=0.3)
            out = "fireflies.png"
            fig.tight_layout()
            fig.savefig(out, dpi=120)
            print(f"График:     {out}")
        except ImportError:
            print("matplotlib не найден — график не сохранён (pip install matplotlib)")


if __name__ == "__main__":
    main()
