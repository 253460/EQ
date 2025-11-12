# eqcore/eq.py
# 役割：1バンドEQ。パラメータ保持＋係数設計＋適用＋単体応答

from __future__ import annotations
from typing import Optional, Tuple
import math
import numpy as np
from scipy.signal import lfilter, lfilter_zi, freqz

from .types import EQParams
from .designer import BiquadDesigner

class EQ:
    """2次IIR(=biquad) 1段。prepare(fs)→process(x) の流れで利用。"""

    def __init__(self, params: EQParams) -> None:
        self.params = params
        self.fs: Optional[float] = None
        self.b: Optional[np.ndarray] = None
        self.a: Optional[np.ndarray] = None
        self.zi_mono: Optional[np.ndarray] = None  # 1ch用の内部状態

    def prepare(self, fs: float) -> None:
        """fsに対して係数(b,a)を生成し、内部状態を初期化。"""
        self.fs = float(fs)
        k  = self.params.kind.lower()
        f0 = float(self.params.f0)
        qs = float(self.params.q_or_s)
        g  = float(self.params.gain_db)

        if   k == "peaking":   b, a = BiquadDesigner.peaking  (self.fs, f0, qs, g)
        elif k == "lowshelf":  b, a = BiquadDesigner.lowshelf (self.fs, f0, qs, g)
        elif k == "highshelf": b, a = BiquadDesigner.highshelf(self.fs, f0, qs, g)
        elif k == "lowpass":   b, a = BiquadDesigner.lowpass  (self.fs, f0, qs)
        elif k == "highpass":  b, a = BiquadDesigner.highpass (self.fs, f0, qs)
        elif k == "notch":     b, a = BiquadDesigner.notch    (self.fs, f0, qs)
        else:
            raise ValueError(f"Unknown kind: {k}")

        self.b, self.a = b.astype(np.float64), a.astype(np.float64)
        self.zi_mono = lfilter_zi(self.b, self.a) * 0.0
