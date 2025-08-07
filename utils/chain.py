

import os
import sys
from datetime import datetime
import os.path
import re
import time
from os.path import basename

# 获取当前文件(final.py)的绝对路径，并逐级向上直到找到项目的根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)  # 因为final.py在utils下，所以只需要一级
sys.path.append(root_dir)


import tqdm
from IPython.core.compilerop import code_name

import utils.tools as tools
import ast

from utils import readDoc
from utils.splitDoc import split
from utils.tools import selfVerify, word_replace
import config
# 维护一个全局敏感词字典
sensative_word_dic = {}
replace_word_dic = {}
def clear_dicts():
    global sensative_word_dic, replace_word_dic
    sensative_word_dic = {}
    replace_word_dic = {}

def convert_to_list(output_str):
    """
    从模型输出中提取切词结果，并将其转换为一个列表。

    参数:
        output_str (str): 模型输出的字符串，格式为 "##...##"，中间用 "#" 分隔，但可能包含其他内容。

    返回:
        list: 包含分割结果的列表。
    """
    # 使用正则表达式去除开头和结尾的 "##" 及其之间的任意字符
    match = re.search(r'##(.*?)##', output_str)
    if not match:
        raise ValueError("输入字符串不符合预期格式，未找到 '##...##'")

    # 提取中间部分
    trimmed_str = match.group(1)

    # 使用 "#" 分割字符串
    segments = trimmed_str.split('#')

    # 去除可能存在的空字符串（如果存在连续的 "#"）
    segments = [segment.strip() for segment in segments if segment.strip()]

    return segments

def convert_to_list1(s):
    pattern = "[*]"
    if s[0]!="[":
        try:
            s = "["+re.match(pattern,s)[0]+']'
        except:
            pass
    try:
        result = ast.literal_eval(s)
        return result
    except (SyntaxError, ValueError):
        return []

fastFilterWord = [".","。",",","，","！","!","“","”","{","}","(",")","（","）","{","}"]

def getResult(text):
    pattern = r'##(.*?)##'
    # 使用 findall 方法查找所有匹配项
    matches = re.findall(pattern, text)
    if len(matches)==0:
        return "No"
    return matches[0]

def identify(sentence):
    # 使用gptner类似的方法
    filter_result = tools.sensitive_sentence_filter(sentence)
    history = tools.bufferMemory.load_memory_variables({})
    self_result = tools.selfVerify(history)
    # self_result = getResult(self_result)
    positive = 0
    negative = 0
    while "No" in self_result:
        if negative + positive >= 5:
            if negative > positive:
                return
            else:
                filter_result = "##Yes##"
                break
        filter_result = tools.sensitive_sentence_filter(sentence)
        history = tools.bufferMemory.load_memory_variables({})
        self_result = tools.selfVerify(history)
        if "No" in filter_result:
            negative += 1
        else:
            positive += 1
    filter_result = getResult(filter_result)
    # 通过校验
    if "No" in filter_result:
        return sentence
    # 实体识别,使用另一种方式
    for type in config.Config.types:
        result = tools.identity_no_cut(sentence,type)
        if result!="":
            sensative_word_dic[result]= sentence

def IdentifyChain(sentence,word_cut = 1):
    # 使用wordcut方法
    filter_result = tools.sensitive_sentence_filter(sentence)
    history = tools.bufferMemory.load_memory_variables({})
    self_result = tools.selfVerify(history)
    # self_result = getResult(self_result)
    positive = 0
    negative = 0
    while  "No" in self_result  :
        if negative+positive>=5:
            if negative>positive:
                return
            else:
                filter_result = "##Yes##"
                break
        filter_result = tools.sensitive_sentence_filter(sentence)
        history = tools.bufferMemory.load_memory_variables({})
        self_result = tools.selfVerify(history)
        if "No" in filter_result:
            negative+=1
        else:
            positive+=1
    filter_result = getResult(filter_result)
    # 通过校验
    if "No" in filter_result:
        return sentence

    # 切词LLM
    if word_cut == 1:
        words_cut = tools.word_cut(sentence)
        words = convert_to_list1(words_cut)
    else:
        words = tools.word_cut_hanLP(sentence)
    t = 0
    while len(words)==0 and t<5:
        words_cut = tools.word_cut(sentence)
        words = convert_to_list(words_cut)
        t+=1
    if t>=5:
        print(sentence)
        return sentence
    # 敏感词识别
    for word in words:
        if word in sensative_word_dic.keys() or word in fastFilterWord:
            continue

        # sensitive_result = getResult(sensitive_result)
        # sensitive_result = tools.sensitive_info_identify(sentence, word,history)

        # sensitive_result = tools.sensitive_info_identify1(sentence, word, history)
        sensitive_result = tools.sensitive_identify(sentence,word)
        if "Yes" in sensitive_result:
            cur_prompt = "human: 在" + sentence + "中,\n   " + word + "\n   这部分是" + config.Config.entities + "中的某一种吗?\n"+"AI: "+sensitive_result
            self_result = selfVerify(cur_prompt)
            if "No" in self_result:
                sensitive_result = "No"
        else:
            cur_prompt = "human: 在" + sentence + "中,\n   " + word + "\n   这部分是" + config.Config.entities + "中的某一种吗?\n"+"AI: "+sensitive_result
            self_result = selfVerify(cur_prompt)
            if "No" in self_result:
                sensitive_result = "Yes"
        if "Yes" in sensitive_result:
            sensative_word_dic[word] = sentence

def Replace(patten=2):
    if patten==1:
        # 全匿名
        ReplaceChain_1()
    elif patten == 3:
        # 从示例中学习
        ReplaceChain_3()

    else:
        ReplaceChain()
def ReplaceChain():
    for word,sentence  in tqdm.tqdm(sensative_word_dic.items()):
        result = word_replace(sentence,word)
        result = getResult(result)
        t=0
        while result=="No" and t<5 :
            result = word_replace(sentence, word)
            result = getResult(result)
            t+=1
        replace_word_dic[word] = result
        # if t>=5:
        #     result = word_replace(sentence, word)
        #     result = getResult(result)
        #     replace_word_dic[word] = result

def ReplaceChain_1():
    for word,sentence  in tqdm.tqdm(sensative_word_dic.items()):
        slen = 1+len(word)//5
        result =  word[:slen]+"*"*(len(word)-slen)
        replace_word_dic[word] = result
def ReplaceChain_3():
    #根据示例来学习
    # todo
    ReplaceChain()


def final(path = config.Config.docPath,entity_type = config.Config.entities,demos=config.Config.demos,patten = 2):
    print(config.Config.docPath)
    config.Config.docPath = path
    config.Config.entities = entity_type
    config.demos = demos
    document = readDoc.read(config.Config.docPath)
    print(document)
    splitDoc = split(document)
    for doc in tqdm.tqdm(splitDoc):
        sentence = doc.page_content
        #print("sentence:",sentence)
        try:
            IdentifyChain(sentence,patten)
            # identify(sentence)
        except:
            IdentifyChain(sentence,patten)
            # identify(sentence)
    print(sensative_word_dic)
    Replace(patten)
    for doc in splitDoc:
        contains = []
        sentence = doc.page_content
        for word ,replace_word in replace_word_dic.items():
            if word in sentence:
                contains.append(word)
        for con in contains:
            doc.page_content = doc.page_content.replace(con,replace_word_dic[con])
    # 合并分割后的文本
    merged_text = ""
    for doc in splitDoc:
        merged_text += doc.page_content
    # 将合并后的文本写入文件
    print(replace_word_dic)
    
    basename = os.path.basename(config.Config.docPath)
    # 获取当前时间戳，并格式化为字符串（例如：20231030_153045）
    time_sample = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 拼接文件路径
    file_path = os.path.join(config.Config.outputPath, f"{time_sample}_{basename}")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(merged_text)

    print(f"文本已成功写入 {file_path}")
    # 把敏感词返回给前端
    word_dics = replace_word_dic
    clear_dicts()
    return file_path,word_dics

if __name__ == '__main__':
    # sentence = "根據Canalys數據，本季度我們全球智能手機出貨量排名穩居前三"
    # IdentifyChain(sentence)
    # print(sensative_word_dic)
    # print(sensative_word_dic.keys())
    # s = ' ["，","小米集团","已","在全球","獲得","超","3.9萬件","專利"]'
    # words = convert_to_list(s)
    # while len(words) == 0:
    #     print(convert_to_list(s))
    #     print(type(words))
    final()
