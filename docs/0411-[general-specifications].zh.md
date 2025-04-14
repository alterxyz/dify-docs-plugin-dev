---
dimensions:
  type:
    primary: reference
    detail: core
  level: beginner
standard_title: General Specifications
language: zh
---

# (🚧)通用规范定义

本文将简要介绍插件开发中常见的结构。

### 路径规范

在 Manifest 或任意 yaml 文件中填写文件路径时，根据不同的类型的文件，遵循下面两条规范：

* 如果目标文件是一个图片或视频等多媒体文件时，例如填写插件的 `icon` ，你应该将这些文件放置于插件根目录下的 `_assets` 文件夹中。
* 如果目标文件是一个普通文本文件，如 `.py` `.yaml` 等代码文件，你应该填写该文件在插件项目内的绝对路径。

### 通用结构

在定义插件时，有一些数据结构是可以在工具、模型、Endpoint 之间共用的，这里定义了这些共用结构。

#### I18nObject

`I18nObject` 是一个符合 [IETF BCP 47](https://tools.ietf.org/html/bcp47) 标准的国际化结构，目前支持的四种语言为

* en\_US
* zh\_Hans
* ja\_Jp
* pt\_BR

#### ProviderConfig

`ProviderConfig` 为一个通用的供应商表单结构，适用于 `Tool`与`Endpoint`

* `name`(string)：表单项名称
* `label`([I18nObject](general-specifications.md#i18nobject), requierd)：遵循 [IETF BCP 47](https://tools.ietf.org/html/bcp47)
* `type`([provider\_config\_type](general-specifications.md#providerconfigtype-string), requierd)：表单类型
* `scope`([provider\_config\_scope](general-specifications.md#providerconfigscope-string))：可选项范围，根据`type`变动
* `required`(bool)：不能为空
* `default`(any)：默认值，仅支持基础类型 `float` `int` `string`
* `options`(list\[[provider\_config\_option](general-specifications.md#providerconfigoption-object)])：可选项，仅当 type 为 `select` 时使用
* `helper`(object)：帮助文档链接的 label，遵循 [IETF BCP 47](https://tools.ietf.org/html/bcp47)
* `url` (string)：帮助文档链接
* `placeholder`(object)：遵循 [IETF BCP 47](https://tools.ietf.org/html/bcp47)

#### ProviderConfigOption(object)

* `value`(string, required)：值
* `label`(object, required)：遵循 [IETF BCP 47](https://tools.ietf.org/html/bcp47)

#### ProviderConfigType(string)

* `secret-input` (string)：配置信息将被加密
* `text-input`(string)：普通文本
* `select`(string)：下拉框
* `boolean`(bool)：开关
* `model-selector`(object)：模型配置信息，包含供应商名称、模型名称、模型参数等
* `app-selector`(object)：app id
* `tool-selector`(object)：工具配置信息，包含工具供应商、名称、参数等
* `dataset-selector`(string)：TBD

#### ProviderConfigScope(string)

* 当 `type` 为 `model-selector` 时
  * `all`
  * `llm`
  * `text-embedding`
  * `rerank`
  * `tts`
  * `speech2text`
  * `moderation`
  * `vision`
* 当 `type` 为 `app-selector` 时
  * `all`
  * `chat`
  * `workflow`
  * `completion`
* 当`type` 为 `tool-selector` 时
  * `all`
  * `plugin`
  * `api`
  * `workflow`

#### ModelConfig

* `provider` (string): 包含 plugin\_id 的模型供应商名称，形如 `langgenius/openai/openai`。
* `model` (string): 具体的模型名称。
* `model_type` (enum): 模型类型的枚举，可以参考该文档。

#### NodeResponse

* `inputs` (dict): 最终输入到节点中的变量。
* `outputs` (dict): 节点的输出结果。
* `process_data` (dict): 节点运行过程中产生的数据。

#### ToolSelector

* `provider_id` (string): 工具供应商名称
* `tool_name` (string): 工具名称
* `tool_description` (string): 工具描述
* `tool_configuration` (dict\[str, Any]): 工具的配置信息
* `tool_parameters` (dict\[str, dict]): 需要 LLM 推理的参数
  * `name` (string): 参数名称
  * `type` (string): 参数类型
  * `required` (bool): 是否必填
  * `description` (string): 参数描述
  * `default` (any): 默认
  * `options`(list\[string]): 可选项