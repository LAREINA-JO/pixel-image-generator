import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io
import math

# --- 引入高级科学计算库 ---
try:
    from skimage import color as sk_color
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False

# --- 尝试导入可选库 ---
try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False

try:
    from streamlit_cropper import st_cropper
    HAS_CROPPER = True
except ImportError:
    HAS_CROPPER = False

# --- 1. 定义高级色卡 (完整 Mard 官方色卡数据) ---
MARD_PALETTE = {
    # --- A 系列 (黄色/暖色系) ---
    "Mard A1": (250, 245, 205), "Mard A2": (252, 254, 214), "Mard A3": (252, 255, 146),
    "Mard A4": (247, 236, 92),  "Mard A5": (255, 228, 75),  "Mard A6": (253, 169, 81),
    "Mard A7": (250, 140, 79),  "Mard A8": (249, 224, 69),  "Mard A9": (249, 156, 95),
    "Mard A10": (244, 126, 54), "Mard A11": (254, 219, 153), "Mard A12": (253, 162, 118),
    "Mard A13": (254, 198, 103), "Mard A14": (248, 88, 66), "Mard A15": (251, 246, 94),
    "Mard A16": (254, 255, 151), "Mard A17": (253, 225, 115), "Mard A18": (252, 191, 128),
    "Mard A19": (253, 126, 119), "Mard A20": (249, 214, 110), "Mard A21": (250, 227, 147),
    "Mard A22": (237, 248, 120), "Mard A23": (225, 201, 189), "Mard A24": (243, 246, 169),
    "Mard A25": (255, 215, 133), "Mard A26": (254, 200, 50),

    # --- B 系列 (绿色系) ---
    "Mard B1": (223, 241, 57),  "Mard B2": (100, 243, 67),  "Mard B3": (159, 246, 133),
    "Mard B4": (95, 223, 52),   "Mard B5": (57, 225, 88),   "Mard B6": (100, 224, 164),
    "Mard B7": (63, 174, 124),  "Mard B8": (29, 158, 84),   "Mard B9": (42, 80, 55),
    "Mard B10": (154, 209, 186), "Mard B11": (98, 112, 50), "Mard B12": (26, 110, 61),
    "Mard B13": (200, 232, 125), "Mard B14": (172, 232, 76), "Mard B15": (48, 83, 53),
    "Mard B16": (192, 237, 156), "Mard B17": (158, 179, 62), "Mard B18": (230, 237, 79),
    "Mard B19": (38, 183, 142),  "Mard B20": (202, 237, 207), "Mard B21": (23, 98, 104),
    "Mard B22": (10, 66, 65),    "Mard B23": (52, 59, 26),    "Mard B24": (232, 250, 166),
    "Mard B25": (78, 132, 109),  "Mard B26": (144, 124, 53),  "Mard B27": (208, 224, 175),
    "Mard B28": (158, 229, 187), "Mard B29": (198, 223, 95),  "Mard B30": (227, 251, 177),
    "Mard B31": (178, 230, 148), "Mard B32": (146, 173, 96),

    # --- C 系列 (蓝色系) ---
    "Mard C1": (255, 254, 228), "Mard C2": (171, 248, 254), "Mard C3": (158, 224, 248),
    "Mard C4": (68, 205, 251),  "Mard C5": (6, 171, 227),   "Mard C6": (84, 167, 233),
    "Mard C7": (57, 119, 204),  "Mard C8": (15, 82, 189),   "Mard C9": (51, 73, 195),
    "Mard C10": (61, 187, 227), "Mard C11": (42, 222, 211), "Mard C12": (30, 51, 78),
    "Mard C13": (205, 231, 254), "Mard C14": (214, 253, 252), "Mard C15": (33, 197, 196),
    "Mard C16": (24, 88, 162),  "Mard C17": (2, 209, 243),  "Mard C18": (33, 50, 68),
    "Mard C19": (24, 134, 144), "Mard C20": (26, 112, 169), "Mard C21": (190, 221, 252),
    "Mard C22": (107, 177, 187), "Mard C23": (200, 226, 249), "Mard C24": (126, 197, 249),
    "Mard C25": (169, 232, 224), "Mard C26": (66, 173, 209),  "Mard C27": (208, 222, 239),
    "Mard C28": (189, 206, 237), "Mard C29": (54, 74, 137),

    # --- D 系列 (紫/深蓝系) ---
    "Mard D1": (172, 183, 239), "Mard D2": (134, 141, 211), "Mard D3": (54, 83, 175),
    "Mard D4": (22, 44, 126),   "Mard D5": (179, 78, 198),  "Mard D6": (179, 123, 220),
    "Mard D7": (135, 88, 169),  "Mard D8": (227, 210, 254), "Mard D9": (214, 186, 245),
    "Mard D10": (48, 26, 73),   "Mard D11": (188, 186, 226), "Mard D12": (220, 153, 206),
    "Mard D13": (181, 3, 143),  "Mard D14": (136, 40, 147), "Mard D15": (47, 30, 142),
    "Mard D16": (226, 228, 240), "Mard D17": (199, 211, 249), "Mard D18": (154, 100, 184),
    "Mard D19": (216, 194, 217), "Mard D20": (156, 52, 173), "Mard D21": (148, 5, 149),
    "Mard D22": (56, 57, 149),  "Mard D23": (250, 219, 248), "Mard D24": (118, 138, 225),
    "Mard D25": (73, 80, 194),  "Mard D26": (214, 198, 235),

    # --- E 系列 (粉/紫红色系) ---
    "Mard E1": (246, 212, 203), "Mard E2": (252, 193, 221), "Mard E3": (246, 189, 232),
    "Mard E4": (233, 99, 158),  "Mard E5": (241, 85, 159),  "Mard E6": (236, 64, 114),
    "Mard E7": (198, 54, 116),  "Mard E8": (253, 219, 233), "Mard E9": (229, 117, 199),
    "Mard E10": (211, 57, 151), "Mard E11": (247, 218, 212), "Mard E12": (248, 147, 191),
    "Mard E13": (181, 2, 106),  "Mard E14": (250, 212, 191), "Mard E15": (245, 201, 202),
    "Mard E16": (251, 244, 236), "Mard E17": (247, 227, 236), "Mard E18": (251, 203, 219),
    "Mard E19": (246, 187, 209), "Mard E20": (215, 198, 206), "Mard E21": (192, 157, 164),
    "Mard E22": (181, 139, 159), "Mard E23": (147, 125, 138), "Mard E24": (222, 190, 229),

    # --- F 系列 (红/棕色系) ---
    "Mard F1": (255, 146, 128), "Mard F2": (247, 61, 72),   "Mard F3": (239, 77, 62),
    "Mard F4": (249, 43, 64),   "Mard F5": (227, 3, 40),    "Mard F6": (145, 54, 53),
    "Mard F7": (145, 25, 50),   "Mard F8": (187, 1, 38),    "Mard F9": (224, 103, 122),
    "Mard F10": (135, 70, 40),  "Mard F11": (111, 50, 29),  "Mard F12": (248, 81, 109),
    "Mard F13": (244, 92, 69),  "Mard F14": (252, 173, 178), "Mard F15": (213, 5, 39),
    "Mard F16": (248, 192, 169), "Mard F17": (232, 155, 125), "Mard F18": (208, 126, 74),
    "Mard F19": (190, 69, 74),  "Mard F20": (198, 148, 149), "Mard F21": (242, 187, 198),
    "Mard F22": (247, 195, 208), "Mard F23": (236, 128, 109), "Mard F24": (224, 157, 175),
    "Mard F25": (232, 72, 84),

    # --- G 系列 (肤色/大地色系) ---
    "Mard G1": (255, 228, 211), "Mard G2": (252, 198, 172), "Mard G3": (241, 196, 165),
    "Mard G4": (220, 179, 135), "Mard G5": (231, 179, 78),  "Mard G6": (243, 160, 20),
    "Mard G7": (152, 80, 58),   "Mard G8": (75, 43, 28),    "Mard G9": (228, 182, 133),
    "Mard G10": (218, 140, 66), "Mard G11": (218, 200, 152), "Mard G12": (254, 201, 147),
    "Mard G13": (178, 113, 75), "Mard G14": (139, 104, 76), "Mard G15": (246, 248, 227),
    "Mard G16": (242, 216, 193), "Mard G17": (121, 84, 78), "Mard G18": (255, 228, 214),
    "Mard G19": (221, 125, 65), "Mard G20": (165, 69, 47),  "Mard G21": (179, 133, 97),

    # --- H 系列 (灰度/黑白) ---
    "Mard H1": (251, 251, 251), "Mard H2": (255, 255, 255), "Mard H3": (180, 180, 180),
    "Mard H4": (135, 135, 135), "Mard H5": (70, 70, 72),    "Mard H6": (44, 44, 44),
    "Mard H7": (1, 1, 1),       "Mard H8": (231, 214, 220), "Mard H9": (239, 237, 238),
    "Mard H10": (236, 234, 235), "Mard H11": (205, 205, 205), "Mard H12": (253, 246, 238),
    "Mard H13": (244, 239, 209), "Mard H14": (206, 215, 212), "Mard H15": (152, 166, 166),
    "Mard H16": (27, 18, 19),   "Mard H17": (240, 238, 239), "Mard H18": (252, 255, 248),
    "Mard H19": (242, 238, 229), "Mard H20": (150, 160, 159), "Mard H21": (248, 251, 230),
    "Mard H22": (202, 202, 218), "Mard H23": (155, 156, 148),

    # --- M 系列 (莫兰迪/低饱和系) ---
    "Mard M1": (187, 198, 182), "Mard M2": (144, 153, 148), "Mard M3": (105, 126, 128),
    "Mard M4": (224, 212, 188), "Mard M5": (208, 203, 174), "Mard M6": (176, 170, 134),
    "Mard M7": (176, 167, 150), "Mard M8": (174, 128, 130), "Mard M9": (168, 135, 100),
    "Mard M10": (198, 178, 187), "Mard M11": (157, 118, 147), "Mard M12": (100, 75, 81),
    "Mard M13": (199, 146, 102), "Mard M14": (195, 116, 99), "Mard M15": (116, 125, 122),
}

# --- 2. 核心算法 (优化版: Numpy + Lab + Dithering) ---

def create_quantized_grid_numpy(image, palette_dict, dithering=True, alpha_threshold=128):
    """
    终极完美版：
    1. 严格 Alpha 过滤。
    2. 【新增】边缘感知 (Edge-Aware)：如果像素处于边缘，强制关闭该像素的抖动扩散，
       彻底阻断杂色产生。
    """
    # 1. 预处理
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.size
    img_arr = np.array(img_rgba)
    
    alpha_channel = img_arr[:, :, 3] 
    rgb_channel = img_arr[:, :, :3] 
    
    # 2. 准备色卡
    palette_names = list(palette_dict.keys())
    palette_rgb = np.array([palette_dict[name] for name in palette_names]) 
    palette_rgb_float = palette_rgb.astype(float)
    
    result_grid = [[None for _ in range(w)] for _ in range(h)]
    color_counts = {}

    if dithering:
        # --- 模式 A: 边缘感知抖动 ---
        current_pixels = rgb_channel.astype(float)
        
        for y in range(h):
            for x in range(w):
                # 1. 自身透明度检查
                if alpha_channel[y, x] < alpha_threshold:
                    result_grid[y][x] = None
                    continue
                
                # --- 2. 【核心修改】边缘检测 ---
                # 检查上下左右是否有透明像素 (即是否处于边缘)
                # 如果是边缘像素，我们就不让它把误差传给别人，也不让它接收过多的误差影响
                is_edge = False
                if x + 1 < w and alpha_channel[y, x+1] < alpha_threshold: is_edge = True
                elif x - 1 >= 0 and alpha_channel[y, x-1] < alpha_threshold: is_edge = True
                elif y + 1 < h and alpha_channel[y+1, x] < alpha_threshold: is_edge = True
                elif y - 1 >= 0 and alpha_channel[y-1, x] < alpha_threshold: is_edge = True
                
                old_rgb = current_pixels[y, x].copy()
                
                # Redmean 距离匹配
                rmean = (old_rgb[0] + palette_rgb_float[:, 0]) / 2
                dr = old_rgb[0] - palette_rgb_float[:, 0]
                dg = old_rgb[1] - palette_rgb_float[:, 1]
                db = old_rgb[2] - palette_rgb_float[:, 2]
                
                dists_sq = (2 + rmean/256) * (dr**2) + 4 * (dg**2) + (2 + (255-rmean)/256) * (db**2)
                
                idx = np.argmin(dists_sq)
                best_name = palette_names[idx]
                best_rgb = palette_rgb_float[idx]
                
                # 记录结果
                rgb_int = tuple(best_rgb.astype(int))
                color_counts[best_name] = color_counts.get(best_name, 0) + 1
                result_grid[y][x] = {'color': rgb_int, 'name': best_name, 'hex': '#%02x%02x%02x' % rgb_int}
                
                # --- 3. 误差扩散控制 ---
                # 只有当像素 "不是边缘" 时，才允许扩散误差。
                # 这相当于在轮廓线上建立了一道“防火墙”，误差撞到边缘就消失了，不会变成杂色。
                if not is_edge:
                    quant_error = old_rgb - best_rgb
                    
                    # 只有目标像素也是"非透明"的，才传误差 (双重保险)
                    if x + 1 < w and alpha_channel[y, x+1] >= alpha_threshold:
                        current_pixels[y, x+1] += quant_error * 7 / 16
                    if y + 1 < h:
                        if x - 1 >= 0 and alpha_channel[y+1, x-1] >= alpha_threshold:
                            current_pixels[y+1, x-1] += quant_error * 3 / 16
                        if alpha_channel[y+1, x] >= alpha_threshold:
                            current_pixels[y+1, x] += quant_error * 5 / 16
                        if x + 1 < w and alpha_channel[y+1, x+1] >= alpha_threshold:
                            current_pixels[y+1, x+1] += quant_error * 1 / 16
        
    else:
        # --- 模式 B: 关闭抖动 (无变化) ---
        if HAS_SKIMAGE:
            palette_lab = sk_color.rgb2lab(palette_rgb / 255.0)
            img_lab = sk_color.rgb2lab(rgb_channel / 255.0)
            flat_img = img_lab.reshape(-1, 3)
            
            indices = []
            chunk_size = 2000 
            for i in range(0, len(flat_img), chunk_size):
                chunk = flat_img[i:i+chunk_size]
                diff = chunk[:, np.newaxis, :] - palette_lab[np.newaxis, :, :]
                dists = np.sum(diff**2, axis=2)
                indices.append(np.argmin(dists, axis=1))
            indices = np.concatenate(indices)
            
            for idx_flat, palette_idx in enumerate(indices):
                y, x = divmod(idx_flat, w)
                if alpha_channel[y, x] < alpha_threshold:
                    result_grid[y][x] = None
                    continue
                name = palette_names[palette_idx]
                rgb_int = tuple(palette_rgb[palette_idx].astype(int))
                color_counts[name] = color_counts.get(name, 0) + 1
                result_grid[y][x] = {'color': rgb_int, 'name': name, 'hex': '#%02x%02x%02x' % rgb_int}
        else:
             st.error("缺少 scikit-image 库")

    return result_grid, color_counts


def reduce_palette_smart(image, max_colors):
    """
    智能缩减色卡：提取图片特征色 -> 映射到 Mard 色卡。
    """
    img_rgb = image.convert("RGB")
    # 使用 Pillow 的 quantize 快速提取主要颜色
    try:
        quantized = img_rgb.quantize(colors=max_colors, method=2) # method=2: MAXCOVERAGE
    except:
        quantized = img_rgb.quantize(colors=max_colors)
        
    extracted_palette = quantized.getpalette()[:max_colors*3]
    
    selected_keys = set()
    
    # 简单的寻找最近 Mard 颜色 (这里只用 RGB 距离即可，目的是圈定范围)
    for i in range(0, len(extracted_palette), 3):
        r, g, b = extracted_palette[i], extracted_palette[i+1], extracted_palette[i+2]
        min_dist = float('inf')
        best_name = None
        for name, mard_rgb in MARD_PALETTE.items():
            dist = (r - mard_rgb[0])**2 + (g - mard_rgb[1])**2 + (b - mard_rgb[2])**2
            if dist < min_dist:
                min_dist = dist
                best_name = name
        if best_name:
            selected_keys.add(best_name)
            
    return list(selected_keys)

def create_printable_sheet(grid_data, color_map, width, height):
    """生成的打印图纸"""
    cell_size = 30
    margin = 60 
    img_width = margin * 2 + width * cell_size 
    img_height = margin * 2 + height * cell_size
    
    sheet = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(sheet)
    
    # 绘制网格
    for y, row in enumerate(grid_data):
        for x, cell in enumerate(row):
            top_left_x = margin + x * cell_size
            top_left_y = margin + y * cell_size
            bottom_right_x = top_left_x + cell_size
            bottom_right_y = top_left_y + cell_size
            
            if cell:
                draw.rectangle([top_left_x, top_left_y, bottom_right_x, bottom_right_y], fill=cell['color'], outline="lightgray")
                short_code = cell['name'].replace("Mard ", "")
                # 智能文字颜色
                text_color = "black" if (cell['color'][0]*0.299 + cell['color'][1]*0.587 + cell['color'][2]*0.114) > 150 else "white"
                draw.text((top_left_x + 3, top_left_y + 8), short_code, fill=text_color)
            else:
                draw.rectangle([top_left_x, top_left_y, bottom_right_x, bottom_right_y], fill="white", outline="lightgray")

    # 绘制 10x10 粗线
    for i in range(0, width + 1, 10):
        line_x = margin + i * cell_size
        draw.line([(line_x, margin), (line_x, margin + height * cell_size)], fill="black", width=2)
    for i in range(0, height + 1, 10):
        line_y = margin + i * cell_size
        draw.line([(margin, line_y), (margin + width * cell_size, line_y)], fill="black", width=2)

    # 绘制行列号
    for x in range(width):
        num_str = str(x + 1)
        text_w = len(num_str) * 6
        x_pos = margin + x * cell_size + (cell_size - text_w) / 2
        y_pos = margin - 15 
        fill_color = "black" if (x + 1) % 5 == 0 else "gray"
        draw.text((x_pos + 3, y_pos), num_str, fill=fill_color)

    for y in range(height):
        num_str = str(y + 1)
        text_w = len(num_str) * 6
        x_pos = margin - text_w - 5 
        y_pos = margin + y * cell_size + 8 
        fill_color = "black" if (y + 1) % 5 == 0 else "gray"
        draw.text((x_pos, y_pos), num_str, fill=fill_color)

    return sheet

# --- 主程序 ---
st.set_page_config(page_title="拼豆生成器 Pro", layout="wide")
st.title("🧩 专业版拼豆图纸生成器 (Numpy加速版)")

if not HAS_SKIMAGE:
    st.warning("⚠️ 未检测到 `scikit-image` 库。建议安装以获得最佳色彩匹配效果 (pip install scikit-image)")

if 'result_grid' not in st.session_state:
    st.session_state.result_grid = None
if 'result_stats' not in st.session_state:
    st.session_state.result_stats = None
if 'result_dims' not in st.session_state:
    st.session_state.result_dims = (0, 0)

def reset_results():
    st.session_state.result_grid = None
    st.session_state.result_stats = None
    st.session_state.result_dims = (0, 0)

st.sidebar.header("1. 上传图片")
uploaded_file = st.sidebar.file_uploader(
    "支持 JPG/PNG/WEBP", 
    type=["jpg", "png", "jpeg", "webp"],
    on_change=reset_results 
)

st.sidebar.header("2. 生成设置")
use_rembg = st.sidebar.checkbox("启用智能抠图 (去除背景)", value=False)
mirror_mode = st.sidebar.checkbox("↔️ 镜像翻转", value=False)
target_width = st.sidebar.slider("目标宽度 (格/豆)", 10, 100, 40)
# 【新增】边缘处理阈值
alpha_threshold = st.sidebar.slider(
    "边缘过滤阈值 (去除杂边)", 
    min_value=10, 
    max_value=250, 
    value=150, 
    help="值越高，边缘裁剪越干净（减少半透明光晕）；值越低，保留越多边缘细节。"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 颜色与算法")
enable_color_limit = st.sidebar.checkbox("限制颜色数量 (推荐开启抖动)", value=False)
max_color_count = 200
if enable_color_limit:
    max_color_count = st.sidebar.number_input("最大颜色数量", min_value=2, max_value=60, value=15)

# 抖动开关
use_dithering = st.sidebar.checkbox("✨ 开启色彩抖动 (增强细节)", value=True, help="在颜色受限时，通过噪点模拟过渡色，使画面更细腻。")

generate_btn = st.sidebar.button("🚀 开始生成图纸")

if uploaded_file:
    original_image = Image.open(uploaded_file).convert("RGBA")
    
    st.subheader("🖼️ 步骤一：图片准备")
    enable_crop = st.checkbox("✂️ 启用手动裁剪", value=False)
    
    final_processing_img = original_image

    if enable_crop and HAS_CROPPER:
        st.caption("请在红框内拖动选择区域：")
        # 限制显示大小以加快裁剪响应
        display_width = 700
        if original_image.width > display_width:
             # 仅用于显示的缩略图
             aspect = original_image.height / original_image.width
             editing_image = original_image.resize((display_width, int(display_width * aspect)))
        else:
             editing_image = original_image
        
        cropped_img = st_cropper(editing_image, realtime_update=True, box_color='#8B1A1A', aspect_ratio=None)
        st.image(cropped_img, caption="裁剪预览", width=150)
        # 注意：这里实际上是用缩略图裁剪的，如果追求极致，应该映射回原图坐标，但对于拼豆来说够用了
        final_processing_img = cropped_img
    else:
        st.image(original_image, caption="原图预览", width=300)

    if generate_btn:
        with st.spinner("正在进行矩阵运算与色彩量化..."):
            img_to_process = final_processing_img
            
            if mirror_mode:
                img_to_process = img_to_process.transpose(Image.FLIP_LEFT_RIGHT)

            if use_rembg and HAS_REMBG:
                try:
                    img_to_process = remove(img_to_process)
                except Exception as e:
                    st.error(f"抠图出错: {e}")

            # 计算尺寸
            aspect_ratio = img_to_process.height / img_to_process.width
            target_height = int(target_width * aspect_ratio)
            
            # 【优化】使用 LANCZOS 高质量重采样
            resample_method = Image.Resample.LANCZOS if hasattr(Image, 'Resample') else Image.LANCZOS
            small_img = img_to_process.resize((target_width, target_height), resample_method)

            # --- 颜色策略 ---
            active_palette_keys = list(MARD_PALETTE.keys())
            msg = "📚 使用全量 Mard 色卡"
            
            if enable_color_limit:
                try:
                    active_palette_keys = reduce_palette_smart(small_img, max_color_count)
                    msg = f"🎨 已优化色卡：仅使用 {len(active_palette_keys)} 种最匹配的颜色"
                except Exception as e:
                    st.warning(f"色卡缩减失败: {e}")

            st.info(msg)
            
            # 构建仅包含选中颜色的字典
            active_palette_dict = {k: MARD_PALETTE[k] for k in active_palette_keys}

            # --- 【核心】调用 Numpy 优化函数 ---
            try:
                grid_data, color_usage = create_quantized_grid_numpy(
                    small_img, 
                    active_palette_dict, 
                    dithering=use_dithering,
                    alpha_threshold=alpha_threshold  # <--- 传入这个新参数
                )
                
                st.session_state.result_grid = grid_data
                st.session_state.result_stats = color_usage
                st.session_state.result_dims = (target_width, target_height)
                
            except Exception as e:
                st.error(f"生成失败: {e}")
                st.code(str(e))

    # 结果显示
    if st.session_state.result_grid is not None:
        st.markdown("---")
        st.subheader("🎨 步骤二：生成结果")
        
        grid_data = st.session_state.result_grid
        color_usage = st.session_state.result_stats
        t_w, t_h = st.session_state.result_dims

        with st.expander(f"📊 颜色清单 (共 {len(color_usage)} 色)", expanded=True):
            cols = st.columns(4)
            sorted_usage = sorted(color_usage.items(), key=lambda x: x[1], reverse=True)
            for idx, (name, count) in enumerate(sorted_usage):
                rgb = MARD_PALETTE.get(name, (0,0,0))
                hex_c = '#%02x%02x%02x' % rgb
                cols[idx % 4].markdown(
                    f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
                    f"<div style='width:15px;height:15px;background:{hex_c};border:1px solid #999;border-radius:3px;margin-right:8px;'></div>"
                    f"<b>{name}</b>: {count}</div>", 
                    unsafe_allow_html=True
                )

        t1, t2 = st.tabs(["💻 交互式网格", "🖨️ 打印图纸"])

        with t1:
            st.caption("👇 鼠标移动到格子上，会立即显示色号与RGB数值。")
            
            # --- 恢复你原来的高清 HTML/CSS 渲染逻辑 ---
            html_rows = "<tr><th style='background:none; border:none;'></th>" 
            for x in range(t_w):
                fw = "bold" if (x+1)%5==0 else "normal"
                col_color = "#333" if (x+1)%5==0 else "#999"
                html_rows += f"<th class='axis-x' style='color:{col_color}; font-weight:{fw}'>{x+1}</th>"
            html_rows += "</tr>"

            for y, row in enumerate(grid_data):
                html_rows += "<tr>"
                fw = "bold" if (y+1)%5==0 else "normal"
                col_color = "#333" if (y+1)%5==0 else "#999"
                html_rows += f"<td class='axis-y' style='color:{col_color}; font-weight:{fw}'>{y+1}</td>"
                
                for cell in row:
                    if cell:
                        short_name = cell['name'].replace("Mard ", "")
                        rgb_str = f"RGB{cell['color']}"
                        tooltip = f"{short_name}  {rgb_str}"
                        # 关键：恢复 data-name 属性配合 CSS 实现高清悬浮窗
                        html_rows += f'<td class="pixel-cell" style="background-color: {cell["hex"]};" data-name="{tooltip}"></td>'
                    else:
                        html_rows += '<td class="pixel-cell empty"></td>'
                html_rows += "</tr>"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ background-color: #ffffff !important; margin: 0; padding: 20px; font-family: sans-serif; }}
                .container {{ display: flex; justify-content: center; padding-top: 50px; padding-bottom: 50px; overflow-x: auto; }}
                .pixel-grid {{ border-collapse: separate; border-spacing: 0; background-color: white; }}
                /* 恢复坐标轴样式 */
                .axis-x {{ width: 20px; font-size: 10px; text-align: center; vertical-align: bottom; padding-bottom: 2px; border: none; }}
                .axis-y {{ height: 20px; font-size: 10px; text-align: right; padding-right: 5px; border: none; white-space: nowrap; }}
                /* 恢复格子样式 */
                .pixel-cell {{ width: 20px; min-width: 20px; height: 20px; border: 1px solid #ddd; position: relative; box-sizing: border-box; }}
                .pixel-cell.empty {{ background-color: #f8f8f8; border: 1px dashed #eee; }}
                
                /* 恢复高清悬浮提示框 (Tooltip) */
                .pixel-cell:hover::after {{ 
                    content: attr(data-name); 
                    position: absolute; 
                    bottom: 110%; 
                    left: 50%; 
                    transform: translateX(-50%); 
                    background-color: #333; 
                    color: #fff; 
                    padding: 5px 10px; 
                    border-radius: 4px; 
                    font-size: 12px; 
                    white-space: nowrap; 
                    z-index: 999; 
                    pointer-events: none; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }}
                .pixel-cell:hover::before {{ 
                    content: ''; 
                    position: absolute; 
                    bottom: 90%; 
                    left: 50%; 
                    transform: translateX(-50%); 
                    border-width: 6px; 
                    border-style: solid; 
                    border-color: #333 transparent transparent transparent; 
                    z-index: 999; 
                }}
                .pixel-cell:hover {{ border: 2px solid #333; z-index: 10; }}
            </style>
            </head>
            <body>
                <div class="container">
                    <table class="pixel-grid">
                        {html_rows}
                    </table>
                </div>
            </body>
            </html>
            """
            
            calc_height = max(500, t_h * 24 + 150)
            st.components.v1.html(html_content, height=calc_height, scrolling=True)

        with t2:
            printable_img = create_printable_sheet(grid_data, color_usage, t_w, t_h)
            st.image(printable_img, use_container_width=True)
            
            buf = io.BytesIO()
            printable_img.save(buf, format="JPEG", quality=95)
            st.download_button("📥 下载 JPG 图纸", data=buf.getvalue(), file_name="perler_pattern.jpg", mime="image/jpeg")

else:
    if st.session_state.result_grid is not None:
         reset_results()
    st.info("👈 请在左侧上传图片开始")