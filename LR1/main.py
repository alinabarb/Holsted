import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from math import log2

# импортируем наш парсер из соседнего файлика
from metrik1 import parsecpp


def calculate_metrics(operators, operands):
    # считаем уникальные элементы (словари)
    n1 = len(operators)
    n2 = len(operands)

    # считаем сколько раз они всего встречаются
    N1 = sum(operators.values())
    N2 = sum(operands.values())

    # базовые метрики
    n = n1 + n2
    N = N1 + N2

    # объем (защита от логарифма нуля, если код пустой)
    V = N * log2(n) if n > 0 else 0

    # расширенные метрики по формулам из методы
    # если операндов нет, ставим 0, чтобы не словить ошибку деления на ноль
    D = (n1 / 2) * (N2 / n2) if n2 > 0 else 0 
    E = D * V
    T = E / 18 # 18 - это число Струда для времени

    # возвращаем словарик, сразу всё округляем до целых (int), чтобы без точек
    return {
        "n1": int(n1), "n2": int(n2),
        "N1": int(N1), "N2": int(N2),
        "n": int(n), "N": int(N), "V": int(V),
        "D": int(D), "E": int(E), "T": int(T)
    }


class HalsteadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор метрик Холстеда")
        self.root.geometry("1150x850")
        self.root.minsize(950, 750)

        # тут будем хранить наши посчитанные данные
        self.operators = {}
        self.operands = {}
        self.metrics = {}

        self.setup_ui()

    def setup_ui(self):
        # верхняя менюшка с кнопками
        top_panel = ttk.Frame(self.root, padding=10)
        top_panel.pack(fill="x")

        ttk.Button(top_panel, text="Выбрать файл", command=self.load_file).pack(side="left", padx=5)
        ttk.Button(top_panel, text="Рассчитать", command=self.run_analysis).pack(side="left", padx=5)
        ttk.Button(top_panel, text="Очистить", command=self.reset_all).pack(side="left", padx=5)

        self.filepath_lbl = ttk.Label(top_panel, text="Файл не выбран", foreground="gray")
        self.filepath_lbl.pack(side="left", padx=15)

        # окошко для кода
        code_frame = ttk.LabelFrame(self.root, text="Исходный код (C++)", padding=8)
        code_frame.pack(fill="both", expand=False, padx=10, pady=(0, 10))

        self.code_text = tk.Text(code_frame, wrap="none", font=("Menlo", 12), height=10)
        self.code_text.pack(side="left", fill="both", expand=True)

        # прикручиваем скролл к текстовому полю
        scroll_y = ttk.Scrollbar(code_frame, orient="vertical", command=self.code_text.yview)
        scroll_y.pack(side="right", fill="y")
        self.code_text.configure(yscrollcommand=scroll_y.set)

        # блок под две таблицы
        tables_frame = ttk.Frame(self.root)
        tables_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 1. таблица операторов (слева)
        op_frame = ttk.LabelFrame(tables_frame, text="Операторы", padding=5)
        op_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.tree_op = ttk.Treeview(op_frame, columns=("j", "name", "count"), show="headings")
        self.tree_op.heading("j", text="j")
        self.tree_op.heading("name", text="Оператор")
        self.tree_op.heading("count", text="f1j")

        self.tree_op.column("j", width=50, anchor="center")
        self.tree_op.column("name", width=250, anchor="w")
        self.tree_op.column("count", width=80, anchor="center")

        self.tree_op.pack(side="left", fill="both", expand=True)

        op_scroll = ttk.Scrollbar(op_frame, orient="vertical", command=self.tree_op.yview)
        op_scroll.pack(side="right", fill="y")
        self.tree_op.configure(yscrollcommand=op_scroll.set)

        # 2. таблица операндов (справа)
        opd_frame = ttk.LabelFrame(tables_frame, text="Операнды", padding=5)
        opd_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.tree_opd = ttk.Treeview(opd_frame, columns=("i", "name", "count"), show="headings")
        self.tree_opd.heading("i", text="i")
        self.tree_opd.heading("name", text="Операнд")
        self.tree_opd.heading("count", text="f2i")

        self.tree_opd.column("i", width=50, anchor="center")
        self.tree_opd.column("name", width=250, anchor="w")
        self.tree_opd.column("count", width=80, anchor="center")

        self.tree_opd.pack(side="left", fill="both", expand=True)

        opd_scroll = ttk.Scrollbar(opd_frame, orient="vertical", command=self.tree_opd.yview)
        opd_scroll.pack(side="right", fill="y")
        self.tree_opd.configure(yscrollcommand=opd_scroll.set)

        # вывод итоговых метрик снизу 
        metrics_frame = ttk.Frame(self.root, padding=10)
        metrics_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_basic = ttk.Label(
            metrics_frame,
            text="Словарь программы η = ...\nДлина программы N = ...\nОбъем программы V = ...",
            justify="left", font=("Helvetica Neue", 13)
        )
        self.lbl_basic.pack(side="left", fill="x", expand=True)

        self.lbl_extended = ttk.Label(
            metrics_frame,
            text="Расширенные метрики:\nСложность D = ...\nТрудоемкость E = ...\nВремя T = ...",
            justify="left", font=("Helvetica Neue", 12)
        )
        self.lbl_extended.pack(side="left", fill="x", expand=True)

    def load_file(self):
        # диалог выбора файла
        filepath = filedialog.askopenfilename(
            title="Выбери код для анализа",
            filetypes=[("C++ файлы", "*.cpp *.h *.cc"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return

        try:
            # читаем файл и закидываем в текстовое поле
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert("1.0", content)
            self.filepath_lbl.config(text=filepath, foreground="")
        except Exception as e:
            messagebox.showerror("ошибочка", f"Не получилось открыть файл:\n{e}")

    def run_analysis(self):
        # забираем текст из поля ввода
        code = self.code_text.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Пусто", "Сначала загрузи или вставь код!")
            return

        try:
            # парсим и считаем
            self.operators, self.operands = parsecpp(code)
            self.metrics = calculate_metrics(self.operators, self.operands)
            
            # обновляем UI
            self.fill_tables()
            self.update_labels()
        except Exception as e:
            messagebox.showerror("Ошибка парсинга", f"Что-то пошло не так при анализе:\n{e}")

    def fill_tables(self):
        # чистим старые записи
        for row in self.tree_op.get_children():
            self.tree_op.delete(row)
        for row in self.tree_opd.get_children():
            self.tree_opd.delete(row)

        # сортируем словари по убыванию значений (чтобы частые были сверху)
        sorted_ops = sorted(self.operators.items(), key=lambda item: item[1], reverse=True)
        sorted_opds = sorted(self.operands.items(), key=lambda item: item[1], reverse=True)
        
        # заполняем операторы
        for j, (op, count) in enumerate(sorted_ops, start=1):
            self.tree_op.insert("", "end", values=(f"{j}.", op, count))

        # заполняем операнды
        for i, (opd, count) in enumerate(sorted_opds, start=1):
            self.tree_opd.insert("", "end", values=(f"{i}.", opd, count))

        # добавляем итоговую строчку с суммами в самый низ
        m = self.metrics
        self.tree_op.insert("", "end", values=(f"η1 = {m['n1']}", "", f"N1 = {m['N1']}"))
        self.tree_opd.insert("", "end", values=(f"η2 = {m['n2']}", "", f"N2 = {m['N2']}"))

    def update_labels(self):
        m = self.metrics

        # обновляем текст снизу
        self.lbl_basic.config(
            text=(
                f"Словарь программы η = {m['n1']} + {m['n2']} = {m['n']}\n"
                f"Длина программы N = {m['N1']} + {m['N2']} = {m['N']}\n"
                f"Объем программы V = {m['N']} * log2({m['n']}) = {m['V']}"
            )
        )

        self.lbl_extended.config(
            text=(
                "Расширенные метрики:\n"
                f"Сложность D = {m['D']}\n"
                f"Трудоемкость E = {m['E']}\n"
                f"Время T = {m['T']} сек"
            )
        )

    def reset_all(self):
        # сбрасываем вообще всё
        self.code_text.delete("1.0", tk.END)
        self.filepath_lbl.config(text="Файл не выбран", foreground="gray")

        for row in self.tree_op.get_children():
            self.tree_op.delete(row)
        for row in self.tree_opd.get_children():
            self.tree_opd.delete(row)

        self.lbl_basic.config(text="Словарь программы η = ...\nДлина программы N = ...\nОбъем программы V = ...")
        self.lbl_extended.config(text="Расширенные метрики:\nСложность D = ...\nТрудоемкость E = ...\nВремя T = ...")

        self.operators.clear()
        self.operands.clear()
        self.metrics.clear()


if __name__ == "__main__":
    window = tk.Tk()
    app = HalsteadApp(window)
    window.mainloop()