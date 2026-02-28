"""
童趣糖果主题系统
"""
from PySide6.QtGui import QColor, QLinearGradient


class CandyTheme:
    """童趣糖果主题"""
    
    COLORS = {
        'primary': '#FF9EB5',
        'primary_light': '#FFB8C8',
        'primary_dark': '#FF7A9A',
        'secondary': '#B8E0FF',
        'secondary_light': '#D4EEFF',
        'secondary_dark': '#8ACDFF',
        'accent': '#FFE5A0',
        'accent_light': '#FFF3CC',
        'accent_dark': '#FFD670',
        'pink': '#FFB5C5',
        'pink_light': '#FFD6E0',
        'lavender': '#E6E6FA',
        'mint': '#B5F2D6',
        'coral': '#FFB5A7',
        'success': '#7DD99A',
        'success_light': '#B5F0C0',
        'success_dark': '#5BC47A',
        'warning': '#FFDB7D',
        'warning_light': '#FFEAB8',
        'warning_dark': '#EBC050',
        'error': '#FF9A9A',
        'error_light': '#FFBDBD',
        'error_dark': '#E57070',
        'background': '#FFF8F5',
        'surface': '#FFFFFF',
        'surface_soft': '#FFF5F0',
        'surface_variant': '#FFF0EB',
        'text_primary': '#5D4E4E',
        'text_secondary': '#8B7E7E',
        'text_tertiary': '#B5A8A8',
        'text_light': '#FFFFFF',
        'border': '#FFDDD8',
        'border_light': '#FFF0EC',
        'border_focus': '#FFB5C5',
        'shadow': '#FFCDD8',
        'shadow_soft': '#FFF0F5',
    }
    
    RAINBOW_COLORS = [
        '#FFB5C5',
        '#FFD6A0',
        '#FFE5A0',
        '#B5F2D6',
        '#B8E0FF',
        '#D4B5FF',
        '#FFB5C5'
    ]
    
    OPACITY = {
        'normal': 1.0,
        'hover': 0.95,
        'pressed': 0.9,
        'disabled': 0.7
    }
    
    @staticmethod
    def get_color(name):
        """获取颜色"""
        return QColor(CandyTheme.COLORS.get(name, '#000000'))
    
    @staticmethod
    def get_rainbow_gradient(x1, y1, x2, y2):
        """获取彩虹渐变"""
        gradient = QLinearGradient(x1, y1, x2, y2)
        colors = CandyTheme.RAINBOW_COLORS
        for i, color in enumerate(colors):
            gradient.setColorAt(i / (len(colors) - 1), QColor(color))
        return gradient
    
    @staticmethod
    def get_gradient(start_color, end_color, x1, y1, x2, y2):
        """获取双色渐变"""
        gradient = QLinearGradient(x1, y1, x2, y2)
        gradient.setColorAt(0, QColor(start_color))
        gradient.setColorAt(1, QColor(end_color))
        return gradient
