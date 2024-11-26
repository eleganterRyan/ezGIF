import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
from gif_maker import GifMaker
import os

class GifMakerGUI:
    def __init__(self):
        self.window = TkinterDnD.Tk()  # 使用TkinterDnD替代普通的Tk
        self.window.title("GIF制作器")
        self.window.geometry("800x600")
        
        self.gif_maker = GifMaker()
        self.preview_images = []  # 存储预览图片对象
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 添加图片按钮
        self.add_btn = ttk.Button(control_frame, text="添加图片", command=self.add_image)
        self.add_btn.pack(pady=5)
        
        # 图片大小设置
        size_frame = ttk.LabelFrame(control_frame, text="输出大小")
        size_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(size_frame, text="宽:").grid(row=0, column=0, padx=5)
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=8)
        self.width_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(size_frame, text="高:").grid(row=1, column=0, padx=5)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=8)
        self.height_entry.grid(row=1, column=1, padx=5)
        
        # 过渡帧设置
        transition_frame = ttk.LabelFrame(control_frame, text="过渡设置")
        transition_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(transition_frame, text="过渡帧数:").pack(side=tk.LEFT, padx=5)
        self.transition_frames_var = tk.StringVar(value="15")
        self.transition_frames_entry = ttk.Entry(
            transition_frame, 
            textvariable=self.transition_frames_var, 
            width=5
        )
        self.transition_frames_entry.pack(side=tk.LEFT, padx=5)
        
        # 生成GIF按钮
        self.create_btn = ttk.Button(control_frame, text="生成GIF", command=self.create_gif)
        self.create_btn.pack(pady=5)
        
        # 右侧图列表框架
        list_frame = ttk.LabelFrame(main_frame, text="拖拽图片到此处或点击添加图片按钮")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建可滚动的画布
        self.canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 设置文件拖放功能
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_drop)
        
        # 设置图片项目的拖放功能
        # self.scrollable_frame.bind('<Button-1>', self.on_drag_start)
        # self.scrollable_frame.bind('<B1-Motion>', self.on_drag_motion)
        # self.scrollable_frame.bind('<ButtonRelease-1>', self.on_drag_end)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
    def create_image_frame(self, index, image_data):
        """创建单个图片的预览框架"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        frame.index = index  # 存储索引
        
        # 添加拖动提示
        drag_label = ttk.Label(frame, text="☰", cursor="fleur")  # 只在拖动图标上显示移动光标
        drag_label.pack(side=tk.LEFT, padx=(2, 5))
        
        # 将拖拽事件绑定到拖动图标上
        drag_label.bind('<Button-1>', self.on_drag_start)
        drag_label.bind('<B1-Motion>', self.on_drag_motion)
        drag_label.bind('<ButtonRelease-1>', self.on_drag_end)
        
        # 预览图片
        img = Image.open(image_data['path'])
        original_size = img.size  # 获取原始分辨率
        img.thumbnail((100, 100))  # 缩放预览图
        photo = ImageTk.PhotoImage(img)
        self.preview_images.append(photo)  # 保持引用
        
        label = ttk.Label(frame, image=photo)
        label.pack(side=tk.LEFT, padx=5)
        
        # 文件信息框架（文件名和分辨率）
        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT, padx=5)
        
        # 文件名
        name_label = ttk.Label(info_frame, text=image_data['name'])
        name_label.pack(anchor='w')
        
        # 分辨率信息
        resolution_label = ttk.Label(
            info_frame, 
            text=f"分辨率: {original_size[0]}×{original_size[1]}", 
            font=('Arial', 8)  # 使用小一号的字体
        )
        resolution_label.pack(anchor='w')
        
        # 持续时间设置
        duration_frame = ttk.Frame(frame)
        duration_frame.pack(side=tk.LEFT, padx=5)
        
        duration_var = tk.StringVar(value=str(image_data['duration']))
        duration_entry = ttk.Entry(duration_frame, textvariable=duration_var, width=8)
        duration_entry.pack(side=tk.LEFT)
        ttk.Label(duration_frame, text="ms").pack(side=tk.LEFT)
        
        # 删除按钮
        delete_btn = ttk.Button(
            frame, 
            text="删除",
            command=lambda idx=index: self.delete_image(idx)
        )
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # 更新持续时间的回调
        def update_duration(event=None):
            try:
                new_duration = int(duration_var.get())
                self.gif_maker.update_duration(index, new_duration)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
                duration_var.set(str(image_data['duration']))
        
        duration_entry.bind('<FocusOut>', update_duration)
        duration_entry.bind('<Return>', update_duration)
        
        return frame
        
    def refresh_image_list(self):
        """刷新图片列表显示"""
        # 清除现有项目
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.preview_images.clear()
        
        # 重新创建所有项目
        for i, image_data in enumerate(self.gif_maker.image_items):
            self.create_image_frame(i, image_data)
    
    def add_image(self):
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg")]
        )
        for file in files:
            self.gif_maker.add_image(file)
        self.refresh_image_list()
    
    def create_gif(self):
        if not self.gif_maker.image_items:
            messagebox.showerror("错误", "请先添加图片")
            return
            
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            transition_frames = int(self.transition_frames_var.get())
            if transition_frames < 1:
                raise ValueError("过渡帧数必须大于0")
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数值")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF文件", "*.gif")]
        )
        if output_path:
            try:
                self.gif_maker.create_gif(
                    output_path, 
                    size=(width, height),
                    transition_frames=transition_frames
                )
                messagebox.showinfo("成功", "GIF生成成功！")
            except Exception as e:
                messagebox.showerror("错误", f"生成GIF失败: {str(e)}")
    
    # 拖拽相关方法
    def on_drag_start(self, event):
        """开始拖动图片项目"""
        widget = event.widget  # 直接使用触发事件的widget（拖动图标）
        frame = widget.winfo_parent()
        frame = self.window.nametowidget(frame)
        if hasattr(frame, 'index'):
            self._drag_data = {
                'widget': frame,
                'index': frame.index,
                'y': event.y_root
            }
            # 移除全局光标设置
            # self.window.config(cursor="fleur")  
    
    def on_drag_motion(self, event):
        """拖动图片项目时的处理"""
        if hasattr(self, '_drag_data'):
            # 获取当前鼠标位置下的部件
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if widget:
                # 获取目标框架
                target_frame = widget.winfo_parent()
                if target_frame:
                    target_frame = self.window.nametowidget(target_frame)
                    
                    # 确保目标框架有index属性且图片列表不为空
                    if (hasattr(target_frame, 'index') and 
                        len(self.gif_maker.image_items) > 0):
                        
                        # 获取目标索引值（而不是直接使用属性）
                        target_index = getattr(target_frame, 'index')
                        current_index = self._drag_data['index']
                        
                        # 确保索引是有效的整数
                        if (isinstance(target_index, int) and 
                            isinstance(current_index, int) and
                            0 <= target_index < len(self.gif_maker.image_items) and
                            0 <= current_index < len(self.gif_maker.image_items) and
                            target_index != current_index):
                            
                            try:
                                # 移动图片
                                self.gif_maker.move_image(current_index, target_index)
                                self.refresh_image_list()
                                self._drag_data['index'] = target_index
                                self._drag_data['y'] = event.y_root
                            except Exception as e:
                                print(f"移动图片时出错: {str(e)}")
    
    def on_drag_end(self, event):
        """结束拖动图片项目"""
        if hasattr(self, '_drag_data'):
            # 移除全局光标设置
            # self.window.config(cursor="")
            del self._drag_data
    
    def delete_image(self, index):
        """删除图片"""
        if self.gif_maker.delete_image(index):
            self.refresh_image_list()
    
    def on_drop(self, event):
        """处理文件拖放"""
        # 获取拖放的文件路径
        files = event.data
        if files:
            # 在Windows系统中，文件路径可能带有大括号和引号，需要处理
            files = files.replace('{', '').replace('}', '')
            file_list = files.split() if ' ' in files else [files]
            
            # 过滤出支持的图片文件
            valid_extensions = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
            for file_path in file_list:
                if file_path.endswith(valid_extensions):
                    self.gif_maker.add_image(file_path)
            
            self.refresh_image_list()