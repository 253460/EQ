# eqcore/io_.py
# 役割：音声I/O。読み込みは float64 & (N,C) で統一、保存は既定 float32。

from __future__ import annotations
import numpy as np
import soundfile as sf

class AudioIO:
    @staticmethod
    def read(path: str):
        """読み込み：float64, shape=(N,C) に統一（モノラルでも2次元）。"""
        y, fs = sf.read(path, dtype="float64", always_2d=True)
        return y, int(fs)

    @staticmethod
    def write(path: str, y: np.ndarray, fs: int, float64: bool = False):
        """
        書き出し形式：
          - デフォルト          : 32bit float WAV (subtype="FLOAT")
          - float64=True のとき : 64bit float WAV (subtype="DOUBLE")
        """
        if not np.isfinite(y).all():
            raise ValueError("NaN/Inf を含むサンプルを検出しました。")

        # クリップチェックだけはそのまま
        peak = float(np.max(np.abs(y)))
        if peak > 1.0:
            print(f"[warn] peak={peak:.3f} > 1.0。クリップの可能性があります。")

        if float64:
            dtype = np.float64
            subtype = "DOUBLE"
        else:
            dtype = np.float32
            subtype = "FLOAT"

        sf.write(path, y.astype(dtype), fs, subtype=subtype)

