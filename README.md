# PDF 翻译为中文 Markdown Skill

将 PDF 文档（全部或部分）翻译为中文 Markdown 格式的 Claude Code skill。

**核心特性**：Claude 驱动翻译架构，充分利用 Claude 的强翻译能力，确保术语准确性和翻译质量。

## 架构说明

本 skill 采用 **Claude 驱动翻译** 架构：

- **Python 脚本**：负责 PDF 文本提取、结构识别、格式化输出
- **Claude**：负责实际翻译工作（术语一致性、上下文理解、翻译质量）

这种架构避免了外部翻译 API 的质量限制，充分利用了 Claude 的语言能力。

## 安装

### 方法 1：从 GitHub 克隆（推荐用于开发）

```bash
git clone https://github.com/your-username/pdf-trans2md.git
# 然后将 skill 目录链接或复制到 ~/.claude/skills/pdf-trans2md/
```

### 方法 2：直接安装 Skill

将此 skill 目录放置在 `~/.claude/skills/pdf-trans2md/` 下。

### 依赖

```bash
pip install pypdf
```

## 快速开始

### 准备翻译任务

```bash
# 提取 PDF 并生成翻译指南
/pdf-trans2md document.pdf --pages 1-10 --mode bilingual --prepare-only
```

输出：
- `document_translation_guide.md` - 翻译指南（含规则和结构化数据）
- `document_structured.json` - 结构化 JSON 数据

### Claude 翻译

1. 阅读 `document_translation_guide.md`
2. 按照 SKILL.md 中的翻译规则进行翻译
3. 保存结果到 `document_zh.md` 或指定路径

## 功能特性

- ✅ 支持整个PDF翻译
- ✅ 支持指定页码范围（`--pages 16-32`）
- ✅ 支持多页码范围（`--pages 1-10,20-30`）
- ✅ 支持章节选择（`--chapter 5`）
- ✅ **支持两种翻译模式**：
  - `zh`: 仅输出中文（默认）
  - `bilingual`: 中英文对照，原文用引用块标记
- ✅ 保留代码示例和格式（代码块绝对不翻译）
- ✅ 自动识别章节结构
- ✅ 生成目录（TOC）
- ✅ 自定义输出标题和路径
- ✅ 增强的代码块检测（缩进 + 关键字模式）
- ✅ 自动清理中间文件（翻译完成后删除 `*_translation_guide.md` 和 `*_structured.json`）

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

# 纯文本模式（禁用结构检测）
/pdf-trans2md doc.pdf --no-structure

# 仅准备文件（不执行翻译）
/pdf-trans2md doc.pdf --prepare-only

# 保留中间文件（默认会在翻译完成后自动清理）
/pdf-trans2md doc.pdf --keep-intermediate
```

## 翻译规则（Claude 遵循）

### 代码块 - 绝对不翻译
- 保持所有代码内容完全不变
- 保留所有缩进、注释、字符串
- 代码中的自然语言注释可选择性翻译（双语模式）

### 章节标题 - 准确翻译
- 保持标题层级（# 数量）
- 技术术语首次出现可保留英文+中文

### 段落 - 流畅翻译
- 保持技术术语一致性
- 代码标识符、API 名称保持英文

### 双语模式特殊处理
- 保留原文引用块：`> **原文 (English):**`
- 中文翻译在前，原文在引用块中

## 技术实现

### 依赖

- Python 3.8+
- pypdf 库：`pip install pypdf`

### 工作流程

1. **内容提取**：使用 pypdf 提取 PDF 文本
2. **结构分析**：识别章节、代码块、列表等
3. **准备翻译**：生成结构化 JSON 和翻译指南
4. **Claude 翻译**：按照 SKILL.md 规则翻译
5. **格式化输出**：生成结构化 Markdown
6. **文件保存**：输出到指定位置

### 脚本位置

- 主脚本：`scripts/pdf_trans2md.py`
- Skill 定义：`SKILL.md`
- 翻译指南模板：脚本自动生成

## 测试

项目包含测试材料和评估用例：

```bash
# 测试结构检测
python -c "
from scripts.pdf_trans2md import detect_structure
blocks = detect_structure(open('test-materials/sample_content.md').read())
print(f'Detected {len(blocks)} blocks')
"
```

测试文件：
- `test-materials/sample_content.md` - 包含代码块、章节、列表的测试文档
- `evals/evals.json` - 3 个测试用例定义

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

### Windows 编码

脚本已内置 Windows 控制台 UTF-8 编码修复。如遇编码问题：
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

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

### 错误：UnicodeEncodeError (Windows)

```
解决：脚本已自动处理；如仍有问题，手动添加 sys.stdout.reconfigure(encoding='utf-8')
```

### 代码块未正确识别

```
解决：尝试使用 --no-structure 选项，或调整原文档缩进格式
```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个 skill。

贡献前请：
1. 阅读 `SKILL.md` 了解架构和翻译规则
2. 运行现有测试确保不破坏功能
3. 遵循现有的代码风格

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**版本**: 2.0
**更新日期**: 2026-06-07
**架构**: Claude 驱动翻译
