"""
缓存管理器模块 - 标准化缓存存储方案

功能特性：
- 多级缓存架构（内存缓存 + 文件缓存）
- LRU淘汰策略
- 兼容旧版本 .mp3 文件格式
- 缓存键命名规范
- 性能监控指标
- 异常处理机制
"""
import os
import json
import hashlib
import time
import threading
import pickle
from datetime import datetime
from collections import OrderedDict
from typing import Any, Optional, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum


class CacheLevel(Enum):
    MEMORY = "memory"
    FILE = "file"
    BOTH = "both"


@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: float
    updated_at: float
    expires_at: Optional[float]
    access_count: int
    size_bytes: int
    metadata: Dict[str, Any]
    
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    total_hits: int = 0
    total_misses: int = 0
    total_errors: int = 0
    memory_entries: int = 0
    file_entries: int = 0
    total_size_bytes: int = 0
    avg_access_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total = self.total_hits + self.total_misses
        return self.total_hits / total if total > 0 else 0.0


class CacheKeyBuilder:
    SEPARATOR = ":"
    VERSION_PREFIX = "v"
    
    @staticmethod
    def build(namespace: str, category: str, identifier: str, version: str = "1") -> str:
        parts = [namespace, category, identifier, f"{CacheKeyBuilder.VERSION_PREFIX}{version}"]
        return CacheKeyBuilder.SEPARATOR.join(parts)
    
    @staticmethod
    def to_filename(key: str) -> str:
        hash_key = hashlib.md5(key.encode('utf-8')).hexdigest()
        return f"{hash_key}.cache"
    
    @staticmethod
    def to_hash(identifier: str) -> str:
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()


class CacheSerializer:
    class Format(Enum):
        JSON = "json"
        PICKLE = "pickle"
        RAW = "raw"
    
    @staticmethod
    def serialize(data: Any, fmt: Format = Format.JSON) -> bytes:
        try:
            if fmt == CacheSerializer.Format.JSON:
                return json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif fmt == CacheSerializer.Format.PICKLE:
                return pickle.dumps(data)
            elif fmt == CacheSerializer.Format.RAW:
                if isinstance(data, bytes):
                    return data
                elif isinstance(data, str):
                    return data.encode('utf-8')
                else:
                    raise ValueError(f"RAW format requires bytes or str")
        except Exception as e:
            raise CacheError(f"Serialization failed: {e}")
    
    @staticmethod
    def deserialize(data: bytes, fmt: Format = Format.JSON) -> Any:
        try:
            if fmt == CacheSerializer.Format.JSON:
                return json.loads(data.decode('utf-8'))
            elif fmt == CacheSerializer.Format.PICKLE:
                return pickle.loads(data)
            elif fmt == CacheSerializer.Format.RAW:
                return data
        except Exception as e:
            raise CacheError(f"Deserialization failed: {e}")


class CacheError(Exception):
    pass


class MemoryCache:
    def __init__(self, max_size: int = 100, max_memory_mb: float = 50):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._max_size = max_size
        self._max_memory_bytes = max_memory_mb * 1024 * 1024
        self._current_memory = 0
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    self._remove(key)
                    return None
                self._cache.move_to_end(key)
                entry.access_count += 1
                return entry
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None, 
            metadata: Optional[Dict] = None) -> CacheEntry:
        with self._lock:
            now = time.time()
            expires_at = now + ttl_seconds if ttl_seconds else None
            size = self._estimate_size(value)
            
            entry = CacheEntry(
                key=key, value=value, created_at=now, updated_at=now,
                expires_at=expires_at, access_count=0, size_bytes=size,
                metadata=metadata or {}
            )
            
            if key in self._cache:
                self._current_memory -= self._cache[key].size_bytes
            
            self._cache[key] = entry
            self._current_memory += size
            self._evict_if_needed()
            return entry
    
    def delete(self, key: str) -> bool:
        with self._lock:
            return self._remove(key)
    
    def _remove(self, key: str) -> bool:
        if key in self._cache:
            self._current_memory -= self._cache[key].size_bytes
            del self._cache[key]
            return True
        return False
    
    def _estimate_size(self, value: Any) -> int:
        try:
            if isinstance(value, bytes):
                return len(value)
            elif isinstance(value, str):
                return len(value.encode('utf-8'))
            else:
                return len(pickle.dumps(value))
        except:
            return 1024
    
    def _evict_if_needed(self):
        while (len(self._cache) > self._max_size or 
               self._current_memory > self._max_memory_bytes):
            if not self._cache:
                break
            oldest_key = next(iter(self._cache))
            self._remove(oldest_key)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._current_memory = 0
    
    def get_stats(self) -> Dict:
        with self._lock:
            return {
                'entries': len(self._cache),
                'memory_mb': self._current_memory / (1024 * 1024),
                'max_entries': self._max_size,
                'max_memory_mb': self._max_memory_bytes / (1024 * 1024)
            }


class FileCache:
    INDEX_FILE = "cache_index.json"
    DATA_DIR = "data"
    
    def __init__(self, cache_dir: str, max_size_mb: float = 500):
        self._cache_dir = cache_dir
        self._data_dir = os.path.join(cache_dir, self.DATA_DIR)
        self._index_path = os.path.join(cache_dir, self.INDEX_FILE)
        self._index: Dict[str, dict] = {}
        self._lock = threading.RLock()
        self._max_size_bytes = max_size_mb * 1024 * 1024
        
        self._ensure_dirs()
        self._load_index()
        self._migrate_old_files()
    
    def _ensure_dirs(self):
        os.makedirs(self._cache_dir, exist_ok=True)
        os.makedirs(self._data_dir, exist_ok=True)
    
    def _load_index(self):
        try:
            if os.path.exists(self._index_path):
                with open(self._index_path, 'r', encoding='utf-8') as f:
                    self._index = json.load(f)
        except Exception as e:
            print(f"[Cache] 加载索引失败: {e}")
            self._index = {}
    
    def _save_index(self):
        try:
            with open(self._index_path, 'w', encoding='utf-8') as f:
                json.dump(self._index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Cache] 保存索引失败: {e}")
    
    def _migrate_old_files(self):
        try:
            old_count = 0
            for f in os.listdir(self._cache_dir):
                if f.endswith('.mp3'):
                    old_path = os.path.join(self._cache_dir, f)
                    if os.path.isfile(old_path):
                        file_hash = f.replace('.mp3', '')
                        key = f"voice:tts:{file_hash}:v1"
                        
                        if key not in self._index:
                            size = os.path.getsize(old_path)
                            mtime = os.path.getmtime(old_path)
                            self._index[key] = {
                                'created_at': mtime,
                                'updated_at': mtime,
                                'expires_at': None,
                                'access_count': 0,
                                'size_bytes': size,
                                'format': 'raw',
                                'file_type': 'mp3',
                                'metadata': {'migrated': True}
                            }
                            old_count += 1
            
            if old_count > 0:
                self._save_index()
                print(f"[Cache] 迁移 {old_count} 个旧格式文件到索引")
                
        except Exception as e:
            print(f"[Cache] 迁移旧文件失败: {e}")
    
    def _get_file_path(self, key: str) -> str:
        info = self._index.get(key, {})
        file_type = info.get('file_type', 'cache')
        filename = CacheKeyBuilder.to_filename(key).replace('.cache', f'.{file_type}')
        
        if file_type == 'mp3':
            return os.path.join(self._cache_dir, filename.replace('.mp3', '.mp3').split('/')[-1])
        return os.path.join(self._data_dir, filename)
    
    def _find_mp3_file(self, key: str) -> Optional[str]:
        info = self._index.get(key, {})
        if info.get('file_type') == 'mp3':
            file_hash = key.split(':')[2] if ':' in key else CacheKeyBuilder.to_hash(key)
            mp3_path = os.path.join(self._cache_dir, f"{file_hash}.mp3")
            if os.path.exists(mp3_path):
                return mp3_path
        return None
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            if key not in self._index:
                return None
            
            info = self._index[key]
            
            if info.get('expires_at') and time.time() > info['expires_at']:
                self.delete(key)
                return None
            
            file_path = self._find_mp3_file(key) or self._get_file_path(key)
            
            if not os.path.exists(file_path):
                self.delete(key)
                return None
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                fmt = CacheSerializer.Format(info.get('format', 'raw'))
                value = CacheSerializer.deserialize(data, fmt)
                
                info['access_count'] = info.get('access_count', 0) + 1
                info['last_access'] = time.time()
                self._save_index()
                
                return CacheEntry(
                    key=key, value=value,
                    created_at=info['created_at'],
                    updated_at=info['updated_at'],
                    expires_at=info.get('expires_at'),
                    access_count=info['access_count'],
                    size_bytes=info['size_bytes'],
                    metadata=info.get('metadata', {})
                )
            except Exception as e:
                print(f"[Cache] 读取文件失败: {e}")
                return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None,
            fmt: CacheSerializer.Format = CacheSerializer.Format.RAW,
            metadata: Optional[Dict] = None) -> bool:
        with self._lock:
            try:
                data = CacheSerializer.serialize(value, fmt)
                file_path = self._get_file_path(key)
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    f.write(data)
                
                now = time.time()
                expires_at = now + ttl_seconds if ttl_seconds else None
                
                self._index[key] = {
                    'created_at': now,
                    'updated_at': now,
                    'expires_at': expires_at,
                    'access_count': 0,
                    'size_bytes': len(data),
                    'format': fmt.value,
                    'file_type': 'cache',
                    'metadata': metadata or {}
                }
                
                self._save_index()
                return True
            except Exception as e:
                print(f"[Cache] 写入文件失败: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key not in self._index:
                return False
            
            file_path = self._get_file_path(key)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            
            del self._index[key]
            self._save_index()
            return True
    
    def clear(self):
        with self._lock:
            for key in list(self._index.keys()):
                self.delete(key)
    
    def get_stats(self) -> Dict:
        with self._lock:
            total_size = sum(info['size_bytes'] for info in self._index.values())
            return {
                'entries': len(self._index),
                'total_size_mb': total_size / (1024 * 1024),
                'max_size_mb': self._max_size_bytes / (1024 * 1024),
                'cache_dir': self._cache_dir
            }


class CacheManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, cache_dir: Optional[str] = None, 
                 memory_max_size: int = 100,
                 memory_max_mb: float = 50,
                 file_max_mb: float = 500):
        
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._cache_dir = cache_dir or os.path.join(os.getcwd(), "cache")
        self._memory_cache = MemoryCache(max_size=memory_max_size, max_memory_mb=memory_max_mb)
        self._file_cache = FileCache(self._cache_dir, max_size_mb=file_max_mb)
        self._stats = CacheStats()
        self._access_times: List[float] = []
        self._initialized = True
        
        print(f"[CacheManager] 初始化完成: {self._cache_dir}")
    
    def get(self, key: str, level: CacheLevel = CacheLevel.BOTH) -> Optional[Any]:
        start_time = time.perf_counter()
        
        try:
            if level in (CacheLevel.MEMORY, CacheLevel.BOTH):
                entry = self._memory_cache.get(key)
                if entry:
                    self._record_hit(start_time)
                    return entry.value
            
            if level in (CacheLevel.FILE, CacheLevel.BOTH):
                entry = self._file_cache.get(key)
                if entry:
                    self._memory_cache.set(key, entry.value, metadata=entry.metadata)
                    self._record_hit(start_time)
                    return entry.value
            
            self._record_miss(start_time)
            return None
            
        except Exception as e:
            self._record_error(start_time)
            print(f"[CacheManager] 获取失败: {e}")
            return None
    
    def set(self, key: str, value: Any, 
            ttl_seconds: Optional[float] = None,
            level: CacheLevel = CacheLevel.BOTH,
            fmt: CacheSerializer.Format = CacheSerializer.Format.RAW,
            metadata: Optional[Dict] = None) -> bool:
        
        try:
            if level in (CacheLevel.MEMORY, CacheLevel.BOTH):
                self._memory_cache.set(key, value, ttl_seconds, metadata)
            
            if level in (CacheLevel.FILE, CacheLevel.BOTH):
                self._file_cache.set(key, value, ttl_seconds, fmt, metadata)
            
            return True
            
        except Exception as e:
            print(f"[CacheManager] 设置失败: {e}")
            return False
    
    def delete(self, key: str, level: CacheLevel = CacheLevel.BOTH) -> bool:
        try:
            result = True
            if level in (CacheLevel.MEMORY, CacheLevel.BOTH):
                result = self._memory_cache.delete(key) and result
            if level in (CacheLevel.FILE, CacheLevel.BOTH):
                result = self._file_cache.delete(key) and result
            return result
        except Exception as e:
            print(f"[CacheManager] 删除失败: {e}")
            return False
    
    def exists(self, key: str, level: CacheLevel = CacheLevel.BOTH) -> bool:
        return self.get(key, level) is not None
    
    def clear(self, level: CacheLevel = CacheLevel.BOTH):
        if level in (CacheLevel.MEMORY, CacheLevel.BOTH):
            self._memory_cache.clear()
        if level in (CacheLevel.FILE, CacheLevel.BOTH):
            self._file_cache.clear()
    
    def _record_hit(self, start_time: float):
        self._stats.total_hits += 1
        self._record_access_time(start_time)
    
    def _record_miss(self, start_time: float):
        self._stats.total_misses += 1
        self._record_access_time(start_time)
    
    def _record_error(self, start_time: float):
        self._stats.total_errors += 1
        self._record_access_time(start_time)
    
    def _record_access_time(self, start_time: float):
        elapsed = (time.perf_counter() - start_time) * 1000
        self._access_times.append(elapsed)
        if len(self._access_times) > 100:
            self._access_times = self._access_times[-100:]
        self._stats.avg_access_time_ms = sum(self._access_times) / len(self._access_times)
    
    def get_stats(self) -> Dict:
        memory_stats = self._memory_cache.get_stats()
        file_stats = self._file_cache.get_stats()
        
        self._stats.memory_entries = memory_stats['entries']
        self._stats.file_entries = file_stats['entries']
        self._stats.total_size_bytes = file_stats.get('total_size_mb', 0) * 1024 * 1024
        
        return {
            'performance': {
                'total_hits': self._stats.total_hits,
                'total_misses': self._stats.total_misses,
                'total_errors': self._stats.total_errors,
                'hit_rate': f"{self._stats.hit_rate:.2%}",
                'avg_access_time_ms': f"{self._stats.avg_access_time_ms:.2f}"
            },
            'memory': memory_stats,
            'file': file_stats
        }
    
    def health_check(self) -> Dict:
        try:
            test_key = "__health_check__"
            test_value = "test"
            
            self.set(test_key, test_value, level=CacheLevel.BOTH)
            result = self.get(test_key, level=CacheLevel.BOTH)
            self.delete(test_key, level=CacheLevel.BOTH)
            
            return {
                'status': 'healthy' if result == test_value else 'unhealthy',
                'memory_cache': 'ok',
                'file_cache': 'ok',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
