class AudioIO:
    @staticmethod
    def write(path: str, y: np.ndarray, fs: int):
        """
        32-bit FLOAT で保存。
        ・保存直前に float32 に変換
        ・NaN/Inf を検出したら例外で止める
        ・|y|>1.0 なら注意を出す
        """
        if not np.isfinite(y).all():
            raise ValueError("NaN/Inf を含むサンプルを検出しました。")

        peak = float(np.max(np.abs(y)))
        if peak > 1.0:
            print(f"[warn] peak={peak:.3f} > 1.0。"
                  "FLOATでは保存できるが、再生でクリップする可能性があります。"
                  "必要なら正規化してください。")

        sf.write(path, y.astype(np.float32), fs, subtype="FLOAT")
