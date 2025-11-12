# eqcore/designer.py
# 役割：biquad 係数（a0=1 正規化）を生成

from __future__ import annotations

import math
import numpy as np

from .convert import (
    A_from_gain_db,
    sanitize_f0,
    sanitize_Q,
    sanitize_S,
    sanitize_gain,
)


class BiquadDesigner:
    """係数設計器"""

    # ---------------------------
    # Peaking
    # ---------------------------
    @staticmethod
    def peaking(fs: float, f0: float, Q: float, gain_db: float):
        f0 = sanitize_f0(fs, f0)
        Q = sanitize_Q(Q)
        gain_db = sanitize_gain(gain_db)

        A = A_from_gain_db(gain_db)
        w0 = 2.0 * math.pi * f0 / fs
        c = math.cos(w0)
        s = math.sin(w0)
        alpha = s / (2.0 * Q)

        b0 = 1 + alpha * A
        b1 = -2 * c
        b2 = 1 - alpha * A

        a0 = 1 + alpha / A
        a1 = -2 * c
        a2 = 1 - alpha / A

        b = np.array([b0, b1, b2], np.float64) / a0
        a = np.array([1.0, a1 / a0, a2 / a0], np.float64)

        return b, a

    # ---------------------------
    # Low Shelf
    # ---------------------------
    @staticmethod
    def lowshelf(fs: float, f0: float, S: float, gain_db: float):
        f0 = sanitize_f0(fs, f0)
        S = sanitize_S(S)
        gain_db = sanitize_gain(gain_db)

        A = A_from_gain_db(gain_db)
        w0 = 2.0 * math.pi * f0 / fs
        c = math.cos(w0)
        s = math.sin(w0)

        alpha = (
            s / 2.0
            * math.sqrt((A + 1.0 / A) * (1.0 / S - 1.0) + 2.0)
        )

        b0 = A * ((A + 1) - (A - 1) * c + 2 * math.sqrt(A) * alpha)
        b1 = 2 * A * ((A - 1) - (A + 1) * c)
        b2 = A * ((A + 1) - (A - 1) * c - 2 * math.sqrt(A) * alpha)

        a0 = (A + 1) + (A - 1) * c + 2 * math.sqrt(A) * alpha
        a1 = -2 * ((A - 1) + (A + 1) * c)
        a2 = (A + 1) + (A - 1) * c - 2 * math.sqrt(A) * alpha

        b = np.array([b0, b1, b2], np.float64) / a0
        a = np.array([1.0, a1 / a0, a2 / a0], np.float64)

        return b, a

    # ---------------------------
    # High Shelf
    # ---------------------------
    @staticmethod
    def highshelf(fs: float, f0: float, S: float, gain_db: float):
        f0 = sanitize_f0(fs, f0)
        S = sanitize_S(S)
        gain_db = sanitize_gain(gain_db)

        A = A_from_gain_db(gain_db)
        w0 = 2.0 * math.pi * f0 / fs
        c = math.cos(w0)
        s = math.sin(w0)

        alpha = (
            s / 2.0
            * math.sqrt((A + 1.0 / A) * (1.0 / S - 1.0) + 2.0)
        )

        b0 = A * ((A + 1) + (A - 1) * c + 2 * math.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * c)
        b2 = A * ((A + 1) + (A - 1) * c - 2 * math.sqrt(A) * alpha)

        a0 = (A + 1) - (A - 1) * c + 2 * math.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * c)
        a2 = (A + 1) - (A - 1) * c - 2 * math.sqrt(A) * alpha

        b = np.array([b0, b1, b2], np.float64) / a0
        a = np.array([1.0, a1 / a0, a2 / a0], np.float64)

        return b, a

    # ---------------------------
    # Low Pass
    # ---------------------------
    @staticmethod
    def lowpass(fs: float, f0: float, Q: float):
        f0 = sanitize_f0(fs, f0)
        Q = sanitize_Q(Q)

        w0 = 2.0 * math.pi * f0 / fs
        c = math.cos(w0)
        s = math.sin(w0)
        alpha = s / (2.0 * Q)

        b0 = (1 - c) / 2.0
        b1 = 1 - c
        b2 = (1 - c) / 2.0

        a0 = 1 + alpha
        a1 = -2 * c
        a2 = 1 - alpha

        b = np.array([b0, b1, b2], np.float64) / a0
        a = np.array([1.0, a1 / a0, a2 / a0], np.float64)

        return b, a

    # ---------------------------
    # High Pass
    # ---------------------------
    @staticmethod
    def highpass(fs: float, f0: float, Q: float):
        f0 = sanitize_f0(fs, f0)
        Q = sanitize_Q(Q)

        w0 = 2.0 * math.pi * f0 / fs
        c = math.cos(w0)
        s = math.sin(w0)
        alpha = s / (2.0 * Q)

        b0 = (1 + c) / 2.0
        b1 = -(1 + c)
        b2 = (1 + c) / 2.0

        a0 = 1 + alpha
        a1 = -2 * c
        a2 = 1 - alpha

        b = np.array([b0, b1, b2], np.float64) / a0
        a = np.array([1.0, a1 / a0, a2 / a0], np.float64)

        return b, a

    # ---------------------------
    # Notch
    # ---------------------------
    @staticmethod
    def notch(fs: float, f0: float, Q: float):
        f0 = sanitize_f0(fs, f0)
        Q = sanitize_Q(Q)

        w0 = 2.0 * math.pi * f0 / fs
        c = math.cos(w0)
        s = math.sin(w0)
        alpha = s / (2.0 * Q)

        b0 = 1.0
        b1 = -2.0 * c
        b2 = 1.0

        a0 = 1.0 + alpha
        a1 = -2.0 * c
        a2 = 1.0 - alpha

        b = np.array([b0, b1, b2], np.float64) / a0
        a = np.array([1.0, a1 / a0, a2 / a0], np.float64)

        return b, a
