import sys
import os
import threading
import time
import tkinter as tk
from tkinter import ttk
from customtkinter import CTk, CTkButton, CTkTextbox, CTkEntry, CTkLabel, CTkCheckBox, StringVar, CTkFrame

class CodeSnapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代码缩进工具 CodeSnap 1.2 ———— QwejayHuang")
        self.root.geometry("800x600")

        # 设置程序图标
        if getattr(sys, 'frozen', False):  # 判断是否打包
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "icon.ico")
        self.root.iconbitmap(icon_path)

        self.total_indent = 0
        self.auto_mode = False
        self.last_clipboard_content = ""
        self.processing_clipboard = False

        # 创建Notebook（TAB控件）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # 创建第一个TAB：代码缩进功能
        self.tab_indent = CTkFrame(self.notebook)
        self.notebook.add(self.tab_indent, text="代码缩进")
        self.setup_indent_tab()

        # 创建第二个TAB：批量替换功能
        self.tab_replace = CTkFrame(self.notebook)
        self.notebook.add(self.tab_replace, text="批量替换")
        self.setup_replace_tab()

        # 启动剪贴板监听线程
        self.clipboard_listener_thread = threading.Thread(target=self.clipboard_listener, daemon=True)
        self.clipboard_listener_thread.start()

    def setup_indent_tab(self):
        """初始化代码缩进TAB"""
        self.tab_indent.rowconfigure(1, weight=1)
        self.tab_indent.columnconfigure(0, weight=1)

        input_frame = CTkFrame(self.tab_indent, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        CTkLabel(input_frame, text="每次缩进", font=("Roboto", 12)).pack(side="left", padx=5, pady=5)
        self.indent_entry = CTkEntry(input_frame, width=50, font=("Roboto", 12))
        self.indent_entry.insert(0, "4")
        self.indent_entry.pack(side="left", padx=5, pady=5)
        CTkLabel(input_frame, text="字符", font=("Roboto", 12)).pack(side="left", padx=5, pady=5)

        button_frame = CTkFrame(self.tab_indent, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        CTkButton(button_frame, text="开始", font=("Roboto", 12), width=80, command=self.add_indentation).pack(side="left", padx=5, pady=5)
        CTkButton(button_frame, text="复制", font=("Roboto", 12), width=80, command=self.copy_to_clipboard).pack(side="left", padx=5, pady=5)
        CTkButton(button_frame, text="粘贴", font=("Roboto", 12), width=80, command=self.paste_from_clipboard).pack(side="left", padx=5, pady=5)
        CTkButton(button_frame, text="清除", font=("Roboto", 12), width=80, command=self.clear_text).pack(side="left", padx=5, pady=5)

        self.auto_mode_var = tk.BooleanVar(value=False)
        CTkCheckBox(button_frame, text="自动模式", variable=self.auto_mode_var, command=self.toggle_auto_mode).pack(side="left", padx=5, pady=5)

        self.code_text = CTkTextbox(self.tab_indent, wrap="none", font=("Roboto Mono", 12), fg_color="#ffffff", text_color="#000000")
        self.code_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.status_var = StringVar()
        self.status_var.set("就绪")
        CTkLabel(self.tab_indent, textvariable=self.status_var, font=("Roboto", 12), anchor="w").grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.context_menu = tk.Menu(self.tab_indent, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_to_clipboard)
        self.context_menu.add_command(label="粘贴", command=self.paste_from_clipboard)
        self.context_menu.add_command(label="全选", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="清除", command=self.clear_text)

        self.code_text.bind("<Button-3>", self.show_context_menu)
        self.code_text.bind("<Control-Return>", lambda event: self.add_indentation() or "break")
        self.code_text.bind("<Control-l>", lambda event: self.clear_text() or "break")
        self.code_text.bind("<Control-c>", lambda event: self.copy_to_clipboard() or "break")
        self.code_text.bind("<Control-v>", lambda event: self.paste_from_clipboard() or "break")
        self.code_text.bind("<Control-a>", lambda event: self.select_all() or "break")

    def setup_replace_tab(self):
        """初始化批量替换TAB"""
        self.tab_replace.rowconfigure(1, weight=1)
        self.tab_replace.columnconfigure(0, weight=1)

        # 查找和替换输入框
        input_frame = CTkFrame(self.tab_replace, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        CTkLabel(input_frame, text="查找", font=("Roboto", 12)).pack(side="left", padx=5, pady=5)
        self.find_entry = CTkTextbox(input_frame, width=200, height=150, font=("Roboto", 12))  # 增加高度
        self.find_entry.pack(side="left", padx=5, pady=5)

        CTkLabel(input_frame, text="替换为", font=("Roboto", 12)).pack(side="left", padx=5, pady=5)
        self.replace_entry = CTkTextbox(input_frame, width=200, height=150, font=("Roboto", 12))  # 增加高度
        self.replace_entry.pack(side="left", padx=5, pady=5)

        CTkButton(input_frame, text="替换", font=("Roboto", 12), width=80, command=self.batch_replace).pack(side="left", padx=5, pady=5)

        # 主文本框
        self.replace_text = CTkTextbox(self.tab_replace, wrap="none", font=("Roboto Mono", 12), fg_color="#ffffff", text_color="#000000")
        self.replace_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # 状态栏
        self.replace_status_var = StringVar()
        self.replace_status_var.set("就绪")
        CTkLabel(self.tab_replace, textvariable=self.replace_status_var, font=("Roboto", 12), anchor="w").grid(row=2, column=0, sticky="ew", padx=10, pady=10)

    def toggle_auto_mode(self):
        """切换自动模式"""
        self.auto_mode = self.auto_mode_var.get()
        self.status_var.set("自动模式已启用" if self.auto_mode else "自动模式已禁用")

    def clipboard_listener(self):
        """监听剪贴板变化"""
        while True:
            if self.auto_mode and not self.processing_clipboard:
                try:
                    clipboard_content = self.root.clipboard_get()
                    if clipboard_content != self.last_clipboard_content:
                        self.last_clipboard_content = clipboard_content
                        self.processing_clipboard = True
                        self.root.after(0, self.process_clipboard_content)
                except tk.TclError:
                    pass
            time.sleep(1)

    def process_clipboard_content(self):
        """处理剪贴板内容"""
        if self.auto_mode:
            try:
                self.code_text.delete("1.0", "end")
                self.code_text.insert("1.0", self.last_clipboard_content)
                self.add_indentation()
                self.copy_to_clipboard()
                self.last_clipboard_content = self.code_text.get("1.0", "end-1c")
            finally:
                self.processing_clipboard = False

    def add_indentation(self):
        """添加缩进"""
        try:
            indent_spaces = int(self.indent_entry.get())
        except ValueError:
            indent_spaces = 4

        self.total_indent += indent_spaces
        code = self.code_text.get("1.0", "end-1c")
        indented_code = "".join(" " * indent_spaces + line if line.strip() else line for line in code.splitlines(True))

        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", indented_code)
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
            insert_pos = self.code_text.index("insert")
            try:
                self.code_text.delete("sel.first", "sel.last")
            except tk.TclError:
                pass
            self.code_text.insert(insert_pos, clipboard_text)
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

    def batch_replace(self):
        """批量替换文本"""
        find_lines = self.find_entry.get("1.0", "end-1c").splitlines()
        replace_lines = self.replace_entry.get("1.0", "end-1c").splitlines()

        if not find_lines:
            self.replace_status_var.set("查找内容不能为空！")
            return

        content = self.replace_text.get("1.0", "end-1c")
        total_replacements = 0
        total_deletions = 0

        for find_text, replace_text in zip(find_lines, replace_lines):
            if not find_text:
                continue  # 忽略空行
            count = content.count(find_text)
            if count > 0:
                if replace_text:  # 如果替换框不为空，则替换
                    content = content.replace(find_text, replace_text)
                    total_replacements += count
                else:  # 如果替换框为空，则删除
                    content = content.replace(find_text, "")
                    total_deletions += count

        self.replace_text.delete("1.0", "end")
        self.replace_text.insert("1.0", content)
        self.replace_status_var.set(f"替换完成！共替换 {total_replacements} 处，删除 {total_deletions} 处。")

if __name__ == "__main__":
    root = CTk()
    app = CodeSnapApp(root)
    root.mainloop()