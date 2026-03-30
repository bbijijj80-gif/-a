"""
ЯДРО СИСТЕМЫ УПРАВЛЕНИЯ ПЕКАРНЕЙ-КОФЕЙНЕЙ
Без этого модуля запуск программы невозможен!
Содержит всю бизнес-логику приложения.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


# === КОНСТАНТЫ ЯДРА ===
CORE_VERSION = "1.0.0"
CORE_SIGNATURE = "BAKERY_CORE_AUTHENTIC"
DATA_FILE = "bakery_data.json"


class CoreAuthenticationError(Exception):
    """Ошибка аутентификации ядра"""
    pass


class CoreValidationError(Exception):
    """Ошибка валидации данных ядра"""
    pass


@dataclass
class Product:
    """Товар (выпечка или напиток)"""
    id: int
    name: str
    category: str  # 'pastry' или 'drink'
    price: float
    cost: float  # себестоимость
    quantity: int
    created_at: str


@dataclass
class Sale:
    """Продажа"""
    id: int
    items: List[Dict]  # [{product_id, quantity, price}]
    total: float
    timestamp: str
    seller: str


@dataclass
class InventoryItem:
    """Элемент инвентаря (ингредиенты)"""
    id: int
    name: str
    quantity: float
    unit: str  # кг, л, шт
    min_quantity: float  # минимальный остаток


class BakeryCore:
    """
    ГЛАВНОЕ ЯДРО СИСТЕМЫ
    Содержит всю бизнес-логику пекарни-кофейни
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if BakeryCore._initialized:
            return
        
        # Проверка подлинности ядра
        self._verify_core_integrity()
        
        self.products: Dict[int, Product] = {}
        self.sales: List[Sale] = []
        self.inventory: Dict[int, InventoryItem] = {}
        self.settings: Dict = {
            'shop_name': 'Пекарня-Кофейня',
            'seller_name': '',
            'tax_rate': 0.06,
            'currency': '₽'
        }
        self._next_product_id = 1
        self._next_sale_id = 1
        self._next_inventory_id = 1
        
        BakeryCore._initialized = True
    
    def _verify_core_integrity(self):
        """Проверка целостности ядра - критически важная функция"""
        # Проверка сигнатуры
        if not hasattr(self, '_signature'):
            self._signature = CORE_SIGNATURE
        
        if self._signature != CORE_SIGNATURE:
            raise CoreAuthenticationError(
                "НАРУШЕНИЕ ЦЕЛОСТНОСТИ ЯДРА! Программа не может быть запущена."
            )
        
        # Проверка версии
        current_version = tuple(map(int, CORE_VERSION.split('.')))
        if current_version[0] < 1:
            raise CoreAuthenticationError("Несовместимая версия ядра!")
        
        print(f"✓ Ядро системы версии {CORE_VERSION} успешно инициализировано")
        print(f"✓ Сигнатура подтверждена: {self._signature}")
    
    def initialize(self, data_path: Optional[str] = None) -> bool:
        """Инициализация ядра с загрузкой данных"""
        if data_path:
            return self.load_data(data_path)
        return True
    
    # === МЕТОДЫ УПРАВЛЕНИЯ ТОВАРАМИ ===
    
    def add_product(self, name: str, category: str, price: float, 
                    cost: float, quantity: int) -> Product:
        """Добавление нового товара"""
        if category not in ['pastry', 'drink']:
            raise CoreValidationError("Категория должна быть 'pastry' или 'drink'")
        
        if price <= 0 or cost <= 0:
            raise CoreValidationError("Цена и себестоимость должны быть положительными")
        
        if quantity < 0:
            raise CoreValidationError("Количество не может быть отрицательным")
        
        product = Product(
            id=self._next_product_id,
            name=name,
            category=category,
            price=price,
            cost=cost,
            quantity=quantity,
            created_at=datetime.now().isoformat()
        )
        
        self.products[self._next_product_id] = product
        self._next_product_id += 1
        
        return product
    
    def update_product_quantity(self, product_id: int, quantity_change: int) -> bool:
        """Обновление количества товара (после продажи или поступления)"""
        if product_id not in self.products:
            raise CoreValidationError(f"Товар с ID {product_id} не найден")
        
        product = self.products[product_id]
        new_quantity = product.quantity + quantity_change
        
        if new_quantity < 0:
            raise CoreValidationError("Недостаточно товара на складе")
        
        product.quantity = new_quantity
        return True
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Получение товаров по категории"""
        return [p for p in self.products.values() if p.category == category]
    
    def get_available_products(self) -> List[Product]:
        """Получение всех доступных товаров (в наличии)"""
        return [p for p in self.products.values() if p.quantity > 0]
    
    # === МЕТОДЫ ОБРАБОТКИ ПРОДАЖ ===
    
    def create_sale(self, items: List[Dict], seller: str) -> Sale:
        """
        Создание новой продажи
        items: [{'product_id': int, 'quantity': int}, ...]
        """
        if not items:
            raise CoreValidationError("Продажа должна содержать хотя бы один товар")
        
        sale_items = []
        total = 0.0
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            if product_id not in self.products:
                raise CoreValidationError(f"Товар с ID {product_id} не найден")
            
            product = self.products[product_id]
            
            if product.quantity < quantity:
                raise CoreValidationError(
                    f"Недостаточно товара '{product.name}'. В наличии: {product.quantity}"
                )
            
            # Обновляем количество товара
            self.update_product_quantity(product_id, -quantity)
            
            item_total = product.price * quantity
            total += item_total
            
            sale_items.append({
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'price': product.price,
                'total': item_total
            })
        
        sale = Sale(
            id=self._next_sale_id,
            items=sale_items,
            total=total,
            timestamp=datetime.now().isoformat(),
            seller=seller
        )
        
        self.sales.append(sale)
        self._next_sale_id += 1
        
        return sale
    
    def get_daily_sales(self, date: Optional[str] = None) -> List[Sale]:
        """Получение продаж за день"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return [
            s for s in self.sales 
            if s.timestamp.startswith(date)
        ]
    
    def calculate_daily_revenue(self, date: Optional[str] = None) -> float:
        """Расчет дневной выручки"""
        daily_sales = self.get_daily_sales(date)
        return sum(s.total for s in daily_sales)
    
    def calculate_daily_profit(self, date: Optional[str] = None) -> float:
        """Расчет дневной прибыли (выручка - себестоимость)"""
        daily_sales = self.get_daily_sales(date)
        
        profit = 0.0
        for sale in daily_sales:
            for item in sale.items:
                product = self.products.get(item['product_id'])
                if product:
                    profit += (product.price - product.cost) * item['quantity']
        
        return profit
    
    # === МЕТОДЫ УПРАВЛЕНИЯ ИНВЕНТАРЕМ ===
    
    def add_inventory_item(self, name: str, quantity: float, 
                          unit: str, min_quantity: float) -> InventoryItem:
        """Добавление элемента инвентаря"""
        item = InventoryItem(
            id=self._next_inventory_id,
            name=name,
            quantity=quantity,
            unit=unit,
            min_quantity=min_quantity
        )
        
        self.inventory[self._next_inventory_id] = item
        self._next_inventory_id += 1
        
        return item
    
    def update_inventory(self, item_id: int, quantity_change: float) -> bool:
        """Обновление количества ингредиента"""
        if item_id not in self.inventory:
            raise CoreValidationError(f"Ингредиент с ID {item_id} не найден")
        
        item = self.inventory[item_id]
        new_quantity = item.quantity + quantity_change
        
        if new_quantity < 0:
            raise CoreValidationError("Недостаточно ингредиента")
        
        item.quantity = new_quantity
        return True
    
    def get_low_stock_items(self) -> List[InventoryItem]:
        """Получение ингредиентов с низким остатком"""
        return [
            item for item in self.inventory.values()
            if item.quantity <= item.min_quantity
        ]
    
    # === МЕТОДЫ ОТЧЕТНОСТИ ===
    
    def get_sales_report(self, start_date: str, end_date: str) -> Dict:
        """Отчет о продажах за период"""
        filtered_sales = [
            s for s in self.sales
            if start_date <= s.timestamp[:10] <= end_date
        ]
        
        total_revenue = sum(s.total for s in filtered_sales)
        total_profit = self._calculate_period_profit(filtered_sales)
        
        # Группировка по товарам
        product_stats = {}
        for sale in filtered_sales:
            for item in sale.items:
                pid = item['product_id']
                if pid not in product_stats:
                    product_stats[pid] = {
                        'name': item['product_name'],
                        'quantity_sold': 0,
                        'revenue': 0
                    }
                product_stats[pid]['quantity_sold'] += item['quantity']
                product_stats[pid]['revenue'] += item['total']
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'total_sales': len(filtered_sales),
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'products': list(product_stats.values())
        }
    
    def _calculate_period_profit(self, sales: List[Sale]) -> float:
        """Расчет прибыли за период"""
        profit = 0.0
        for sale in sales:
            for item in sale.items:
                product = self.products.get(item['product_id'])
                if product:
                    profit += (product.price - product.cost) * item['quantity']
        return profit
    
    # === МЕТОДЫ СОХРАНЕНИЯ/ЗАГРУЗКИ ДАННЫХ ===
    
    def save_data(self, filepath: str) -> bool:
        """Сохранение данных ядра в файл"""
        try:
            data = {
                'core_version': CORE_VERSION,
                'core_signature': self._signature,
                'products': {str(k): asdict(v) for k, v in self.products.items()},
                'sales': [asdict(s) for s in self.sales],
                'inventory': {str(k): asdict(v) for k, v in self.inventory.items()},
                'settings': self.settings,
                'next_ids': {
                    'product': self._next_product_id,
                    'sale': self._next_sale_id,
                    'inventory': self._next_inventory_id
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            raise CoreValidationError(f"Ошибка сохранения данных: {e}")
    
    def load_data(self, filepath: str) -> bool:
        """Загрузка данных ядра из файла"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверка версии ядра
            if data.get('core_version') != CORE_VERSION:
                print(f"Предупреждение: версия данных {data.get('core_version')}, "
                      f"версия ядра {CORE_VERSION}")
            
            # Проверка сигнатуры
            if data.get('core_signature') != CORE_SIGNATURE:
                raise CoreAuthenticationError("Повреждение данных! Несоответствие сигнатуры ядра.")
            
            # Загрузка продуктов
            self.products = {
                int(k): Product(**v) for k, v in data.get('products', {}).items()
            }
            
            # Загрузка продаж
            self.sales = [Sale(**v) for v in data.get('sales', [])]
            
            # Загрузка инвентаря
            self.inventory = {
                int(k): InventoryItem(**v) for k, v in data.get('inventory', {}).items()
            }
            
            # Загрузка настроек
            self.settings.update(data.get('settings', {}))
            
            # Восстановление счетчиков ID
            next_ids = data.get('next_ids', {})
            self._next_product_id = next_ids.get('product', 1)
            self._next_sale_id = next_ids.get('sale', 1)
            self._next_inventory_id = next_ids.get('inventory', 1)
            
            return True
        except json.JSONDecodeError as e:
            raise CoreValidationError(f"Повреждение файла данных: {e}")
        except Exception as e:
            raise CoreValidationError(f"Ошибка загрузки данных: {e}")
    
    def export_report(self, filepath: str, report_type: str = 'daily') -> bool:
        """Экспорт отчета в текстовый файл"""
        try:
            if report_type == 'daily':
                report = self.get_sales_report(
                    datetime.now().strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d')
                )
            else:
                report = self.get_sales_report(
                    (datetime.now()).strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d')
                )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write(f"ОТЧЕТ: {self.settings['shop_name']}\n")
                f.write(f"Период: {report['period']['start']} - {report['period']['end']}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Всего продаж: {report['total_sales']}\n")
                f.write(f"Выручка: {report['total_revenue']:.2f} {self.settings['currency']}\n")
                f.write(f"Прибыль: {report['total_profit']:.2f} {self.settings['currency']}\n\n")
                f.write("ПРОДАЖИ ПО ТОВАРАМ:\n")
                f.write("-" * 50 + "\n")
                for prod in report['products']:
                    f.write(f"{prod['name']}: {prod['quantity_sold']} шт. = "
                           f"{prod['revenue']:.2f} {self.settings['currency']}\n")
            
            return True
        except Exception as e:
            raise CoreValidationError(f"Ошибка экспорта отчета: {e}")
    
    def get_core_info(self) -> Dict:
        """Получение информации о ядре"""
        return {
            'version': CORE_VERSION,
            'signature': self._signature,
            'initialized': self._initialized,
            'products_count': len(self.products),
            'sales_count': len(self.sales),
            'inventory_count': len(self.inventory)
        }


# === ФАБРИЧНЫЙ МЕТОД ДЛЯ СОЗДАНИЯ ЯДРА ===
def create_core() -> BakeryCore:
    """
    Единственный способ создать экземпляр ядра
    Проверяет целостность перед созданием
    """
    core = BakeryCore()
    return core


# === ТОЧКА ВХОДА ДЛЯ ПРОВЕРКИ ===
if __name__ == "__main__":
    print("Запуск проверки ядра...")
    try:
        core = create_core()
        info = core.get_core_info()
        print(f"\nЯдро успешно инициализировано!")
        print(f"Версия: {info['version']}")
        print(f"Статус: {'Активно' if info['initialized'] else 'Неактивно'}")
    except CoreAuthenticationError as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("Программа не может быть запущена без целостного ядра!")
        exit(1)
