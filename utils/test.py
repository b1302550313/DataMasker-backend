# 初始化自定义LLM
from utils.chat import CustomHTTPLLM
from  utils.readDoc import read
from  utils.splitDoc import split
url = "http://172.16.108.178:11451/qwen"
custom_llm = CustomHTTPLLM(url=url)
message = [
    {"role":"system","content":"输出用户提供的内容中,是否包含以下内容:公司名称、组织名称、具体日期、产品名称、人名、地名。"},
    {"role":"system","content":"如果存在上述内容，请将所有的具体内容直接输出，按换行符隔开"}
]
# 调用LLM进行推理
response = custom_llm("根據Canalys數據，本季度我們全球智能手機出貨量排名穩居前三 ",message = message)
print(response)
原文:"“ 宙 斯 盾 ” 舰 上 用 于 弹 道 导 弹 防 御 的 拦 截 导 弹 包 括 “ 标 准 ” - 3 ( S M - 3 ) ? “ 标 准 ” - 2 ( S M - 2 ) 以 及 “ 标 准 ” - 6 ( S M - 6 ) ? "
"弹 道 导 弹 "
"“标 准 ” - 3 ( S M - 3 ) "
"“ 标 准 ” - 2 ( S M - 2 )"
#
# text_path = "D:/language python/GeneralNERDataMasking/datasets/小米财报2024_formal.txt"
# document = read(text_path)
# splitres = split(document)
# # 查看分割后的文档
# for i, doc in enumerate(splitres):
#     print(f"Chunk {i + 1}:")
#     print(doc.page_content)  # 打印文本内容
#     print(doc.metadata)  # 打印元数据
#     print("-" * 50)
# # print(splitres)
