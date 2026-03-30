using System;
using System.Runtime.InteropServices;

namespace BakeryCoffeeCore
{
    // Класс для экспорта функций ядра в C++ приложение
    // Это позволяет C++ коду вызывать методы C# ядра
    public class KernelExport
    {
        // Экспортируемая функция для инициализации ядра
        [DllExport("InitializeKernel", CallingConvention = StdCall)]
        public static int InitializeKernel()
        {
            try
            {
                var kernel = BusinessKernel.GetInstance();
                kernel.Initialize();
                
                if (kernel.IsInitialized)
                {
                    return 1; // Успех
                }
                
                return 0; // Ошибка
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка: {ex.Message}");
                return -1;
            }
        }
        
        // Экспортируемая функция для получения статуса ядра
        [DllExport("GetKernelStatus", CallingConvention = StdCall)]
        [return: MarshalAs(UnmanagedType.LPStr)]
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
    }
    
    // Атрибут для экспорта функций из DLL
    [AttributeUsage(AttributeTargets.Method)]
    public class DllExportAttribute : Attribute
    {
        public string Name { get; }
        public CallingConvention CallingConvention { get; }
        
        public DllExportAttribute(string name, CallingConvention callingConvention)
        {
            Name = name;
            CallingConvention = callingConvention;
        }
    }
}
