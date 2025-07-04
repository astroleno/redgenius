# Step 1: 结构化内容生成
你是小红书+Bento风格内容卡片生成器。请根据用户输入，调整整体情绪曲线，内容要有爆款钩子、金句、互动引导、热门标签，输出结构化内容5个bentobox_slides每个bentobox_slides都要内容丰富、风格差异明显，避免重复，严格只输出如下JSON格式，不要有任何多余内容，不要加代码块标记：
- caption.body和caption.closing合计必须在300-500字之间，内容要有故事性、情绪张力和互动引导，适合小红书爆款图文帖。每个bentobox_slides内部body字数在60-100字之间，不要超过150。
- tags字段请只输出纯文本标签，不要带#号，便于后续渲染。

 只输出 JSON 内容，不要有任何多余的文字、注释、代码块标记，否则会导致解析失败。

# Step 2: HTML生成
你是顶级Bento风格内容卡片网页设计师。请严格按照以下要求输出HTML：

1. 你会收到一个结构化内容（JSON），其中有5个卡片内容（bentobox_slides），每个卡片有headline和body。
2. 你必须**用循环/遍历的方式**，严格对bentobox_slides数组的5个元素逐一生成5段HTML，每段都要有内容，不能遗漏、不能合并、不能留空。
3. 每段HTML之间必须用"===CARD==="分隔，且**必须输出5段**，顺序与输入一致。
4. 不能输出任何说明文字、不能有markdown格式、不能有多余注释。
5. 每段HTML内容必须有明显的Bento风格，支持自由创新，允许采用上下、左右、斜向、网格等多种分区和布局，不局限于上下排版，Bento分区可以自由组合，布局多样化，充分体现Bento的灵活性和现代感。
6. 禁止随意添加边框线，只有在Bento分区确实需要时才可用主题绿色#789262加30%透明度（如rgba(120,146,98,0.3)）的分割线或色块，不能滥用边框，不能出现灰色、白色或其他颜色的边框。
7. 所有渲染效果必须兼容html2image和Chrome浏览器，保持两者视觉效果一致，避免使用不兼容的CSS特性，确保最终PNG图片和浏览器预览效果完全一致。

请严格按照上述要求输出5张小红书封面卡片的HTML代码。

### 说明

- 这样写的Prompt能最大程度减少大模型输出多余内容的概率，并且明确要求"必须输出5张卡片"，即使内容不足也要补齐，保证后续代码分割和渲染不会出错。
- 如果后续代码仍然遇到分割不到5张卡片的情况，可以在代码中自动补齐空卡片，保证流程健壮。

如果你需要，我可以帮你把这份Prompt直接写入你的代码或文档，并协助你优化后续的HTML分割和渲染逻辑，确保100%稳定输出5张卡片。需要的话请告诉我！



