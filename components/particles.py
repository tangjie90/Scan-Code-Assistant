"""
粒子效果系统 - 视觉特效
"""
import random
import math


class Particle:
    """单个粒子"""
    
    COLORS = {
        'star': ['#FFD700', '#FFA500', '#FF6B9D', '#FECA57'],
        'heart': ['#FF6B9D', '#FF8E8E', '#FFB6C1', '#E84393'],
        'coin': ['#FFD700', '#FFC125', '#EEB422', '#F39C12'],
        'rainbow': ['#FF6B6B', '#FFA502', '#FECA57', '#5FD068', '#54A0FF', '#A29BFE', '#FD79A8'],
        'celebration': ['#FF6B9D', '#54A0FF', '#5FD068', '#FECA57', '#A29BFE', '#FF9F43']
    }
    
    def __init__(self, x, y, particle_type='star'):
        self.x = x
        self.y = y
        self.type = particle_type
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 3
        
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.035)
        self.size = random.uniform(6, 14)
        self.color = random.choice(self.COLORS.get(particle_type, self.COLORS['star']))
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.vx *= 0.99
        self.life -= self.decay
        self.size *= 0.97
        self.rotation += self.rotation_speed
    
    def draw(self, canvas):
        if self.life <= 0 or self.size < 1:
            return
        
        if self.type == 'star':
            self._draw_star(canvas)
        elif self.type == 'heart':
            self._draw_heart(canvas)
        elif self.type == 'coin':
            self._draw_coin(canvas)
        else:
            self._draw_circle(canvas)
    
    def _draw_star(self, canvas):
        points = []
        for i in range(5):
            angle = math.radians(self.rotation + i * 72 - 90)
            outer_x = self.x + self.size * math.cos(angle)
            outer_y = self.y + self.size * math.sin(angle)
            
            inner_angle = math.radians(self.rotation + i * 72 + 36 - 90)
            inner_x = self.x + self.size * 0.4 * math.cos(inner_angle)
            inner_y = self.y + self.size * 0.4 * math.sin(inner_angle)
            
            points.extend([outer_x, outer_y, inner_x, inner_y])
        
        canvas.create_polygon(points, fill=self.color, outline='', tags='particle')
    
    def _draw_heart(self, canvas):
        r = self.size * 0.6
        canvas.create_oval(self.x - r, self.y - r * 1.2, self.x, self.y, 
                          fill=self.color, outline='', tags='particle')
        canvas.create_oval(self.x, self.y - r * 1.2, self.x + r, self.y, 
                          fill=self.color, outline='', tags='particle')
        canvas.create_polygon(
            self.x - r, self.y,
            self.x + r, self.y,
            self.x, self.y + r * 1.5,
            fill=self.color, outline='', tags='particle'
        )
    
    def _draw_coin(self, canvas):
        canvas.create_oval(
            self.x - self.size, self.y - self.size * 0.8,
            self.x + self.size, self.y + self.size * 0.8,
            fill=self.color, outline='#B8860B', width=2, tags='particle'
        )
        canvas.create_text(self.x, self.y, text='$', 
                          font=('Arial', int(self.size * 0.8), 'bold'),
                          fill='#B8860B', tags='particle')
    
    def _draw_circle(self, canvas):
        canvas.create_oval(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=self.color, outline='', tags='particle'
        )


class ParticleSystem:
    """粒子效果系统"""
    
    EFFECTS = {
        'scan_success': ('star', 15),
        'gold_stars': ('star', 25),
        'coin_rain': ('coin', 30),
        'hearts': ('heart', 20),
        'rainbow': ('rainbow', 35),
        'celebration': ('celebration', 40),
        'payment_success': ('celebration', 50)
    }
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.particles = []
        self.animation_id = None
    
    def emit(self, x, y, particle_type='star', count=20):
        """发射粒子"""
        for _ in range(count):
            self.particles.append(Particle(x, y, particle_type))
        
        if not self.animation_id:
            self._animate()
    
    def emit_effect(self, effect_name, x=None, y=None):
        """根据效果名称发射粒子"""
        if effect_name not in self.EFFECTS:
            effect_name = 'scan_success'
        
        particle_type, count = self.EFFECTS[effect_name]
        
        if x is None or y is None:
            x = self.canvas.winfo_width() // 2
            y = self.canvas.winfo_height() // 2
        
        self.emit(x, y, particle_type, count)
    
    def _animate(self):
        """动画循环"""
        self.canvas.delete('particle')
        
        for particle in self.particles[:]:
            particle.update()
            if particle.life > 0 and particle.size >= 1:
                particle.draw(self.canvas)
            else:
                self.particles.remove(particle)
        
        if self.particles:
            self.animation_id = self.canvas.after(16, self._animate)
        else:
            self.animation_id = None
    
    def clear(self):
        """清除所有粒子"""
        self.particles = []
        self.canvas.delete('particle')
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None
