"""
童趣卡通购物清单组件 - 完全Canvas重写版本
特色：圆角虚线边框、彩色渐变表头、宽松行高
"""
import tkinter as tk


class CandyCart(tk.Canvas):
    """卡通风格购物清单 - 童趣糖果风格"""
    
    COLORS = {
        'bg': '#FFFFFF',
        'header_pink': '#FF9EB5',
        'header_blue': '#B8E0FF',
        'header_yellow': '#FFE5A0',
        'border': '#FFDDD8',
        'border_dashed': '#FFB5C5',
        'text': '#5D4E4E',
        'text_light': '#8B7E7E',
        'row_even': '#FFF8F5',
        'row_odd': '#FFFFFF',
        'row_hover': '#FFF0EB',
        'shadow': '#FFCDD8',
    }
    
    def __init__(self, parent, width=500, height=300, **kwargs):
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#FFFFFF'
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent_bg,
                        **kwargs)
        
        self.width = width
        self.height = height
        self.corner_radius = 20
        self.items = []
        self.on_select = None
        self.scroll_offset = 0
        self.row_height = 52
        self.header_height = 50
        self.hovered_row = -1
        
        self._draw_background()
        self._draw_header()
        
        self.bind('<Configure>', self._on_resize)
        self.bind('<MouseWheel>', self._on_scroll)
        self.bind('<Button-4>', self._on_scroll)
        self.bind('<Button-5>', self._on_scroll)
        self.bind('<Motion>', self._on_motion)
        self.bind('<Leave>', self._on_leave)
    
    def _draw_background(self):
        """绘制圆角虚线边框背景"""
        self.delete('background')
        
        r = self.corner_radius
        w = self.width
        h = self.height
        
        self._create_rounded_rect(
            4, 4, w - 4, h - 4,
            r, fill=self.COLORS['shadow'], outline='', tags='background'
        )
        
        self._create_rounded_rect(
            0, 0, w - 8, h - 8,
            r, fill=self.COLORS['bg'], outline='', tags='background'
        )
        
        self._draw_dashed_border(0, 0, w - 8, h - 8, r)
    
    def _draw_dashed_border(self, x1, y1, x2, y2, r):
        """绘制圆角虚线边框"""
        dash_len = 8
        gap_len = 4
        
        self.create_line(x1 + r, y1, x2 - r, y1, 
                        fill=self.COLORS['border_dashed'], width=2, 
                        dash=(dash_len, gap_len), tags='background')
        self.create_line(x1 + r, y2, x2 - r, y2, 
                        fill=self.COLORS['border_dashed'], width=2, 
                        dash=(dash_len, gap_len), tags='background')
        self.create_line(x1, y1 + r, x1, y2 - r, 
                        fill=self.COLORS['border_dashed'], width=2, 
                        dash=(dash_len, gap_len), tags='background')
        self.create_line(x2, y1 + r, x2, y2 - r, 
                        fill=self.COLORS['border_dashed'], width=2, 
                        dash=(dash_len, gap_len), tags='background')
        
        self._draw_dashed_corner(x1, y1, r, 'top_left', dash_len, gap_len)
        self._draw_dashed_corner(x2, y1, r, 'top_right', dash_len, gap_len)
        self._draw_dashed_corner(x1, y2, r, 'bottom_left', dash_len, gap_len)
        self._draw_dashed_corner(x2, y2, r, 'bottom_right', dash_len, gap_len)
    
    def _draw_dashed_corner(self, x, y, r, position, dash_len, gap_len):
        """绘制虚线圆角"""
        if position == 'top_left':
            start, extent = 180, 90
        elif position == 'top_right':
            start, extent = 270, 90
        elif position == 'bottom_left':
            start, extent = 90, 90
        else:
            start, extent = 0, 90
        
        self.create_arc(
            x - r if 'left' in position else x - r,
            y - r if 'top' in position else y - r,
            x + r if 'left' in position else x + r,
            y + r if 'top' in position else y + r,
            start=start, extent=extent, style='arc',
            outline=self.COLORS['border_dashed'], width=2,
            dash=(dash_len, gap_len), tags='background'
        )
    
    def _draw_header(self):
        """绘制彩色渐变表头"""
        self.delete('header')
        
        header_height = self.header_height
        r = self.corner_radius
        w = self.width - 8
        
        colors = [
            self.COLORS['header_pink'],
            self.COLORS['header_blue'],
            self.COLORS['header_yellow']
        ]
        
        section_width = w / 3
        
        for i, color in enumerate(colors):
            x1 = i * section_width
            x2 = (i + 1) * section_width
            if i == 2:
                x2 = w
            
            self.create_rectangle(
                x1, 0, x2, header_height,
                fill=color, outline='', tags='header'
            )
        
        self.create_arc(
            0, 0, 2 * r, 2 * r,
            start=180, extent=90,
            fill=colors[0], outline='', tags='header'
        )
        self.create_arc(
            w - 2 * r, 0, w, 2 * r,
            start=270, extent=90,
            fill=colors[-1], outline='', tags='header'
        )
        
        self.create_rectangle(
            r, 0, w - r, r,
            fill=colors[0], outline='', tags='header'
        )
        
        headers = [('序号', 0.12), ('时间', 0.32), ('商品名称', 0.62), ('金额', 0.88)]
        for text, x_ratio in headers:
            self.create_text(
                w * x_ratio, header_height / 2,
                text=text,
                fill=self.COLORS['text'],
                font=('Microsoft YaHei UI', 13, 'bold'),
                tags='header'
            )
        
        self.create_line(
            0, header_height, w, header_height,
            fill='#FFFFFF', width=3, tags='header'
        )
    
    def _draw_items(self):
        """绘制商品列表"""
        self.delete('item')
        
        start_y = self.header_height + 8
        visible_height = self.height - self.header_height - 16
        visible_rows = int(visible_height / self.row_height) + 1
        
        for i, item in enumerate(self.items):
            y = start_y + i * self.row_height - self.scroll_offset
            
            if y < start_y - self.row_height or y > self.height - 20:
                continue
            
            if y + self.row_height > self.height - 16:
                row_height = self.height - 16 - y
            else:
                row_height = self.row_height - 4
            
            if row_height <= 0:
                continue
            
            bg_color = self.COLORS['row_even'] if i % 2 == 0 else self.COLORS['row_odd']
            if i == self.hovered_row:
                bg_color = self.COLORS['row_hover']
            
            self._draw_rounded_row(8, y, self.width - 16, y + row_height, bg_color, i)
            
            w = self.width - 16
            self.create_text(
                w * 0.12, y + row_height / 2,
                text=str(item.get('id', i + 1)),
                fill=self.COLORS['text'],
                font=('Microsoft YaHei UI', 12),
                tags='item'
            )
            
            self.create_text(
                w * 0.32, y + row_height / 2,
                text=item.get('time', ''),
                fill=self.COLORS['text_light'],
                font=('Microsoft YaHei UI', 11),
                tags='item'
            )
            
            self.create_text(
                w * 0.62, y + row_height / 2,
                text=item.get('name', '')[:12],
                fill=self.COLORS['text'],
                font=('Microsoft YaHei UI', 12),
                anchor='center',
                tags='item'
            )
            
            amount_text = f"¥{item.get('amount', 0):.0f}"
            self.create_text(
                w * 0.88, y + row_height / 2,
                text=amount_text,
                fill='#FF6B6B',
                font=('Microsoft YaHei UI', 13, 'bold'),
                tags='item'
            )
    
    def _draw_rounded_row(self, x1, y1, x2, y2, color, index):
        """绘制圆角行背景"""
        r = 10
        
        self.create_rectangle(x1 + r, y1, x2 - r, y2, 
                             fill=color, outline='', tags='item')
        self.create_rectangle(x1, y1 + r, x2, y2 - r, 
                             fill=color, outline='', tags='item')
        self.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, 
                        fill=color, outline='', tags='item')
        self.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, 
                        fill=color, outline='', tags='item')
        self.create_oval(x1, y2 - 2 * r, x1 + 2 * r, y2, 
                        fill=color, outline='', tags='item')
        self.create_oval(x2 - 2 * r, y2 - 2 * r, x2, y2, 
                        fill=color, outline='', tags='item')
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """创建圆角矩形"""
        tags = kwargs.pop('tags', '')
        
        self.create_rectangle(x1 + r, y1, x2 - r, y2, tags=tags, **kwargs)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, tags=tags, **kwargs)
        self.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, tags=tags, **kwargs)
        self.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, tags=tags, **kwargs)
        self.create_oval(x1, y2 - 2 * r, x1 + 2 * r, y2, tags=tags, **kwargs)
        self.create_oval(x2 - 2 * r, y2 - 2 * r, x2, y2, tags=tags, **kwargs)
    
    def _on_resize(self, event):
        """响应大小变化"""
        self.width = event.width
        self.height = event.height
        self._draw_background()
        self._draw_header()
        self._draw_items()
    
    def _on_scroll(self, event):
        """处理滚动"""
        if event.num == 4 or event.delta > 0:
            self.scroll_offset = max(0, self.scroll_offset - 30)
        elif event.num == 5 or event.delta < 0:
            max_scroll = max(0, len(self.items) * self.row_height - (self.height - self.header_height - 20))
            self.scroll_offset = min(max_scroll, self.scroll_offset + 30)
        self._draw_items()
    
    def _on_motion(self, event):
        """鼠标移动事件"""
        y = event.y
        row = int((y - self.header_height - 8 + self.scroll_offset) / self.row_height)
        if 0 <= row < len(self.items):
            if self.hovered_row != row:
                self.hovered_row = row
                self._draw_items()
    
    def _on_leave(self, event):
        """鼠标离开事件"""
        self.hovered_row = -1
        self._draw_items()
    
    def set_items(self, items):
        """设置商品列表"""
        self.items = items
        self.scroll_offset = 0
        self._draw_items()
    
    def add_item(self, item):
        """添加商品"""
        self.items.append(item)
        max_scroll = max(0, len(self.items) * self.row_height - (self.height - self.header_height - 20))
        self.scroll_offset = max_scroll
        self._draw_items()
    
    def clear(self):
        """清空列表"""
        self.items = []
        self.scroll_offset = 0
        self._draw_items()
    
    def get_item_count(self):
        """获取商品数量"""
        return len(self.items)
