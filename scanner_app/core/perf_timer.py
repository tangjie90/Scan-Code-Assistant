"""
性能分析模块 - 测量语音播报各环节耗时
"""
import time
import functools

class PerformanceTimer:
    """性能计时器"""
    
    def __init__(self):
        self.timings = {}
        self._start_times = {}
    
    def start(self, name):
        """开始计时"""
        self._start_times[name] = time.perf_counter()
    
    def stop(self, name):
        """停止计时并记录"""
        if name in self._start_times:
            elapsed = (time.perf_counter() - self._start_times[name]) * 1000
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(elapsed)
            del self._start_times[name]
            return elapsed
        return 0
    
    def get_stats(self, name):
        """获取统计数据"""
        if name in self.timings and self.timings[name]:
            times = self.timings[name]
            return {
                'count': len(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'total': sum(times)
            }
        return None
    
    def print_report(self):
        """打印报告"""
        print("\n" + "="*60)
        print("性能分析报告")
        print("="*60)
        
        total_time = 0
        for name in self.timings:
            stats = self.get_stats(name)
            if stats:
                total_time += stats['total']
                print(f"\n{name}:")
                print(f"  次数: {stats['count']}")
                print(f"  平均: {stats['avg']:.2f}ms")
                print(f"  最小: {stats['min']:.2f}ms")
                print(f"  最大: {stats['max']:.2f}ms")
                print(f"  总计: {stats['total']:.2f}ms")
        
        print(f"\n总耗时: {total_time:.2f}ms")
        print("="*60)


perf_timer = PerformanceTimer()


def timed(name):
    """计时装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            perf_timer.start(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = perf_timer.stop(name)
                print(f"[PERF] {name}: {elapsed:.2f}ms")
        return wrapper
    return decorator
