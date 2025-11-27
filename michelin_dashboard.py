import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import colorsys

# 设置页面
st.set_page_config(
    page_title="米其林餐厅分析",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 简约风格的CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    .section-header {
        font-size: 1.4rem;
        color: #34495e;
        margin-top: 2.5rem;
        margin-bottom: 1.2rem;
        font-weight: 400;
        border-bottom: 2px solid #e0e6ea;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ea;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .metric-card h3 {
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
        color: #5d6d7e;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card h2 {
        font-size: 2.2rem;
        margin: 0;
        font-weight: 300;
        color: #2c3e50;
    }
    .price-level-btn {
        width: 100%;
        margin: 2px 0;
        border-radius: 8px;
        border: 1px solid #ccd1d1;
        background: white;
        transition: all 0.3s ease;
        padding: 0.5rem;
    }
    .price-level-btn:hover {
        background: #f2f4f4;
        border-color: #e74c3c;
    }
    .price-level-btn.active {
        background: #e74c3c;
        color: white;
        border-color: #e74c3c;
    }
    .price-level-label {
        text-align: center;
        margin-top: 10px;
        font-weight: 500;
        color: #2c3e50;
    }
    /* 自定义radio样式 */
    .stRadio > div {
        flex-direction: column;
    }
    .stRadio > div > label {
        margin-bottom: 5px;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #e0e6ea;
        background: white;
        transition: all 0.3s ease;
    }
    .stRadio > div > label:hover {
        background: #f8f9fa;
        border-color: #e74c3c;
    }
    .stRadio > div > label[data-testid="stRadioLabel"] > div:first-child {
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# 配色方案 - 更新为红色系
COLOR_SCHEME = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'accent': '#e74c3c',
    'accent2': '#c0392b',
    'background': '#ffffff',
    'text': '#2c3e50',
    'text_light': '#5d6d7e',
    'border': '#e0e6ea',
    'hover': '#f2f4f4'
}

# 生成动态红色系颜色序列
def generate_red_colors(n_colors):
    """生成n个不同的红色系颜色"""
    base_reds = [
        '#7d1d1d',  # 极深红
        '#a52a2a',  # 深红
        '#c0392b',  # 中深红
        '#e74c3c',  # 主红
        '#ec7063',  # 亮红
        '#f1948a',  # 浅红
        '#f5b7b1',  # 更浅红
        '#fadbd8',  # 浅粉红
        '#fdedec',  # 极浅粉红
    ]
    
    if n_colors <= len(base_reds):
        return base_reds[:n_colors]
    
    # 如果需要更多颜色，动态生成
    colors = []
    # 基础红色色调范围 (0-15度在色轮上)
    hues = np.linspace(0, 15, min(n_colors, 20))  # 限制最大20种色调变化
    
    for i in range(n_colors):
        # 使用HSL颜色空间生成变化
        hue = hues[i % len(hues)] / 360.0  # 色调 (红色区域)
        saturation = 0.7 - (i * 0.6 / n_colors)  # 饱和度从0.7到0.1
        lightness = 0.3 + (i * 0.5 / n_colors)   # 亮度从0.3到0.8
        
        # 转换为RGB
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255), 
            int(rgb[2] * 255)
        )
        colors.append(hex_color)
    
    return colors

# 红色系连续色阶
COLOR_SCALES = {
    'reds': [
        [0.0, '#fdedec'],  # 极浅粉红
        [0.1, '#fadbd8'],  # 浅粉红
        [0.3, '#f5b7b1'],  # 更浅红
        [0.5, '#f1948a'],  # 浅红
        [0.7, '#ec7063'],  # 亮红
        [0.85, '#e74c3c'], # 主红
        [1.0, '#c0392b']   # 中深红
    ],
    'sequential': [
        [0.0, '#fdedec'],
        [0.2, '#fadbd8'], 
        [0.4, '#f1948a'],
        [0.6, '#e74c3c'],
        [0.8, '#c0392b'],
        [1.0, '#7d1d1d']
    ],
    'price_scale': [
        [0.0, "#fdedec"],    # 极浅粉红
        [0.2, "#f5b7b1"],    # 更浅红
        [0.4, "#e74c3c"],    # 主红
        [0.6, "#c0392b"],    # 中红
        [0.8, "#a52a2a"],    # 深红
        [1.0, "#7d1d1d"]     # 极深红
    ],
    'high_contrast': [
        [0.0, '#fef5f5'],    # 非常浅红
        [0.15, '#fdedec'],   # 极浅粉红
        [0.3, '#fadbd8'],    # 浅粉红
        [0.45, '#f5b7b1'],   # 更浅红
        [0.6, '#f1948a'],    # 浅红
        [0.75, '#e74c3c'],   # 主红
        [0.9, '#c0392b'],    # 中红
        [1.0, '#a52a2a']     # 深红
    ]
}

# 标题
st.markdown('<h1 class="main-header">🍽️ 米其林餐厅全球分析</h1>', unsafe_allow_html=True)

# 加载数据
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cleaned.csv', encoding='utf-8', encoding_errors='ignore')
        df = df.dropna(subset=['Name', 'Cuisine', 'Location'], how='all')
        
        # 清理空行
        df = df.dropna(how='all')
        
        if 'Price_level' not in df.columns:
            df['Price_level'] = df['Price'].str.len()
        
        # 清理和标准化菜系数据
        def clean_cuisine(cuisine):
            if pd.isna(cuisine):
                return []
            # 移除多余空格，分割菜系
            cuisines = [c.strip() for c in str(cuisine).split(',')]
            # 去重并返回
            return list(set(cuisines))
        
        df['Cuisine_list'] = df['Cuisine'].apply(clean_cuisine)

        # 【新增】清理和标准化设施数据
        def clean_facilities(facilities):
            if pd.isna(facilities):
                return []
            facility_list = [f.strip() for f in str(facilities).split(',') if f.strip()]
            return list(set(facility_list))

        df['Facilities_list'] = df['FacilitiesAndServices'].apply(clean_facilities)
        
        df['Country'] = df['Location'].str.split(',').str[-1].str.strip()
        df['City'] = df['Location'].str.split(',').str[0].str.strip()
        
        # 国家名称标准化
        country_mapping = {
            'USA': 'United States',
            'UK': 'United Kingdom', 
            'China Mainland': 'China',
            'Taiwan': 'Taiwan',
            'Hong Kong': 'Hong Kong'
        }
        df['Country'] = df['Country'].replace(country_mapping)
        
        # 添加大洲信息
        continent_mapping = {
            'Japan': 'Asia', 'China': 'Asia', 'Taiwan': 'Asia', 'Hong Kong': 'Asia',
            'Singapore': 'Asia', 'South Korea': 'Asia', 'Thailand': 'Asia',
            'United States': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
            'France': 'Europe', 'United Kingdom': 'Europe', 'Italy': 'Europe', 
            'Spain': 'Europe', 'Germany': 'Europe', 'Switzerland': 'Europe',
            'Netherlands': 'Europe', 'Belgium': 'Europe',
            'Australia': 'Oceania', 'New Zealand': 'Oceania',
            'Brazil': 'South America', 'Argentina': 'South America'
        }
        df['Continent'] = df['Country'].map(continent_mapping)
        
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

@st.cache_data
def get_continent_coordinates():
    """大洲主要城市的坐标数据"""
    continent_coords = {
        'Asia': {
            'Tokyo': [35.6762, 139.6503], 'Osaka': [34.6937, 135.5023], 
            'Kyoto': [35.0116, 135.7681], 'Shanghai': [31.2304, 121.4737],
            'Beijing': [39.9042, 116.4074], 'Hong Kong': [22.3193, 114.1694],
            'Singapore': [1.3521, 103.8198], 'Seoul': [37.5665, 126.9780],
            'Bangkok': [13.7563, 100.5018]
        },
        'Europe': {
            'Paris': [48.8566, 2.3522], 'London': [51.5074, -0.1278],
            'Rome': [41.9028, 12.4964], 'Madrid': [40.4168, -3.7038],
            'Berlin': [52.5200, 13.4050], 'Amsterdam': [52.3676, 4.9041],
            'Vienna': [48.2082, 16.3738], 'Brussels': [50.8503, 4.3517]
        },
        'North America': {
            'New York': [40.7128, -74.0060], 'Chicago': [41.8781, -87.6298],
            'San Francisco': [37.7749, -122.4194], 'Los Angeles': [34.0522, -118.2437],
            'Toronto': [43.6532, -79.3832], 'Vancouver': [49.2827, -123.1207],
            'Mexico City': [19.4326, -99.1332]
        },
        'South America': {
            'São Paulo': [-23.5505, -46.6333], 'Rio de Janeiro': [-22.9068, -43.1729],
            'Buenos Aires': [-34.6037, -58.3816], 'Lima': [-12.0464, -77.0428],
            'Bogotá': [4.7110, -74.0721]
        },
        'Oceania': {
            'Sydney': [-33.8688, 151.2093], 'Melbourne': [-37.8136, 144.9631],
            'Auckland': [-36.8485, 174.7633], 'Brisbane': [-27.4698, 153.0251]
        }
    }
    return continent_coords

df = load_data()

if df.empty:
    st.warning("没有找到数据，请检查数据文件路径")
    st.stop()

# 获取唯一的菜系列表（去重后）
@st.cache_data
def get_unique_cuisines(df):
    """获取去重后的唯一菜系列表"""
    all_cuisines = []
    for cuisine_list in df['Cuisine_list'].dropna():
        all_cuisines.extend(cuisine_list)
    
    # 去重并排序
    unique_cuisines = sorted(list(set(all_cuisines)))
    return unique_cuisines

# 【新增】获取唯一的设系列表
@st.cache_data
def get_unique_facilities(df):
    all_facilities = []
    for facility_list in df['Facilities_list'].dropna():
        all_facilities.extend(facility_list)
    return sorted(list(set(all_facilities)))

# 获取前N菜系（基于餐厅计数，不是菜系出现次数）
@st.cache_data
def get_top_cuisines_by_restaurants(df, top_n=10):
    """获取基于餐厅数量的前N大菜系"""
    cuisine_restaurant_count = {}
    
    for idx, row in df.iterrows():
        if isinstance(row['Cuisine_list'], list):
            for cuisine in row['Cuisine_list']:
                if cuisine in cuisine_restaurant_count:
                    cuisine_restaurant_count[cuisine] += 1
                else:
                    cuisine_restaurant_count[cuisine] = 1
    
    # 按餐厅数量排序
    sorted_cuisines = sorted(cuisine_restaurant_count.items(), key=lambda x: x[1], reverse=True)
    top_cuisines = [cuisine for cuisine, count in sorted_cuisines[:top_n]]
    
    return top_cuisines

# 【新增】获取筛选后的前N菜系
@st.cache_data
def get_filtered_top_cuisines_by_restaurants(filtered_df, top_n=10):
    """基于筛选后的数据获取前N大菜系"""
    cuisine_restaurant_count = {}
    
    for idx, row in filtered_df.iterrows():
        if isinstance(row['Cuisine_list'], list):
            for cuisine in row['Cuisine_list']:
                if cuisine in cuisine_restaurant_count:
                    cuisine_restaurant_count[cuisine] += 1
                else:
                    cuisine_restaurant_count[cuisine] = 1
    
    # 按餐厅数量排序
    sorted_cuisines = sorted(cuisine_restaurant_count.items(), key=lambda x: x[1], reverse=True)
    top_cuisines = [cuisine for cuisine, count in sorted_cuisines[:top_n]]
    
    return top_cuisines

# 【新增】计算菜系统计数据（统一函数）
@st.cache_data
def calculate_cuisine_stats(filtered_df, top_cuisines_list):
    """计算菜系统计数据，确保逻辑一致性"""
    stats_data = []
    
    for cuisine in top_cuisines_list:
        # 筛选包含该菜系的餐厅
        cuisine_restaurants = filtered_df[filtered_df['Cuisine_list'].apply(
            lambda x: cuisine in x if isinstance(x, list) else False
        )]
        
        if len(cuisine_restaurants) > 0:
            # 基本统计
            restaurant_count = len(cuisine_restaurants)
            avg_price_level = cuisine_restaurants['Price_level'].mean()
            
            # 星级统计（只计算有星级的餐厅）
            starred_restaurants = cuisine_restaurants[cuisine_restaurants['Award'].isin(['1 Star', '2 Stars', '3 Stars'])]
            starred_count = len(starred_restaurants)
            starred_percentage = (starred_count / restaurant_count * 100) if restaurant_count > 0 else 0
            
            # 平均星级评分（只计算有星级的餐厅）
            award_mapping = {'1 Star': 1, '2 Stars': 2, '3 Stars': 3}
            if len(starred_restaurants) > 0:
                starred_restaurants['Award_Score'] = starred_restaurants['Award'].map(award_mapping)
                avg_award_score = starred_restaurants['Award_Score'].mean()
            else:
                avg_award_score = 0
            
            stats_data.append({
                'Cuisine': cuisine,
                'Restaurant_Count': restaurant_count,
                'Avg_Price_Level': avg_price_level,
                'Starred_Count': starred_count,
                'Starred_Percentage': starred_percentage,
                'Avg_Award_Score': avg_award_score
            })
    
    return pd.DataFrame(stats_data) if stats_data else pd.DataFrame()

# 获取数据
unique_cuisines = get_unique_cuisines(df)
unique_facilities = get_unique_facilities(df)

# 侧边栏过滤器
st.sidebar.header("🔍 数据筛选")

# 大洲选择菜单
continents = ['全部'] + sorted(df['Continent'].dropna().unique().tolist())
selected_continent = st.sidebar.selectbox("选择大洲", continents)

# 城市选择菜单（基于选择的大洲）
if selected_continent != '全部':
    available_cities = ['全部'] + sorted(df[df['Continent'] == selected_continent]['City'].dropna().unique().tolist())
else:
    available_cities = ['全部'] + sorted(df['City'].dropna().unique().tolist())

selected_city = st.sidebar.selectbox("选择城市", available_cities)

# 菜系选择菜单（多选）- 使用去重后的菜系列表
selected_cuisines = st.sidebar.multiselect(
    "选择菜系（可多选）",
    options=unique_cuisines,
    default=[]
)

# 米其林评级筛选
awards = ['全部'] + sorted(df['Award'].dropna().unique().tolist())
selected_award = st.sidebar.selectbox("米其林评级", awards)

# 【新增】设施筛选
st.sidebar.markdown("---")
selected_facilities = st.sidebar.multiselect(
    "选择设施（可多选）",
    options=unique_facilities,
    default=[],
    help="筛选包含所有选定设施的餐厅"
)


# 价格等级选择器 - 修改为使用radio组件，避免双击问题
st.sidebar.markdown("---")
st.sidebar.subheader("💰 价格等级")

# 价格等级描述
price_level_descriptions = {
    '全部': "所有价格等级",
    1: "经济型",
    2: "中价位", 
    3: "高消费",
    4: "奢华型"
}

# 初始化session state
if 'selected_price_level' not in st.session_state:
    st.session_state.selected_price_level = '全部'

# 使用radio组件替代按钮
price_options = ['全部', 1, 2, 3, 4]
price_labels = [f"{option} - {price_level_descriptions[option]}" for option in price_options]

# 创建radio选择器
selected_price_label = st.sidebar.radio(
    "选择价格等级:",
    options=price_labels,
    index=price_options.index(st.session_state.selected_price_level),
    key="price_level_radio"
)

# 从选择的标签中提取价格等级
selected_price_level = price_options[price_labels.index(selected_price_label)]

# 更新session state
st.session_state.selected_price_level = selected_price_level

# 显示当前选择的价格等级
current_description = price_level_descriptions.get(st.session_state.selected_price_level, "未知等级")
st.sidebar.markdown(f'<div class="price-level-label" style="color: #e74c3c; font-weight: bold;">当前选择: {current_description}</div>', unsafe_allow_html=True)

# 应用筛选
filtered_df = df.copy()
if selected_continent != '全部':
    filtered_df = filtered_df[filtered_df['Continent'] == selected_continent]
if selected_city != '全部':
    filtered_df = filtered_df[filtered_df['City'] == selected_city]
if selected_award != '全部':
    filtered_df = filtered_df[filtered_df['Award'] == selected_award]
if selected_cuisines:
    filtered_df = filtered_df[filtered_df['Cuisine_list'].apply(
        lambda x: any(cuisine in x for cuisine in selected_cuisines) if isinstance(x, list) else False
    )]

# 【新增】应用设施筛选逻辑
if selected_facilities:
    filtered_df = filtered_df[filtered_df['Facilities_list'].apply(lambda x: all(facility in x for facility in selected_facilities) if isinstance(x, list) else False)]

if st.session_state.selected_price_level != '全部':
    filtered_df = filtered_df[filtered_df['Price_level'] == st.session_state.selected_price_level]

# 关键指标卡片
st.markdown('<h2 class="section-header">📊 核心指标</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>餐厅总数</h3>
        <h2>{len(filtered_df):,}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    unique_cities = filtered_df['City'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <h3>覆盖城市</h3>
        <h2>{unique_cities}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    selected_cuisines_count = len(selected_cuisines) if selected_cuisines else 0
    st.markdown(f"""
    <div class="metric-card">
        <h3>选中菜系</h3>
        <h2>{selected_cuisines_count}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # 替换为更有意义的指标：有星级餐厅占比
    total_restaurants = len(filtered_df)
    starred_restaurants = len(filtered_df[filtered_df['Award'].isin(['1 Star', '2 Stars', '3 Stars'])])
    starred_percentage = (starred_restaurants / total_restaurants * 100) if total_restaurants > 0 else 0
    
    st.markdown(f"""
    <div class="metric-card">
        <h3>有星级餐厅占比</h3>
        <h2>{starred_percentage:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

# 大洲地图展示 - 修改为红色系
st.markdown('<h2 class="section-header">🗺️ 大洲餐厅分布</h2>', unsafe_allow_html=True)

if selected_continent != '全部':
    continent_coords = get_continent_coordinates()
    
    if selected_continent in continent_coords:
        # 获取该大洲的城市数据
        continent_cities = filtered_df[filtered_df['Continent'] == selected_continent]['City'].value_counts().reset_index()
        continent_cities.columns = ['City', 'Count']
        
        # 添加坐标
        continent_cities['Lat'] = continent_cities['City'].map(
            lambda x: continent_coords[selected_continent].get(x, [None, None])[0]
        )
        continent_cities['Lon'] = continent_cities['City'].map(
            lambda x: continent_coords[selected_continent].get(x, [None, None])[1]
        )
        
        continent_cities = continent_cities.dropna(subset=['Lat', 'Lon'])
        
        if not continent_cities.empty:
            # 创建大洲地图 - 使用红色系颜色方案
            fig = px.scatter_mapbox(
                continent_cities,
                lat='Lat',
                lon='Lon',
                size='Count',
                hover_name='City',
                hover_data={'Count': True},
                size_max=25,
                color='Count',
                color_continuous_scale=COLOR_SCALES['reds'],  # 使用红色系颜色方案
                zoom=3,
                title=f"{selected_continent} 米其林餐厅分布 - 价格等级: {current_description}"
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                height=500,
                margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"暂无 {selected_continent} 的城市坐标数据")
    else:
        st.info(f"暂无 {selected_continent} 的地图数据")
else:
    # 显示全球视图
    if not filtered_df.empty:
        # 获取所有城市的统计数据
        city_counts = filtered_df['City'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        
        # 为所有城市添加坐标（简化版）
        all_coords = get_continent_coordinates()
        city_coords = {}
        for continent, cities in all_coords.items():
            city_coords.update(cities)
        
        city_counts['Lat'] = city_counts['City'].map(lambda x: city_coords.get(x, [None])[0] if x in city_coords else None)
        city_counts['Lon'] = city_counts['City'].map(lambda x: city_coords.get(x, [None, None])[1] if x in city_coords else None)
        
        city_counts = city_counts.dropna(subset=['Lat', 'Lon'])
        
        if not city_counts.empty:
            fig = px.scatter_mapbox(
                city_counts,
                lat='Lat',
                lon='Lon',
                size='Count',
                hover_name='City',
                hover_data={'Count': True},
                size_max=20,
                color='Count',
                color_continuous_scale=COLOR_SCALES['reds'],  # 使用红色系颜色方案
                zoom=1,
                title=f"全球米其林餐厅分布 - 价格等级: {current_description}"
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                height=500,
                margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无全球城市坐标数据")
    else:
        st.info("请选择筛选条件来查看地图分布")

# 前N菜系的多维度分析
st.markdown('<h2 class="section-header">📈 菜系深度分析</h2>', unsafe_allow_html=True)

# 添加菜系数量选择器
col_config1, col_config2 = st.columns([1, 4])

with col_config1:
    # 菜系数量选择旋钮
    top_n_cuisines = st.number_input(
        "选择显示菜系数量",
        min_value=5,
        max_value=30,  # 增加到30个菜系
        value=10,
        step=1,
        help="选择要显示的前N个菜系数量（最多30个）"
    )

# 【修复】获取筛选后的前N菜系数据，确保数据一致性
top_n_cuisines_list = get_filtered_top_cuisines_by_restaurants(filtered_df, top_n_cuisines)

# 生成动态颜色序列
dynamic_colors = generate_red_colors(len(top_n_cuisines_list))

# 【修复】使用统一函数计算菜系统计数据
cuisine_stats_df = calculate_cuisine_stats(filtered_df, top_n_cuisines_list)

if not cuisine_stats_df.empty:
    # 第一行：菜系分布和评级关系
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<h3 style="color: #34495e; margin-bottom: 1rem;">前{top_n_cuisines}菜系餐厅数量</h3>', unsafe_allow_html=True)
        
        # 使用统一统计数据
        sorted_cuisine_stats = cuisine_stats_df.sort_values('Restaurant_Count', ascending=True)
        
        fig = px.bar(
            sorted_cuisine_stats,
            x='Restaurant_Count',
            y='Cuisine',
            orientation='h',
            labels={'Restaurant_Count': '餐厅数量', 'Cuisine': '菜系'},
            color='Restaurant_Count',
            color_continuous_scale=COLOR_SCALES['sequential']  # 使用红色系颜色方案
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='white',
            coloraxis_colorbar=dict(
                title='餐厅数量'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(f'<h3 style="color: #34495e; margin-bottom: 1rem;">前{top_n_cuisines}菜系与星级分布</h3>', unsafe_allow_html=True)
        
        # 创建菜系与评级的气泡图数据
        bubble_data = []
        
        # 定义评级顺序
        award_order = ['Bib Gourmand', '1 Star', '2 Stars', '3 Stars']
        
        for cuisine in top_n_cuisines_list:
            # 筛选该菜系的餐厅
            cuisine_restaurants = filtered_df[filtered_df['Cuisine_list'].apply(
                lambda x: cuisine in x if isinstance(x, list) else False
            )]
            
            for award in award_order:
                # 计算该菜系在该评级下的餐厅数量
                count = len(cuisine_restaurants[cuisine_restaurants['Award'] == award])
                
                if count > 0:
                    bubble_data.append({
                        'Cuisine': cuisine,
                        'Award': award,
                        'Count': count,
                        'Award_Order': award_order.index(award)  # 用于排序
                    })
        
        if bubble_data:
            bubble_df = pd.DataFrame(bubble_data)
            
            # 创建气泡图 - 使用动态颜色
            fig = px.scatter(
                bubble_df,
                x='Cuisine',
                y='Award',
                size='Count',
                color='Cuisine',
                hover_name='Cuisine',
                hover_data={'Count': True, 'Cuisine': False, 'Award': True},
                size_max=30,
                labels={
                    'Cuisine': '菜系',
                    'Award': '米其林评级',
                    'Count': '餐厅数量'
                },
                color_discrete_sequence=dynamic_colors  # 使用动态生成的红色系颜色
            )
            
            # 自定义气泡大小范围，确保可视化效果
            fig.update_traces(
                marker=dict(
                    sizemode='area',
                    sizeref=2.*max(bubble_df['Count'])/(30.**2),
                    sizemin=4
                )
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_tickangle=-45,
                showlegend=False,
                paper_bgcolor='white',
                xaxis_title='菜系',
                yaxis_title='米其林评级',
                yaxis={'categoryorder': 'array', 'categoryarray': award_order}
            )
            
            # 改进悬停信息显示
            fig.update_traces(
                hovertemplate="<br>".join([
                    "菜系: %{x}",
                    "评级: %{y}",
                    "餐厅数量: %{marker.size}",
                    "<extra></extra>"
                ])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无菜系与评级数据")
    
    # 第二行：价格分析和星级评分
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<h3 style="color: #34495e; margin-bottom: 1rem;">前{top_n_cuisines}菜系平均价格等级</h3>', unsafe_allow_html=True)
    
        # 使用统一统计数据
        sorted_price_stats = cuisine_stats_df.sort_values('Avg_Price_Level', ascending=False)
        
        # 保留两位小数
        sorted_price_stats['Avg_Price_Level'] = sorted_price_stats['Avg_Price_Level'].round(2)
        
        fig = px.bar(
            sorted_price_stats,
            x='Cuisine',
            y='Avg_Price_Level',
            color='Avg_Price_Level',
            color_continuous_scale=COLOR_SCALES['price_scale']
        )
        
        # 更新图表布局，设置中文标签
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_tickangle=-45,
            showlegend=False,
            paper_bgcolor='white',
            # 设置x轴和y轴标签为中文
            xaxis_title='菜系',
            yaxis_title='平均价格等级',
            # 设置颜色条标题为中文
            coloraxis_colorbar=dict(
                title='平均价格等级'
            )
        )
        
        # 更新悬停信息为中文
        fig.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>" +
                "平均价格等级: %{y:.2f}<br>" +
                "<extra></extra>"
            )
        )
        
        # 更新y轴格式显示两位小数
        fig.update_yaxes(tickformat=".2f")
        
        st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.markdown(f'<h3 style="color: #34495e; margin-bottom: 1rem;">前{top_n_cuisines}菜系星级评分分布</h3>', unsafe_allow_html=True)
        
        # 使用统一统计数据
        sorted_award_stats = cuisine_stats_df.sort_values('Avg_Award_Score', ascending=False)
        
        # 保留两位小数
        sorted_award_stats['Avg_Award_Score'] = sorted_award_stats['Avg_Award_Score'].round(2)
        sorted_award_stats['Starred_Percentage'] = sorted_award_stats['Starred_Percentage'].round(1)
        
        # 创建散点图 - 修复悬停信息问题
        fig = px.scatter(
            sorted_award_stats,
            x='Cuisine',
            y='Avg_Award_Score',
            size='Restaurant_Count',
            color='Avg_Award_Score',
            hover_data={
                'Cuisine': False,  # 不在悬停数据中重复显示
                'Avg_Award_Score': ':.2f',
                'Restaurant_Count': True,
                'Starred_Count': True,
                'Starred_Percentage': ':.1f'
            },
            size_max=40,
            labels={
                'Cuisine': '菜系',
                'Avg_Award_Score': '平均星级评分',
                'Restaurant_Count': '总餐厅数量',
                'Starred_Count': '有星级餐厅数量',
                'Starred_Percentage': '有星级餐厅占比(%)'
            },
            color_continuous_scale=COLOR_SCALES['sequential']
        )
        
        # 自定义气泡大小范围
        fig.update_traces(
            marker=dict(
                sizemode='area',
                sizeref=2.*max(sorted_award_stats['Restaurant_Count'])/(40.**2),
                sizemin=8,
                opacity=0.7,
                line=dict(width=1, color='white')
            )
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_tickangle=-45,
            showlegend=False,
            paper_bgcolor='white',
            xaxis_title='菜系',
            yaxis_title='平均星级评分'
        )
        
        # 修复悬停信息显示 - 确保有星级餐厅数量显示为整数
        fig.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>" +
                "平均星级评分: %{y:.2f}<br>" +
                "总餐厅数量: %{customdata[1]}<br>" +
                "有星级餐厅: %{customdata[2]:.0f}<br>" +  # 使用 :.0f 格式确保显示为整数
                "<extra></extra>"
            )
        )
        
        # 更新y轴格式显示两位小数
        fig.update_yaxes(tickformat=".2f")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 第三行：综合关系气泡图
    st.markdown(f'<h3 style="color: #34495e; margin-bottom: 1rem;">前{top_n_cuisines}菜系综合关系分析</h3>', unsafe_allow_html=True)
    
    # 使用统一统计数据
    fig = px.scatter(
        cuisine_stats_df,
        x='Avg_Price_Level',
        y='Avg_Award_Score',
        size='Restaurant_Count',
        color='Cuisine',
        hover_name='Cuisine',
        size_max=40,
        labels={
            'Avg_Price_Level': '平均价格等级',
            'Avg_Award_Score': '平均星级评分',
            'Restaurant_Count': '餐厅数量'
        },
        color_discrete_sequence=dynamic_colors  # 使用动态生成的红色系颜色
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        paper_bgcolor='white'
    )
    
    # 更新坐标轴格式显示两位小数
    fig.update_xaxes(tickformat=".2f")
    fig.update_yaxes(tickformat=".2f")
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("暂无菜系数据")

# --- 【新增】设施与评级/价格分析 ---
st.markdown('<h2 class="section-header">🏨 设施与评级/价格分析</h2>', unsafe_allow_html=True)

if not filtered_df.empty:
    # 准备用于分析的数据
    facility_df = filtered_df.explode('Facilities_list')
    
    # 获取最常见的15个设施进行分析，避免图表过于拥挤
    top_n_facilities = 15
    if not facility_df.empty and 'Facilities_list' in facility_df.columns and facility_df['Facilities_list'].notna().any():
        common_facilities = facility_df['Facilities_list'].value_counts().nlargest(top_n_facilities).index.tolist()
        
        # 1. 分组条形图
        st.markdown('<h3 style="color: #34495e; margin-bottom: 1rem;">不同星级餐厅的设施分布 (热门设施)</h3>', unsafe_allow_html=True)
        
        analysis_df = facility_df[facility_df['Facilities_list'].isin(common_facilities)]
        award_order = ['1 Star', '2 Stars', '3 Stars'] # 仅关注星级餐厅
        analysis_df = analysis_df[analysis_df['Award'].isin(award_order)]

        if not analysis_df.empty:
            facility_award_counts = analysis_df.groupby(['Facilities_list', 'Award']).size().reset_index(name='Count')
            
            fig_bar = px.bar(
                facility_award_counts,
                x='Facilities_list',
                y='Count',
                color='Award',
                barmode='group',
                labels={'Facilities_list': '设施', 'Count': '餐厅数量', 'Award': '米其林评级'},
                title='热门设施在不同星级餐厅中的数量',
                category_orders={'Award': award_order, 'Facilities_list': common_facilities},
                color_discrete_map={ # 适配为红色系
                    '1 Star': '#f1948a',  # 浅红
                    '2 Stars': '#e74c3c',  # 主红
                    '3 Stars': '#a52a2a'   # 深红
                }
            )
            fig_bar.update_layout(xaxis_tickangle=-45, paper_bgcolor='white', yaxis_title='餐厅数量', xaxis_title=None)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("根据当前筛选条件，没有足够的星级餐厅设施数据来生成分组条形图。")

        # 2. 热力图
        st.markdown('<h3 style="color: #34495e; margin-top: 2rem; margin-bottom: 1rem;">设施在不同评级/价格中的普及率</h3>', unsafe_allow_html=True)
        heatmap_axis = st.radio(
            "选择热力图分析维度", ('米其林星级', '价格等级'),
            horizontal=True, key='heatmap_toggle'
        )

        # 确保 heatmap_df 中有有效的设施列表
        heatmap_df = filtered_df.dropna(subset=['Facilities_list'])
        heatmap_df = heatmap_df[heatmap_df['Facilities_list'].apply(lambda x: isinstance(x, list) and len(x) > 0 and any(fac in common_facilities for fac in x))]
        
        if not heatmap_df.empty:
            if heatmap_axis == '米其林星级':
                columns = ['1 Star', '2 Stars', '3 Stars']
                heatmap_data = pd.DataFrame(index=common_facilities, columns=columns).fillna(0.0)

                for award in columns:
                    total_restaurants = len(heatmap_df[heatmap_df['Award'] == award])
                    if total_restaurants > 0:
                        for facility in common_facilities:
                            count_with_facility = len(heatmap_df[(heatmap_df['Award'] == award) & (heatmap_df['Facilities_list'].apply(lambda x: facility in x))])
                            heatmap_data.loc[facility, award] = (count_with_facility / total_restaurants) * 100
                
                title = '设施在不同星级餐厅中的普及率 (%)'
                xaxis_title = '米其林评级'
            
            else: # 价格等级
                columns = sorted(heatmap_df['Price_level'].dropna().unique().astype(int))
                heatmap_data = pd.DataFrame(index=common_facilities, columns=columns).fillna(0.0)

                for price_level in columns:
                    total_restaurants = len(heatmap_df[heatmap_df['Price_level'] == price_level])
                    if total_restaurants > 0:
                        for facility in common_facilities:
                            count_with_facility = len(heatmap_df[(heatmap_df['Price_level'] == price_level) & (heatmap_df['Facilities_list'].apply(lambda x: facility in x))])
                            heatmap_data.loc[facility, price_level] = (count_with_facility / total_restaurants) * 100
                
                title = '设施在不同价格等级餐厅中的普及率 (%)'
                xaxis_title = '价格等级'

            fig_heatmap = px.imshow(
                heatmap_data,
                text_auto=".0f",
                aspect="auto",
                labels=dict(x=xaxis_title, y="设施", color="普及率 (%)"),
                title=title,
                color_continuous_scale=COLOR_SCALES['sequential'] # 使用红色系
            )
            fig_heatmap.update_layout(paper_bgcolor='white', yaxis={'tickmode': 'array', 'tickvals': common_facilities, 'autorange': 'reversed'})
            fig_heatmap.update_traces(hovertemplate='设施: %{y}<br>' + xaxis_title + ': %{x}<br>普及率: %{z:.1f}%<extra></extra>')
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("根据当前筛选条件，没有足够的设施数据来生成热力图。")
    else:
        st.info("当前筛选条件下，餐厅不包含可分析的设施信息。")
else:
    st.info("请调整筛选条件以查看设施分析。")

# 数据表格
st.markdown('<h2 class="section-header">📋 餐厅详情</h2>', unsafe_allow_html=True)

if not filtered_df.empty:
    # 【修改】增加 Description 列
    display_columns = ['Name', 'City', 'Country', 'Continent', 'Price', 'Cuisine', 'Award', 'Price_level', 'Description']
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    
    # 显示筛选后的数据
    display_df = filtered_df[available_columns].reset_index(drop=True)
    
    # 如果有数值列，格式化显示两位小数
    numeric_columns = display_df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        display_df[col] = display_df[col].round(2)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=300
    )
    
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 下载筛选数据",
        data=csv,
        file_name="michelin_restaurants.csv",
        mime="text/csv"
    )
else:
    st.info("暂无符合条件的数据")

# 显示筛选统计信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 筛选统计")
st.sidebar.markdown(f"**筛选结果**: {len(filtered_df)} 家餐厅")
if selected_continent != '全部':
    st.sidebar.markdown(f"**大洲**: {selected_continent}")
if selected_city != '全部':
    st.sidebar.markdown(f"**城市**: {selected_city}")
if selected_award != '全部':
    st.sidebar.markdown(f"**评级**: {selected_award}")
st.sidebar.markdown(f"**价格等级**: {current_description}")

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #5d6d7e; padding: 2rem; font-size: 0.9rem;'>"
    f"米其林餐厅全球分析 | 大洲视图 | 价格等级: {current_description}" +
    "</div>",
    unsafe_allow_html=True
)
