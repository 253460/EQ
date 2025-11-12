# eqcore/io_.py
# 役割：音声I/O。読み込み

from __future__ import annotations

import numpy as np
import soundfile as sf


class AudioIO:
    @staticmethod
    def read(path: str):
        """
        読み込み：内部は float64、shape=(N, C) に統一。
        ・モノラルでも 2次元（(N, 1)）で返す 
        """
        y, fs = sf.read(path, dtype="float64", always_2d=True)
        return y, int(fs)

    @staticmethod
    def write(path: str, y: np.ndarray, fs: int, pcm16: bool = False):
        """
        書き出し：既定は 32-bit FLOAT、--pcm16 指定で 16-bit PCM。
        """
        if not np.isfinite(y).all():
            raise ValueError("NaN/Inf を含むサンプルを検出しました。")

        peak = float(np.max(np.abs(y)))
        if pcm16 and peak > 1.0:
            print(
                f"[warn] PCM16でクリップの可能性: peak={peak:.3f} > 1.0。"
                "保存前に正規化を推奨。"
            )

        subtype = "PCM_16" if pcm16 else "FLOAT"
        sf.write(path, y.astype(np.float32), fs, subtype=subtype)
