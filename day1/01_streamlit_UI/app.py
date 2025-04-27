import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import time
from PIL import Image
import io

# ページ設定
st.set_page_config(
    page_title="万華鏡パターンジェネレーター",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #6A0DAD;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-title {
        font-size: 1.2rem !important;
        color: #8A2BE2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #6A0DAD;
        color: white;
        border-radius: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #666;
    }
    .info-box {
        background-color: #f0f0f7;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# タイトルとサブタイトル
st.markdown("<h1 class='main-title'>✨ 万華鏡パターンジェネレーター ✨</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>美しい万華鏡パターンを創り出そう</p>", unsafe_allow_html=True)

# 色のテーマプリセット
color_themes = {
    "レインボー": ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"],
    "オーシャン": ["#0077be", "#87ceeb", "#00ffff", "#006994", "#00008B", "#120a8f", "#000000"],
    "サンセット": ["#ff7e5f", "#feb47b", "#ffac81", "#ff8c69", "#ff7f50", "#ff6347", "#ff4500"],
    "パステル": ["#ffb6c1", "#ffc0cb", "#f08080", "#e6e6fa", "#b0e0e6", "#add8e6", "#87ceeb"],
    "モノクロ": ["#000000", "#222222", "#444444", "#666666", "#888888", "#aaaaaa", "#ffffff"],
    "ネオン": ["#ff00ff", "#00ffff", "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff"],
}

# サイドバー - 設定パネル
st.sidebar.title("パターン設定")

# 設定パラメータ
complexity = st.sidebar.slider("複雑さ", 1, 20, 8)
segments = st.sidebar.slider("セグメント数", 4, 24, 8, 2)
scale = st.sidebar.slider("スケール", 0.1, 5.0, 2.0, 0.1)
zoom = st.sidebar.slider("ズーム", 0.5, 2.0, 1.0, 0.1)
rotation = st.sidebar.slider("回転角度", 0.0, 360.0, 0.0, 5.0)

# カラーテーマ選択
selected_theme = st.sidebar.selectbox("カラーテーマ", list(color_themes.keys()))
use_custom_colors = st.sidebar.checkbox("カスタムカラー", False)

if use_custom_colors:
    custom_colors = []
    cols = st.sidebar.columns(3)
    for i in range(5):
        if i < 3:
            col = cols[i]
        else:
            col = cols[i-3]
        color = col.color_picker(f"色 {i+1}", f"#{np.random.bytes(3).hex()}")
        custom_colors.append(color)
    colors = custom_colors
else:
    colors = color_themes[selected_theme]

# 解像度設定
resolution = st.sidebar.select_slider(
    "解像度",
    options=["低 (500x500)", "中 (800x800)", "高 (1200x1200)"],
    value="中 (800x800)"
)

# 解像度の数値を取得
if resolution == "低 (500x500)":
    fig_size = 5
    dpi = 100
elif resolution == "中 (800x800)":
    fig_size = 8
    dpi = 100
else:
    fig_size = 12
    dpi = 100

# シード値設定
use_random_seed = st.sidebar.checkbox("ランダムシード", True)
if not use_random_seed:
    seed = st.sidebar.number_input("シード値", 0, 99999, 42, 1)
else:
    seed = np.random.randint(0, 100000)

# 万華鏡パターン生成関数
def generate_kaleidoscope(complexity, segments, scale, zoom, rotation, colors, seed, fig_size, dpi):
    np.random.seed(seed)
    
    # プロットの設定
    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 背景色設定
    fig.patch.set_facecolor('black')
    
    # カラーマップの作成
    cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)
    
    # 座標グリッドの作成
    x = np.linspace(-scale, scale, 1000)
    y = np.linspace(-scale, scale, 1000)
    X, Y = np.meshgrid(x, y)
    
    # 極座標に変換
    r = np.sqrt(X**2 + Y**2) * zoom
    theta = np.arctan2(Y, X) + np.radians(rotation)
    
    # 複雑なパターンを生成するための関数
    pattern = np.zeros_like(r)
    
    for i in range(complexity):
        freq = i + 1
        amplitude = 1 / (i + 1)
        phase = np.random.random() * 2 * np.pi
        
        # 様々な周波数成分を加える
        pattern += amplitude * np.sin(freq * segments * theta + phase * r)
    
    # 正規化して0-1の範囲にする
    pattern = (pattern - np.min(pattern)) / (np.max(pattern) - np.min(pattern))
    
    # マンデルブロ的な要素を追加する
    mask = r < scale
    pattern = pattern * mask
    
    # プロット
    ax.imshow(pattern, cmap=cmap, extent=[-scale, scale, -scale, scale], origin='lower')
    
    # 画像をバイトストリームに変換
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, facecolor='black')
    buf.seek(0)
    plt.close(fig)
    
    return buf

# メインコンテンツ
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("生成されたパターン")
    
    # パターン生成ボタン
    if st.button("新しいパターンを生成", key="generate"):
        if use_random_seed:
            seed = np.random.randint(0, 100000)
            st.session_state['current_seed'] = seed
        else:
            st.session_state['current_seed'] = seed
    
    # セッション状態を使用してシード値を保存
    if 'current_seed' not in st.session_state:
        st.session_state['current_seed'] = seed
    
    # プログレスバーを表示
    progress_bar = st.progress(0)
    for i in range(101):
        progress_bar.progress(i/100)
        time.sleep(0.01)
    
    # パターン生成と表示
    image_buf = generate_kaleidoscope(
        complexity, 
        segments, 
        scale, 
        zoom, 
        rotation, 
        colors, 
        st.session_state['current_seed'],
        fig_size,
        dpi
    )
    
    image = Image.open(image_buf)
    st.image(image, use_column_width=True)
    
    # 現在のシード値を表示
    st.caption(f"現在のシード値: {st.session_state['current_seed']}")
    
    # ダウンロードボタン
    btn = st.download_button(
        label="画像をダウンロード",
        data=image_buf,
        file_name=f"kaleidoscope_{st.session_state['current_seed']}.png",
        mime="image/png"
    )

with col2:
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.subheader("万華鏡について")
    st.write("""
    万華鏡（まんげきょう）は、筒の中に置かれた複数の鏡と色とりどりの小片により、
    美しく対称的なパターンを映し出す光学装置です。
    
    このアプリでは数学的アルゴリズムを使って、デジタルの万華鏡パターンを生成しています。
    サイドバーの設定を変更して、様々なパターンを探索してみましょう。
    
    **設定の意味:**
    * **複雑さ**: パターンの細かさを調整します
    * **セグメント数**: 対称的に繰り返される部分の数です
    * **スケール**: パターン全体の大きさを調整します
    * **ズーム**: 中心部分の拡大率を変更します
    * **回転角度**: パターン全体を回転させます
    
    お気に入りのパターンが見つかったら、「画像をダウンロード」ボタンでPNG形式で保存できます。
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("このパターンの統計")
    st.metric("複雑度スコア", f"{complexity * segments / 5:.1f}/100")
    
    # 複雑さに応じたパターン名を生成
    pattern_types = [
        "シンプルスター", "クリスタルフラワー", "コズミックスパイラル", 
        "カレイドスコープノヴァ", "フラクタルディメンション"
    ]
    complexity_level = min(4, int((complexity * segments) / 20))
    st.metric("パターンタイプ", pattern_types[complexity_level])
    
    # 色数のカウント
    if use_custom_colors:
        color_count = len(set(custom_colors))
    else:
        color_count = len(set(colors))
    st.metric("使用色数", color_count)

# フッター
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("© 2025 万華鏡パターンジェネレーター | 松尾研究室 AI エンジニアリング実践 課題")
st.markdown("</div>", unsafe_allow_html=True)