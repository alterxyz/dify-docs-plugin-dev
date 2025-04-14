---
dimensions:
  type:
    primary: conceptual
    detail: architecture
  level: beginner
standard_title: Cheatsheet
language: zh
---

## Dify Plugin 开发速查表

### 环境要求

- Python 版本 ≥ 3.12
- Dify 插件脚手架工具 (dify-plugin-daemon)

### 获取 Dify Plugin 开发包

[Dify Plugin CLI](https://github.com/langgenius/dify-plugin-daemon/releases)

#### 不同平台安装方法

**macOS ARM (M 系列芯片):**

```bash
# 下载 dify-plugin-darwin-arm64
chmod +x dify-plugin-darwin-arm64
./dify-plugin-darwin-arm64 version
```

**macOS Intel:**

```bash
# 下载 dify-plugin-darwin-amd64
chmod +x dify-plugin-darwin-amd64
./dify-plugin-darwin-amd64 version
```

**Linux:**

```bash
# 下载 dify-plugin-linux-amd64
chmod +x dify-plugin-linux-amd64
./dify-plugin-linux-amd64 version
```

**全局安装 (推荐):**

```bash
# 重命名并移动到系统路径
# 示例 (macOS ARM)
mv dify-plugin-darwin-arm64 dify
sudo mv dify /usr/local/bin/
dify version
```

### 运行开发包

#### 初始化和验证

如果开发包名为 `dpd`, 其他名字请手动替换

```bash
chmod +x dpd
./dpd version
```

### 插件开发流程

#### 1. 新建插件

```bash
./dpd plugin init
```

按提示完成插件基本信息配置

#### 2. 开发模式运行

```bash
./dpd plugin dev ./yourapp
```

#### 3. 调试与测试

验证插件有效性:

```bash
./dpd plugin validate ./yourapp
```

运行插件单元测试:

```bash
cd yourapp
pytest
```

#### 4. 打包与部署

打包插件:

```bash
./dpd plugin package ./yourapp
```

发布插件:

```bash
./dpd plugin publish ./yourapp-{version}.zip
```

### 插件分类

#### 工具标签

分类 `tag` [class ToolLabelEnum(Enum)](https://github.com/langgenius/dify-plugin-sdks/blob/main/python/dify_plugin/entities/tool.py)

```python
class ToolLabelEnum(Enum):
    SEARCH = "search"
    IMAGE = "image"
    VIDEOS = "videos"
    WEATHER = "weather"
    FINANCE = "finance"
    DESIGN = "design"
    TRAVEL = "travel"
    SOCIAL = "social"
    NEWS = "news"
    MEDICAL = "medical"
    PRODUCTIVITY = "productivity"
    EDUCATION = "education"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    OTHER = "other"
```

### 插件类型参考

Dify 支持多种类型的插件开发：

- **工具插件**: 集成第三方 API 和服务
- **模型插件**: 集成 AI 模型
- **Agent 策略插件**: 自定义 Agent 思考和决策策略
- **扩展插件**: 扩展 Dify 平台功能，例如 Endpoint 和 WebAPP

### 常用代码片段

#### 工具定义示例

```python
from typing import List, Optional
from pydantic import BaseModel, Field
from dify_plugin.tool import Tool, ToolLabelEnum

class SearchParams(BaseModel):
    query: str = Field(..., description="搜索查询关键词")
    limit: int = Field(default=5, description="返回结果数量限制")

class SearchResult(BaseModel):
    title: str = Field(..., description="结果标题")
    url: str = Field(..., description="结果URL")
    snippet: str = Field(..., description="结果摘要")

class SearchTool(Tool):
    name: str = "search"
    description: str = "搜索互联网信息"
    labels: List[str] = [ToolLabelEnum.SEARCH]
    parameters: BaseModel = SearchParams
    returns: BaseModel = SearchResult
```

#### 工具实现示例

```python
@tool.on_invoke
def on_tool_invoke(params: dict) -> dict:
    query = params["query"]
    limit = params.get("limit", 5)

    # 实现搜索逻辑
    results = search_api_call(query, limit)

    # 返回结果
    return {
        "title": results["title"],
        "url": results["url"],
        "snippet": results["snippet"]
    }
```

#### 认证配置示例

```python
from dify_plugin.auth import AuthModel, AccessTokenAuth

class MyPluginAuth(AuthModel):
    api_key: str = Field(..., description="API密钥")

@plugin.on_auth
def on_auth(auth: dict) -> AccessTokenAuth:
    return AccessTokenAuth(
        access_token=auth["api_key"],
        header_key="Authorization",
        header_value_prefix="Bearer "
    )
```

### 常见问题

- **插件无法加载**: 检查 `manifest.yml` 格式是否正确
- **权限问题**: `chmod +x dpd` 确保有执行权限
- **依赖问题**: 检查 `requirements.txt` 是否完整
- **API 错误**: 检查认证信息是否正确
- **macOS 安全警告**: 若提示 "Apple 无法验证" 错误，请前往 "设置 → 隐私与安全性 → 安全性"，选择 "仍要打开"

### 参考资源

- [官方帮助文档](https://docs.dify.ai/v/zh-hans/)
- [插件开发 SDK](https://github.com/langgenius/dify-plugin-sdks)
- [插件示例库](https://github.com/langgenius/dify-plugin-examples)