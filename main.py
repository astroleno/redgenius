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
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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
STEP1_API_KEY = os.getenv('STEP1_API_KEY')
STEP1_BASE_URL = os.getenv('STEP1_BASE_URL')
STEP1_MODEL = os.getenv('STEP1_MODEL')

STEP2_API_KEY = os.getenv('STEP2_API_KEY')
STEP2_BASE_URL = os.getenv('STEP2_BASE_URL')
STEP2_MODEL = os.getenv('STEP2_MODEL')

# 检查环境变量
def check_env_vars():
    """检查环境变量是否正确配置"""
    logging.info("检查环境变量配置...")
    
    if not STEP1_API_KEY:
        logging.error("STEP1_API_KEY 未配置")
        return False
    if not STEP1_BASE_URL:
        logging.error("STEP1_BASE_URL 未配置")
        return False
    if not STEP1_MODEL:
        logging.error("STEP1_MODEL 未配置")
        return False
        
    if not STEP2_API_KEY:
        logging.error("STEP2_API_KEY 未配置")
        return False
    if not STEP2_BASE_URL:
        logging.error("STEP2_BASE_URL 未配置")
        return False
    if not STEP2_MODEL:
        logging.error("STEP2_MODEL 未配置")
        return False
    
    logging.info("环境变量配置检查通过")
    logging.info(f"STEP1_BASE_URL: {STEP1_BASE_URL}")
    logging.info(f"STEP1_MODEL: {STEP1_MODEL}")
    logging.info(f"STEP2_BASE_URL: {STEP2_BASE_URL}")
    logging.info(f"STEP2_MODEL: {STEP2_MODEL}")
    return True

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

# 清理和解析JSON内容的函数
def clean_and_parse_json(content):
    """
    清理大模型返回的内容并解析JSON，兼容对象和数组，优先直接json.loads
    """
    try:
        if not content or content.strip() == "":
            logging.error("API返回内容为空")
            return None
        content = content.strip()
        # 去除代码块包裹
        if content.startswith("```json"):
            content = content[7:].strip()
        if content.startswith("```"):
            content = content[3:].strip()
        content = content.strip()
        # 直接判断首字符
        if content.startswith("{") or content.startswith("["):
            result = json.loads(content)
        else:
            # 兜底：尝试提取第一个对象或数组
            match_obj = re.search(r'\{[\s\S]*\}', content)
            match_arr = re.search(r'\[[\s\S]*\]', content)
            if match_obj:
                result = json.loads(match_obj.group(0))
            elif match_arr:
                result = json.loads(match_arr.group(0))
            else:
                result = json.loads(content)
        return result
    except Exception as e:
        logging.error(f"JSON解析失败，原始内容：{content}")
        logging.error(f"错误信息：{e}")
        save_file("debug_failed_json.txt", content)
        raise

# 主流程
def main():
    logging.info('==== 自动化内容生成流程启动 ===')
    
    # 检查环境变量
    if not check_env_vars():
        logging.error("环境变量配置错误，程序终止")
        return
    
    # 1. 读取Prompt和用户文本
    prompt_path = 'test/prompt_0.md'
    user_text_path = 'test/test.md'
    prompt = read_file(prompt_path)
    user_text = read_file(user_text_path)
    if not prompt or not user_text:
        logging.error('Prompt或用户文本读取失败，流程终止')
        return

    # 2. 结构化内容生成（一步）
    try:
        openai.api_key = STEP1_API_KEY
        openai.base_url = STEP1_BASE_URL
        step1_prompt = prompt.split('# Step 2:')[0]
        full_input = step1_prompt + f"\n\n用户输入：\n{user_text}\n"
        logging.info('开始调用OpenAI STEP1_MODEL生成结构化内容...')
        response = openai.chat.completions.create(
            model=STEP1_MODEL,
            messages=[
                {"role": "system", "content": "你是一个顶级内容策划师，严格按照用户的Prompt和格式要求输出。"},
                {"role": "user", "content": full_input}
            ],
            temperature=0.7
        )
        result_content = response.choices[0].message.content
        logging.info(f"API调用成功，返回内容长度: {len(result_content) if result_content else 0}")
        logging.info(f"结构化内容原始返回：{result_content}")
        result = clean_and_parse_json(result_content)
        if result is None:
            logging.error("JSON解析失败，流程终止")
            return
        logging.info('结构化内容解析成功')
    except Exception as e:
        logging.error(f'结构化内容生成或解析失败: {e}')
        logging.error(f'错误类型: {type(e).__name__}')
        return

    # 3. 保存结构化内容
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join('outputs', timestamp)
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, 'output.json')
    save_file(json_path, json.dumps(result, ensure_ascii=False, indent=2))
    logging.info('结构化内容已保存')

    # 4. 第二步：用STEP2_MODEL生成HTML
    try:
        openai.api_key = STEP2_API_KEY
        openai.base_url = STEP2_BASE_URL
        step2_prompt = prompt.split('# Step 2:')[1]
        html_input = f"请根据以下结构化内容生成完整HTML：\n{json.dumps(result, ensure_ascii=False)}\n{step2_prompt}"
        logging.info('开始调用Gemini STEP2_MODEL生成HTML...')
        logging.info(f"HTML输入内容长度: {len(html_input)}")
        response2 = openai.chat.completions.create(
            model=STEP2_MODEL,
            messages=[
                {"role": "system", "content": "你是前端开发专家，严格按照用户的Prompt和格式要求输出。"},
                {"role": "user", "content": html_input}
            ],
            temperature=0.7
        )
        html_content = response2.choices[0].message.content.strip()
        logging.info('HTML生成成功')
        logging.info(f"HTML内容长度：{len(html_content)}")
    except Exception as e:
        logging.error(f'HTML生成失败: {e}')
        logging.error(f'错误类型: {type(e).__name__}')
        return

    # 5. 保存HTML
    html_path = os.path.join(output_dir, 'output.html')
    save_file(html_path, html_content)
    logging.info('HTML已保存')

    # 6. 渲染每个卡片HTML为独立PNG
    try:
        # 去除HTML代码块标记
        if html_content.startswith("```html"):
            html_content = html_content.replace("```html", "").replace("```", "").strip()
        
        html_cards = html_content.split("===CARD===")
        logging.info(f"分割得到 {len(html_cards)} 个HTML片段")
        
        # 自动补齐到5张卡片
        if len(html_cards) < 5:
            logging.warning(f"HTML卡片数量不足5，实际数量：{len(html_cards)}，自动补齐到5张")
            save_file(os.path.join(output_dir, 'debug_html_content.txt'), html_content)
            
            # 生成空白卡片模板
            blank_card_template = '''<html>
  <head>
    <meta charset="utf-8">
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body style="background:#111111;">
    <div class="card-container" id="card-{idx}" style="width:1125px;height:1500px;background:#111111;color:#FFFFFF;padding:40px;position:relative;font-family:Arial,sans-serif;display:flex;flex-direction:column;justify-content:center;align-items:center;">
      <div style="text-align:center;">
        <h2 style="font-size:48px;font-weight:bold;margin-bottom:20px;color:#ffa500;">空白卡片 {idx}</h2>
        <p style="font-size:24px;line-height:1.8;color:#FFFFFF;opacity:0.7;">此卡片内容待补充</p>
      </div>
      <div class="logo" style="position:absolute;bottom:24px;right:36px;opacity:0.5;font-size:1.2rem;color:#fff;">@造化自见</div>
    </div>
  </body>
</html>'''
            
            # 补齐空白卡片
            for i in range(len(html_cards), 5):
                blank_card = blank_card_template.format(idx=i+1)
                html_cards.append(blank_card)
                logging.info(f"已添加空白卡片 {i+1}")
        
        rendered_count = 0
        for idx, card_html in enumerate(html_cards, 1):
            card_html = card_html.strip()
            if not card_html:
                logging.warning(f'第{idx}张卡片内容为空，跳过')
                continue
            logging.info(f"处理第{idx}张卡片，内容长度：{len(card_html)}")
            try:
                hti = Html2Image()
                # Html2Image 2.0.7版本不支持save_path参数，默认保存到当前目录
                hti.screenshot(
                    html_str=card_html, 
                    save_as=f'image_{idx}.png', 
                    size=(1125, 1500)
                )
                # 移动文件到输出目录
                import shutil
                source_file = f'image_{idx}.png'
                target_file = os.path.join(output_dir, f'image_{idx}.png')
                if os.path.exists(source_file):
                    shutil.move(source_file, target_file)
                    rendered_count += 1
                    logging.info(f'卡片{idx}已渲染为PNG图片，路径：{target_file}')
                else:
                    logging.error(f'卡片{idx}渲染失败：文件未生成')
            except Exception as card_error:
                logging.error(f'卡片{idx}渲染失败: {card_error}')
                # 保存失败的HTML用于调试
                save_file(os.path.join(output_dir, f'failed_card_{idx}.html'), card_html)
        logging.info(f'成功渲染 {rendered_count} 张卡片为PNG图片')
    except Exception as e:
        logging.error(f'HTML转多张PNG失败: {e}')

    # 7. 保存文案和标签
    caption = result.get('caption', {})
    caption_body = caption.get('body', '')
    caption_closing = caption.get('closing', '')
    tags = result.get('tags', [])
    post_txt = f"caption.body: {caption_body}\ncaption.closing: {caption_closing}\ntags: {', '.join(tags)}\n"
    post_path = os.path.join(output_dir, 'post.txt')
    save_file(post_path, post_txt)
    logging.info('文案和标签已保存')

    logging.info('==== 流程执行完毕 ===')

if __name__ == '__main__':
    main()