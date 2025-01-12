import tkinter as tk
import customtkinter as ctk
import sys
import os

class CodeSnapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代码缩进工具 CodeSnap 1.1 ———— QwejayHuang")
        self.root.geometry("800x500")  # 设置窗口初始大小

        # 设置程序图标
        if getattr(sys, 'frozen', False):  # 判断是否打包
            base_path = sys._MEIPASS  # 获取打包后的资源路径
        else:
            base_path = os.path.dirname(__file__)  # 获取当前脚本路径
        icon_path = os.path.join(base_path, "icon.ico")
        self.root.iconbitmap(icon_path)  # 设置程序图标

        # 全局变量，用于记录累计缩进的字符数
        self.total_indent = 0

        # 配置主题和颜色
        ctk.set_appearance_mode("light")  # 设置主题模式（light/dark）
        ctk.set_default_color_theme("blue")  # 设置颜色主题

        # 初始化界面
        self.setup_ui()

    def setup_ui(self):
        """初始化用户界面"""
        # 配置网格布局的行和列的权重，使文本框随窗口大小变化
        self.root.rowconfigure(1, weight=1)  # 文本框所在行
        self.root.columnconfigure(0, weight=1)  # 文本框所在列

        # 创建输入框区域
        input_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # 添加“缩进”标签
        indent_label_left = ctk.CTkLabel(input_frame, text="每次缩进", font=("Roboto", 12))
        indent_label_left.pack(side="left", padx=5, pady=5)

        # 添加输入框
        self.indent_entry = ctk.CTkEntry(input_frame, width=50, font=("Roboto", 12))
        self.indent_entry.insert(0, "4")  # 设置默认值
        self.indent_entry.pack(side="left", padx=5, pady=5)

        # 添加“字符”标签
        indent_label_right = ctk.CTkLabel(input_frame, text="字符", font=("Roboto", 12))
        indent_label_right.pack(side="left", padx=5, pady=5)

        # 创建按钮区域
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # 添加“开始”按钮
        start_button = ctk.CTkButton(button_frame, text="开始 (Ctrl+Enter)", font=("Roboto", 12), command=self.add_indentation)
        start_button.pack(side="left", padx=5, pady=5)

        # 添加“复制”按钮
        copy_button = ctk.CTkButton(button_frame, text="复制 (Ctrl+C)", font=("Roboto", 12), command=self.copy_to_clipboard)
        copy_button.pack(side="left", padx=5, pady=5)

        # 添加“粘贴”按钮
        paste_button = ctk.CTkButton(button_frame, text="粘贴 (Ctrl+V)", font=("Roboto", 12), command=self.paste_from_clipboard)
        paste_button.pack(side="left", padx=5, pady=5)

        # 添加“清除”按钮
        clear_button = ctk.CTkButton(button_frame, text="清除 (Ctrl+L)", font=("Roboto", 12), command=self.clear_text)
        clear_button.pack(side="left", padx=5, pady=5)

        # 创建文本框用于显示代码
        self.code_text = ctk.CTkTextbox(self.root, wrap="none", font=("Roboto Mono", 12), fg_color="#ffffff", text_color="#000000")
        self.code_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # 创建状态栏
        self.status_var = ctk.StringVar()
        self.status_var.set("就绪")
        status_bar = ctk.CTkLabel(self.root, textvariable=self.status_var, font=("Roboto", 12), anchor="w")
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_to_clipboard)
        self.context_menu.add_command(label="粘贴", command=self.paste_from_clipboard)
        self.context_menu.add_command(label="全选", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="清除", command=self.clear_text)

        # 绑定右键点击事件
        self.code_text.bind("<Button-3>", self.show_context_menu)

        # 快捷键绑定
        self.code_text.bind("<Control-Return>", lambda event: self.add_indentation() or "break")  # Ctrl + Enter
        self.code_text.bind("<Control-l>", lambda event: self.clear_text() or "break")  # Ctrl + L
        self.code_text.bind("<Control-c>", lambda event: self.copy_to_clipboard() or "break")  # Ctrl + C
        self.code_text.bind("<Control-v>", lambda event: self.paste_from_clipboard() or "break")  # Ctrl + V
        self.code_text.bind("<Control-a>", lambda event: self.select_all() or "break")  # Ctrl + A

    def add_indentation(self):
        """添加缩进"""
        try:
            # 获取输入框中的缩进空格数，如果为空则使用默认值 4
            indent_spaces = int(self.indent_entry.get())
        except ValueError:
            indent_spaces = 4  # 默认值

        # 累加缩进字符数
        self.total_indent += indent_spaces

        # 获取文本框中的代码
        code = self.code_text.get("1.0", "end-1c")  # 去除末尾的换行符

        # 在每一行前添加缩进
        indented_code = ""
        for line in code.splitlines(True):  # 保留换行符
            if line.strip():  # 如果行不为空
                indented_code += " " * indent_spaces + line
            else:
                indented_code += line  # 保留空行

        # 清空文本框并插入缩进后的代码
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", indented_code)

        # 更新状态栏
        self.status_var.set(f"缩进成功！累计 {self.total_indent} 字符。")

    def clear_text(self):
        """清空文本框"""
        self.total_indent = 0
        self.code_text.delete("1.0", "end")
        self.status_var.set("文本框已清空！")

    def copy_to_clipboard(self):
        """复制选中文本"""
        try:
            selected_text = self.code_text.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.status_var.set("已复制选中文本！")
        except tk.TclError:
            all_text = self.code_text.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(all_text)
            self.status_var.set("已复制所有文本！")
        except Exception as e:
            self.status_var.set(f"复制失败！错误：{e}")

    def paste_from_clipboard(self):
        """粘贴剪贴板内容"""
        try:
            clipboard_text = self.root.clipboard_get()
            # 保存当前光标位置
            insert_pos = self.code_text.index("insert")
            try:
                # 尝试获取选中文本并删除
                self.code_text.delete("sel.first", "sel.last")
            except tk.TclError:
                # 没有选中文本，跳过删除操作
                pass
            # 在保存的位置插入剪贴板内容
            self.code_text.insert(insert_pos, clipboard_text)
            # 更新光标位置到插入文本的末尾
            self.code_text.mark_set("insert", f"{insert_pos} + {len(clipboard_text)} chars")
            self.status_var.set("已粘贴内容！")
        except tk.TclError:
            self.status_var.set("剪贴板为空！")
        except Exception as e:
            self.status_var.set(f"粘贴失败！错误：{e}")

    def select_all(self):
        """全选文本"""
        self.code_text.tag_add("sel", "1.0", "end-1c")
        self.code_text.mark_set("insert", "1.0")
        self.code_text.see("insert")
        self.status_var.set("已全选文本！")

    def show_context_menu(self, event):
        """显示右键菜单"""
        self.context_menu.post(event.x_root, event.y_root)


# 主程序入口
if __name__ == "__main__":
    root = ctk.CTk()
    app = CodeSnapApp(root)
    root.mainloop()
