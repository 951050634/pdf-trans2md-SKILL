# Python 异步编程指南

## 1. 简介

异步编程是现代 Python 开发中的重要范式。它允许程序在等待 I/O 操作时执行其他任务，从而提高整体效率。

## 2. 核心概念

### 2.1 协程（Coroutines）

协程是异步编程的基本构建块。在 Python 中，协程使用 `async def` 关键字定义。

```python
async def fetch_data(url):
    """异步获取数据"""
    response = await aiohttp.get(url)
    return await response.json()
```

### 2.2 事件循环（Event Loop）

事件循环负责调度和执行协程。它是 asyncio 库的核心组件。

```python
import asyncio

async def main():
    tasks = [
        fetch_data("https://api.example.com/1"),
        fetch_data("https://api.example.com/2")
    ]
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. 常用模式

### 3.1 并发执行

使用 `asyncio.gather()` 可以并发执行多个协程：

```python
results = await asyncio.gather(
    task1(),
    task2(),
    task3()
)
```

### 3.2 超时控制

使用 `asyncio.wait_for()` 设置超时：

```python
try:
    result = await asyncio.wait_for(
        slow_operation(),
        timeout=5.0
    )
except asyncio.TimeoutError:
    print("操作超时")
```

### 3.3 任务取消

```python
task = asyncio.create_task(long_running())
# ... 稍后
task.cancel()
try:
    await task
except asyncio.CancelledError:
    print("任务已取消")
```

## 4. 实际应用场景

异步编程特别适合以下场景：

- **网络请求**：同时向多个 API 端点发送请求
- **数据库操作**：批量执行数据库查询
- **文件 I/O**：使用 `aiofiles` 进行异步文件操作
- **Web 服务器**：使用 FastAPI 或 aiohttp 处理并发请求

## 5. 最佳实践

1. 始终使用 `async` 和 `await` 关键字
2. 避免在协程中执行 CPU 密集型任务
3. 使用适当的超时和错误处理
4. 考虑使用连接池提高性能

## 6. 常见错误

### 6.1 忘记使用 await

```python
# 错误：协程对象未被执行
fetch_data(url)

# 正确
await fetch_data(url)
```

### 6.2 在事件循环外调用

```python
# 错误：在非异步函数中直接调用
result = fetch_data(url)

# 正确：使用 asyncio.run()
result = asyncio.run(fetch_data(url))
```

## 7. 性能对比

| 方式 | 1000个请求耗时 | 内存占用 |
|------|----------------|----------|
| 同步 | 120s | 50MB |
| 异步 | 3s | 80MB |

异步方式在 I/O 密集型任务中性能提升显著。

## 8. 总结

异步编程是 Python 生态系统的重要组成部分。掌握 asyncio 可以显著提升应用性能，特别是在处理网络和 I/O 操作时。

**参考资料：**
- Python 官方文档：https://docs.python.org/3/library/asyncio.html
- Real Python 教程
- "Fluent Python" 第 2 版

---

*本文档生成于 2026 年 6 月 7 日*
