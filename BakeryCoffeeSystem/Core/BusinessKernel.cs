using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace BakeryCoffeeCore
{
    // Основная сущность продукта
    public class Product
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public decimal Price { get; set; }
        public string Category { get; set; } // "coffee", "bakery", "other"
        public int Stock { get; set; }

        public Product(int id, string name, decimal price, string category, int stock = 100)
        {
            Id = id;
            Name = name;
            Price = price;
            Category = category;
            Stock = stock;
        }
    }

    // Сущность заказа
    public class Order
    {
        public int Id { get; set; }
        public DateTime DateTime { get; set; }
        public List<OrderItem> Items { get; set; }
        public decimal TotalAmount { get; set; }
        public bool IsPaid { get; set; }

        public Order(int id)
        {
            Id = id;
            DateTime = DateTime.Now;
            Items = new List<OrderItem>();
            TotalAmount = 0;
            IsPaid = false;
        }

        public void AddItem(Product product, int quantity)
        {
            if (product.Stock < quantity)
                throw new InvalidOperationException($"Недостаточно товара: {product.Name}");

            var item = new OrderItem(product, quantity);
            Items.Add(item);
            TotalAmount += item.Subtotal;
            product.Stock -= quantity;
        }

        public void CompletePayment()
        {
            IsPaid = true;
        }
    }

    // Элемент заказа
    public class OrderItem
    {
        public Product Product { get; set; }
        public int Quantity { get; set; }
        public decimal Subtotal => Product.Price * Quantity;

        public OrderItem(Product product, int quantity)
        {
            Product = product;
            Quantity = quantity;
        }
    }

    // Отчёт о продажах
    public class SalesReport
    {
        public DateTime Date { get; set; }
        public int TotalOrders { get; set; }
        public decimal TotalRevenue { get; set; }
        public Dictionary<string, int> CategorySales { get; set; }

        public SalesReport(DateTime date)
        {
            Date = date;
            TotalOrders = 0;
            TotalRevenue = 0;
            CategorySales = new Dictionary<string, int>();
        }
    }

    // ГЛАВНОЕ ЯДРО - без него работа невозможна
    public class BusinessKernel
    {
        private static BusinessKernel _instance;
        private bool _isInitialized;
        private List<Product> _products;
        private List<Order> _orders;
        private int _nextOrderId;
        private int _nextProductId;

        // Приватный конструктор для паттерна Singleton
        private BusinessKernel()
        {
            _isInitialized = false;
            _products = new List<Product>();
            _orders = new List<Order>();
            _nextOrderId = 1;
            _nextProductId = 1;
        }

        // Единственный способ получить экземпляр ядра
        public static BusinessKernel GetInstance()
        {
            if (_instance == null)
            {
                _instance = new BusinessKernel();
            }
            return _instance;
        }

        // Инициализация ядра - обязательна для запуска
        public void Initialize()
        {
            if (_isInitialized)
                throw new InvalidOperationException("Ядро уже инициализировано");

            // Загрузка стандартных продуктов
            LoadDefaultProducts();
            _isInitialized = true;
        }

        public bool IsInitialized => _isInitialized;

        private void LoadDefaultProducts()
        {
            _products.Add(new Product(_nextProductId++, "Эспрессо", 150, "coffee"));
            _products.Add(new Product(_nextProductId++, "Капучино", 200, "coffee"));
            _products.Add(new Product(_nextProductId++, "Латте", 220, "coffee"));
            _products.Add(new Product(_nextProductId++, "Круассан", 120, "bakery"));
            _products.Add(new Product(_nextProductId++, "Булочка с корицей", 100, "bakery"));
            _products.Add(new Product(_nextProductId++, "Чизкейк", 250, "bakery"));
        }

        // Методы бизнес-логики
        public List<Product> GetAllProducts()
        {
            CheckInitialized();
            return new List<Product>(_products);
        }

        public Product GetProductById(int id)
        {
            CheckInitialized();
            return _products.FirstOrDefault(p => p.Id == id);
        }

        public Order CreateOrder()
        {
            CheckInitialized();
            return new Order(_nextOrderId++);
        }

        public void ProcessOrder(Order order)
        {
            CheckInitialized();
            if (order.Items.Count == 0)
                throw new InvalidOperationException("Заказ пуст");

            order.CompletePayment();
            _orders.Add(order);
        }

        public SalesReport GenerateDailyReport(DateTime date)
        {
            CheckInitialized();
            var report = new SalesReport(date);
            var dailyOrders = _orders.Where(o => o.DateTime.Date == date.Date && o.IsPaid).ToList();

            report.TotalOrders = dailyOrders.Count;
            report.TotalRevenue = dailyOrders.Sum(o => o.TotalAmount);

            foreach (var order in dailyOrders)
            {
                foreach (var item in order.Items)
                {
                    if (!report.CategorySales.ContainsKey(item.Product.Category))
                        report.CategorySales[item.Product.Category] = 0;
                    report.CategorySales[item.Product.Category] += item.Quantity;
                }
            }

            return report;
        }

        public void SaveData(string filePath)
        {
            CheckInitialized();
            using (var writer = new StreamWriter(filePath))
            {
                writer.WriteLine($"Дата сохранения: {DateTime.Now}");
                writer.WriteLine($"Всего заказов: {_orders.Count}");
                writer.WriteLine($"Всего товаров: {_products.Count}");
                foreach (var order in _orders)
                {
                    writer.WriteLine($"Заказ #{order.Id}: {order.TotalAmount} руб. (Оплачен: {order.IsPaid})");
                }
            }
        }

        private void CheckInitialized()
        {
            if (!_isInitialized)
                throw new InvalidOperationException("Ядро не инициализировано! Запуск без ядра невозможен.");
        }
    }
}
