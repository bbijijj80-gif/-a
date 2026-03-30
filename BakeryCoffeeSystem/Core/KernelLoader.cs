using System;
using System.IO;
using System.Reflection;

namespace BakeryCoffeeCore
{
    public class KernelLoader
    {
        // Статический метод для загрузки и инициализации ядра
        // Вызывается из C++ приложения через C++/CLI или P/Invoke
        public static int InitializeKernel()
        {
            try
            {
                var kernel = BusinessKernel.GetInstance();
                kernel.Initialize();
                
                if (kernel.IsInitialized)
                {
                    Console.WriteLine("Ядро успешно инициализировано");
                    return 1; // Успех
                }
                
                return 0; // Ошибка
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка инициализации ядра: {ex.Message}");
                return -1;
            }
        }
        
        public static string GetKernelStatus()
        {
            try
            {
                var kernel = BusinessKernel.GetInstance();
                return kernel.IsInitialized ? "ACTIVE" : "INACTIVE";
            }
            catch
            {
                return "ERROR";
            }
        }
        
        // Точка входа для проверки обязательности ядра
        public static void Main(string[] args)
        {
            Console.WriteLine("=== Bakery Coffee Business Kernel ===");
            Console.WriteLine("Это ядро системы. Без него приложение не может работать.");
            
            var result = InitializeKernel();
            
            if (result == 1)
            {
                Console.WriteLine("Ядро работает. Система готова к использованию.");
                Console.WriteLine("Статус: " + GetKernelStatus());
            }
            else
            {
                Console.WriteLine("КРИТИЧЕСКАЯ ОШИБКА: Ядро не удалось инициализировать!");
                Console.WriteLine("Приложение не может быть запущено без рабочего ядра.");
                Environment.Exit(1);
            }
        }
    }
}
