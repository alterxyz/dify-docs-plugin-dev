---
dimensions:
  type:
    primary: implementation
    detail: basic
  level: beginner
standard_title: Getting Started New Model
language: zh
todo: refine from this draft
---

# 快速接入一个新模型

你可能仅是想快速接入一个新型号的模型，那么本文将以简明的方式带你接入一个新的模型。你无需专业的编程背景，只需按照以下步骤操作即可。
如果新模型涉及了一些新功能，例如 Sonnet 3.7 支持了 thinking 参数，那么本文或许不适合。

## 初始化开发工具

首先，初始化 Dify 插件开发工具包。我们将其配置为 `dify`

然后，fork 我们的官方插件仓库，并在本地打开。

打开你需要添加的模型文件夹，例如 `models/vertex_ai/models/llm/gemini-2.0-pro-exp-02-05.yaml`

我们复制这个文件，并将其重命名为 2.5 ：
`models/vertex_ai/models/llm/gemini-2.5-pro-exp-03-25.yaml`

然后去 Google 的相关官网确定参数，并进行相应的修改：

| 参数 | Gemini 2.0 | Gemini 2.5 |
| --- | --- | --- |
| model | `gemini-2.0-pro-exp-02-05` | `gemini-2.5-pro-exp-03-25` |
| label: en_US | Gemini 2.0 pro exp 02-05 | Gemini 2.5 pro exp 03-25 |
| context_size | 1048576 | 2097152 |
| max_output_tokens | 8192 | 65535 |

以及，我们修改下版本号：

models/vertex_ai/manifest.yaml

`version: 0.0.8` -> `version: 0.0.9`

## 尝试运行

这里，我们将尝试快速运行，你也可以尝试远程调试 （一些链接）。

我们直接打包这个模型插件:

```bash
dify plugin package ./vertex_ai
```

然后，我们直接安装这个插件，通过本地文件上传的方式。

测试通过后，提交 pr 到 Dify 的 GitHub 仓库。

🎉恭喜，你成功添加了一个新的模型。