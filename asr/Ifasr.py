# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa


    def upload(self):
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        param_dict["speaker_number"] = "2"
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url =lfasr_host + api_upload+"?"+urllib.parse.urlencode(param_dict),
                                headers = {"Content-type":"application/json"},data=data)
        print("upload_url:",response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result


    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['resultType'] = "transfer,predict"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result['content']['orderInfo']['status']
            print("status=",status)
            if status == 4:
                break
            time.sleep(5)
        print("get_result resp:",result)
        return result

def process_lfasr(input_file_path, output_file_path):
    # 读取 JSON 文件
    with open(input_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 获取并解析 orderResult 字段中的 JSON 字符串
    order_result_str = data['content']['orderResult']
    order_result = json.loads(order_result_str)

    # 定义要替换的词列表
    unwanted_words = ['嗯', '啊', '哦', '呃','哈','呀','噢','嘛','呗','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    
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
                
    
    # 将处理后的结果保存到输出文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for sentence in processed_sentences:
            output_file.write(sentence + '\n')
    
    print(f"处理完成，结果已保存到 {output_file_path}")
    

def asrAPI_lfasr(audio_file_path,output_file_path):
    api =RequestApi(appid="1aeed0d3",
                     secret_key="220615c7ac2fd6bdaf37e2b482e4ad08",
                     upload_file_path=audio_file_path)

    result=api.get_result()
    # 指定文件路径
    file_path = output_file_path

    # 将JSON对象写入文件
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    print(f"JSON数据已成功保存到 {file_path}")

    return api




# 输入讯飞开放平台的appid，secret_key和待转写的文件路径
if __name__ == '__main__':
    api = RequestApi(appid="1aeed0d3",
                     secret_key="220615c7ac2fd6bdaf37e2b482e4ad08",
                     upload_file_path=r"audio\\test.wav")

    result=api.get_result()
    # 指定文件路径
    file_path = "data.json"

    # 将JSON对象写入文件
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    print(f"JSON数据已成功保存到 {file_path}")