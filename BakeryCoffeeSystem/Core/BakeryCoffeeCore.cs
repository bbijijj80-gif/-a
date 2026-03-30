using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace BakeryCoffeeCore
{
    // Основные модели данных
    public class Product
    {
        public int Id { get; set; }
        public string Name { get; set; } = "";
        public decimal Price { get; set; }
        public string Category { get; set; } = "";
        public int Stock { get; set; }
    }

    public class OrderItem
    {
        public int ProductId { get; set; }
        public string ProductName { get; set; } = "";
        public int Quantity { get; set; }
        public decimal Price { get; set; }
        public decimal Total => Price * Quantity;
    }

    public class Order
    {
        public int Id { get; set; }
        public DateTime DateTime { get; set; }
        public List<OrderItem> Items { get; set; } = new();
        public decimal TotalAmount => Items.Sum(i => i.Total);
        public string SellerName { get; set; } = "";
        public bool IsPaid { get; set; }
    }

    public class ShiftReport
    {
        public DateTime Date { get; set; }
        public string SellerName { get; set; } = "";
        public List<Order> Orders { get; set; } = new();
        public decimal TotalRevenue => Orders.Sum(o => o.TotalAmount);
        public int TotalOrders => Orders.Count;
    }

    // Ядро системы - без него работа невозможна
    public class CoreEngine
    {
        private readonly string _dataPath;
        private readonly string _productsFile;
        private readonly string _ordersFile;
        private readonly string _settingsFile;
        
        private List<Product> _products = new();
        private List<Order> _orders = new();
        private bool _isInitialized = false;

        public CoreEngine(string dataPath)
        {
            _dataPath = dataPath;
            _productsFile = Path.Combine(_dataPath, "products.json");
            _ordersFile = Path.Combine(_dataPath, "orders.json");
            _settingsFile = Path.Combine(_dataPath, "settings.json");
        }

        // Инициализация ядра - обязательный шаг
        public void Initialize()
        {
            if (!Directory.Exists(_dataPath))
            {
                Directory.CreateDirectory(_dataPath);
            }

            LoadData();
            _isInitialized = true;
            
            if (!_products.Any())
            {
                InitializeDefaultProducts();
            }
        }

        public bool IsReady => _isInitialized;

        private void LoadData()
        {
            if (File.Exists(_productsFile))
            {
                var json = File.ReadAllText(_productsFile, System.Text.Encoding.UTF8);
                _products = JsonSerializer.Deserialize<List<Product>>(json) ?? new List<Product>();
            }

            if (File.Exists(_ordersFile))
            {
                var json = File.ReadAllText(_ordersFile, System.Text.Encoding.UTF8);
                _orders = JsonSerializer.Deserialize<List<Order>>(json) ?? new List<Order>();
            }
        }

        private void SaveData()
        {
            if (!_isInitialized)
                throw new InvalidOperationException("Ядро не инициализировано!");

            var productsJson = JsonSerializer.Serialize(_products, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_productsFile, productsJson, System.Text.Encoding.UTF8);

            var ordersJson = JsonSerializer.Serialize(_orders, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_ordersFile, ordersJson, System.Text.Encoding.UTF8);
        }

        private void InitializeDefaultProducts()
        {
            _products = new List<Product>
            {
                new Product { Id = 1, Name = "Эспрессо", Price = 120, Category = "Кофе", Stock = 100 },
                new Product { Id = 2, Name = "Капучино", Price = 180, Category = "Кофе", Stock = 100 },
                new Product { Id = 3, Name = "Латте", Price = 200, Category = "Кофе", Stock = 100 },
                new Product { Id = 4, Name = "Круассан", Price = 150, Category = "Выпечка", Stock = 50 },
                new Product { Id = 5, Name = "Багет", Price = 80, Category = "Выпечка", Stock = 30 },
                new Product { Id = 6, Name = "Чизкейк", Price = 250, Category = "Десерты", Stock = 20 }
            };
            SaveData();
        }

        // Управление продуктами
        public List<Product> GetProducts()
        {
            CheckInitialized();
            return _products.ToList();
        }

        public Product? GetProduct(int id)
        {
            CheckInitialized();
            return _products.FirstOrDefault(p => p.Id == id);
        }

        public void AddProduct(Product product)
        {
            CheckInitialized();
            product.Id = _products.Max(p => p.Id) + 1;
            _products.Add(product);
            SaveData();
        }

        public void UpdateStock(int productId, int quantity)
        {
            CheckInitialized();
            var product = GetProduct(productId);
            if (product != null)
            {
                product.Stock += quantity;
                SaveData();
            }
        }

        // Управление заказами
        public Order CreateOrder(string sellerName)
        {
            CheckInitialized();
            return new Order
            {
                Id = _orders.Max(o => o.Id) + 1,
                DateTime = DateTime.Now,
                SellerName = sellerName,
                IsPaid = false
            };
        }

        public void AddItemToOrder(Order order, int productId, int quantity)
        {
            CheckInitialized();
            var product = GetProduct(productId);
            if (product != null && product.Stock >= quantity)
            {
                order.Items.Add(new OrderItem
                {
                    ProductId = productId,
                    ProductName = product.Name,
                    Quantity = quantity,
                    Price = product.Price
                });
                product.Stock -= quantity;
                SaveData();
            }
            else
            {
                throw new InvalidOperationException("Недостаточно товара на складе");
            }
        }

        public void CompleteOrder(Order order)
        {
            CheckInitialized();
            order.IsPaid = true;
            _orders.Add(order);
            SaveData();
        }

        public List<Order> GetTodayOrders()
        {
            CheckInitialized();
            var today = DateTime.Today;
            return _orders.Where(o => o.DateTime.Date == today).ToList();
        }

        public ShiftReport GenerateShiftReport(string sellerName)
        {
            CheckInitialized();
            var today = DateTime.Today;
            return new ShiftReport
            {
                Date = today,
                SellerName = sellerName,
                Orders = _orders.Where(o => o.DateTime.Date == today && o.SellerName == sellerName).ToList()
            };
        }

        public decimal GetDailyRevenue()
        {
            CheckInitialized();
            return GetTodayOrders().Sum(o => o.TotalAmount);
        }

        private void CheckInitialized()
        {
            if (!_isInitialized)
                throw new InvalidOperationException("Ядро не инициализировано! Запуск без ядра невозможен.");
        }
    }

    // Экспорт функций для C++ через C-style interface
    public static class CoreExport
    {
        private static CoreEngine? _engine;
        private static Order? _currentOrder;

        [System.Runtime.InteropServices.DllExport("Core_Initialize", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int Initialize([System.Runtime.InteropServices.In] byte[] dataPath)
        {
            try
            {
                var path = System.Text.Encoding.UTF8.GetString(dataPath).TrimEnd('\0');
                _engine = new CoreEngine(path);
                _engine.Initialize();
                return _engine.IsReady ? 1 : 0;
            }
            catch
            {
                return 0;
            }
        }

        [System.Runtime.InteropServices.DllExport("Core_IsReady", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int IsReady()
        {
            return _engine?.IsReady == true ? 1 : 0;
        }

        [System.Runtime.InteropServices.DllExport("Core_GetProductsJson", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int GetProductsJson(byte[] buffer, int bufferSize)
        {
            if (_engine == null) return 0;
            
            var products = _engine.GetProducts();
            var json = JsonSerializer.Serialize(products, new JsonSerializerOptions { WriteIndented = false });
            var bytes = System.Text.Encoding.UTF8.GetBytes(json);
            
            if (bytes.Length > bufferSize) return -1;
            
            Array.Copy(bytes, buffer, bytes.Length);
            return bytes.Length;
        }

        [System.Runtime.InteropServices.DllExport("Core_CreateOrder", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int CreateOrder([System.Runtime.InteropServices.In] byte[] sellerName)
        {
            if (_engine == null) return -1;
            
            var name = System.Text.Encoding.UTF8.GetString(sellerName).TrimEnd('\0');
            _currentOrder = _engine.CreateOrder(name);
            return _currentOrder.Id;
        }

        [System.Runtime.InteropServices.DllExport("Core_AddItemToOrder", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int AddItemToOrder(int productId, int quantity)
        {
            if (_engine == null || _currentOrder == null) return 0;
            
            try
            {
                _engine.AddItemToOrder(_currentOrder, productId, quantity);
                return 1;
            }
            catch
            {
                return 0;
            }
        }

        [System.Runtime.InteropServices.DllExport("Core_CompleteOrder", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int CompleteOrder()
        {
            if (_engine == null || _currentOrder == null) return 0;
            
            _engine.CompleteOrder(_currentOrder);
            var total = (int)(_currentOrder.TotalAmount * 100);
            _currentOrder = null;
            return total;
        }

        [System.Runtime.InteropServices.DllExport("Core_GetDailyRevenue", CallingConvention = System.Runtime.InteropServices.CallingConvention.StdCall)]
        public static int GetDailyRevenue()
        {
            if (_engine == null) return 0;
            return (int)(_engine.GetDailyRevenue() * 100);
        }
    }
}
