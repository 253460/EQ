# eqcore/eq.py
# 役割：1バンドEQ。パラメータ保持＋係数設計＋適用＋単体応答

from __future__ import annotations
from typing import Optional, Tuple
import math
import numpy as np
from scipy.signal import lfilter, lfilter_zi, freqz

from .eq_params import EQParams
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

    def process(self, x: np.ndarray) -> np.ndarray:
        """波形を通す。xは (N,) または (N,C)。"""
        if self.b is None or self.a is None or self.zi_mono is None:
            raise RuntimeError("prepare(fs) を先に呼んでください。")
        y = x.astype(np.float64, copy=True)
        if y.ndim == 1:
            y, self.zi_mono = lfilter(self.b, self.a, y, zi=self.zi_mono)
            return y
        elif y.ndim == 2:
            for ch in range(y.shape[1]):
                zi = self.zi_mono.copy()
                y[:, ch], zi = lfilter(self.b, self.a, y[:, ch], zi=zi)
            return y
        else:
            raise ValueError(f"Unsupported shape: {y.shape}")

    def freq_response(self, n_fft: int = 4096) -> Tuple[np.ndarray, np.ndarray]:
        """この段だけの周波数応答（Hz, dB）"""
        if self.fs is None or self.b is None or self.a is None:
            raise RuntimeError("prepare(fs) 後に呼び出してください。")
        w = np.linspace(0, np.pi, n_fft)
        _, H = freqz(self.b, self.a, worN=w)
        f = w * self.fs / (2.0 * math.pi)
        mag = 20.0 * np.log10(np.maximum(1e-12, np.abs(H)))
        return f, mag

    def export(self) -> dict:
        """プリセット保存用の辞書を返す（棚はSで保存）"""
        d = {"type": self.params.kind, "f0": float(self.params.f0)}
        if self.params.kind in ("lowshelf", "highshelf"):
            d["slope"] = float(self.params.q_or_s); d["gain_db"] = float(self.params.gain_db)
        elif self.params.kind == "peaking":
            d["Q"] = float(self.params.q_or_s);     d["gain_db"] = float(self.params.gain_db)
        else:
            d["Q"] = float(self.params.q_or_s)
        return d
