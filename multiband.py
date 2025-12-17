# eqcore/multiband.py
# 役割：複数のEQを順に適用。順序編集・合成特性の計算も担当。

from __future__ import annotations
from typing import List, Optional, Tuple
import math
import numpy as np
from scipy.signal import freqz

from .eq import EQ

class EQChain:
    """EQ（1段）を直列合成するクラス。"""

    def __init__(self, bands: Optional[List[EQ]] = None) -> None:
        self.bands: List[EQ] = list(bands) if bands else []
        self.fs: Optional[float] = None

    # --- 編集 ---
    def add(self, band: EQ, index: Optional[int] = None) -> None:
        if index is None: self.bands.append(band)
        else:             self.bands.insert(int(index), band)

    def remove(self, index: int) -> None:
        del self.bands[index]

    def move(self, src: int, dst: int) -> None:
        b = self.bands.pop(src); self.bands.insert(dst, b)

    # --- 実行 ---
    def prepare(self, fs: float) -> None:
        self.fs = float(fs)
        for b in self.bands:
            b.prepare(self.fs)

    def process(self, x: np.ndarray) -> np.ndarray:
        if self.fs is None:
            raise RuntimeError("prepare(fs) を先に呼んでください。")
        y = x.astype(np.float64, copy=True)
        for b in self.bands:
            y = b.process(y)
        return y

    def freq_response(self, n_fft: int = 4096) -> Tuple[np.ndarray, np.ndarray]:
        """チェーン全体の応答（Hz, dB）"""
        if self.fs is None:
            raise RuntimeError("prepare(fs) 後に呼び出してください。")
        w = np.linspace(0, np.pi, n_fft)
        H_total = np.ones_like(w, dtype=np.complex128)
        for b in self.bands:
            _, H = freqz(b.b, b.a, worN=w)
            H_total *= H
        f = w * self.fs / (2.0 * math.pi)
        mag = 20.0 * np.log10(np.maximum(1e-12, np.abs(H_total)))
        return f, mag
