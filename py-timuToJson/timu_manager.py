import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
import re
import time
import random
import json
import os

class TimuManager:
    def __init__(self):
        # 初始化数据库
        self.init_database()
        # 创建GUI界面
        self.create_gui()
    
    def init_database(self):
        # 创建或连接到SQLite数据库
        self.conn = sqlite3.connect('timu_database.db')
        self.cursor = self.conn.cursor()
        # 创建题目表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS timu (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            option TEXT,
            answer TEXT,
            analysis TEXT,
            source TEXT,
            create_time TEXT
        )
        ''')
        self.conn.commit()
    
    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("题目管理器")
        self.root.geometry("800x600")
        
        # 创建标签页
        tab_control = ttk.Notebook(self.root)
        
        # 导入标签页
        import_tab = ttk.Frame(tab_control)
        tab_control.add(import_tab, text="导入题目")
        
        # 管理标签页
        manage_tab = ttk.Frame(tab_control)
        tab_control.add(manage_tab, text="题目管理")
        
        # 导出标签页
        export_tab = ttk.Frame(tab_control)
        tab_control.add(export_tab, text="导出题目")
        
        tab_control.pack(expand=1, fill="both")
        
        # 设置导入标签页内容
        self.setup_import_tab(import_tab)
        # 设置管理标签页内容
        self.setup_manage_tab(manage_tab)
        # 设置导出标签页内容
        self.setup_export_tab(export_tab)
        
        # 窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_import_tab(self, parent):
        # 创建导入方式选择
        tk.Label(parent, text="选择导入方式:", font=('Arial', 12)).pack(pady=10)
        
        frame = ttk.Frame(parent)
        frame.pack(pady=10)
        
        btn_txt = ttk.Button(frame, text="从TXT文件导入", command=self.import_from_txt)
        btn_txt.pack(side=tk.LEFT, padx=10)
        
        btn_json = ttk.Button(frame, text="从JSON文件导入", command=self.import_from_json)
        btn_json.pack(side=tk.LEFT, padx=10)
        
        btn_folder = ttk.Button(frame, text="从文件夹批量导入", command=self.batch_import_from_folder)
        btn_folder.pack(side=tk.LEFT, padx=10)
        
        # 导入状态显示
        self.status_var = tk.StringVar()
        self.status_var.set("等待导入...")
        status_label = tk.Label(parent, textvariable=self.status_var, fg="blue", font=('Arial', 10))
        status_label.pack(pady=20)
    
    def setup_manage_tab(self, parent):
        # 创建搜索框
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索题目:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ttk.Button(search_frame, text="搜索", command=self.search_timu)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(search_frame, text="刷新", command=self.refresh_timu_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建题目列表
        columns = ("id", "title", "answer", "source")
        self.timu_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        # 设置列宽和标题
        self.timu_tree.heading("id", text="ID")
        self.timu_tree.heading("title", text="题目")
        self.timu_tree.heading("answer", text="答案")
        self.timu_tree.heading("source", text="来源")
        
        self.timu_tree.column("id", width=100)
        self.timu_tree.column("title", width=400)
        self.timu_tree.column("answer", width=50)
        self.timu_tree.column("source", width=100)
        
        self.timu_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.timu_tree, orient=tk.VERTICAL, command=self.timu_tree.yview)
        self.timu_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加右键菜单
        self.timu_tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="查看详情", command=self.view_timu_detail)
        self.context_menu.add_command(label="删除题目", command=self.delete_timu)
        
        # 初始加载题目列表
        self.refresh_timu_list()
    
    def setup_export_tab(self, parent):
        tk.Label(parent, text="导出设置:", font=('Arial', 12)).pack(pady=10)
        
        frame = ttk.Frame(parent)
        frame.pack(pady=10)
        
        btn_export_json = ttk.Button(frame, text="导出为JSON文件", command=self.export_to_json)
        btn_export_json.pack(side=tk.LEFT, padx=10)
        
        btn_export_filter = ttk.Button(frame, text="按条件导出", command=self.export_with_filter)
        btn_export_filter.pack(side=tk.LEFT, padx=10)
        
        # 导出状态显示
        self.export_status_var = tk.StringVar()
        self.export_status_var.set("准备导出...")
        status_label = tk.Label(parent, textvariable=self.export_status_var, fg="green", font=('Arial', 10))
        status_label.pack(pady=20)
    
    def import_from_txt(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[('txt', '*.txt')])
            if not file_path:
                return
            
            self.status_var.set(f"正在导入: {os.path.basename(file_path)}...")
            self.root.update()
            
            with open(file_path, 'r', encoding='UTF-8') as f:
                data = f.read()
                data = data.replace('．', '.')
                
            # 不同题目分割
            pattern = re.compile(r'(?:^|\n\s*)\d+?[\.。]')
            data_list = pattern.split(data)
            
            # 将每个题目分为题目、选项、答案
            imported_count = 0
            for i, item in enumerate(data_list[1:], 1):  # 跳过第一个空项
                # 题目
                title_match = re.search(r'^(.*?)(?=\n[A-E])', item, re.DOTALL)
                title = title_match.group(1).strip() if title_match else ""
                
                # 选项
                option = re.findall(r'[A-E][\.。]?(.+?)(?=\n[A-E]|\n答案|\n解析|$)', item, re.DOTALL)
                option = [opt.strip() for opt in option]
                
                # 答案
                daan = re.findall(r'答案[:：]([A-E]+)', item)
                analysis = ''
                
                if not daan:
                    daan = re.findall(r'答案[:：]([\s\S]+?)\n解析', item)
                    if daan:
                        daan = daan[0].strip()
                        jiexi = re.findall(r'解析[:：]([\s\S]+)', item)
                        analysis = jiexi[0].strip() if jiexi else ''
                    else:
                        daan = re.findall(r'答案[:：]([\s\S]+)', item)
                        daan = daan[0].strip() if daan else ''
                else:
                    daan = daan[0].strip()
                    jiexi = re.findall(r'解析[:：]([\s\S]+)', item)
                    analysis = jiexi[0].strip() if jiexi else ''
                
                # 生成ID
                timu_id = time.strftime("%Y%m%d%H%M", time.localtime()) + str(random.randint(0, 1000000))
                
                # 插入数据库
                try:
                    self.cursor.execute(
                        "INSERT INTO timu (id, title, option, answer, analysis, source, create_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (timu_id, title, json.dumps(option), daan, analysis, os.path.basename(file_path), time.strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    imported_count += 1
                except sqlite3.IntegrityError:
                    # ID重复，重新生成ID
                    timu_id = time.strftime("%Y%m%d%H%M", time.localtime()) + str(random.randint(0, 1000000))
                    self.cursor.execute(
                        "INSERT INTO timu (id, title, option, answer, analysis, source, create_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (timu_id, title, json.dumps(option), daan, analysis, os.path.basename(file_path), time.strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    imported_count += 1
            
            self.conn.commit()
            self.status_var.set(f"导入完成！成功导入 {imported_count} 道题目")
            self.refresh_timu_list()
            messagebox.showinfo("导入成功", f"成功导入 {imported_count} 道题目！")
        except Exception as e:
            self.status_var.set(f"导入失败: {str(e)}")
            messagebox.showerror("导入失败", f"导入过程中出现错误：{str(e)}")
    
    def import_from_json(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[('json', '*.json')])
            if not file_path:
                return
            
            self.status_var.set(f"正在导入: {os.path.basename(file_path)}...")
            self.root.update()
            
            with open(file_path, 'r', encoding='UTF-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for item in data:
                # 生成新ID或使用原有ID
                timu_id = item.get('id', time.strftime("%Y%m%d%H%M", time.localtime()) + str(random.randint(0, 1000000)))
                
                # 确保选项是JSON字符串
                option = json.dumps(item.get('option', [])) if isinstance(item.get('option', []), list) else item.get('option', '[]')
                
                # 插入数据库
                try:
                    self.cursor.execute(
                        "INSERT INTO timu (id, title, option, answer, analysis, source, create_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (timu_id, item.get('title', ''), option, item.get('answer', ''), item.get('analysis', ''), 
                         os.path.basename(file_path), time.strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    imported_count += 1
                except sqlite3.IntegrityError:
                    # ID重复，更新现有记录
                    self.cursor.execute(
                        "UPDATE timu SET title=?, option=?, answer=?, analysis=?, source=? WHERE id=?",
                        (item.get('title', ''), option, item.get('answer', ''), item.get('analysis', ''), 
                         os.path.basename(file_path), timu_id)
                    )
                    imported_count += 1
            
            self.conn.commit()
            self.status_var.set(f"导入完成！成功导入/更新 {imported_count} 道题目")
            self.refresh_timu_list()
            messagebox.showinfo("导入成功", f"成功导入/更新 {imported_count} 道题目！")
        except Exception as e:
            self.status_var.set(f"导入失败: {str(e)}")
            messagebox.showerror("导入失败", f"导入过程中出现错误：{str(e)}")
    
    def batch_import_from_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            if not folder_path:
                return
            
            self.status_var.set(f"正在批量导入文件夹中的文件...")
            self.root.update()
            
            total_imported = 0
            # 支持的文件类型
            supported_extensions = ['.txt', '.json']
            
            for filename in os.listdir(folder_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in supported_extensions:
                    continue
                
                file_path = os.path.join(folder_path, filename)
                self.status_var.set(f"正在导入: {filename}...")
                self.root.update()
                
                if file_ext == '.txt':
                    # 使用TXT导入方法
                    with open(file_path, 'r', encoding='UTF-8') as f:
                        data = f.read()
                        data = data.replace('．', '.')
                    
                    # 不同题目分割
                    pattern = re.compile(r'(?:^|\n\s*)\d+?[\.。]')
                    data_list = pattern.split(data)
                    
                    for item in data_list[1:]:  # 跳过第一个空项
                        # 题目
                        title_match = re.search(r'^(.*?)(?=\n[A-E])', item, re.DOTALL)
                        title = title_match.group(1).strip() if title_match else ""
                        
                        # 选项
                        option = re.findall(r'[A-E][\.。]?(.+?)(?=\n[A-E]|\n答案|\n解析|$)', item, re.DOTALL)
                        option = [opt.strip() for opt in option]
                        
                        # 答案
                        daan = re.findall(r'答案[:：]([A-E]+)', item)
                        analysis = ''
                        
                        if not daan:
                            daan = re.findall(r'答案[:：]([\s\S]+?)\n解析', item)
                            if daan:
                                daan = daan[0].strip()
                                jiexi = re.findall(r'解析[:：]([\s\S]+)', item)
                                analysis = jiexi[0].strip() if jiexi else ''
                            else:
                                daan = re.findall(r'答案[:：]([\s\S]+)', item)
                                daan = daan[0].strip() if daan else ''
                        else:
                            daan = daan[0].strip()
                            jiexi = re.findall(r'解析[:：]([\s\S]+)', item)
                            analysis = jiexi[0].strip() if jiexi else ''
                        
                        # 生成ID
                        timu_id = time.strftime("%Y%m%d%H%M", time.localtime()) + str(random.randint(0, 1000000))
                        
                        # 插入数据库
                        try:
                            self.cursor.execute(
                                "INSERT INTO timu (id, title, option, answer, analysis, source, create_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (timu_id, title, json.dumps(option), daan, analysis, filename, time.strftime("%Y-%m-%d %H:%M:%S"))
                            )
                            total_imported += 1
                        except sqlite3.IntegrityError:
                            # ID重复，重新生成ID
                            timu_id = time.strftime("%Y%m%d%H%M", time.localtime()) + str(random.randint(0, 1000000))
                            self.cursor.execute(
                                "INSERT INTO timu (id, title, option, answer, analysis, source, create_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (timu_id, title, json.dumps(option), daan, analysis, filename, time.strftime("%Y-%m-%d %H:%M:%S"))
                            )
                            total_imported += 1
                elif file_ext == '.json':
                    # 使用JSON导入方法
                    with open(file_path, 'r', encoding='UTF-8') as f:
                        data = json.load(f)
                    
                    for item in data:
                        # 生成新ID或使用原有ID
                        timu_id = item.get('id', time.strftime("%Y%m%d%H%M", time.localtime()) + str(random.randint(0, 1000000)))
                        
                        # 确保选项是JSON字符串
                        option = json.dumps(item.get('option', [])) if isinstance(item.get('option', []), list) else item.get('option', '[]')
                        
                        # 插入数据库
                        try:
                            self.cursor.execute(
                                "INSERT INTO timu (id, title, option, answer, analysis, source, create_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (timu_id, item.get('title', ''), option, item.get('answer', ''), item.get('analysis', ''), 
                                 filename, time.strftime("%Y-%m-%d %H:%M:%S"))
                            )
                            total_imported += 1
                        except sqlite3.IntegrityError:
                            # ID重复，跳过或更新
                            pass
            
            self.conn.commit()
            self.status_var.set(f"批量导入完成！成功导入 {total_imported} 道题目")
            self.refresh_timu_list()
            messagebox.showinfo("批量导入成功", f"成功导入 {total_imported} 道题目！")
        except Exception as e:
            self.status_var.set(f"批量导入失败: {str(e)}")
            messagebox.showerror("批量导入失败", f"批量导入过程中出现错误：{str(e)}")
    
    def refresh_timu_list(self):
        # 清空现有列表
        for item in self.timu_tree.get_children():
            self.timu_tree.delete(item)
        
        # 查询所有题目
        self.cursor.execute("SELECT id, title, answer, source FROM timu ORDER BY create_time DESC")
        timu_list = self.cursor.fetchall()
        
        # 填充列表
        for item in timu_list:
            # 截断过长的题目
            title = item[1][:50] + "..." if len(item[1]) > 50 else item[1]
            self.timu_tree.insert("", tk.END, values=item)
    
    def search_timu(self):
        keyword = self.search_var.get()
        if not keyword:
            self.refresh_timu_list()
            return
        
        # 清空现有列表
        for item in self.timu_tree.get_children():
            self.timu_tree.delete(item)
        
        # 根据关键字搜索
        self.cursor.execute("SELECT id, title, answer, source FROM timu WHERE title LIKE ? OR answer LIKE ? OR source LIKE ?", 
                           (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        timu_list = self.cursor.fetchall()
        
        # 填充列表
        for item in timu_list:
            title = item[1][:50] + "..." if len(item[1]) > 50 else item[1]
            self.timu_tree.insert("", tk.END, values=item)
    
    def show_context_menu(self, event):
        # 选中点击的项目
        item = self.timu_tree.identify_row(event.y)
        if item:
            self.timu_tree.selection_set(item)
            self.timu_tree.focus(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def view_timu_detail(self):
        selected_item = self.timu_tree.selection()
        if not selected_item:
            return
        
        item = self.timu_tree.item(selected_item)
        timu_id = item["values"][0]
        
        # 查询详细信息
        self.cursor.execute("SELECT * FROM timu WHERE id=?", (timu_id,))
        timu = self.cursor.fetchone()
        
        if timu:
            # 创建详情窗口
            detail_window = tk.Toplevel(self.root)
            detail_window.title("题目详情")
            detail_window.geometry("600x400")
            
            # 显示详细信息
            tk.Label(detail_window, text="题目:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
            title_text = tk.Text(detail_window, height=3, width=70)
            title_text.pack(padx=10)
            title_text.insert(tk.END, timu[1])
            title_text.config(state=tk.DISABLED)
            
            tk.Label(detail_window, text="选项:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
            try:
                options = json.loads(timu[2])
                option_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
            except:
                option_text = timu[2]
            
            option_text_widget = tk.Text(detail_window, height=5, width=70)
            option_text_widget.pack(padx=10)
            option_text_widget.insert(tk.END, option_text)
            option_text_widget.config(state=tk.DISABLED)
            
            tk.Label(detail_window, text="答案:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
            answer_entry = ttk.Entry(detail_window, width=50)
            answer_entry.pack(padx=10)
            answer_entry.insert(0, timu[3])
            
            tk.Label(detail_window, text="解析:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
            analysis_text = tk.Text(detail_window, height=5, width=70)
            analysis_text.pack(padx=10)
            analysis_text.insert(tk.END, timu[4])
            
            # 保存按钮
            def save_changes():
                new_answer = answer_entry.get()
                new_analysis = analysis_text.get(1.0, tk.END).strip()
                
                self.cursor.execute("UPDATE timu SET answer=?, analysis=? WHERE id=?", 
                                   (new_answer, new_analysis, timu_id))
                self.conn.commit()
                messagebox.showinfo("保存成功", "题目信息已更新！")
                self.refresh_timu_list()
                detail_window.destroy()
            
            save_btn = ttk.Button(detail_window, text="保存修改", command=save_changes)
            save_btn.pack(pady=10)
    
    def delete_timu(self):
        selected_item = self.timu_tree.selection()
        if not selected_item:
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", "确定要删除选中的题目吗？"):
            return
        
        item = self.timu_tree.item(selected_item)
        timu_id = item["values"][0]
        
        # 删除题目
        self.cursor.execute("DELETE FROM timu WHERE id=?", (timu_id,))
        self.conn.commit()
        
        # 更新列表
        self.refresh_timu_list()
        messagebox.showinfo("删除成功", "题目已成功删除！")
    
    def export_to_json(self):
        try:
            # 查询所有题目
            self.cursor.execute("SELECT id, title, option, answer, analysis FROM timu")
            timu_list = self.cursor.fetchall()
            
            if not timu_list:
                messagebox.showinfo("提示", "没有题目可以导出！")
                return
            
            # 转换为JSON格式
            json_data = []
            for item in timu_list:
                try:
                    options = json.loads(item[2])
                except:
                    options = []
                
                json_data.append({
                    "id": item[0],
                    "title": item[1],
                    "option": options,
                    "answer": item[3],
                    "analysis": item[4]
                })
            
            # 选择保存路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json")],
                initialfile=time.strftime("%Y%m%d%H%M%S", time.localtime())
            )
            
            if not file_path:
                return
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            
            self.export_status_var.set(f"导出成功！文件已保存至: {os.path.basename(file_path)}")
            messagebox.showinfo("导出成功", f"成功导出 {len(json_data)} 道题目到 {file_path}！")
        except Exception as e:
            self.export_status_var.set(f"导出失败: {str(e)}")
            messagebox.showerror("导出失败", f"导出过程中出现错误：{str(e)}")
    
    def export_with_filter(self):
        # 创建过滤窗口
        filter_window = tk.Toplevel(self.root)
        filter_window.title("按条件导出")
        filter_window.geometry("400x300")
        
        # 来源过滤
        tk.Label(filter_window, text="按来源过滤:", font=('Arial', 10)).pack(anchor=tk.W, padx=20, pady=10)
        
        # 获取所有来源
        self.cursor.execute("SELECT DISTINCT source FROM timu")
        sources = self.cursor.fetchall()
        
        source_vars = []
        source_frame = ttk.Frame(filter_window)
        source_frame.pack(fill=tk.X, padx=20)
        
        for i, source in enumerate(sources):
            var = tk.BooleanVar(value=True)
            source_vars.append((source[0], var))
            
            # 每行显示3个选项
            col = i % 3
            row = i // 3
            
            chk = tk.Checkbutton(source_frame, text=source[0], variable=var)
            chk.grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
        
        # 导出按钮
        def do_export():
            # 获取选中的来源
            selected_sources = [source for source, var in source_vars if var.get()]
            
            if not selected_sources:
                messagebox.showinfo("提示", "请至少选择一个来源！")
                return
            
            # 构建SQL查询
            placeholders = ",".join(["?"] * len(selected_sources))
            query = f"SELECT id, title, option, answer, analysis FROM timu WHERE source IN ({placeholders})"
            
            self.cursor.execute(query, selected_sources)
            timu_list = self.cursor.fetchall()
            
            if not timu_list:
                messagebox.showinfo("提示", "没有符合条件的题目可以导出！")
                return
            
            # 转换为JSON格式
            json_data = []
            for item in timu_list:
                try:
                    options = json.loads(item[2])
                except:
                    options = []
                
                json_data.append({
                    "id": item[0],
                    "title": item[1],
                    "option": options,
                    "answer": item[3],
                    "analysis": item[4]
                })
            
            # 选择保存路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json")],
                initialfile=f"filtered_{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
            )
            
            if not file_path:
                return
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            
            self.export_status_var.set(f"条件导出成功！文件已保存至: {os.path.basename(file_path)}")
            messagebox.showinfo("导出成功", f"成功导出 {len(json_data)} 道题目到 {file_path}！")
            filter_window.destroy()
        
        export_btn = ttk.Button(filter_window, text="导出", command=do_export)
        export_btn.pack(pady=20)
    
    def on_closing(self):
        # 关闭数据库连接
        self.conn.close()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TimuManager()
    app.run()