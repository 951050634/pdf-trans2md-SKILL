# PDF 翻译为 Markdown Skill

将 PDF 文档（全部或部分）翻译为中文 Markdown 格式的 Claude Code skill。

## 安装

将此 skill 目录放置在 `~/.claude/skills/pdf-trans2md/` 下。

## 快速开始

```
/pdf-trans2md C:\Users\Admin\Desktop\document.pdf
```

## 功能特性

- ✅ 支持整个PDF翻译
- ✅ 支持指定页码范围（`--pages 16-32`）
- ✅ 支持多页码范围（`--pages 1-10,20-30`）
- ✅ 支持章节选择（`--chapter 5`）
- ✅ **支持两种翻译模式**：
  - `zh`: 仅输出中文（默认）
  - `bilingual`: 中英文对照，原文用引用块标记
- ✅ 保留代码示例和格式
- ✅ 自动识别章节结构
- ✅ 生成目录（TOC）
- ✅ 自定义输出标题和路径

## 使用示例

### 基本翻译

```bash
# 翻译整个PDF
/pdf-trans2md document.pdf

# 翻译特定页码范围
/pdf-trans2md document.pdf --pages 16-32

# 指定输出文件
/pdf-trans2md document.pdf --output output.md

# 中英文对照模式
/pdf-trans2md document.pdf --mode bilingual
```

### 高级用法

```bash
# 翻译多个部分
/pdf-trans2md manual.pdf --pages 1-5,100-120

# 翻译特定章节
/pdf-trans2md book.pdf --chapter 5 --title "第五章：核心概念"

# 禁用目录生成
/pdf-trans2md doc.pdf --no-toc

# 中英文对照模式（适用于学习和对照）
/pdf-trans2md guide.pdf --mode bilingual --pages 1-20
```

## 技术实现

### 依赖

- Python 3.8+
- pypdf 库：`pip install pypdf`

### 工作流程

1. **内容提取**：使用 pypdf 提取 PDF 文本
2. **结构分析**：识别章节、代码块、列表等
3. **翻译处理**：调用 LLM 翻译为中文
4. **格式化输出**：生成结构化 Markdown
5. **文件保存**：输出到指定位置

### 脚本位置

- 主脚本：`scripts/pdf_trans2md.py`
- Skill 定义：`SKILL.md`

## 注意事项

### PDF 保护

如果 PDF 受密码保护，需要先解密：
- 使用 PDF 阅读器（Adobe Acrobat 等）移除密码保护
- 或使用命令行工具：`qpdf --decrypt input.pdf output.pdf`

### 扫描件 PDF

扫描的 PDF（图像而非文本）需要先进行 OCR：
- 使用 `ocrmypdf`：`ocrmypdf input.pdf output.pdf`
- 或使用 Adobe Acrobat 的 OCR 功能

### 大文件处理

对于大型 PDF（>100MB），建议：
- 分批翻译（使用 `--pages` 指定范围）
- 确保有足够的内存
- 考虑使用 `--no-toc` 加速处理

### 编码问题

- 所有输出使用 UTF-8 编码
- 特殊字符可能需要手动调整
- 确保终端支持 UTF-8 显示

## 故障排除

### 错误：PDF is password-protected

```
解决：使用 PDF 阅读器解密，或提供无保护版本
```

### 错误：No text content extracted

```
可能原因：扫描件 PDF
解决：先进行 OCR 处理
```

### 错误：UnicodeEncodeError

```
解决：确保 Python 脚本使用 UTF-8 编码
```

## 扩展功能

未来可能添加的功能：
- [ ] 集成在线翻译 API（Google Translate、DeepL）
- [ ] 支持更多 PDF 库（pdfminer、PyMuPDF）
- [ ] 自动检测文档语言
- [ ] 保留原始图片和图表
- [ ] 生成双语对照版本
- [ ] 支持 LaTeX/PDF 公式转换

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个 skill。

## 许可证

MIT License
