"""
アプリケーション設定
"""

from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict

THEMES = ("light", "dark", "auto")

MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600


@dataclass
class UIConfig:
    """UI関連設定"""

    theme: str = "auto"
    window_width: int = 1200
    window_height: int = 900
    log_level: str = "INFO"


@dataclass
class AppConfig:
    """アプリケーション設定

    保存形式は {"ui": {...}} 。未知のセクションやキーは読み飛ばすため、
    古い設定ファイルを読み込んでもエラーにならない。
    """

    ui: UIConfig = field(default_factory=UIConfig)

    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式に変換"""
        return {"ui": asdict(self.ui)}

    def update_from_dict(self, data: Dict[str, Any]):
        """辞書から設定を更新（未知のセクション・キーは無視）"""
        ui_data = data.get("ui")
        if not isinstance(ui_data, dict):
            return

        known_keys = {f.name for f in fields(UIConfig)}
        for key, value in ui_data.items():
            if key in known_keys:
                setattr(self.ui, key, value)

    def reset_to_defaults(self):
        """設定をデフォルトにリセット"""
        self.ui = UIConfig()
