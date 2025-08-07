"""
langchain tools 的实现
"""
import re
import hanlp
# from langchain.chains import ConversationChain
# from langchain.chains.llm import LLMChain

import config.Config
from config.Config import LLM as llm
from utils.prompt import selfVerifyTemplate, selfVerifyPrompt, sentenceFilterPrompt, wordCutPrompt, \
    sensitiveInfoIdentifyPrompt, wordReplacePrompt, identity_Prompt, wordCutPrompt1, sensitiveInfoIdentifyPrompt1, \
    sensitiveIdentifyPrompt

from langchain.memory import ConversationSummaryMemory,ConversationBufferMemory,ConversationEntityMemory

tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)


bufferMemory = ConversationBufferMemory()
sensativeMemory = ConversationBufferMemory()
# 自我校验工具
self_verify_chain = selfVerifyPrompt| llm
def selfVerify(history):
    # self_verify_chain = LLMChain(llm = llm, prompt = selfVerifyPrompt)
    result = self_verify_chain.invoke(history)
    return result.strip()


# 敏感词过滤工具
# 使用 RunnableSequence 替代 LLMChain
sentence_filter_chain = sentenceFilterPrompt | llm
# sentence_filter_chain = ConversationChain(llm,memory = bufferMemory)
def sensitive_sentence_filter(sentence):
    bufferMemory.clear()
    inputs = {
        "实体类型1": config.Config.entities,
        "实体类型2": config.Config.entities,
        "实体类型3": config.Config.entities,
        "实体类型4": config.Config.entities,
        "userInput": sentence
    }
    cur_prompt = sentenceFilterPrompt.format(**inputs)
    result = sentence_filter_chain.invoke(inputs)
    # 保存对话记录到内存
    bufferMemory.chat_memory.add_user_message(cur_prompt)
    bufferMemory.chat_memory.add_ai_message(result)
    return result.strip()

def getResultIdentify(sentence):
    pattern = r'##(.*?)##'
    result = re.findall(pattern,sentence)
    if len(result)>0:
        return result[0]
    return ""

sentenceChain_No_wordCut = identity_Prompt | llm
def identity_no_cut(sentence,type):
    inputs = {
        "userInput":sentence,
        "type":type,
    }
    # identity_prompt = identity_Prompt.format()
    result = sentenceChain_No_wordCut.invoke(inputs)
    return getResultIdentify(result)

# 切词工具
word_cut_chain = wordCutPrompt | llm
# word_cut_chain = wordCutPrompt1 | llm
def word_cut(sentence):
    # word_cut_chain = LLMChain(llm = llm, prompt = wordCutPrompt)
    inputs = {
        "userInput" : sentence,
        "切词示例" : config.Config.word_cut_demo
    }
    result = word_cut_chain.invoke(
        inputs
    )
    return result.strip()

def word_cut_hanLP(sentence):
    ret = tok(sentence)
    return ret

def word_mask(word):
    size = len(word)
    if size <=2:
        return "*"*size
    else:
        return "*"*(size-2)+word[size-2:]

# ["文档类型","敏感信息种类","识别示例","sentence","userInput"],

# 敏感词识别
sensitive_info_chain = sensitiveInfoIdentifyPrompt | llm
def sensitive_info_identify(sentence, word,history):
    # bufferMemory.clear()
    inputs = {
        "history":history,
        "word" : word,
        "sentence" : sentence,
        "sensitive_type":config.Config.entities,
    }
    result = sensitive_info_chain.invoke(
        inputs
    )


    # cur_prompt = sensitiveInfoIdentifyPrompt.format(**inputs)
    # sensativeMemory.chat_memory.add_user_message(cur_prompt)
    # sensativeMemory.chat_memory.add_ai_message(result)
    # print(sensativeMemory.load_memory_variables({}))
    # print(cur_prompt)
    return result.strip()


sensitive_info_chain1 = sensitiveInfoIdentifyPrompt1 | llm
def sensitive_info_identify1(sentence, word,history):
    # bufferMemory.clear()
    inputs = {
        "word" : word,
        "sensitive_type":config.Config.entities,
    }
    result = sensitive_info_chain1.invoke(
        inputs
    )
    return result.strip()

sensitive_identity_chain = sensitiveIdentifyPrompt| llm
def sensitive_identify(sentence, word):
    # bufferMemory.clear()
    inputs = {
        "sentence":sentence,
        "docType":config.Config.docType,
        "demos":config.Config.demos,
        "word" : word,
        "entity_type":config.Config.entities,
    }
    result = sensitive_identity_chain.invoke(
        inputs
    )
    return result.strip()

# 敏感词替换工具
word_replace_chain = wordReplacePrompt | llm
def word_replace(sentence,word):
    # word_replace_chain = LLMChain(llm = llm,prompt = wordCutPrompt)
    inputs = {
        "sentence" : sentence,
        "word" : word
    }
    result = word_replace_chain.invoke(
        inputs
    )
    return result.strip()


