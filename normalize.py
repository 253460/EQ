# eqcore/normalize.py
# 役割：整音。LUFS目標化（pyloudnorm任意）とピーク正規化。

from __future__ import annotations
import numpy as np
from .convert import lin_from_db

class Normalizer:
    @staticmethod
    def lufs_inplace(y: np.ndarray, fs: int, target_lufs: float) -> None:
        """LUFS正規化：pyloudnormが無ければ何もしない。"""
        try:
            import pyloudnorm as pyln
        except Exception:
            return
        meter = pyln.Meter(fs)
        y_mono = y if y.ndim == 1 else np.mean(y, axis=1)
        loud = meter.integrated_loudness(y_mono.astype(np.float64))
        gain_db = float(target_lufs - loud)
        y *= lin_from_db(gain_db)

    @staticmethod
    def peak_inplace(y: np.ndarray, peak_dbfs: float = -0.5, eps: float = 1e-12) -> None:
        """ピークを目標dBFSに合わせる"""
        peak = float(np.max(np.abs(y)))
        if peak < eps:
            return
        limit = lin_from_db(peak_dbfs)
        y *= (limit / peak)
