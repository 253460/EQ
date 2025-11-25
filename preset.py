# eqcore/preset.py
# 役割：プリセットJSONからEQ列を作る／保存する。棚Q→Sの変換もここで。

from __future__ import annotations
from typing import List, Dict, Any
import json

from .eq_params import EQParams
from .eq import EQ
from .convert import shelf_Qs_to_S

class Preset:
    """プリセットの読み書きと、EQインスタンス列の生成を担当。"""

    def __init__(self, bands: List[EQ]) -> None:
        self.bands = bands  # 記載順＝適用順

    @staticmethod
    def _band_from_obj(obj: Dict[str, Any]) -> EQ:
        typ = str(obj["type"]).lower()
        f0  = float(obj["f0"])
        g   = float(obj.get("gain_db", 0.0))

        if typ in ("lowshelf", "highshelf"):
            if "slope" in obj:
                s = float(obj["slope"])
            elif "Q" in obj:   # UIや古いプリセットでQの場合に対応
                s = float(shelf_Qs_to_S(float(obj["Q"]), g))
            else:
                s = 1.0
            return EQ(EQParams(kind=typ, f0=f0, q_or_s=s, gain_db=g))

        if typ == "peaking":
            q = float(obj.get("Q", 1.0))
            return EQ(EQParams(kind=typ, f0=f0, q_or_s=q, gain_db=g))

        # lowpass/highpass/notch
        q = float(obj.get("Q", 0.707))
        return EQ(EQParams(kind=typ, f0=f0, q_or_s=q, gain_db=0.0))

    @classmethod
    def load(cls, path: str) -> "Preset":
        with open(path, "r") as f:
            obj = json.load(f)
        bands = [cls._band_from_obj(b) for b in obj.get("bands", [])]
        return cls(bands)

    def save(self, path: str) -> None:
        obj = {"bands": [b.export() for b in self.bands]}
        with open(path, "w") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
