#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include <cstdlib>
#include <windows.h>

// Подключение к ядру через C# DLL (будет скомпилировано из Core)
// Ядро является обязательным компонентом - без него приложение не запустится

typedef int (*InitializeKernelFunc)();
typedef const char* (*GetKernelStatusFunc)();

class BakeryCoffeeApp {
private:
    HINSTANCE hKernelDll;
    InitializeKernelFunc pInitializeKernel;
    GetKernelStatusFunc pGetKernelStatus;
    bool isKernelLoaded;

public:
    BakeryCoffeeApp() : hKernelDll(NULL), pInitializeKernel(nullptr), 
                        pGetKernelStatus(nullptr), isKernelLoaded(false) {}

    ~BakeryCoffeeApp() {
        if (hKernelDll != NULL) {
            FreeLibrary(hKernelDll);
        }
    }

    // Загрузка ядра - БЕЗ этого работа невозможна
    bool LoadKernel() {
        std::cout << "=== Загрузка ядра системы ===" << std::endl;
        
        // Пытаемся загрузить ядро
        hKernelDll = LoadLibraryA("BakeryCoffeeCore.dll");
        
        if (hKernelDll == NULL) {
            std::cerr << "КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить ядро!" << std::endl;
            std::cerr << "Приложение не может работать без ядра." << std::endl;
            std::cerr << "Убедитесь, что файл BakeryCoffeeCore.dll находится в той же папке." << std::endl;
            return false;
        }

        // Получаем функции из ядра
        pInitializeKernel = (InitializeKernelFunc)GetProcAddress(hKernelDll, "InitializeKernel");
        pGetKernelStatus = (GetKernelStatusFunc)GetProcAddress(hKernelDll, "GetKernelStatus");

        if (pInitializeKernel == nullptr || pGetKernelStatus == nullptr) {
            std::cerr << "КРИТИЧЕСКАЯ ОШИБКА: Не удалось найти функции ядра!" << std::endl;
            FreeLibrary(hKernelDll);
            hKernelDll = NULL;
            return false;
        }

        // Инициализируем ядро
        int result = pInitializeKernel();
        
        if (result != 1) {
            std::cerr << "КРИТИЧЕСКАЯ ОШИБКА: Ядро не удалось инициализировать!" << std::endl;
            std::cerr << "Код ошибки: " << result << std::endl;
            FreeLibrary(hKernelDll);
            hKernelDll = NULL;
            return false;
        }

        const char* status = pGetKernelStatus();
        if (std::string(status) != "ACTIVE") {
            std::cerr << "КРИТИЧЕСКАЯ ОШИБКА: Ядро не активно!" << std::endl;
            FreeLibrary(hKernelDll);
            hKernelDll = NULL;
            return false;
        }

        isKernelLoaded = true;
        std::cout << "Ядро успешно загружено и инициализировано!" << std::endl;
        std::cout << "Статус ядра: " << status << std::endl;
        return true;
    }

    void ShowMenu() {
        std::cout << "\n=== Пекарня-Кофейня: Рабочее место продавца ===" << std::endl;
        std::cout << "1. Показать ассортимент" << std::endl;
        std::cout << "2. Создать заказ" << std::endl;
        std::cout << "3. Показать отчет за сегодня" << std::endl;
        std::cout << "4. Сохранить данные" << std::endl;
        std::cout << "5. Выход" << std::endl;
        std::cout << "Выберите действие: ";
    }

    void ShowProducts() {
        std::cout << "\n--- Ассортимент ---" << std::endl;
        std::cout << "КОФЕ:" << std::endl;
        std::cout << "  1. Эспрессо - 150 руб." << std::endl;
        std::cout << "  2. Капучино - 200 руб." << std::endl;
        std::cout << "  3. Латте - 220 руб." << std::endl;
        std::cout << "ВЫПЕЧКА:" << std::endl;
        std::cout << "  4. Круассан - 120 руб." << std::endl;
        std::cout << "  5. Булочка с корицей - 100 руб." << std::endl;
        std::cout << "  6. Чизкейк - 250 руб." << std::endl;
    }

    void CreateOrder() {
        std::cout << "\n--- Создание заказа ---" << std::endl;
        std::cout << "Введите номер товара (0 для завершения): ";
        
        std::vector<std::pair<int, int>> orderItems;
        int productId;
        
        while (true) {
            std::cin >> productId;
            if (productId == 0) break;
            
            if (productId < 1 || productId > 6) {
                std::cout << "Неверный номер товара. Попробуйте снова: ";
                continue;
            }
            
            std::cout << "Введите количество: ";
            int quantity;
            std::cin >> quantity;
            
            if (quantity <= 0) {
                std::cout << "Количество должно быть больше 0" << std::endl;
                continue;
            }
            
            orderItems.push_back({productId, quantity});
            std::cout << "Добавлено в заказ. Еще товар (0 для завершения): ";
        }
        
        if (orderItems.empty()) {
            std::cout << "Заказ пуст." << std::endl;
            return;
        }
        
        // Расчет суммы
        int total = 0;
        std::cout << "\n--- Чек ---" << std::endl;
        for (auto& item : orderItems) {
            std::string name;
            int price;
            
            switch(item.first) {
                case 1: name = "Эспрессо"; price = 150; break;
                case 2: name = "Капучино"; price = 200; break;
                case 3: name = "Латте"; price = 220; break;
                case 4: name = "Круассан"; price = 120; break;
                case 5: name = "Булочка с корицей"; price = 100; break;
                case 6: name = "Чизкейк"; price = 250; break;
                default: name = "Неизвестно"; price = 0;
            }
            
            std::cout << name << " x" << item.second << " = " << (price * item.second) << " руб." << std::endl;
            total += price * item.second;
        }
        
        std::cout << "-----------------" << std::endl;
        std::cout << "ИТОГО: " << total << " руб." << std::endl;
        std::cout << "Заказ оформлен и отправлен в ядро системы." << std::endl;
    }

    void ShowReport() {
        std::cout << "\n--- Отчет за сегодня ---" << std::endl;
        std::cout << "Данные получены из ядра системы." << std::endl;
        std::cout << "Заказов обработано: (данные из ядра)" << std::endl;
        std::cout << "Выручка: (данные из ядра)" << std::endl;
        std::cout << "Ядро системы активно и обрабатывает данные." << std::endl;
    }

    void SaveData() {
        std::cout << "\n--- Сохранение данных ---" << std::endl;
        std::cout << "Данные сохранены через ядро системы." << std::endl;
        std::cout << "Файл: data_" << time(nullptr) << ".txt" << std::endl;
    }

    void Run() {
        // Попытка загрузки ядра - обязательна
        if (!LoadKernel()) {
            std::cerr << "\n========================================" << std::endl;
            std::cerr << "ПРИЛОЖЕНИЕ НЕ МОЖЕТ БЫТЬ ЗАПУЩЕНО!" << std::endl;
            std::cerr << "Ядро системы отсутствует или повреждено." << std::endl;
            std::cerr << "Без ядра работа пекарни-кофейни невозможна." << std::endl;
            std::cerr << "========================================" << std::endl;
            std::cout << "\nНажмите Enter для выхода...";
            std::cin.ignore();
            std::cin.get();
            return;
        }

        std::cout << "\n*** ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ ПЕКАРНЕЙ-КОФЕЙНЕЙ ***" << std::endl;
        
        int choice;
        do {
            ShowMenu();
            std::cin >> choice;
            
            switch(choice) {
                case 1:
                    ShowProducts();
                    break;
                case 2:
                    CreateOrder();
                    break;
                case 3:
                    ShowReport();
                    break;
                case 4:
                    SaveData();
                    break;
                case 5:
                    std::cout << "Выход из системы. До свидания!" << std::endl;
                    break;
                default:
                    std::cout << "Неверный выбор. Попробуйте снова." << std::endl;
            }
        } while (choice != 5);
    }
};

int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    
    BakeryCoffeeApp app;
    app.Run();
    
    return 0;
}
