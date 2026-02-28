"""
购物清单表格组件 - 修复版
"""
from PySide6.QtWidgets import QTableView, QHeaderView, QStyledItemDelegate, QStyle
from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath, QPen
from ..styles.theme import CandyTheme


class CartTableModel(QAbstractTableModel):
    """购物车数据模型"""
    
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ['序号', '时间', '商品名称', '金额']
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        if role == Qt.DisplayRole:
            return str(self._data[row][col])
        
        if role == Qt.ForegroundRole:
            return QColor('#5D4E4E')
        
        if role == Qt.BackgroundRole:
            if row % 2 == 0:
                return QColor('#FFF0EB')
            else:
                return QColor('#FFFFFF')
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
    
    def add_item(self, item):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(item)
        self.endInsertRows()
    
    def clear(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()
    
    def get_data(self):
        return self._data.copy()


class CandyTableDelegate(QStyledItemDelegate):
    """自定义表格委托 - 圆角行背景"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.row_height = 48
        self.corner_radius = 8
    
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = option.rect
        
        row = index.row()
        
        if row % 2 == 0:
            bg_color = QColor('#FFF0EB')
        else:
            bg_color = QColor('#FFFFFF')
        
        if option.state & QStyle.State_Selected:
            bg_color = QColor('#FFD6E0')
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        path = QPainterPath()
        path.addRoundedRect(rect.adjusted(4, 2, -4, -2), self.corner_radius, self.corner_radius)
        painter.fillPath(path, bg_color)
        
        text = index.data(Qt.DisplayRole)
        if text is None:
            text = ""
        
        text_color = QColor('#5D4E4E')
        
        col = index.column()
        if col == 3:
            text_color = QColor('#FF6B6B')
        
        painter.setPen(QPen(text_color))
        painter.setFont(QFont('Microsoft YaHei UI', 12))
        painter.drawText(rect, Qt.AlignCenter, str(text))
        
        painter.restore()
    
    def sizeHint(self, option, index):
        return QRect(0, 0, 100, self.row_height)


class CandyTable(QTableView):
    """童趣糖果表格"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.table_model = CartTableModel()
        self.setModel(self.table_model)
        
        self.table_delegate = CandyTableDelegate(self)
        self.setItemDelegate(self.table_delegate)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setFixedHeight(50)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(48)
        
        self.setAlternatingRowColors(False)
        self.setShowGrid(False)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        
        self._apply_styles()
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QTableView {
                background-color: #FFFFFF;
                border: 2px dashed #FFB5C5;
                border-radius: 16px;
                outline: none;
            }
            QTableView::item {
                padding: 8px;
                border: none;
            }
            QTableView::item:selected {
                background-color: #FFD6E0;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF9EB5, stop:0.33 #B8E0FF, stop:0.66 #FFE5A0, stop:1 #FF9EB5);
                color: white;
                font-size: 13px;
                font-weight: bold;
                font-family: "Microsoft YaHei UI";
                padding: 12px 8px;
                border: none;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
            QHeaderView {
                background-color: transparent;
            }
        """)
    
    def add_item(self, item):
        """添加商品"""
        self.table_model.add_item(item)
        self.scrollToBottom()
    
    def clear(self):
        """清空表格"""
        self.table_model.clear()
    
    def get_data(self):
        """获取数据"""
        return self.table_model.get_data()
