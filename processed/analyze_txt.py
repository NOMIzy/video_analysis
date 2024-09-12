import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import os
from wordcloud import WordCloud
import pandas as pd
import jieba
import imageio.v2 as imageio
import random


# 定义颜色函数，返回红色或紫色的RGB值
def red_purple_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "rgb({}, {}, {})".format(random.randint(150, 255), random.randint(0, 50), random.randint(0, 100))


# 示例代码：生成词云
def generate_wordcloud(text_data,output_path='D:/ziyan/store_video_analysis/temp/wordcloud.png',unwanted_words = [
    '谢','好','1','2','3','4','5','6','7','8','9','0','的','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','，','。',"?",'你','我','\n',"。", "，", "！", "？", "：", "；", "“", "”", "‘", "’", 
    "（", "）", "《", "》", "【", "】", "……", "——", "、", "·","呢", "啊", "呃", "嗯", "嘛", "吧", "哦", "哎", "哇", "啊哈", 
    "啥", "喔", "哟", "嗐", "嘿", "哼",'是','了','吗','.','个',"他","们"
    ]):

    # 批量替换语气词为空字符串
    for word in unwanted_words:
        text_data = text_data.replace(word, '')
    word_list=jieba.cut(text_data,cut_all=True)
    # 遍历 word_list ，对 word 出现的频率进行统计
    counts = {}
    for word in word_list:
        counts[word] = counts.get(word, 0)+1
    font="C:\Windows\Fonts\\simhei.ttf"

    # 清除当前画布
    plt.clf()
    wordcloud = WordCloud(font_path=font,width=800, height=400, random_state=0, max_font_size=100, background_color='white',scale=8,color_func=red_purple_color_func).fit_words(counts)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(output_path,dpi=600)  # 保存图片为PNG格式
    plt.show()

def word_count(text,output_path="D:/ziyan/store_video_analysis/temp/word_frequency_analysis.png",unwanted_words = [
    '谢','好','1','2','3','4','5','6','7','8','9','0','的','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','，','。',"?",'你','我',"。", "，", "！", "？", "：", "；", "“", "”", "‘", "’", 
    "（", "）", "《", "》", "【", "】", "……", "——", "、", "·","呢", "啊", "呃", "嗯", "嘛", "吧", "哦", "哎", "哇", "啊哈", 
    "啥", "喔", "哟", "嗐", "嘿", "哼",'是','了','吗','.','个',"他","们"
    ]):

    # 批量替换语气词为空字符串
    for word in unwanted_words:
        text = text.replace(word, '')
    words =jieba.cut(text,cut_all=True)

    # 使用 Counter 计算每个词的频率
    word_counts = Counter(words)

    # 获取词语和对应的频率
    labels, values = zip(*word_counts.items())

    # 对频率从高到低排序
    sorted_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)[:50]
    sorted_labels = [labels[i] for i in sorted_indices]
    sorted_values = [values[i] for i in sorted_indices]

    plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
    # 创建图表
    plt.figure(figsize=(25, 15))
    sns.barplot(x=sorted_values, y=sorted_labels, palette="viridis")

    # 添加标题和标签
    plt.title('词频分析')
    plt.xlabel('出现次数')
    plt.ylabel('词语')

    # 保存图像
    plt.savefig(output_path, format='png', dpi=600)

    # 显示图表
    plt.show()

    print(f"图像已保存到: {output_path}")

'''
这个脚本支持对指定文件夹下所有txt转写文件的内容处理词频
'''
def read_txt_files_from_folder(folder_path):
    # 获取指定文件夹中的所有txt文件
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
    file_contents = {}
    
    # 读取每个txt文件的内容
    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        with open(file_path, 'r',encoding='gbk') as file:
            file_contents[txt_file] = file.read()
    
    return file_contents

# 使用
folder_path = 'D:\ziyan\\video\\test\\'  # 替换为转写文件夹路径
txt_file_contents = read_txt_files_from_folder(folder_path)
total_content=''
analysis_output_path='' # 替换为输出文件夹路径

for filename, content in txt_file_contents.items():
    print(f"文件名: {filename}")
    total_content+=content

output_path1=folder_path+"word_frequency_analysis.png"
output_path2=folder_path+"word_cloud.png"
word_count(text=total_content,output_path=output_path1)
generate_wordcloud(text_data=total_content,output_path=output_path2)