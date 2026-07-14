# pdf-trans2md

将 PDF 翻译为中文 Markdown 的 Codex Skill。默认通过**当前 AI 模型的多模态视觉能力**读取页面图像，重点处理双栏期刊论文、跨栏标题、图表、公式、图注、脚注和跨页段落。

## 核心原则

- 默认 `vision`：直接理解 PDF 页面或渲染后的页面图像。
- 页面渲染只生成图像，不提取文本。
- 不绑定任何特定模型。
- 不因 PDF 存在文本层而自动使用 `pypdf`。
- 只有用户明确要求文本提取时，才使用 `text` 后端。
- `bilingual` 输出始终先原文，再以 Markdown 引用块给出中文译文。

## 默认工作流

```text
PDF → 页面图像 → AI 视觉版面分析 → 双栏阅读顺序 → 翻译 → Markdown → 逐页复核
```

对标准双栏页面，通常按照：

1. 顶部跨栏内容；
2. 左栏从上到下；
3. 右栏从上到下；
4. 底部跨栏内容；
5. 脚注。

实际顺序必须以页面视觉布局为准。

## 使用示例

```text
/pdf-trans2md paper.pdf
/pdf-trans2md paper.pdf --pages 1-8
/pdf-trans2md paper.pdf --mode bilingual
/pdf-trans2md paper.pdf --layout double-column --output paper_zh.md
```

显式文本提取模式：

```text
/pdf-trans2md paper.pdf --input-mode text
/pdf-trans2md paper.pdf --text-extract
```

没有明确的文本提取意图时，不得调用文本后端。

## 双语输出格式

```markdown
The proposed method improves multimodal representation learning.

> **译文：**
> 所提出的方法改进了多模态表征学习。
```

标题：

```markdown
## 3. Experimental Results

> **译文标题：3. 实验结果**
```

旧版“中文在前、原文在引用块”的格式已废弃。

## 辅助脚本

### 页面渲染：默认视觉模式

```text
python scripts/render_pdf_pages.py paper.pdf --pages 1-5 --dpi 240
```

功能：

- 将 PDF 页面渲染为 PNG/JPEG；
- 支持任意页码范围；
- 支持 PyMuPDF 或 Poppler；
- 可在查看完整页后生成左栏或右栏裁剪；
- 生成 `manifest.json`；
- **不提取 PDF 文本**。

双栏裁剪示例：

```text
python scripts/render_pdf_pages.py paper.pdf --pages 3 --crop left
python scripts/render_pdf_pages.py paper.pdf --pages 3 --crop right
```

必须先查看完整页，再决定是否裁栏；`--crop left|right` 需要 PyMuPDF 后端。

### 文本提取：仅显式回退

```text
python scripts/extract_pdf_text.py paper.pdf --input-mode text --pages 1-5
```

该脚本：

- 强制要求 `--input-mode text`；
- 使用 `pypdf` 提取文本；
- 输出结构化 JSON 和翻译指南；
- 不负责实际翻译；
- 不能保证双栏、公式、表格或图注的布局顺序。

## 依赖

视觉渲染后端任选其一：

```text
python -m pip install pymupdf
```

或安装 Poppler，使以下命令可用：

```text
pdftoppm
pdfinfo
```

显式文本模式才需要：

```text
python -m pip install pypdf
```

## 适用场景

- 双栏或多栏期刊论文；
- 扫描 PDF；
- 图表、公式和图注密集文档；
- 技术手册、白皮书和电子书；
- 中文或中英对照 Markdown 阅读稿。

## 限制与处理

- 页面模糊：提高 DPI 或局部裁剪。
- 复杂合并单元格：可转为 HTML 表格或结构化列表。
- 公式字符不确定：标记 `[公式符号待核对]`，不得猜测。
- 加密 PDF：需要密码或解密版本。
- 视觉路径不可用：报告缺失依赖；未经用户同意，不得静默回退到文本提取。

## 仓库结构

```text
pdf-trans2md/
├── SKILL.md
├── README.md
├── REFACTORING_REPORT.md
├── scripts/
│   ├── render_pdf_pages.py
│   └── extract_pdf_text.py
├── evals/
│   └── evals.json
└── test-materials/
```

## 版本

- v3.0：multimodal vision-first；双栏论文优先；双语格式改为原文在前、中文引用块在后。
- v2.x：旧版 Python-first / 特定模型描述，已停止作为默认架构。
