---
name: pdf-trans2md
description: 将PDF文件（全部或部分）翻译为中文并输出为Markdown文件。支持指定页码范围、自动识别章节结构、保留代码示例和格式。
user-invocable: true
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# PDF 翻译为 Markdown Skill

将 PDF 文档翻译为中文 Markdown 格式。适用于技术文档、论文、书籍等内容。

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
- `--mode <模式>`: 翻译模式
  - `zh` (默认): 仅输出中文翻译
  - `bilingual`: 中英文对照，原文用引用块标记
- `--preserve-code`: 保留代码块的原始格式（默认开启）
- `--toc`: 在输出开头生成目录（默认开启）

## 工作流程

1. **检测PDF文件**：验证文件存在性和可访问性
2. **提取内容**：使用 pypdf 库提取指定页码的文本内容
3. **结构分析**：识别章节标题、代码块、列表等结构
4. **翻译处理**：将英文内容翻译为中文，保持技术术语准确性
5. **格式化输出**：生成结构化的 Markdown 文件
6. **保存文件**：输出到指定位置并报告完成

## 实现细节

### 内容提取

使用 Python 的 `pypdf` 库提取文本：
- 支持 UTF-8 编码
- 保留段落结构
- 识别代码块和列表

### 翻译策略

- 技术术语保持英文或提供标准中文对照
- 代码示例、命令行、配置不翻译
- 保持原文档的层级结构
- 保留链接、引用和脚注格式

### 输出格式

生成的 Markdown 包含：
- 原始标题层级（#、##、###）
- 代码块（```）保持不变
- 列表和表格格式
- 页码标记（可选）

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

## 注意事项

1. **PDF 保护**：如果PDF受密码保护，需要先解密或提供无保护版本
2. **编码问题**：某些PDF可能包含特殊字符，提取时可能需要调整
3. **大文件**：对于非常大的PDF（>100MB），建议分批翻译
4. **OCR PDF**：扫描的PDF（图像而非文本）需要先进行OCR处理

## 故障排除

### 无法读取PDF

```
错误：PDF is password-protected
解决：使用 PDF 阅读器解密文件，或提供解密后的版本
```

### 编码错误

```
错误：UnicodeEncodeError
解决：确保使用 UTF-8 编码保存输出文件
```

### 提取内容为空

```
错误：页面无文本内容
解决：PDF 可能是扫描件，需要 OCR；或尝试使用其他 PDF 库如 pdfminer
```
