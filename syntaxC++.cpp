// Демонстрационная программа: разнообразные синтаксические конструкции C++
#include <iostream>
#include <string>
using namespace std;

enum Color { RED, GREEN, BLUE };   // перечисление

struct Point {                      // структура
    int x;
    int y;
};

// Рекурсивная пользовательская функция
long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Перегрузка функции (overload) №1
int square(int a) { return a * a; }
// Перегрузка функции №2
double square(double a) { return a * a; }

// Функция с параметром по умолчанию
int power(int base, int exp = 2) {
    int result = 1;
    for (int i = 0; i < exp; i++) result *= base;
    return result;
}

// Функция, принимающая структуру по ссылке (изменяет исходные данные)
void movePoint(Point &p, int dx, int dy) {
    p.x += dx;
    p.y += dy;
}

// Функция с указателем и проверкой на nullptr
bool isPositive(const int *value) {
    if (value == nullptr) return false;
    return *value > 0;
}

// Функция, возвращающая название цвета (switch)
string colorName(Color c) {
    switch (c) {
        case RED:   return "Красный";
        case GREEN: return "Зелёный";
        case BLUE:  return "Синий";
        default:    return "Неизвестный";
    }
}

int main() {
    // --- if / else if / else ---
    int a = 15;
    if (a % 15 == 0) {
        cout << "FizzBuzz" << endl;
    } else if (a % 3 == 0) {
        cout << "Fizz" << endl;
    } else if (a % 5 == 0) {
        cout << "Buzz" << endl;
    } else {
        cout << a << endl;
    }

    // --- тернарный оператор ---
    int x = 10, y = 20;
    int maxVal = (x > y) ? x : y;
    cout << "Максимум: " << maxVal << endl;

    // --- switch ---
    Color myColor = GREEN;
    cout << "Цвет: " << colorName(myColor) << endl;

    // --- for ---
    cout << "Квадраты чисел: ";
    for (int i = 1; i <= 5; i++) {
        cout << square(i) << " ";
    }
    cout << endl;

    // --- while ---
    int n = 5;
    long fact = 1;
    int counter = n;
    while (counter > 0) {
        fact *= counter;
        counter--;
    }
    cout << "Факториал через while: " << fact << endl;
    cout << "Факториал через рекурсию: " << factorial(n) << endl;

    // --- do...while ---
    int attempts = 0;
    do {
        attempts++;
    } while (attempts < 3);
    cout << "Число попыток: " << attempts << endl;

    // --- range-based for (диапазонный цикл) ---
    int numbers[] = {2, 4, 6, 8, 10};
    int sum = 0;
    for (int num : numbers) {
        sum += num;
    }
    cout << "Сумма массива: " << sum << endl;

    // --- вложенный цикл + break/continue ---
    cout << "Таблица (с break/continue):" << endl;
    for (int i = 1; i <= 3; i++) {
        for (int j = 1; j <= 3; j++) {
            if (j == 2) continue;
            if (i == 3 && j == 3) break;
            cout << i << "x" << j << "=" << i * j << " ";
        }
    }
    cout << endl;

    // --- работа со структурой и передачей по ссылке ---
    Point p1 = {0, 0};
    movePoint(p1, 5, 7);
    cout << "Точка после перемещения: (" << p1.x << ", " << p1.y << ")" << endl;

    // --- указатели ---
    int value = 42;
    int *ptr = &value;
    cout << "Значение через указатель: " << *ptr << endl;
    cout << "Положительное? " << (isPositive(ptr) ? "да" : "нет") << endl;

    // --- параметр по умолчанию и перегрузка ---
    cout << "2^5 = " << power(2, 5) << endl;
    cout << "3^2 (по умолчанию) = " << power(3) << endl;
    cout << "square(2.5) = " << square(2.5) << endl;

    // --- try/catch (обработка исключений) ---
    try {
        int divisor = 0;
        if (divisor == 0) {
            throw runtime_error("Деление на ноль!");
        }
        cout << 100 / divisor << endl;
    } catch (const runtime_error &e) {
        cout << "Ошибка: " << e.what() << endl;
    }

    // --- goto ---
    int i = 0;
start_label:
    if (i < 3) {
        cout << "goto итерация: " << i << endl;
        i++;
        goto start_label;
    }

    return 0;
}
