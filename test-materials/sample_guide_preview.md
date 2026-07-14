# 多模态视觉翻译预览

此预览展示 `--mode bilingual` 的强制输出契约。PDF 页面应先由当前 AI 模型进行视觉版面分析；不得默认读取 PDF 文本层。

## 3. Experimental Results

> **译文标题：3. 实验结果**

The proposed method improves multimodal representation learning across all benchmark datasets.

> **译文：**
> 所提出的方法在所有基准数据集上均改进了多模态表征学习。

The main contributions are:

- layout-aware visual reading;
- robust cross-column ordering;
- terminology-consistent translation.

> **译文：**
> 主要贡献包括：
>
> - 感知版面的视觉阅读；
> - 稳健的跨栏顺序处理；
> - 术语一致的翻译。

```python
result = model.predict(inputs)
```

代码块只保留一份，不机械生成双语副本。

**Figure 2. Accuracy under different layout conditions.**

> **译文：**
> **图 2．不同版面条件下的准确率。**

## 页面检查清单

- 先识别跨栏标题和摘要。
- 双栏正文先左栏、后右栏。
- 图注不得拼入邻近正文。
- 中文译文必须在原文之后，并位于引用块。
- 未经用户明确要求，不调用 `pypdf.extract_text()`。
