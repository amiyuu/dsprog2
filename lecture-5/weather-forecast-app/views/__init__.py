cat > views/__init__.py << 'EOF'
"""
画面（View）を管理するパッケージ
"""

from .area_list import AreaListView

__all__ = ['AreaListView']
EOF