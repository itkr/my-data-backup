# GUI モジュール化設計提案

## 🎯 目標構造

```
src/app/gui/
├── app.py                    # メインアプリケーション（100-150行）
├── base/
│   ├── __init__.py
│   ├── base_tab.py          # タブの基底クラス
│   └── mixins.py            # 共通機能のミックスイン
├── modules/
│   ├── __init__.py
│   ├── photo_organizer/
│   │   ├── __init__.py
│   │   ├── tab.py           # PhotoOrganizerTab
│   │   ├── widgets.py       # 専用ウィジェット
│   │   └── config_dialog.py # 設定ダイアログ
│   ├── move/
│   │   ├── __init__.py
│   │   ├── tab.py           # MoveTab
│   │   ├── widgets.py       # 専用ウィジェット
│   │   └── file_browser.py  # ファイルブラウザ
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── tab.py           # SettingsTab
│   │   └── dialogs.py       # 設定ダイアログ群
│   └── logs/
│       ├── __init__.py
│       ├── tab.py           # LogTab
│       └── viewer.py        # ログビューワー
├── widgets/
│   ├── __init__.py
│   ├── progress_bar.py      # カスタム進捗バー
│   ├── file_selector.py     # ファイル選択ウィジェット
│   └── status_display.py    # ステータス表示
└── utils/
    ├── __init__.py
    ├── gui_helpers.py       # GUI共通ヘルパー
    └── event_handlers.py    # イベントハンドラー
```

## 🔧 実装例

### base/base_tab.py
```python
from abc import ABC, abstractmethod
import customtkinter as ctk

class BaseTab(ABC):
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        self.setup_widgets()
    
    @abstractmethod
    def setup_widgets(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass
    
    def show_progress(self, current, total):
        # 共通の進捗表示ロジック
        pass
```

### modules/photo_organizer/tab.py
```python
from ...base.base_tab import BaseTab
from ...widgets.file_selector import FileSelector

class PhotoOrganizerTab(BaseTab):
    def setup_widgets(self):
        # Photo Organizer専用のUI設定
        pass
    
    def execute(self):
        # Photo Organizer実行ロジック
        pass
```

### app.py（簡潔版）
```python
class UnifiedDataBackupApp:
    def __init__(self):
        self.setup_main_window()
        self.setup_tabview()
    
    def setup_tabview(self):
        from .modules.photo_organizer.tab import PhotoOrganizerTab
        from .modules.move.tab import MoveTab
        
        self.photo_tab = PhotoOrganizerTab(self.tabview.add("📸 Photo Organizer"), self.logger)
        self.move_tab = MoveTab(self.tabview.add("🗂️ Move"), self.logger)
```
