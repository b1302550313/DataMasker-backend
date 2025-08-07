import os.path

from langchain_community.document_loaders import TextLoader,Docx2txtLoader,PyPDFLoader
# from spacy.cli.apply import path_help

# 加载文本文件
# loader = TextLoader("path/to/your/file.txt")
# documents = loader.load()

def read(path:str):
    expand_name = os.path.splitext(path)[1]
    # loader = TextLoader
    if expand_name==".txt":
        #loader = TextLoader(path,encoding="utf-8")
        #documents = loader.load()
        #return documents
        return readtxt(path)
    elif expand_name==".pdf":
        return readPDF(path)
    elif expand_name==".docx":
        return readDocx(path)

def readtxt(path:str):
    loader =TextLoader(path,encoding="utf-8")
    documents = loader.load()
    return documents

def readPDF(path:str):
    loader = PyPDFLoader(path)
    documents = loader.load()
    print(documents)
    return documents

def readDocx(path:str):
    loader = Docx2txtLoader(path)
    documents = loader.load()
    print(documents)
    return documents
