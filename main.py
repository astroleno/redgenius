# 直接删除或注释掉如下两行：
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7078'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7078'
import os
import openai
import json
import logging
import re
from datetime import datetime
from html2image import Html2Image
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 加载环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-rssyP1iSRHn1JStXOn46u21ZC9fMpmuNtaqEmoxehMTWWiAk')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://yunwu.ai/v1/')

openai.api_key = OPENAI_API_KEY
openai.base_url = OPENAI_BASE_URL

# 读取文件内容的工具函数
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f'读取文件失败: {filepath}，错误信息: {e}')
        return None

def save_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        logging.error(f'保存文件失败: {filepath}，错误信息: {e}')

# 主流程
def main():
    logging.info('==== 自动化内容生成流程启动 ===')
    # 1. 读取Prompt和用户文本
    prompt_path = 'test/prompt_0.md'
    user_text_path = 'test/test.md'
    prompt = read_file(prompt_path)
    user_text = read_file(user_text_path)
    if not prompt or not user_text:
        logging.error('Prompt或用户文本读取失败，流程终止')
        return

    # 2. 第一步：生成结构化JSON
    try:
        step1_prompt = prompt.split('# Step 2:')[0]
        full_input = step1_prompt + f"\n\n用户输入：\n{user_text}\n"
        logging.info('开始调用Yunwu大模型API生成结构化内容...')
        response = openai.chat.completions.create(
            model="gemini-2.5-pro",
            messages=[
                {"role": "system", "content": "你是一个顶级内容策划师，严格按照用户的Prompt和格式要求输出。"},
                {"role": "user", "content": full_input}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        result_content = response.choices[0].message.content
        logging.info(f"结构化内容原始返回：{result_content}")
        match = re.search(r'\{[\s\S]*\}', result_content)
        if match:
            json_str = match.group(0)
        else:
            json_str = result_content.strip()
        result = json.loads(json_str)
        logging.info('结构化内容解析成功')
    except Exception as e:
        logging.error(f'结构化内容生成或解析失败: {e}')
        return

    # 3. 保存结构化内容
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join('outputs', timestamp)
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, 'output.json')
    save_file(json_path, json.dumps(result, ensure_ascii=False, indent=2))
    logging.info('结构化内容已保存')

    # 4. 第二步：生成HTML
    try:
        step2_prompt = prompt.split('# Step 2:')[1]
        html_input = f"请根据以下结构化内容生成完整HTML：\n{json.dumps(result, ensure_ascii=False)}\n{step2_prompt}"
        logging.info('开始调用Yunwu大模型API生成HTML...')
        response2 = openai.chat.completions.create(
            model="gemini-2.5-pro",
            messages=[
                {"role": "system", "content": "你是前端开发专家，严格按照用户的Prompt和格式要求输出。"},
                {"role": "user", "content": html_input}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        html_content = response2.choices[0].message.content.strip()
        logging.info('HTML生成成功')
    except Exception as e:
        logging.error(f'HTML生成失败: {e}')
        return

    # 5. 保存HTML
    html_path = os.path.join(output_dir, 'output.html')
    save_file(html_path, html_content)
    logging.info('HTML已保存')

    # 6. 渲染HTML为多张PNG
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        card_divs = soup.find_all("div", class_="card-container")
        for idx, card in enumerate(card_divs, 1):
            # 包裹成完整HTML
            single_html = f"""
            <html>
            <head>
            <meta charset="utf-8">
            <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body style="background:#111;">
            {str(card)}
            </body>
            </html>
            """
            image_path = os.path.join(output_dir, f'image_{idx}.png')
            hti = Html2Image()
            hti.screenshot(html_str=single_html, save_as=f'image_{idx}.png', size=(1125, 1500), output_path=output_dir)
        logging.info('所有卡片已渲染为PNG图片')
    except Exception as e:
        logging.error(f'HTML转多张PNG失败: {e}')

    # 7. 保存文案和标签
    caption = result.get('caption', '')
    tags = result.get('tags', [])
    post_txt = f"caption: {caption}\ntags: {', '.join(tags)}\n"
    post_path = os.path.join(output_dir, 'post.txt')
    save_file(post_path, post_txt)
    logging.info('文案和标签已保存')

    logging.info('==== 流程执行完毕 ===')

if __name__ == '__main__':
    main()