# eqcore/convert.py
# 役割：dB↔倍率、棚のQ↔S相互変換、安全な値に丸め（サニタイズ）

from __future__ import annotations

import math
import numpy as np


def lin_from_db(db: float) -> float:
    """dB→ 倍率"""
    return float(10.0 ** (db / 20.0))


def db_from_lin(amp: float, eps: float = 1e-12) -> float:
    """倍率 → dB"""
    return float(20.0 * math.log10(max(eps, float(amp))))


def A_from_gain_db(db: float) -> float:
    """RBJの式で使う A"""
    return float(10.0 ** (db / 40.0))


def sanitize_f0(fs: float, f0: float) -> float:
    """中心周波数を安全範囲に（1 Hz 〜 0.49×Nyquist）"""
    nyq = fs * 0.5
    return float(np.clip(float(f0), 1.0, 0.49 * nyq))


def sanitize_Q(Q: float, lo: float = 0.1) -> float:
    """Q の下限"""
    return float(max(float(Q), lo))


def sanitize_S(S: float, lo: float = 0.2, hi: float = 2.0) -> float:
    """棚の傾き S の実用範囲"""
    return float(np.clip(float(S), lo, hi))


def sanitize_gain(db: float, lim: float = 24.0) -> float:
    """ゲインの上限（±lim dB）"""
    return float(np.clip(float(db), -abs(lim), abs(lim)))


def shelf_S_to_Qs(S: float, gain_db: float) -> float:
    """
<<<<<<< HEAD
    棚の S → 棚Q(Qs) に変換（
=======
    棚の S → 棚Q(Qs) に変換
>>>>>>> 17f2df2 (Update: latest code)
    """
    A = A_from_gain_db(gain_db)
    inv_Q2 = (A + 1.0 / A) * (1.0 / S - 1.0) + 2.0
    return 1.0 / math.sqrt(inv_Q2)


def shelf_Qs_to_S(Qs: float, gain_db: float) -> float:
    """
<<<<<<< HEAD
    棚Q(Qs) → S に変換（
=======
    棚Q(Qs) → S に変換
>>>>>>> 17f2df2 (Update: latest code)
    """
    A = A_from_gain_db(gain_db)

    return 1.0 / (
        1.0
        + (1.0 / (A + 1.0 / A)) * (1.0 / (Qs * Qs) - 2.0)
    )
