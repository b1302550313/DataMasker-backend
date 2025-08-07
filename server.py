import json
import time
import ollama
from flask import  Flask,request,jsonify
app = Flask(__name__)
app.config['JSON_AS_ASCII']=False


test_data = [{'role': 'user', 'content': 'Why is the sky blue?'}]
#responce = ollama.chat(
#model='gemma:7b',
#        messages=test_data,
#)
#print(responce['message']['content'])
#print(type(responce))
#print(type(responce['message']['content']))
# stream = ollama.chat(
#     model='llama2',
#     messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
#     stream=True,
# )
#
# for chunk in stream:
#   print(chunk['message']['content'], end='', flush=True)

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "/Users/l/Desktop/wangshaojiang/QWen2.5_14B"
#model_name = "/data/wangshaojiang/QWen2.5_14B"
#model_name = "/data/wangshaojiang/QWen2.5_32B"
#model_name = "/data/wangshaojiang/QWen3_8B"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

#def chat(messages):
#    stream = ollama.chat(
#        model='gemma:7b',
#        messages=messages,
#    )
#    # for chunk in stream:
#    #     print(chunk['message']['content'])
#    return stream

def chatQWen3(message,time=5):
    if time<=0:
        print("retry 5 times but get no response")
        return "empty response error"
    messages = message["messages"]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=2048
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    if response==None:
        print("response is none,try again")
        chatQWen(message,time-1)

    print(response)
    print("\n\n\n333======================================================================================================================>")
    return response

def chatQWen(message,time=5):
    if time<=0:
        print("retry 5 times but get no response")
        return "empty response error"
    messages = message["messages"]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=2048
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    if response==None:
        print("response is none,try again")
        chatQWen(message,time-1)
        
    print(response)
    print("\n\n\n======================================================================================================================>")
    return response
TIMEOUT=300

@app.route("/qwen",methods=['GET','POST'])
def get_frame():
        if request.method == 'POST':
            global res
            data = request.get_data().decode('utf-8')
            data = json.loads(data)
            print(data)
            print(type(data))
            result = chatQWen(data)
            # result = '收到测试命令'
            # print(result)
            t = time.time()
            while time.time() - t <= TIMEOUT:
                    res = [{'content':result}]
                    break
            # with open('./result/'+imgname.split('.')[0] + ".json", "w") as f:
            # json.dump(res, f, ensure_ascii=False,indent=4)
            return jsonify({'res': res})
        return jsonify({'res': 'get'})

if __name__=="__main__":
    # app.run('127.0.0.1',port=11414)
    # app.run('172.16.108.178',port=11451)
    # app.run("127.0.0.1",port=11451)
    app.run("0.0.0.0",port=11451)


