"""
ПРИЛОЖЕНИЕ ДЛЯ УПРАВЛЕНИЯ ПЕКАРНЕЙ-КОФЕЙНЕЙ
Интерфейс для работы продавца
Требует наличия ядра (core.py) для запуска!
"""

import sys
import os
from datetime import datetime

# Проверка наличия ядра - критически важно!
try:
    from core import create_core, CoreAuthenticationError, CoreValidationError
except ImportError:
    print("=" * 60)
    print("❌ КРИТИЧЕСКАЯ ОШИБКА!")
    print("Ядро системы не найдено или повреждено!")
    print("Без файла core.py запуск программы невозможен!")
    print("=" * 60)
    sys.exit(1)


class BakeryApp:
    """Основное приложение пекарни-кофейни"""
    
    def __init__(self):
        # Попытка создания ядра - без этого программа не запустится
        try:
            self.core = create_core()
        except CoreAuthenticationError as e:
            print(f"\n❌ ОШИБКА АУТЕНТИФИКАЦИИ ЯДРА: {e}")
            print("Программа не может быть запущена!")
            sys.exit(1)
        
        self.data_file = "bakery_data.json"
        self.current_seller = ""
        self.running = True
    
    def start(self):
        """Запуск приложения"""
        print("\n" + "=" * 60)
        print("🥐 СИСТЕМА УПРАВЛЕНИЯ ПЕКАРНЕЙ-КОФЕЙНЕЙ 🥐")
        print("=" * 60)
        
        # Загрузка данных
        if self.core.load_data(self.data_file):
            print("✓ Данные успешно загружены")
        else:
            print("ℹ Создана новая база данных")
            self._initialize_demo_data()
        
        # Приветствие
        info = self.core.get_core_info()
        print(f"\n📊 Статус системы:")
        print(f"   Товаров в меню: {info['products_count']}")
        print(f"   Всего продаж: {info['sales_count']}")
        print(f"   Позиций инвентаря: {info['inventory_count']}")
        
        # Вход продавца
        self._login_seller()
        
        # Главный цикл
        self._main_menu()
    
    def _initialize_demo_data(self):
        """Инициализация демонстрационными данными"""
        print("\n📝 Инициализация базовых данных...")
        
        # Добавляем товары
        self.core.add_product("Круассан классический", "pastry", 120.0, 45.0, 20)
        self.core.add_product("Круассан с шоколадом", "pastry", 140.0, 55.0, 15)
        self.core.add_product("Багет французский", "pastry", 80.0, 30.0, 25)
        self.core.add_product("Пончик с глазурью", "pastry", 90.0, 35.0, 30)
        self.core.add_product("Маффин черничный", "pastry", 110.0, 40.0, 20)
        
        self.core.add_product("Кофе эспрессо", "drink", 90.0, 25.0, 100)
        self.core.add_product("Кофе капучино", "drink", 150.0, 40.0, 100)
        self.core.add_product("Кофе латте", "drink", 170.0, 45.0, 100)
        self.core.add_product("Чай зеленый", "drink", 80.0, 20.0, 50)
        self.core.add_product("Чай черный", "drink", 80.0, 20.0, 50)
        self.core.add_product("Горячий шоколад", "drink", 180.0, 50.0, 30)
        
        # Добавляем ингредиенты
        self.core.add_inventory_item("Мука пшеничная", 25.0, "кг", 5.0)
        self.core.add_inventory_item("Сахар", 10.0, "кг", 2.0)
        self.core.add_inventory_item("Масло сливочное", 5.0, "кг", 1.0)
        self.core.add_inventory_item("Кофе в зернах", 3.0, "кг", 0.5)
        self.core.add_inventory_item("Молоко", 20.0, "л", 5.0)
        self.core.add_inventory_item("Шоколад", 2.0, "кг", 0.5)
        
        # Сохраняем
        self.core.save_data(self.data_file)
        print("✓ Базовые данные созданы")
    
    def _login_seller(self):
        """Вход продавца"""
        while not self.current_seller:
            name = input("\n👤 Введите имя продавца: ").strip()
            if name:
                self.current_seller = name
                self.core.settings['seller_name'] = name
                print(f"✓ Добро пожаловать, {name}!")
            else:
                print("⚠ Имя не может быть пустым")
    
    def _main_menu(self):
        """Главное меню"""
        while self.running:
            print("\n" + "=" * 60)
            print(f"📋 ГЛАВНОЕ МЕНЮ | Продавец: {self.current_seller}")
            print("=" * 60)
            print("1. 💰 Новая продажа")
            print("2. 📦 Просмотр товаров")
            print("3. 📊 Отчет за день")
            print("4. 📝 Управление ассортиментом")
            print("5. 🏪 Инвентарь ингредиентов")
            print("6. ⚙ Настройки")
            print("7. 💾 Сохранить и выйти")
            print("=" * 60)
            
            choice = input("\nВыберите действие (1-7): ").strip()
            
            if choice == '1':
                self._make_sale()
            elif choice == '2':
                self._view_products()
            elif choice == '3':
                self._daily_report()
            elif choice == '4':
                self._manage_products()
            elif choice == '5':
                self._manage_inventory()
            elif choice == '6':
                self._settings()
            elif choice == '7':
                self._save_and_exit()
            else:
                print("⚠ Неверный выбор, попробуйте снова")
    
    def _make_sale(self):
        """Оформление продажи"""
        print("\n" + "=" * 60)
        print("💰 НОВАЯ ПРОДАЖА")
        print("=" * 60)
        
        cart = []
        total = 0.0
        
        while True:
            # Показываем доступные товары
            products = self.core.get_available_products()
            
            if not products:
                print("\n⚠ Нет товаров в наличии!")
                break
            
            print("\n📦 Доступные товары:")
            print("-" * 60)
            for p in products:
                category_icon = "🥐" if p.category == 'pastry' else "☕"
                print(f"{p.id}. {category_icon} {p.name} - {p.price:.0f}{self.core.settings['currency']} "
                      f"(остаток: {p.quantity})")
            
            print("-" * 60)
            print("0. ✅ Завершить продажу")
            
            try:
                choice = int(input("\nВыберите товар (номер): ").strip())
                
                if choice == 0:
                    if not cart:
                        print("⚠ Корзина пуста")
                        continue
                    break
                
                product = next((p for p in products if p.id == choice), None)
                if not product:
                    print("⚠ Товар не найден")
                    continue
                
                qty = int(input(f"Количество '{product.name}': ").strip())
                if qty <= 0:
                    print("⚠ Количество должно быть положительным")
                    continue
                
                if qty > product.quantity:
                    print(f"⚠ Недостаточно товара. В наличии: {product.quantity}")
                    continue
                
                cart.append({'product_id': product.id, 'quantity': qty})
                total += product.price * qty
                
                print(f"✓ Добавлено: {product.name} x{qty} = {product.price * qty:.0f}{self.core.settings['currency']}")
                
            except ValueError:
                print("⚠ Введите число")
        
        if cart:
            try:
                sale = self.core.create_sale(cart, self.current_seller)
                print("\n" + "=" * 60)
                print("✅ ПРОДАЖА ОФОРМЛЕНА")
                print("=" * 60)
                print(f"Номер чека: #{sale.id}")
                print(f"Товаров: {len(sale.items)}")
                print(f"ИТОГО: {sale.total:.2f}{self.core.settings['currency']}")
                print("=" * 60)
                
                # Автосохранение
                self.core.save_data(self.data_file)
                
            except CoreValidationError as e:
                print(f"\n❌ Ошибка при оформлении: {e}")
    
    def _view_products(self):
        """Просмотр товаров"""
        print("\n" + "=" * 60)
        print("📦 АССОРТИМЕНТ ТОВАРОВ")
        print("=" * 60)
        
        print("\n🥐 ВЫПЕЧКА:")
        print("-" * 60)
        pastries = self.core.get_products_by_category('pastry')
        for p in pastries:
            status = "✓" if p.quantity > 0 else "✗"
            profit = p.price - p.cost
            print(f"{status} {p.name}: {p.price:.0f}{self.core.settings['currency']} "
                  f"(себестоимость: {p.cost:.0f}, прибыль: {profit:.0f}, остаток: {p.quantity})")
        
        print("\n☕ НАПИТКИ:")
        print("-" * 60)
        drinks = self.core.get_products_by_category('drink')
        for p in drinks:
            status = "✓" if p.quantity > 0 else "✗"
            profit = p.price - p.cost
            print(f"{status} {p.name}: {p.price:.0f}{self.core.settings['currency']} "
                  f"(себестоимость: {p.cost:.0f}, прибыль: {profit:.0f}, остаток: {p.quantity})")
    
    def _daily_report(self):
        """Отчет за день"""
        print("\n" + "=" * 60)
        print("📊 ОТЧЕТ ЗА ДЕНЬ")
        print("=" * 60)
        
        today = datetime.now().strftime('%Y-%m-%d')
        sales = self.core.get_daily_sales(today)
        revenue = self.core.calculate_daily_revenue(today)
        profit = self.core.calculate_daily_profit(today)
        
        print(f"\n📅 Дата: {today}")
        print(f"💵 Выручка: {revenue:.2f}{self.core.settings['currency']}")
        print(f"💰 Прибыль: {profit:.2f}{self.core.settings['currency']}")
        print(f"🧾 Количество продаж: {len(sales)}")
        
        if sales:
            print("\n📝 Последние продажи:")
            print("-" * 60)
            for sale in sales[-5:]:  # Последние 5 продаж
                time_str = sale.timestamp[11:16]
                print(f"#{sale.id} | {time_str} | {sale.seller} | {sale.total:.2f}{self.core.settings['currency']}")
        
        # Экспорт отчета
        export = input("\n📄 Экспортировать отчет в файл? (y/n): ").strip().lower()
        if export == 'y':
            filename = f"report_{today}.txt"
            self.core.export_report(filename)
            print(f"✓ Отчет сохранен в {filename}")
    
    def _manage_products(self):
        """Управление ассортиментом"""
        print("\n" + "=" * 60)
        print("📝 УПРАВЛЕНИЕ АССОРТИМЕНТОМ")
        print("=" * 60)
        print("1. ➕ Добавить товар")
        print("2. ✏ Изменить количество")
        print("3. ← Назад")
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == '1':
            self._add_product()
        elif choice == '2':
            self._update_product_quantity()
    
    def _add_product(self):
        """Добавление товара"""
        print("\n" + "=" * 60)
        print("➕ ДОБАВИТЬ НОВЫЙ ТОВАР")
        print("=" * 60)
        
        name = input("Название товара: ").strip()
        if not name:
            print("⚠ Название не может быть пустым")
            return
        
        print("\nКатегория:")
        print("1. 🥐 Выпечка")
        print("2. ☕ Напиток")
        
        cat_choice = input("Выберите (1-2): ").strip()
        category = 'pastry' if cat_choice == '1' else 'drink'
        
        try:
            price = float(input("Цена продажи (₽): ").strip())
            cost = float(input("Себестоимость (₽): ").strip())
            quantity = int(input("Начальное количество: ").strip())
            
            product = self.core.add_product(name, category, price, cost, quantity)
            print(f"\n✓ Товар '{product.name}' добавлен с ID={product.id}")
            
            self.core.save_data(self.data_file)
            
        except ValueError:
            print("⚠ Неверный формат данных")
        except CoreValidationError as e:
            print(f"❌ Ошибка: {e}")
    
    def _update_product_quantity(self):
        """Обновление количества товара"""
        products = self.core.get_available_products()
        
        print("\n📦 ТОВАРЫ:")
        for p in products:
            print(f"{p.id}. {p.name} - ост.: {p.quantity}")
        
        try:
            pid = int(input("\nID товара: ").strip())
            change = int(input("Изменение количества (+/-): ").strip())
            
            self.core.update_product_quantity(pid, change)
            print("✓ Количество обновлено")
            
            self.core.save_data(self.data_file)
            
        except ValueError:
            print("⚠ Неверный формат")
        except CoreValidationError as e:
            print(f"❌ Ошибка: {e}")
    
    def _manage_inventory(self):
        """Управление инвентарем"""
        print("\n" + "=" * 60)
        print("🏪 ИНВЕНТАРЬ ИНГРЕДИЕНТОВ")
        print("=" * 60)
        
        inventory = self.core.inventory.values()
        
        print("\nСписок ингредиентов:")
        print("-" * 60)
        for item in inventory:
            status = "⚠ МАЛО" if item.quantity <= item.min_quantity else "✓"
            print(f"{status} {item.name}: {item.quantity} {item.unit} "
                  f"(мин: {item.min_quantity} {item.unit})")
        
        # Предупреждения
        low_stock = self.core.get_low_stock_items()
        if low_stock:
            print("\n⚠️  ТРЕБУЕТСЯ ПОПОЛНЕНИЕ:")
            for item in low_stock:
                print(f"   - {item.name}: осталось {item.quantity} {item.unit}")
        
        print("\n1. ➕ Добавить ингредиент")
        print("2. 🔄 Обновить количество")
        print("3. ← Назад")
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == '1':
            self._add_inventory_item()
        elif choice == '2':
            self._update_inventory()
    
    def _add_inventory_item(self):
        """Добавление ингредиента"""
        print("\n" + "=" * 60)
        print("➕ ДОБАВИТЬ ИНГРЕДИЕНТ")
        print("=" * 60)
        
        name = input("Название: ").strip()
        if not name:
            return
        
        try:
            quantity = float(input("Количество: ").strip())
            unit = input("Единица измерения (кг/л/шт): ").strip()
            min_qty = float(input("Минимальный остаток: ").strip())
            
            self.core.add_inventory_item(name, quantity, unit, min_qty)
            print("✓ Ингредиент добавлен")
            
            self.core.save_data(self.data_file)
            
        except ValueError:
            print("⚠ Неверный формат")
    
    def _update_inventory(self):
        """Обновление инвентаря"""
        print("\nИнгредиенты:")
        for iid, item in self.core.inventory.items():
            print(f"{iid}. {item.name} - {item.quantity} {item.unit}")
        
        try:
            iid = int(input("\nID ингредиента: ").strip())
            change = float(input("Изменение количества (+/-): ").strip())
            
            self.core.update_inventory(iid, change)
            print("✓ Инвентарь обновлен")
            
            self.core.save_data(self.data_file)
            
        except ValueError:
            print("⚠ Неверный формат")
        except CoreValidationError as e:
            print(f"❌ Ошибка: {e}")
    
    def _settings(self):
        """Настройки"""
        print("\n" + "=" * 60)
        print("⚙ НАСТРОЙКИ")
        print("=" * 60)
        print(f"Название заведения: {self.core.settings['shop_name']}")
        print(f"Продавец: {self.core.settings['seller_name']}")
        print(f"Налог: {self.core.settings['tax_rate']*100:.0f}%")
        
        print("\n1. Изменить название заведения")
        print("2. Сменить продавца")
        print("3. ← Назад")
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == '1':
            new_name = input("Новое название: ").strip()
            if new_name:
                self.core.settings['shop_name'] = new_name
                print("✓ Название обновлено")
        elif choice == '2':
            new_seller = input("Имя нового продавца: ").strip()
            if new_seller:
                self.current_seller = new_seller
                self.core.settings['seller_name'] = new_seller
                print("✓ Продавец изменен")
    
    def _save_and_exit(self):
        """Сохранение и выход"""
        print("\n" + "=" * 60)
        confirm = input("Сохранить данные и выйти? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.core.save_data(self.data_file)
            print("✓ Данные сохранены")
            print("👋 До свидания!")
            self.running = False
        else:
            print("↩ Возврат в меню")


def main():
    """Точка входа в приложение"""
    app = BakeryApp()
    app.start()


if __name__ == "__main__":
    main()
