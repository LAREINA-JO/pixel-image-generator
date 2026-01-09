import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# 尝试导入高级库
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
    "Mard A1": (250, 245, 205), "Mard A2": (252, 254, 214), "Mard A3": (255, 255, 146),
    "Mard A4": (247, 236, 92),  "Mard A5": (255, 228, 75),  "Mard A6": (253, 169, 81),
    "Mard A7": (250, 140, 79),  "Mard A8": (249, 224, 69),  "Mard A9": (249, 156, 95),
    "Mard A10": (244, 126, 54), "Mard A11": (254, 219, 153), "Mard A12": (249, 191, 128),
    "Mard A13": (254, 198, 103), "Mard A14": (248, 88, 66), "Mard A15": (251, 246, 94),
    "Mard A16": (254, 255, 151), "Mard A17": (253, 225, 115), "Mard A18": (252, 191, 128),
    "Mard A19": (253, 126, 119), "Mard A20": (249, 214, 110), "Mard A21": (250, 227, 147),
    "Mard A22": (237, 248, 120), "Mard A23": (225, 201, 189), "Mard A24": (243, 246, 169),
    "Mard A25": (254, 215, 133), "Mard A26": (254, 200, 50),

    # --- B 系列 (绿色系) ---
    "Mard B1": (223, 241, 57),  "Mard B2": (100, 243, 67),  "Mard B3": (159, 246, 133),
    "Mard B4": (95, 223, 52),   "Mard B5": (57, 225, 88),   "Mard B6": (64, 244, 164),
    "Mard B7": (63, 174, 124),  "Mard B8": (29, 158, 84),   "Mard B9": (42, 80, 55),
    "Mard B10": (154, 209, 186), "Mard B11": (98, 112, 50), "Mard B12": (26, 110, 61),
    "Mard B13": (200, 232, 125), "Mard B14": (172, 232, 76), "Mard B15": (131, 232, 85),
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
    "Mard D4": (22, 44, 126),   "Mard D5": (179, 78, 198),  "Mard D6": (119, 23, 122),
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
    "Mard F10": (135, 70, 40),  "Mard F11": (111, 50, 29),  "Mard F12": (236, 134, 149),
    "Mard F13": (244, 92, 69),  "Mard F14": (252, 173, 178), "Mard F15": (213, 5, 39),
    "Mard F16": (248, 192, 169), "Mard F17": (232, 155, 125), "Mard F18": (208, 126, 74),
    "Mard F19": (190, 69, 74),  "Mard F20": (198, 148, 149), "Mard F21": (242, 187, 198),
    "Mard F22": (247, 195, 208), "Mard F23": (236, 128, 109), "Mard F24": (224, 157, 175),
    "Mard F25": (232, 72, 84),

    # --- G 系列 (肤色/大地色系) ---
    "Mard G1": (255, 228, 211), "Mard G2": (252, 198, 172), "Mard G3": (241, 196, 165),
    "Mard G4": (220, 179, 135), "Mard G5": (231, 179, 78),  "Mard G6": (242, 120, 36),
    "Mard G7": (152, 80, 58),   "Mard G8": (75, 43, 28),    "Mard G9": (139, 122, 133),
    "Mard G10": (218, 140, 66), "Mard G11": (218, 200, 152), "Mard G12": (212, 183, 147),
    "Mard G13": (178, 113, 75), "Mard G14": (139, 104, 76), "Mard G15": (242, 248, 227),
    "Mard G16": (242, 216, 193), "Mard G17": (121, 84, 78), "Mard G18": (255, 228, 214),
    "Mard G19": (221, 125, 65), "Mard G20": (165, 69, 47),  "Mard G21": (179, 133, 97),

    # --- H 系列 (灰度/黑白) ---
    "Mard H1": (251, 251, 251), "Mard H2": (255, 255, 255), "Mard H3": (180, 180, 180),
    "Mard H4": (135, 135, 135), "Mard H5": (70, 70, 72),    "Mard H6": (44, 44, 44),
    "Mard H7": (23, 23, 23),    "Mard H8": (231, 214, 220), "Mard H9": (239, 237, 238),
    "Mard H10": (236, 234, 235), "Mard H11": (205, 205, 205), "Mard H12": (234, 237, 238),
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

def find_closest_color(pixel):
    if len(pixel) == 4 and pixel[3] < 128:
        return None, (255, 255, 255, 0)
    
    min_dist = float('inf')
    closest_name = "未知"
    closest_rgb = (0, 0, 0)
    r, g, b = pixel[:3]

    for name, (cr, cg, cb) in MARD_PALETTE.items():
        # 加权欧几里得距离，提升人眼感知准确度
        dist = ((r - cr)*0.30)**2 + ((g - cg)*0.59)**2 + ((b - cb)*0.11)**2
        if dist < min_dist:
            min_dist = dist
            closest_name = name
            closest_rgb = (cr, cg, cb)
    return closest_name, closest_rgb

def create_printable_sheet(grid_data, color_map, width, height):
    # 配置
    cell_size = 30
    margin = 50
    # 【修改】不再保留右侧图例区域，只保留网格
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
                # 填充颜色
                draw.rectangle([top_left_x, top_left_y, bottom_right_x, bottom_right_y], fill=cell['color'], outline="lightgray")
                
                # 提取色号 (去除 "Mard " 前缀)
                full_name = cell['name'] # "Mard A13"
                short_code = full_name.replace("Mard ", "") # "A13"
                
                # 智能判断文字颜色
                text_color = "black" if (cell['color'][0]*0.299 + cell['color'][1]*0.587 + cell['color'][2]*0.114) > 150 else "white"
                
                # 绘制色号
                draw.text((top_left_x + 3, top_left_y + 8), short_code, fill=text_color)
            else:
                draw.rectangle([top_left_x, top_left_y, bottom_right_x, bottom_right_y], fill="white", outline="lightgray")

    # 绘制10x10粗线
    for i in range(0, width + 1, 10):
        line_x = margin + i * cell_size
        draw.line([(line_x, margin), (line_x, margin + height * cell_size)], fill="black", width=2)
    for i in range(0, height + 1, 10):
        line_y = margin + i * cell_size
        draw.line([(margin, line_y), (margin + width * cell_size, line_y)], fill="black", width=2)

    # 【修改】不再绘制右侧图例列表
    
    return sheet

# --- 主程序 ---
st.set_page_config(page_title="拼豆生成器", layout="wide")
st.title("🧩 专业版拼豆图纸生成器 (完整 Mard 色卡)")

if 'result_grid' not in st.session_state:
    st.session_state.result_grid = None
if 'result_stats' not in st.session_state:
    st.session_state.result_stats = None
if 'result_dims' not in st.session_state:
    st.session_state.result_dims = (0, 0)

st.sidebar.header("1. 上传图片")
uploaded_file = st.sidebar.file_uploader("支持 JPG/PNG/WEBP", type=["jpg", "png", "jpeg", "webp"])

st.sidebar.header("2. 生成设置")
use_rembg = st.sidebar.checkbox("启用智能抠图 (去除背景)", value=False)
target_width = st.sidebar.slider("目标宽度 (格/豆)", 10, 100, 40)
generate_btn = st.sidebar.button("🚀 开始生成图纸")

if use_rembg and not HAS_REMBG:
    st.sidebar.error("⚠️ 未安装 rembg 库")

if uploaded_file:
    original_image = Image.open(uploaded_file).convert("RGBA")
    
    st.subheader("🖼️ 步骤一：图片准备")
    enable_crop = st.checkbox("✂️ 启用手动裁剪 (Enable Cropping)", value=False)
    
    final_processing_img = original_image

    if enable_crop and HAS_CROPPER:
        st.caption("请在红框内拖动选择区域：")
        display_width = 800
        if original_image.width < display_width:
            aspect = original_image.height / original_image.width
            new_height = int(display_width * aspect)
            editing_image = original_image.resize((display_width, new_height), Image.NEAREST)
        else:
            editing_image = original_image
        
        cropped_img = st_cropper(editing_image, realtime_update=True, box_color='#8B1A1A', aspect_ratio=None)
        st.image(cropped_img, caption="裁剪预览", width=150)
        final_processing_img = cropped_img
    else:
        st.image(original_image, caption="完整原图预览", width=300)

    if generate_btn:
        with st.spinner("正在匹配 200+ 种 Mard 颜色..."):
            img_to_process = final_processing_img
            if use_rembg and HAS_REMBG:
                try:
                    img_to_process = remove(img_to_process)
                except Exception as e:
                    st.error(f"抠图出错: {e}")

            aspect_ratio = img_to_process.height / img_to_process.width
            target_height = int(target_width * aspect_ratio)
            
            if hasattr(Image, 'Resample'):
                resample_method = Image.Resample.BILINEAR
            else:
                resample_method = Image.BILINEAR
            
            small_img = img_to_process.resize((target_width, target_height), resample_method)
            
            pixel_data = small_img.load()
            grid_data = []
            color_usage = {}

            for y in range(target_height):
                row = []
                for x in range(target_width):
                    pixel = pixel_data[x, y]
                    c_name, c_rgb = find_closest_color(pixel)
                    
                    if c_name:
                        color_usage[c_name] = color_usage.get(c_name, 0) + 1
                        row.append({'color': c_rgb, 'name': c_name, 'hex': '#%02x%02x%02x' % c_rgb})
                    else:
                        row.append(None)
                grid_data.append(row)
            
            st.session_state.result_grid = grid_data
            st.session_state.result_stats = color_usage
            st.session_state.result_dims = (target_width, target_height)

    if st.session_state.result_grid is not None:
        st.markdown("---")
        st.subheader("🎨 步骤二：生成结果")
        
        grid_data = st.session_state.result_grid
        color_usage = st.session_state.result_stats
        t_w, t_h = st.session_state.result_dims

        t1, t2 = st.tabs(["🖼️ 交互式网格图 (Web)", "🖨️ 打印用高清图纸 (JPG)"])

        with t1:
            st.caption("👇 鼠标移动到格子上，会立即显示色号与RGB数值。")
            
            html_rows = ""
            for row in grid_data:
                html_rows += "<tr>"
                for cell in row:
                    if cell:
                        short_name = cell['name'].replace("Mard ", "")
                        # 【新增】格式化 RGB 字符串
                        rgb_str = f"RGB{cell['color']}"
                        tooltip = f"{short_name}  {rgb_str}"
                        
                        html_rows += f'<td class="pixel-cell" style="background-color: {cell["hex"]};" data-name="{tooltip}"></td>'
                    else:
                        html_rows += '<td class="pixel-cell empty"></td>'
                html_rows += "</tr>"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{
                    background-color: #ffffff !important;
                    margin: 0;
                    padding: 20px;
                    font-family: sans-serif;
                }}
                .container {{
                    display: flex;
                    justify-content: center;
                    padding-top: 50px;
                    padding-bottom: 50px;
                }}
                .pixel-grid {{
                    border-collapse: collapse;
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .pixel-cell {{
                    width: 20px;
                    height: 20px;
                    border: 1px solid #ddd;
                    position: relative;
                }}
                .pixel-cell.empty {{
                    background-color: #f8f8f8;
                    border: 1px dashed #eee;
                }}
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
            st.image(printable_img, caption="纯净版网格图纸 (无图例)", use_container_width=True)
            
            buf = io.BytesIO()
            printable_img.save(buf, format="JPEG", quality=100)
            st.download_button("📥 下载图纸 (JPG)", data=buf.getvalue(), file_name="pattern_grid.jpg", mime="image/jpeg")
else:
    st.info("👈 请先在左侧侧边栏上传一张图片")