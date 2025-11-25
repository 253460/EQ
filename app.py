# app.py
# 役割：各プログラムを呼び出して実行する

from __future__ import annotations
import argparse
import numpy as np
from eqcore import Preset, EQChain, AudioIO, Normalizer

def build_parser():
    ap = argparse.ArgumentParser(description="OOP EQ（RBJ biquad / JSONプリセット）")
    ap.add_argument("--in", dest="inp", required=True, help="入力WAVパス")
    ap.add_argument("out", help="出力WAVパス")
    ap.add_argument("--preset", required=True, help="EQプリセットJSON（順序適用）")
    ap.add_argument("--export-fr-csv", default=None, help="合成周波数応答CSVの出力先")
    ap.add_argument("--fr-nfft", type=int, default=4096, help="CSV出力の点数")
    ap.add_argument("--lufs-target", type=float, default=None, help="LUFS目標（任意）")
    ap.add_argument("--normalize", action="store_true", help="ピーク正規化を行う")
    ap.add_argument("--peak-target", type=float, default=-0.5, help="ピーク目標[dBFS]")
    ap.add_argument( "--float64",action="store_true",help="64bit float WAVで保存（既定は32bit float）")

    return ap

def main():
    args = build_parser().parse_args()

    # 1) 入力
    y, fs = AudioIO.read(args.inp)

    # 2) プリセット→チェーン
    preset = Preset.load(args.preset)
    chain  = EQChain(preset.bands)
    chain.prepare(fs)

    # 3) 合成応答のCSV（任意）
    if args.export_fr_csv:
        f, mag = chain.freq_response(n_fft=int(args.fr_nfft))
        arr = np.stack([f, mag], axis=1)
        np.savetxt(args.export_fr_csv, arr, delimiter=",",
                   header="freq_Hz,mag_dB", comments="", fmt="%.10f")

    # 4) EQ適用
    y_eq = chain.process(y)

    # 5) 整音（任意）
    if args.lufs_target is not None:
        Normalizer.lufs_inplace(y_eq, fs, float(args.lufs_target))
    if args.normalize:
        Normalizer.peak_inplace(y_eq, float(args.peak_target))

        # 6) 出力
    AudioIO.write(args.out, y_eq, fs, float64=args.float64)


if __name__ == "__main__":
    main()
