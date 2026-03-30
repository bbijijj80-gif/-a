#include <iostream>
#include <windows.h>
#include <string>
#include <vector>
#include <cstring>

// Объявление функций ядра из DLL
typedef int (*Core_Initialize_t)(const char* dataPath);
typedef int (*Core_IsReady_t)();
typedef int (*Core_GetProductsJson_t)(char* buffer, int bufferSize);
typedef int (*Core_CreateOrder_t)(const char* sellerName);
typedef int (*Core_AddItemToOrder_t)(int productId, int quantity);
typedef int (*Core_CompleteOrder_t)();
typedef int (*Core_GetDailyRevenue_t)();

class BakeryCoffeeApp {
private:
    HMODULE hCoreDll;
    Core_Initialize_t fnInitialize;
    Core_IsReady_t fnIsReady;
    Core_GetProductsJson_t fnGetProductsJson;
    Core_CreateOrder_t fnCreateOrder;
    Core_AddItemToOrder_t fnAddItemToOrder;
    Core_CompleteOrder_t fnCompleteOrder;
    Core_GetDailyRevenue_t fnGetDailyRevenue;
    
    std::string dataPath;
    bool coreLoaded;

public:
    BakeryCoffeeApp() : hCoreDll(NULL), coreLoaded(false) {
        char path[MAX_PATH];
        GetModuleFileNameA(NULL, path, MAX_PATH);
        std::string exePath(path);
        size_t pos = exePath.find_last_of("\\/");
        dataPath = (pos != std::string::npos) ? exePath.substr(0, pos) + "\\data" : ".\\data";
    }

    ~BakeryCoffeeApp() {
        if (hCoreDll) {
            FreeLibrary(hCoreDll);
        }
    }

    bool loadCore() {
        std::string dllPath = dataPath + "\\..\\Core\\BakeryCoffeeCore.dll";
        
        // Пробуем загрузить из той же директории
        hCoreDll = LoadLibraryA("BakeryCoffeeCore.dll");
        
        if (!hCoreDll) {
            std::cerr << "ОШИБКА: Не удалось загрузить ядро BakeryCoffeeCore.dll!" << std::endl;
            std::cerr << "Без ядра работа программы невозможна." << std::endl;
            return false;
        }

        fnInitialize = (Core_Initialize_t)GetProcAddress(hCoreDll, "Core_Initialize");
        fnIsReady = (Core_IsReady_t)GetProcAddress(hCoreDll, "Core_IsReady");
        fnGetProductsJson = (Core_GetProductsJson_t)GetProcAddress(hCoreDll, "Core_GetProductsJson");
        fnCreateOrder = (Core_CreateOrder_t)GetProcAddress(hCoreDll, "Core_CreateOrder");
        fnAddItemToOrder = (Core_AddItemToOrder_t)GetProcAddress(hCoreDll, "Core_AddItemToOrder");
        fnCompleteOrder = (Core_CompleteOrder_t)GetProcAddress(hCoreDll, "Core_CompleteOrder");
        fnGetDailyRevenue = (Core_GetDailyRevenue_t)GetProcAddress(hCoreDll, "Core_GetDailyRevenue");

        if (!fnInitialize || !fnIsReady || !fnGetProductsJson || !fnCreateOrder || 
            !fnAddItemToOrder || !fnCompleteOrder || !fnGetDailyRevenue) {
            std::cerr << "ОШИБКА: Не найдены экспортируемые функции ядра!" << std::endl;
            FreeLibrary(hCoreDll);
            hCoreDll = NULL;
            return false;
        }

        // Инициализация ядра
        if (fnInitialize(dataPath.c_str()) != 1) {
            std::cerr << "ОШИБКА: Не удалось инициализировать ядро!" << std::endl;
            FreeLibrary(hCoreDll);
            hCoreDll = NULL;
            return false;
        }

        if (fnIsReady() != 1) {
            std::cerr << "ОШИБКА: Ядро не готово к работе!" << std::endl;
            FreeLibrary(hCoreDll);
            hCoreDll = NULL;
            return false;
        }

        coreLoaded = true;
        std::cout << "Ядро успешно загружено и инициализировано!" << std::endl;
        return true;
    }

    void showMenu() {
        std::cout << "\n=== Пекарня-Кофейня ===" << std::endl;
        std::cout << "1. Показать товары" << std::endl;
        std::cout << "2. Создать заказ" << std::endl;
        std::cout << "3. Показать выручку за день" << std::endl;
        std::cout << "4. Выход" << std::endl;
        std::cout << "Выбор: ";
    }

    void showProducts() {
        if (!coreLoaded) {
            std::cerr << "Ядро не загружено!" << std::endl;
            return;
        }

        char buffer[8192];
        int len = fnGetProductsJson(buffer, sizeof(buffer));
        
        if (len > 0) {
            std::cout << "\n--- Товары ---" << std::endl;
            std::cout.write(buffer, len);
            std::cout << std::endl;
        } else {
            std::cerr << "Ошибка получения списка товаров" << std::endl;
        }
    }

    void createOrder() {
        if (!coreLoaded) {
            std::cerr << "Ядро не загружено!" << std::endl;
            return;
        }

        std::string sellerName;
        std::cout << "Введите имя продавца: ";
        std::getline(std::cin, sellerName);

        int orderId = fnCreateOrder(sellerName.c_str());
        if (orderId < 0) {
            std::cerr << "Ошибка создания заказа" << std::endl;
            return;
        }

        std::cout << "Заказ #" << orderId << " создан" << std::endl;

        while (true) {
            int productId, quantity;
            std::cout << "ID товара (0 для завершения): ";
            std::cin >> productId;
            
            if (productId == 0) break;

            std::cout << "Количество: ";
            std::cin >> quantity;

            if (fnAddItemToOrder(productId, quantity) != 1) {
                std::cerr << "Ошибка добавления товара в заказ" << std::endl;
            } else {
                std::cout << "Товар добавлен" << std::endl;
            }
        }

        int totalCents = fnCompleteOrder();
        if (totalCents > 0) {
            std::cout << "Заказ завершен! Сумма: " << (totalCents / 100.0) << " руб." << std::endl;
        } else {
            std::cerr << "Ошибка завершения заказа" << std::endl;
        }
    }

    void showDailyRevenue() {
        if (!coreLoaded) {
            std::cerr << "Ядро не загружено!" << std::endl;
            return;
        }

        int revenueCents = fnGetDailyRevenue();
        std::cout << "\nВыручка за сегодня: " << (revenueCents / 100.0) << " руб." << std::endl;
    }

    void run() {
        if (!loadCore()) {
            return;
        }

        while (true) {
            showMenu();
            int choice;
            std::cin >> choice;

            switch (choice) {
                case 1:
                    showProducts();
                    break;
                case 2:
                    createOrder();
                    break;
                case 3:
                    showDailyRevenue();
                    break;
                case 4:
                    std::cout << "До свидания!" << std::endl;
                    return;
                default:
                    std::cout << "Неверный выбор" << std::endl;
            }
        }
    }
};

int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    
    std::cout << "=== Система управления пекарней-кофейней ===" << std::endl;
    
    BakeryCoffeeApp app;
    app.run();
    
    return 0;
}
