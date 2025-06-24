# 项目目标
我需要创建一个自动化工作流脚本，该脚本能读取一个本地的文本文件（txt/md），调用Google AI Studio下的Gemini大语言模型（LLM）API进行内容拆解和bentobox风格HTML生成，然后使用html2image库将HTML渲染为PNG图片，并最终将图片和配套文案输出到本地文件夹。

# 核心功能 (PRD)
1.  **文件读取:** 脚本需要能读取指定路径下的 `.txt` 或 `.md` 文件内容。
2.  **LLM交互:**
    * 调用Google AI Studio下的Gemini大模型API。
    * 使用一个预设的"主控Prompt"，将文件内容发送给LLM。
    * LLM返回一个结构化的JSON对象，其中包含：小红书文案 (`caption`)、标签 (`tags`) 和bentobox风格的HTML (`html`)。
3.  **HTML渲染:**
    * 解析LLM返回的JSON，提取出HTML内容。
    * 使用html2image库将HTML渲染为PNG图片。
4.  **结果输出:**
    * 在项目根目录创建一个 `outputs` 文件夹。
    * 为每一次运行创建一个独立的子文件夹（例如以时间戳命名）。
    * 在该子文件夹中保存导出的 `image.png`、`output.html` 和一个包含文案、标签的 `post.txt` 文件。

# 技术栈
- **语言:** Python
- **核心库:**
  - `requests` (用于API调用)
  - `google-generativeai` (用于LLM交互)
  - `python-dotenv` (用于管理API密钥)
  - `html2image` (用于HTML转PNG)
- **API:**
  - Google AI Studio Gemini API

# 期望的文件结构
- `main.py` (主执行脚本)
- `config.py` (存放配置，如API Key)
- `.env` (存放API密钥和Access Token)
- `.gitignore`
- `requirements.txt`
- `prompts/master_prompt.txt` (存放我们的主控Prompt)
- `inputs/` (存放输入的源文件)
- `outputs/` (存放最终结果)
- `test/` (测试用例和Prompt)