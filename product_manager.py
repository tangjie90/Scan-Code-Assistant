







"""
商品管理模块 - CSV 格式
支持从 products.csv 加载商品配置
用户可直接用 Excel 编辑商品列表
"""
import csv
import os
import sys


def get_project_dir():
    """获取项目根目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_internal_dir():
    """获取 PyInstaller 打包后的 _internal 目录"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), '_internal')
    return os.path.dirname(os.path.abspath(__file__))


def get_products_path():
    """获取商品配置文件路径（优先使用 exe 目录，便于用户编辑）"""
    exe_dir = get_project_dir()
    exe_path = os.path.join(exe_dir, "products.csv")
    
    if os.path.exists(exe_path):
        return exe_path
    
    internal_dir = get_internal_dir()
    internal_path = os.path.join(internal_dir, "products.csv")
    
    if os.path.exists(internal_path):
        return internal_path
    
    return exe_path


def get_config_path():
    """获取配置文件路径（优先使用 exe 目录，便于用户编辑）"""
    exe_dir = get_project_dir()
    exe_path = os.path.join(exe_dir, "config.json")
    
    if os.path.exists(exe_path):
        return exe_path
    
    internal_dir = get_internal_dir()
    internal_path = os.path.join(internal_dir, "config.json")
    
    if os.path.exists(internal_path):
        return internal_path
    
    return exe_path


def load_products():
    """加载商品配置"""
    products = {}
    file_path = get_products_path()
    
    if not os.path.exists(file_path):
        print(f"[INFO] 商品配置文件不存在: {file_path}")
        return products
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                barcode = row.get('条码') or ''
                name = row.get('名称') or ''
                category = row.get('分类') or ''
                
                barcode = barcode.strip() if barcode else ''
                name = name.strip() if name else ''
                category = category.strip() if category else ''
                
                if barcode and name:
                    products[barcode] = {
                        'name': name,
                        'category': category
                    }
        
        print(f"[OK] 已加载 {len(products)} 个商品配置")
    except Exception as e:
        print(f"[WARN] 商品配置加载失败: {e}")
    
    return products


def save_products(products):
    """保存商品配置"""
    file_path = get_products_path()
    
    try:
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['条码', '名称', '分类'])
            
            for barcode, info in products.items():
                writer.writerow([barcode, info['name'], info.get('category', '')])
        
        print(f"[OK] 已保存 {len(products)} 个商品配置")
        return True
    except Exception as e:
        print(f"[ERROR] 商品配置保存失败: {e}")
        return False


def find_product(barcode, products=None):
    """根据条码查找商品"""
    if products is None:
        products = load_products()
    
    return products.get(barcode)


def add_product(barcode, name, category=''):
    """添加商品"""
    products = load_products()
    products[barcode] = {
        'name': name,
        'category': category
    }
    return save_products(products)


def delete_product(barcode):
    """删除商品"""
    products = load_products()
    if barcode in products:
        del products[barcode]
        return save_products(products)
    return False


def get_all_product_names(products=None):
    """获取所有商品名称（用于语音缓存）"""
    if products is None:
        products = load_products()
    
    return [info['name'] for info in products.values() if info.get('name')]


if __name__ == "__main__":
    print("=" * 50)
    print("商品配置测试")
    print("=" * 50)
    
    products = load_products()
    print(f"商品数量: {len(products)}")
    
    for barcode, info in products.items():
        print(f"  {barcode}: {info['name']} ({info.get('category', '未分类')})")
    
    print("=" * 50)
