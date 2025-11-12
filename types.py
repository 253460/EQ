# eqcore/types.py
# 役割：1バンド分の設定（型を明示）

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class EQParams:
    """1バンドの設定"""
    kind: str        # "peaking"/"lowshelf"/"highshelf"/"lowpass"/"highpass"/"notch"
    f0: float
    q_or_s: float    # peaking/LP/HP/Notch: Q、shelf: S
    gain_db: float = 0.0  # peaking/shelfのみ使用
