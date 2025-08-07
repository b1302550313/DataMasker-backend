# from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 初始化文本分割器
# 初始化文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=20,
    chunk_overlap=4,
    separators=["\n\n", "\n", "。", "!","！","，"]  # 多种分隔符
)

def split(documents):
    return text_splitter.split_documents(documents)
# 分割文档
# split_documents = text_splitter.split_documents(documents)