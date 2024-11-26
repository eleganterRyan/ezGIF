from PIL import Image
import imageio
import os
import numpy as np

class GifMaker:
    """GIF制作器类
    
    用于处理图片并生成带有过渡效果的GIF动画。
    支持图片的添加、删除、排序，以及自定义过渡效果。
    """
    
    def __init__(self):
        """初始化GIF制作器"""
        self.image_items = []  # 存储图片信息的列表，每项包含路径、持续时间和文件名
        
    def add_image(self, image_path, duration=1000):
        """添加图片到队列
        
        Args:
            image_path: 图片文件路径
            duration: 图片显示持续时间（毫秒）
            
        Returns:
            bool: 添加是否成功
        """
        try:
            img = Image.open(image_path)
            # 将RGBA或调色板模式转换为RGB模式
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            self.image_items.append({
                'path': image_path,
                'duration': duration,
                'name': os.path.basename(image_path)
            })
            return True
        except Exception as e:
            print(f"添加图片失败: {str(e)}")
            return False
    
    def delete_image(self, index):
        """删除指定索引的图片
        
        Args:
            index: 要删除的图片索引
            
        Returns:
            bool: 删除是否成功
        """
        if 0 <= index < len(self.image_items):
            self.image_items.pop(index)
            return True
        return False
    
    def resize_image(self, image, target_size):
        """调整图片大小，保持原始比例
        
        Args:
            image: PIL Image对象
            target_size: 目标尺寸 (宽, 高)
            
        Returns:
            PIL Image: 调整大小后的图片
        """
        width, height = image.size
        ratio = min(target_size[0]/width, target_size[1]/height)
        new_size = (int(width * ratio), int(height * ratio))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def create_transition_frames(self, img1, img2, steps=10):
        """创建两张图片之间的渐变过渡帧
        
        Args:
            img1: 第一张图片
            img2: 第二张图片
            steps: 过渡步数
            
        Returns:
            list: 过渡帧列表
        """
        img1_array = np.array(img1, dtype=float)
        img2_array = np.array(img2, dtype=float)
        
        transition_frames = []
        for i in range(steps):
            alpha = i / steps  # 计算混合比例
            blend = img1_array * (1 - alpha) + img2_array * alpha  # 线性混合
            frame = Image.fromarray(np.uint8(blend))
            transition_frames.append(frame)
        
        return transition_frames
    
    def create_slide_transition(self, img1, img2, steps=10, direction='right'):
        """创建滑动过渡效果（保留但未使用的功能）
        
        Args:
            img1: 第一张图片
            img2: 第二张图片
            steps: 过渡步数
            direction: 滑动方向 'right', 'left', 'up', 'down'
            
        Returns:
            list: 过渡帧列表
        """
        width, height = img1.size
        transition_frames = []
        
        for i in range(steps):
            frame = Image.new('RGB', (width, height), (255, 255, 255))
            progress = i / steps
            
            if direction == 'right':
                # 第一张图片向右移动
                x1 = int(width * progress)
                frame.paste(img1, (x1, 0))
                # 第二张图片从左边进入
                x2 = int(-width * (1 - progress))
                frame.paste(img2, (x2, 0))
            elif direction == 'left':
                # 第一张图片向左移动
                x1 = int(-width * progress)
                frame.paste(img1, (x1, 0))
                # 第二张图片从右边进入
                x2 = int(width * (1 - progress))
                frame.paste(img2, (x2, 0))
            elif direction == 'down':
                # 第一张图片向下移动
                y1 = int(height * progress)
                frame.paste(img1, (0, y1))
                # 第二张图片从上边进入
                y2 = int(-height * (1 - progress))
                frame.paste(img2, (0, y2))
            elif direction == 'up':
                # 第一张图片向上移动
                y1 = int(-height * progress)
                frame.paste(img1, (0, y1))
                # 第二张图片从下边进入
                y2 = int(height * (1 - progress))
                frame.paste(img2, (0, y2))
            
            transition_frames.append(frame)
        
        return transition_frames
    
    def get_dominant_color(self, image):
        """获取图片的主要颜色（保留但未使用的功能）
        
        Args:
            image: PIL Image对象
            
        Returns:
            tuple: (R, G, B) 颜色元组
        """
        # 将图片缩小以加快处理速度
        small_image = image.resize((50, 50))
        # 确保图片是RGB模式
        if small_image.mode != 'RGB':
            small_image = small_image.convert('RGB')
        
        # 获取所有像素
        pixels = list(small_image.getdata())
        
        # 计算平均颜色
        r_total = sum(p[0] for p in pixels)
        g_total = sum(p[1] for p in pixels)
        b_total = sum(p[2] for p in pixels)
        pixel_count = len(pixels)
        
        return (
            r_total // pixel_count,
            g_total // pixel_count,
            b_total // pixel_count
        )
    
    def create_fade_frames(self, img, steps=10, fade_type='in', fade_color=None):
        """创建淡入或淡出效果的帧
        
        Args:
            img: 图片
            steps: 过渡步数
            fade_type: 'in' 为淡入，'out' 为淡出
            fade_color: 过渡颜色，默认为黑色
            
        Returns:
            list: 过渡帧列表
        """
        img_array = np.array(img, dtype=float)
        if fade_color is None:
            fade_color = (0, 0, 0)
        
        # 创建指定颜色的背景
        color_array = np.full_like(img_array, [fade_color[0], fade_color[1], fade_color[2]])
        
        transition_frames = []
        for i in range(steps):
            if fade_type == 'in':
                alpha = i / steps  # 淡入：从背景色到图片
            else:
                alpha = 1 - (i / steps)  # 淡出：从图片到背景色
            
            blend = img_array * alpha + color_array * (1 - alpha)
            frame = Image.fromarray(np.uint8(blend))
            transition_frames.append(frame)
        
        return transition_frames
    
    def create_gif(self, output_path, size=(800, 600), transition_frames=15):
        """生成GIF文件，包含淡入淡出和过渡效果
        
        Args:
            output_path: 输出GIF路径
            size: 目标图片大小 (宽, 高)
            transition_frames: 过渡帧数
            
        Raises:
            ValueError: 当没有图片或图片处理出错时
        """
        if not self.image_items:
            raise ValueError("没有添加任何图片")
        
        frames = []
        durations = []
        
        processed_images = []
        
        # 首先处理所有图片
        for item in self.image_items:
            try:
                with Image.open(item['path']) as verify_img:
                    try:
                        verify_img.verify()
                    except Exception:
                        raise ValueError(f"图片文件可能已损坏: {item['name']}")
                
                image = Image.open(item['path'])
                background = Image.new('RGB', size, (255, 255, 255))
                resized_image = self.resize_image(image, size)
                
                x = (size[0] - resized_image.size[0]) // 2
                y = (size[1] - resized_image.size[1]) // 2
                
                background.paste(resized_image, (x, y))
                processed_images.append(background)
                
            except Exception as e:
                raise ValueError(f"处理图片 {item['name']} 时出错: {str(e)}")
        
        # 固定使用白色作为过渡色
        transition_color = (255, 255, 255)
        
        # 添加开头淡入效果
        fade_in = self.create_fade_frames(
            processed_images[0], 
            transition_frames, 
            'in',
            transition_color
        )
        frames.extend(fade_in)
        durations.extend([40] * transition_frames)  # 淡入用40ms每帧
        
        # 添加主帧和过渡帧
        for i in range(len(processed_images)):
            # 添加当前帧
            frames.append(processed_images[i])
            durations.append(self.image_items[i]['duration'])
            
            # 添加过渡帧（最后一张图片不需要过渡）
            if i < len(processed_images) - 1:
                transition = self.create_transition_frames(
                    processed_images[i],
                    processed_images[i + 1],
                    transition_frames
                )
                frames.extend(transition)
                
                # 过渡帧时间计算
                transition_base = (self.image_items[i]['duration'] + self.image_items[i + 1]['duration']) // 2
                transition_total_time = transition_base // 3
                frame_duration = max(transition_total_time // transition_frames, 20)
                durations.extend([frame_duration] * transition_frames)
        
        # 添加结尾淡出效果
        fade_out = self.create_fade_frames(
            processed_images[-1], 
            transition_frames, 
            'out',
            transition_color
        )
        frames.extend(fade_out)
        durations.extend([40] * transition_frames)  # 淡出用40ms每帧
        
        # 保存GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0
        )
    
    def move_image(self, old_index, new_index):
        """移动图片位置，用于拖拽排序
        
        Args:
            old_index: 原始位置
            new_index: 目标位置
        """
        item = self.image_items.pop(old_index)
        self.image_items.insert(new_index, item)
    
    def update_duration(self, index, duration):
        """更新指定图片的显示时间
        
        Args:
            index: 图片索引
            duration: 新的显示时间（毫秒）
        """
        self.image_items[index]['duration'] = duration