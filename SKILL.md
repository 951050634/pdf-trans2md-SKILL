---
name: pdf-trans2md
description: 将PDF文件（全部或部分）翻译为中文并输出为Markdown文件。支持指定页码范围、自动识别章节结构、保留代码示例和格式。无论用户是否明确要求，只要涉及PDF翻译、技术文档本地化、PDF转Markdown、双语对照文档，都应该使用此skill。
user-invocable: true
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# PDF 翻译为中文 Markdown Skill

将 PDF 文档翻译为中文 Markdown 格式。适用于技术文档、论文、书籍、用户手册等内容。**翻译工作由 Claude 完成**，Python 脚本仅负责 PDF 内容提取和结构分析。

## 设计理念

本 skill 采用 **Claude 驱动翻译** 架构：

1. **Python 脚本**：负责 PDF 文本提取、结构识别、格式化输出
2. **Claude**：负责实际翻译工作，确保术语准确性和翻译质量
3. **协作流程**：脚本提供结构化内容 → Claude 翻译 → 脚本生成最终 Markdown

这种架构充分利用了 Claude 的强翻译能力，避免了外部翻译 API 的质量限制。

## 使用方法

```
/pdf-trans2md <PDF文件路径> [选项]
```

### 基本用法

```
# 翻译整个PDF
/pdf-trans2md C:\Users\Admin\Desktop\document.pdf

# 翻译指定页码范围（1-based）
/pdf-trans2md C:\Users\Admin\Desktop\document.pdf --pages 16-32

# 翻译多个页码范围
/pdf-trans2md C:\Users\Admin\Desktop\document.pdf --pages 1-10,20-30

# 指定输出文件
/pdf-trans2md C:\Users\Admin\Desktop\document.pdf --output C:\Users\Admin\Desktop\output.md

# 翻译特定章节（需要PDF有目录）
/pdf-trans2md C:\Users\Admin\Desktop\document.pdf --chapter 5
```

### 支持的选项

- `--pages <范围>`: 指定页码范围，支持格式如 `16-32`、`1-10,20-30`
- `--output <路径>`: 指定输出 Markdown 文件路径（默认与PDF同目录，扩展名为 .md）
- `--chapter <章节号>`: 翻译特定章节（需要PDF包含目录信息）
- `--title <标题>`: 自定义输出文件的标题
- `--mode <模式>`:
  - `zh` (默认): 仅输出中文翻译
  - `bilingual`: 中英文对照，原文用引用块标记
- `--preserve-code`: 保留代码块的原始格式（默认开启）
- `--toc`: 在输出开头生成目录（默认开启）
- `--no-structure`: 禁用结构检测，使用纯文本模式

## 工作流程

### 第一阶段：内容提取（Python 脚本）

1. **验证文件**：检查 PDF 存在性、可访问性、是否加密
2. **提取文本**：使用 pypdf 按指定页码提取原始文本
3. **结构分析**：识别章节标题、代码块、列表、表格等元素
4. **内容分块**：将内容组织为结构化块（标题/段落/代码/列表）

### 第二阶段：翻译处理（Claude）

1. **阅读提取内容**：通过 Read 工具查看脚本生成的中间文件
2. **逐块翻译**：
   - 章节标题：准确翻译，保持层级
   - 段落内容：流畅翻译，保持技术术语一致性
   - 代码块：**完全不翻译**，保留原始格式
   - 列表项：翻译文本，保持标记符
3. **双语模式特殊处理**：保留原文引用块
4. **质量检查**：确保术语一致、格式正确

### 第三阶段：格式化输出（Python 脚本或 Claude）

1. **生成 Markdown**：根据翻译结果生成最终文件
2. **添加目录**：自动生成或更新目录
3. **保存文件**：输出到指定位置

## 实现细节

### 内容提取

使用 Python 的 `pypdf` 库提取文本：
- 支持 UTF-8 编码
- 保留段落结构
- 识别代码块和列表
- 记录页码信息

### 结构检测策略

脚本使用正则表达式和启发式规则检测：

```python
# 章节标题检测
- CHAPTER X, 第X章
- \d+\.\d+ 节号格式
- 全大写标题行

# 代码块检测
- 缩进行（4空格或制表符）
- 包含常见代码关键字（def, class, import等）
- 连续多行缩进

# 列表检测
-  bullet 标记（•, -, *, +）
- 编号列表（1., 2., a., b.）
```

### 翻译策略（由 Claude 执行）

**技术术语处理：**
- 首次出现时可保留英文并提供中文
- 后续使用标准中文术语
- 代码标识符、API 名称、配置键保持英文

**代码示例处理：**
- **绝对不翻译**任何代码内容
- 保留所有缩进、注释、字符串字面量
- 注释中的自然语言可选择性翻译（双语模式）

**格式保留：**
- 标题层级（# 数量）完全保持
- 列表嵌套关系保持
- 表格结构保持
- 链接、引用、脚注格式保持

### 输出格式

生成的 Markdown 包含：

**中文模式（默认）：**
```markdown
# 标题

## 1. 简介

翻译后的段落内容...

### 1.1 子章节

更多内容...
```

**双语模式：**
```markdown
# 标题

## 1. 简介

翻译后的段落内容...

> **原文 (English):**
> Original paragraph content...

### 1.1 子章节

> **原文 (English):**
> Original subsection content...
```

代码块在两种模式下都保持不变：
```python
# This code is never translated
def example():
    return "unchanged"
```

## 示例

### 示例 1：仅中文模式（默认）

```
/pdf-trans2md C:\Users\Admin\Desktop\verilator_doc.pdf --pages 16-32
```

输出仅包含中文翻译，适合直接阅读和使用。

### 示例 2：中英文对照模式

```
/pdf-trans2md C:\Users\Admin\Desktop\verilator_doc.pdf --mode bilingual --pages 16-32
```

输出格式：
```markdown
## 5.1 二进制、C++ 和 SystemC 生成

> **原文 (English):**
> Verilator will translate a SystemVerilog design into C++ with the `--cc` option, or into SystemC with the `--sc` option.

Verilator 将使用 `--cc` 选项将 SystemVerilog 设计转换为 C++，或使用 `--sc` 选项转换为 SystemC。
```

**适用场景：**
- 学习技术文档，需要对照原文理解
- 术语对照和准确性验证
- 翻译质量检查

### 示例 3：翻译特定章节

```
/pdf-trans2md C:\Users\Admin\Desktop\verilator_doc.pdf --pages 16-32 --title "第五章 Verilating"
```

### 示例 4：翻译多个部分

```
/pdf-trans2md C:\Users\Admin\Desktop\manual.pdf --pages 1-5,100-120 --output C:\Users\Admin\Desktop\manual_intro_zh.md
```

## 故障排除

### 无法读取PDF

```
错误：PDF is password-protected
解决：使用 PDF 阅读器解密文件，或提供解密后的版本
```

### 提取内容为空

```
错误：页面无文本内容
解决：PDF 可能是扫描件，需要 OCR；或尝试使用其他 PDF 库如 pdfminer
```

### 翻译质量问题

如果翻译结果不理想：
1. 检查原文档是否包含 OCR 错误
2. 尝试分段翻译大文档
3. 在双语模式下对照原文检查

### 格式异常

如果输出 Markdown 格式错乱：
1. 使用 `--no-structure` 选项禁用自动结构检测
2. 手动调整标题层级
3. 检查原 PDF 的文本提取质量

## 注意事项

1. **PDF 保护**：如果PDF受密码保护，需要先解密或提供无保护版本
2. **编码问题**：某些PDF可能包含特殊字符，提取时可能需要调整
3. **大文件**：对于非常大的PDF（>100MB），建议分批翻译
4. **OCR PDF**：扫描的PDF（图像而非文本）需要先进行OCR处理
5. **代码块识别**：如果代码块未被正确识别，可尝试调整原文档的缩进格式

## 相关工具

- **pdfminer.six**：更强大的 PDF 文本提取（可选依赖）
- **pypdf**：当前使用的 PDF 库（必需）
- **报告生成**：如需生成双语对照的 PDF，可配合其他工具使用

---

*Skill 版本：2.0 | 更新日期：2026-06-07*
