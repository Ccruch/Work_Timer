# 工作时间记录应用

import os
import datetime
import json
import tkinter as tk
from tkinter import messagebox, ttk

# 数据存储文件
DATA_FILE = 'work_records.json'

class WorkTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("工作时间记录器")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 让窗口居中显示
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # 确保数据文件存在
        self.ensure_data_file_exists()

        # 创建界面
        self.create_ui()

        # 直接关闭窗口
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def ensure_data_file_exists(self):
        """确保数据文件存在，如果不存在则创建"""
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def load_records(self):
        """从数据文件加载记录并按日期排序"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                records = json.load(f)
                # 按日期升序排序
                records.sort(key=lambda x: x['date'])
                return records
        except Exception as e:
            print(f"加载记录失败: {e}")
            return []

    def save_records(self, records):
        """保存记录到数据文件"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记录失败: {e}")

    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建标签页控件
        tab_control = ttk.Notebook(main_frame)

        # 创建记录标签页
        record_tab = ttk.Frame(tab_control)
        tab_control.add(record_tab, text="添加上下班记录")

        # 创建查看标签页
        view_tab = ttk.Frame(tab_control)
        tab_control.add(view_tab, text="查看历史记录")

        tab_control.pack(fill=tk.BOTH, expand=True)

        # 设置记录标签页
        self.setup_record_tab(record_tab)

        # 设置查看标签页
        self.setup_view_tab(view_tab)

    def setup_record_tab(self, parent):
        """设置添加上下班记录标签页"""
        # 创建框架
        self.frame = ttk.Frame(parent, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 日期选择
        ttk.Label(self.frame, text="日期:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(self.frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        # 记录类型选择
        ttk.Label(self.frame, text="记录类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.record_type = tk.StringVar(value="")
        # ttk.Radiobutton(self.frame, text="同时记录上下班", variable=self.record_type, value="both").grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Radiobutton(self.frame, text="上班", variable=self.record_type, value="start").grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Radiobutton(self.frame, text="下班", variable=self.record_type, value="end").grid(row=3, column=1, sticky=tk.W, pady=2)

        # 时间选择
        ttk.Label(self.frame, text="时间:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar(value=datetime.datetime.now().strftime('%H:%M'))
        self.time_entry = ttk.Entry(self.frame, textvariable=self.time_var, width=15)
        self.time_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        # 备注
        ttk.Label(self.frame, text="备注:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.note_var = tk.StringVar()
        note_text = tk.Text(self.frame, height=5, width=40)
        note_text.grid(row=6, column=1, sticky=tk.W, pady=5)

        # 添加记录按钮
        add_button = ttk.Button(self.frame, text="添加记录", command=lambda: self.add_manual_record(
            self.date_var.get(), self.time_var.get(), note_text.get("1.0", tk.END).strip(), self.record_type.get()))
        add_button.grid(row=7, column=0, columnspan=2, pady=10)

        # 绑定单选按钮事件
        self.record_type.trace_add("write", lambda *args: self.on_record_type_change())
        # 初始更新控件状态
        self.on_record_type_change()

    def on_record_type_change(self):
        """根据记录类型更改控件状态"""
        # 单个时间输入框始终启用
        self.time_entry.config(state="normal")

    def setup_view_tab(self, parent):
        """设置查看历史记录标签页"""
        # 创建框架
        self.frame = ttk.Frame(parent, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 创建树状视图
        columns = ("date", "manual_records", "manual_records2", "manual_records3")
        tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # 设置列标题
        # 设置列标题和对齐方式
        tree.heading("date", text="日期", anchor=tk.CENTER)
        tree.heading("manual_records", text="上班时间", anchor=tk.CENTER)
        tree.heading("manual_records2", text="下班时间", anchor=tk.CENTER)
        tree.heading("manual_records3", text="备注", anchor=tk.CENTER)

        # 设置列宽和对齐方式
        tree.column("date", width=100, anchor=tk.CENTER)
        tree.column("manual_records", width=100, anchor=tk.CENTER)
        tree.column("manual_records2", width=100, anchor=tk.CENTER)
        tree.column("manual_records3", width=300, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        # 加载记录并填充树状视图
        records = self.load_records()
        for record in reversed(records):  # 倒序显示，最新的在上面
            tree.insert("", tk.END, values=(record['date'], record.get('start_time', '未记录'), record.get('end_time', '未记录'), record.get('note', '')))

        # 刷新按钮
        refresh_button = ttk.Button(self.frame, text="刷新", command=lambda: self.refresh_view(tree))
        refresh_button.pack(pady=10)

    def refresh_view(self, tree):
        """刷新历史记录视图"""
        # 清空现有项
        for item in tree.get_children():
            tree.delete(item)

        # 重新加载记录并填充树状视图
        records = self.load_records()
        for record in reversed(records):  # 倒序显示，最新的在上面
            tree.insert("", tk.END, values=(record['date'], record.get('start_time', '未记录'), record.get('end_time', '未记录'), record.get('note', '')))

    def add_manual_record(self, date, time, note, record_type):
        """添加手动上下班记录"""
        if not date:
            messagebox.showerror("错误", "日期不能为空")
            return

        if not time:
            messagebox.showerror("错误", "时间不能为空")
            return

        if not record_type:
            # 创建自动关闭的提示窗口
            top = tk.Toplevel(self.root)
            top.title("提示")
            top.geometry("200x100")
            top.resizable(False, False)
            
            # 计算位置使其在主窗口中央
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 100
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 50
            top.geometry(f"200x100+{x}+{y}")
            
            # 添加标签
            label = ttk.Label(top, text="请选择类型")
            label.pack(expand=True)
            
            # 1秒后自动关闭
            top.after(500, top.destroy)
            return

        # 读取现有记录
        records = self.load_records()

        # 检查是否已有当天记录
        today_record = next((r for r in records if r['date'] == date), None)

        if today_record:
            # 如果已有当天记录，更新对应字段
            if record_type == "start":
                  # 将时间截断到分钟
                  today_record['start_time'] = time[:5] if len(time) >= 5 else time
            else:  # record_type == "end"
                # 将时间截断到分钟
                today_record['end_time'] = time[:5] if len(time) >= 5 else time
            # 更新备注
            today_record['note'] = note if note else today_record.get('note', '')
        else:
            # 如果没有当天记录，创建新记录
            new_record = {
                'date': date,
                'start_time': time[:5] if (record_type == "start" and len(time) >= 5) else '-',
                'end_time': time[:5] if (record_type == "end" and len(time) >= 5) else '-',
                'note': note if note else ''
            }
            records.append(new_record)

        # 保存记录
        self.save_records(records)

        # 显示成功消息
        # 创建自动关闭的成功提示窗口
        top = tk.Toplevel(self.root)
        top.title("成功")
        top.geometry("300x100")
        top.resizable(False, False)
        
        # 计算位置使其在主窗口中央
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 50
        top.geometry(f"300x100+{x}+{y}")
        if record_type == "start":
            message = f"{date[5:]} 上班-_- {time}"
            label = ttk.Label(top, text=message, font=('SimHei', 18), foreground='blue')
        else:
            message = f"{date[5:]} 下班^_^ {time}"
            label = ttk.Label(top, text=message, font=('SimHei', 18), foreground='green')

        # # 添加标签
        # message = f"{date}{'上班🙃🙃🙃' if record_type == 'start' else '下班😁😁😁'}"
        # # 设置字体大小为20，文本颜色为蓝色（可根据需要调整）
        # label = ttk.Label(top, text=message, font=('SimHei', 20), foreground='blue')
        label.pack(expand=True)
        
        # 1秒后自动关闭
        top.after(1000, top.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkTimerApp(root)
    root.mainloop()