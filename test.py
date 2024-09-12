import subprocess
import os
import asr.Ifasr as api
import asr.data_show as data
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import llm.LLMAPI as LLMAPI
import json
import matplotlib.pyplot as plt
from pygwalker.api.streamlit import StreamlitRenderer

# 设置页面配置
st.set_page_config(
    page_title="销售分析demo",
    layout="wide",
)

# 定义三个页面的函数
def page_video_to_text():
    st.title("监控视频-语音转文字-词频分析-对话总结 Demo")
    # 文件上传
    uploaded_file = st.file_uploader("上传 MP4 视频文件", type=["mp4"])
    
    if uploaded_file:
        
        # 保存上传的文件
        video_path = os.path.join("temp", "uploaded_video.mp4")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.video(video_path)  # 显示视频
        
        # 使用 ffmpeg 提取音频
        audio_output_path = os.path.join("temp", "audio.wav")
        command = f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_output_path}"
        subprocess.run(command, shell=True)
        
        # 检查音频文件是否存在
        if os.path.exists(audio_output_path):
            st.success(f"音频文件 {audio_output_path} 已成功提取。")
            st.audio(audio_output_path, format='audio/wav')
        else:
            st.error("音频文件提取失败。")
        
        
        # 语音转文字按钮
    if st.button("调用语音转文字功能"):
            # 调用语音转文字接口
            api_response_save_path = os.path.join("temp", "response.json")
            response = api.asrAPI_lfasr(audio_file_path=audio_output_path, output_file_path=api_response_save_path)
            
            if response:
                trans_result_path = os.path.join("temp", "tran.txt")
                api.process_lfasr(input_file_path=api_response_save_path, output_file_path=trans_result_path)
                st.success("转写的文字:")
                with open(trans_result_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                st.text_area("转写结果", content, height=300)
            else:
                st.error("语音转文字失败，请检查接口或文件。")
        
    # 创建带有默认文本内容的多行文本框
    default_text = "你是经验丰富的卤味熟食门店销售分析专家，根据录音转文字的销售对话，判断此次对话是否提示需要新进某些产品/某些产品是否品质有变化/某个促销活动有效或者无效/店员话术是否促进了营业额的提升以及是否可以提炼话术和场景"
    user_input = st.text_area("大语言模型提示词", value=default_text)

    if st.button("语言模型分析"):
            trans_result_path = os.path.join("temp", "tran.txt")
            with open(trans_result_path, 'r', encoding='utf-8') as file:
                content = file.read()
            mm=LLMAPI.ModelManager()
            message=[{
                        "role":"user",
                        "content":f"""这是一家名叫紫燕百味鸡的卤味熟食店发生的客户与店员的对话，
                        这家店有百味鸡/紫燕鹅/藤椒鸡/夫妻肺片/猪耳朵等明星产品，还售卖海带/腐竹/木耳/杏鲍菇
                        等小菜，一般用户点单后，店员要切菜、拌菜、打包好以后交给客户，根据以上信息，考虑中文谐音，
                        尽可能还原对话内容，不要有任何多余输出：【{content}】"""
                    }]
            res1=mm.Get_Response_Spark(messages=message)
            st.write(f"模型润色对话：\n {res1}")
            message=[{
                        "role":"user",
                        "content":f"""{user_input} 对话内容为【{res1}】"""
                    }]
            res2=mm.Get_Response_Spark(messages=message)
            st.write(f"模型分析对话：\n {res2}")

    if st.button("关键词-词频统计"):
            trans_result_path = os.path.join("temp", "tran.txt")
            with open(trans_result_path, 'r', encoding='utf-8') as file:
                content = file.read()
            word_count_path="D:/ziyan/store_video_analysis/temp/word_frequency_analysis.png"
            wordcloud_path="D:/ziyan/store_video_analysis/temp/wordcloud.png"
            data.generate_wordcloud(text_data=content,output_path=wordcloud_path)
            data.word_count(text=content,output_path=word_count_path)

            st.image(word_count_path, caption="文本词频", use_column_width=False)
            st.image(wordcloud_path, caption="文本词云", use_column_width=False)
            
            
            

            




def page_table1():
    st.title("门店销售情况统计")
    st.subheader("0801-0831销售统计数据")
    df = pd.read_csv('.\data\store.csv')
    # 设置表格选项
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)  # 设置每页显示10行
    gridOptions = gb.build()
    # 在 Streamlit 页面上展示带分页的表格
    AgGrid(df, gridOptions=gridOptions)

    st.subheader("销售总额")
    # 计算最大值、最小值、平均值和中位数
    max_value = df['销售总额'].max()      # 最大值
    min_value = df['销售总额'].min()      # 最小值
    mean_value = df['销售总额'].mean()    # 平均值
    median_value = df['销售总额'].median() # 中位数
    variance = df['销售总额'].std()    

    # 打印结果
    st.write(f"最大值: {max_value}")
    st.write(f"最小值: {min_value}")
    st.write(f"平均值: {mean_value}")
    st.write(f"中位数: {median_value}")
    st.write(f"标准差: {variance}")



def page_table2():
    st.title("门店流水数据分析")
    st.subheader("苏州翰林店客单+订单总额100以上订单语音分析")
    df = pd.read_csv('.\data\sales.csv')
    # 设置表格选项
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)  # 设置每页显示10行
    gridOptions = gb.build()
    # 在 Streamlit 页面上展示带分页的表格
    AgGrid(df, gridOptions=gridOptions)
    st.image("D:\ziyan\\video\\test\word_frequency_analysis.png")
    st.image("D:\ziyan\\video\\test\word_cloud.png")


def page_table3():
    # 目前数据文件是来自网页响应数据，要在这个插件中使用只要整理成列表数据就可以
    # 读取数据文件1
    file_path = '.\data\\beef_whole_price.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    data=json.loads(data['data']['list'][0]['content'])
    x=[]
    y=[]
    for item in data:
        x.append(item['x'])
        y.append(float(item['y']))
    x=reversed(x)
    y=reversed(y)
    
    # 读取数据文件2
    file_path = '.\data\\beef_price.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data1 = json.load(file)
    data1=json.loads(data1['data']['list'][0]['content'])
    x1=[]
    y1=[]
    for item in data1:
        x1.append(item['x'])
        y1.append(float(item['y']))
    x1.pop(-1) # 这个插件工具如果想在同一页面拖动数据的话，列表长度要一致
    y1.pop(-1)
    x1=reversed(x1)
    y1=reversed(y1)
    
    # 构建 DataFrame，这个插件工具只要能提供列表数据就可以
    df = pd.DataFrame({
        "肉牛胴体价格指数日期": x,
        "肉牛胴体价格指数": y,
        "热鲜牛肉价格监测数据日期": x1,
        "热鲜牛肉价格监测数据": y1
    })

    renderer = StreamlitRenderer(df, spec="./gw_config.json")

    st.title("原材料价格数据可视化工具")

    renderer.explorer()
    st.markdown(
    """
    [参考数据来源网站](https://indices.cnfin.com/3318343/index.html?idx=0&thirdIdx=3318340)
    """,
    unsafe_allow_html=True
    )

# 定义三个页面的函数
def page_avater():
    st.title("基于数字人技术的销售场景培训 Demo")
    video_index = 0

    # 视频文件夹路径
    video_folder = 'D:/ziyan/store_video_analysis/data/avatar_demo'

    # 自动获取文件夹中的所有视频文件
    videos = []
    for folder in sorted(os.listdir(video_folder)):
        folder_path = os.path.join(video_folder, folder)
        if os.path.isdir(folder_path):
            video_file = os.path.join(folder_path, folder + '.mp4')
            if os.path.exists(video_file):
                videos.append(video_file)
    # 对应的视频对话选项
    dialogue_options = [
        ['欢迎光临，这是今天的', '是今天的牛肉，日期新鲜的', '今天的，要来几块？'],
        ['有原味和酱香两种，要什么口味的？', '要什么口味的？', '酱香还是原味？'],
        ['要哪块？', '这块比较完整'],
        ['还要点什么吗？',"新上的椒盐锁骨很适合下酒，要不要来点"],
        ["还要点什么吗"],
        ["好吃下次还来哈","您慢走"],
        ['好的']

    ]

    for i in range(7):
            # 显示当前视频
        st.video(videos[video_index])

        # 显示对话选项
        option = st.radio("Choose your dialogue option:", dialogue_options[video_index])

        
        video_index = (video_index + 1) % len(videos)
        

    
        



# 创建侧边栏导航
st.sidebar.title("门店销售分析")
page = st.sidebar.radio(" ", ["监控视频-语音转文字-词频分析-对话总结 Demo", "门店销售情况统计", "门店流水分析",'原材料价格数据可视化工具',"数字人培训demo"])

# 根据选择渲染对应页面
if page == "监控视频-语音转文字-词频分析-对话总结 Demo":
    page_video_to_text()
elif page == "门店销售情况统计":
    page_table1()
elif page == "门店流水分析":
    page_table2()
elif page == "原材料价格数据可视化工具":
    page_table3()
elif page == "数字人培训demo":
    page_avater()
