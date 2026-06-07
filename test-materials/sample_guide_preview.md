# PDF 翻译任务指南

请按照以下规则翻译本 PDF 提取的内容：

## 翻译模式
模式: bilingual

## 翻译规则

### 1. 代码块 (code) - 绝对不翻译
- 保持所有代码内容完全不变
- 保留所有缩进、注释、字符串
- 代码中的自然语言注释可选择性翻译（双语模式）

### 2. 章节标题 (chapter, section) - 准确翻译
- 保持标题层级（# 数量）
- 技术术语首次出现可保留英文+中文

### 3. 段落 (paragraph) - 流畅翻译
- 保持技术术语一致性
- 代码标识符、API 名称保持英文

### 4. 列表项 (bullet) - 翻译文本
- 保持列表标记符（-, *, •）
- 保持嵌套关系

### 5. 双语模式特殊处理
- 保留原文引用块：> **原文 (English):**
- 中文翻译在前，原文在引用块中

## 输出格式

文档标题: Python 异步编程指南

## 内容统计
- 总块数: 116
- 需翻译块数: 45
- 代码块数: 30

---

## 待翻译内容（结构化 JSON）

以下是提取的结构化内容，请逐块翻译：

```json
{
  "mode": "bilingual",
  "units": [
    {
      "type": "code",
      "original": "# Python 异步编程指南",
      "translate": false,
      "preserve_format": true
    },
    {
      "type": "empty",
      "original": "",
      "translate": false,
      "preserve_format": false
    },
    {
      "type": "code",
      "original": "## 1. 简介",
      "translate": false,
      "preserve_format": true
    },
    {
      "type": "empty",
      "original": "",
      "translate": false,
      "preserve_format": false
    },
    {
      "type": "paragraph",
      "original": "异步编程是现代 Python 开发中的重要范式。它允许程序在等待 I/O 操作时执行其他任务，从而提高整体效率。",
      "translate": true,
      "preserve_format": false
    },
    {
      "type": "empty",
      "original": "",
      "translate": false,
      "preserve_format": false
    },
    {
      "type": "code",
      "original": "## 2. 核心概念",
      "translate": false,
      "preserve_format": true
    },
    {
      "type": "empty",
      "original": "",
      "translate": false,
      "preserve_format": false
    },
    {
      "type": "code",
      "original": "### 2.1 协程（Coroutines）",
      "translate": false,
      "preserve_format": true
    },
    {
      "type": "empty",
      "original": "",
      "translate": false,
      "preserve_format": false
    },
    {
      "type": "paragraph",
      "original": "协程是异步编程的基本构建块。在 Python 中，协程使用 `async def` 关键字定义。",
      "translate": true,
      "preserve_format": false
    },
    {
  

...[truncated]...