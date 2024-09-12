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
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','，','。',"?",'你','我','\n'
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
    mask_image = imageio.imread("D:\ziyan\store_video_analysis\\asr\ziyan_logo.png")
    # 清除当前画布
    plt.clf()
    wordcloud = WordCloud(mask=mask_image,font_path=font,width=800, height=400, random_state=0, max_font_size=70, background_color='white',scale=8,color_func=red_purple_color_func).fit_words(counts)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(output_path,dpi=600)  # 保存图片为PNG格式
    plt.show()

def word_count(text,output_path="D:/ziyan/store_video_analysis/temp/word_frequency_analysis.png",unwanted_words = [
    '谢','好','1','2','3','4','5','6','7','8','9','0','的','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','，','。',"?",'你','我'
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

def process_json(input_file_path, output_file_path,unwanted_words = [
    '谢','好','1','2','3','4','5','6','7','8','9','0','的','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','，','。',"?",'你','我',
    ]):
    # 读取 JSON 文件
    with open(input_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 获取并解析 orderResult 字段中的 JSON 字符串
    order_result_str = data['content']['orderResult']
    order_result = json.loads(order_result_str)
    
    # 存储处理后的语句
    processed_sentences = []
    
    # 提取并处理语音转写内容
    for item in order_result['lattice']:
        # 解析每个 json_1best 字段
        transcribed_data = json.loads(item['json_1best'])
        
        # 提取每个语句中的内容，并替换不想要的语气词
        for rt in transcribed_data['st']['rt']:
            sentence = ''.join([cw['w'] for ws in rt['ws'] for cw in ws['cw']])
            
            # 批量替换语气词为空字符串
            for word in unwanted_words:
                sentence = sentence.replace(word, '')
            
            # 如果句子不为空，则添加到结果列表中
            if sentence:
                processed_sentences.append(sentence)
                print(sentence)
    
    # 将处理后的结果保存到输出文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for sentence in processed_sentences:
            output_file.write(sentence + '\n')
    
    print(f"处理完成，结果已保存到 {output_file_path}")

if __name__ == '__main__':
    # 无关词列表
    unwanted_words = [
    '谢','好','1','2','3','4','5','6','7','8','9','0','的','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','，','。',"?",'你','我'
    ]
    # 额外关键字列表

    # 处理测试的星火api返回数据，产生文本文件
    process_json(unwanted_words=unwanted_words,input_file_path='data.json', output_file_path='D:\ziyan\store_video_analysis\\asr\show.txt')
    # 对文本文件进行词频分析，词云可视化
    with open('show.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    word_count(unwanted_words=unwanted_words,content=content)
    generate_wordcloud(unwanted_words=unwanted_words,content=content)

