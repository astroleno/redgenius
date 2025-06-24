# 直接删除或注释掉如下两行：
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7078'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7078'
import openai

openai.api_key = 'sk-rssyP1iSRHn1JStXOn46u21ZC9fMpmuNtaqEmoxehMTWWiAk'
openai.base_url = 'https://yunwu.ai/v1/'

response = openai.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role": "system", "content": "你是一个测试助手。"},
        {"role": "user", "content": "你好，请用一句话介绍你自己。"}
    ]
)
print(response.choices[0].message.content)