"""
商品管理器模块 - 现代化设计

特性：
- dataclass 数据模型
- Observer 设计模式
- 线程安全
- 热更新支持
"""
import csv
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from abc import ABC, abstractmethod
from datetime import datetime


@dataclass(frozen=True)
class Product:
    """商品数据模型 - 不可变对象"""
    barcode: str
    name: str
    price: float
    category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'barcode': self.barcode,
            'name': self.name,
            'price': self.price,
            'category': self.category
        }


class ProductObserver(ABC):
    """商品观察者接口"""
    
    @abstractmethod
    def on_products_updated(self, products: Dict[str, Product], version: int):
        """商品数据更新回调"""
        pass
    
    @abstractmethod
    def on_products_update_failed(self, error: str):
        """商品数据更新失败回调"""
        pass


class ProductManager:
    """商品管理器 - 支持热更新"""
    
    ENCODINGS = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
    
    def __init__(self, csv_path: str):
        self._path = Path(csv_path)
        self._products: Dict[str, Product] = {}
        self._observers: List[ProductObserver] = []
        self._lock = threading.RLock()
        self._version = 0
        self._last_modified = 0.0
        self._watcher = None
        
        self._load_products()
    
    @property
    def products(self) -> Dict[str, Product]:
        with self._lock:
            return self._products.copy()
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def count(self) -> int:
        with self._lock:
            return len(self._products)
    
    def add_observer(self, observer: ProductObserver):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: ProductObserver):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def get_product(self, barcode: str) -> Optional[Product]:
        with self._lock:
            return self._products.get(barcode)
    
    def find_by_name(self, name: str) -> Optional[Product]:
        with self._lock:
            for product in self._products.values():
                if name in product.name:
                    return product
        return None
    
    def _load_products(self) -> bool:
        if not self._path.exists():
            print(f"[ProductManager] 文件不存在: {self._path}")
            return False
        
        new_products: Dict[str, Product] = {}
        
        for encoding in self.ENCODINGS:
            try:
                with open(self._path, 'r', encoding=encoding, newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        barcode = (row.get('条码', '') or '').strip()
                        name = (row.get('名称', '') or '').strip()
                        price_str = (row.get('价格', '') or '').strip()
                        category = (row.get('分类', '') or '').strip() or None
                        
                        if barcode and name:
                            try:
                                price = float(price_str) if price_str else 0.0
                            except ValueError:
                                price = 0.0
                            
                            new_products[barcode] = Product(
                                barcode=barcode,
                                name=name,
                                price=price,
                                category=category
                            )
                
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"[ProductManager] 加载失败 ({encoding}): {e}")
                return False
        
        if not new_products:
            print(f"[ProductManager] 警告: 未加载任何商品")
            return False
        
        with self._lock:
            old_count = len(self._products)
            self._products = new_products
            self._version += 1
            self._last_modified = time.time()
        
        print(f"[ProductManager] 加载成功: {len(new_products)} 个商品 (版本 {self._version})")
        return True
    
    def reload(self) -> bool:
        """重新加载商品数据"""
        print(f"[ProductManager] 开始重新加载...")
        
        old_products = self._products.copy()
        
        if self._load_products():
            self._notify_updated()
            return True
        else:
            with self._lock:
                self._products = old_products
            self._notify_failed("加载失败，保留旧数据")
            return False
    
    def _notify_updated(self):
        """通知所有观察者数据已更新"""
        with self._lock:
            products_copy = self._products.copy()
            version = self._version
        
        for observer in self._observers:
            try:
                observer.on_products_updated(products_copy, version)
            except Exception as e:
                print(f"[ProductManager] 观察者通知失败: {e}")
    
    def _notify_failed(self, error: str):
        """通知所有观察者更新失败"""
        for observer in self._observers:
            try:
                observer.on_products_update_failed(error)
            except Exception as e:
                print(f"[ProductManager] 观察者通知失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                'count': len(self._products),
                'version': self._version,
                'last_modified': datetime.fromtimestamp(self._last_modified).isoformat() if self._last_modified else None,
                'file_path': str(self._path)
            }
