# Inspector Labels · 检查器中文标签

保留英文变量名，用一行注释设置 Godot 检查器中的中文显示名称。

```gdscript
# @label 射击间隔
@export var fire_interval: float = 0.1
```

检查器显示「射击间隔」，代码和场景文件仍使用 `fire_interval`。

本插件为纯 GDScript 编辑器插件，针对 **Godot 4.7** 验证，不需要 .NET、GDExtension、联网服务或额外依赖。

## 安装到你的项目

1. 将本目录中的 **`addons/inspector_labels` 整个文件夹**复制到目标项目的 `addons` 目录。
2. 在 Godot 中打开 **项目 → 项目设置 → 插件**。
3. 启用 **Inspector Labels**。
4. 给导出变量添加 `# @label 中文名称`，保存脚本并选中对应节点。

安装时只复制 `addons/inspector_labels`，不需要复制示例项目的 `project.godot`。

## 先看示例

用 Godot 项目管理器导入本目录的 `project.godot`，打开 `examples/demo.tscn`，选中 **Player**。

示例已经启用插件；检查器中的「战斗属性」分组包含射击间隔、最大生命值、无敌持续时间等。无需运行游戏就能查看。

## 使用示例

### 普通数字

```gdscript
extends CharacterBody2D

# @label 射击间隔
## 两次射击之间的间隔，单位：秒。
@export var fire_interval: float = 0.1

# @label 最大生命值
@export var max_health: int = 5
```

`# @label` 指定标签，`##` 继续使用 Godot 原生的文档提示。游戏脚本无需加 `@tool`。

### 范围滑块和复选框

```gdscript
# @label 无敌持续时间
@export_range(0.0, 5.0, 0.1)
var invincible_duration: float = 0.6

# @label 允许攻击
@export var can_attack: bool = true
```

### 枚举、向量和资源

```gdscript
# @label 攻击类型
@export_enum("近战", "远程", "魔法")
var attack_type: int = 1

# @label 出生偏移
@export var spawn_offset: Vector2 = Vector2.ZERO

# @label 角色贴图
@export var portrait: Texture2D
```

### 中文分组

分组直接使用 Godot 原生注解：

```gdscript
@export_group("战斗属性")

# @label 最大生命值
@export var max_health: int = 5
```

## 标签规则

- `# @label 中文名称` 单独占一行，与脚本顶层变量对齐。标签不需要加引号。
- 标记作用于后面的一个导出变量；中间可有空行、说明注释或跨行的 `@export_range(...)` 等注解。
- 兼容 `## @label 中文名称`，但推荐单井号，避免标签标记混入原生文档提示。
- 多个连续标签以最后一个为准；空标签不替换原生名称。
- 未添加标签的属性保持 Godot 原生显示。
- 父脚本中的标签可以继承；自定义 `Resource` 的导出属性同样支持。
- 插件只读取注释，不调用游戏脚本中的函数，也不改变属性默认值、存储键名或运行时行为。

## 修改标签后如何刷新

保存 GDScript 后插件会监听保存和外部重载事件，刷新当前检查器。也可以重新选择节点。

如果标签尚未更新，使用 **项目 → 工具 → 刷新检查器中文标签**。请先保存脚本；尚未保存到磁盘的注释不作为正式标签来源。

## 禁用与卸载

在 **项目 → 项目设置 → 插件** 关闭 Inspector Labels，检查器恢复原生名称，现有数值不会被清除。关闭后可移除项目中的 `addons/inspector_labels` 文件夹；游戏脚本里的注释保留即可。

## 第一版支持范围

- 支持 GDScript 脚本顶层的导出属性，包括整数、浮点数、布尔值、字符串、枚举、向量、颜色、资源引用和数组等 Godot 原生编辑器支持的类型。
- 不处理 C# 字段、函数局部变量或脚本内部 `class Inner:` 中声明的变量。内部类需要中文标签时，可先拆成独立 `.gd` 文件。
- 不翻译 Godot 内置属性、节点名、枚举选项或数组元素名称；本插件负责导出变量的属性标签。
- 中文标签较长时，可以拖宽检查器停靠面板。
- 如果其他插件同时接管同一个属性编辑器，其优先级可能影响标签显示；尚未对第三方检查器插件做组合兼容性保证。

## 验证

测试在独立副本中进行，不修改示例场景或你的游戏项目。Windows PowerShell 中运行：

```powershell
.\tests\run_tests.ps1 -Godot '你的 Godot 控制台版本 exe 的完整路径'
```

自动测试覆盖标签解析、继承、原生控件标签、属性修改、撤销/重做、场景保存和重新加载、资源属性编辑，以及插件禁用和重新启用。测试日志保留在 `.godot/test-runs/`。

另外在 Godot 4.7 图形编辑器中验证了中文显示、数字输入与恢复默认值按钮。

## 文件结构

```text
inspector_labels/
├─ addons/inspector_labels/      要复制到游戏项目的插件
│  ├─ plugin.cfg
│  ├─ plugin.gd
│  ├─ inspector_plugin.gd
│  ├─ label_provider.gd
│  └─ LICENSE
├─ examples/                    玩家、父脚本、Resource 和示例场景
├─ tests/                       自动测试与独立测试运行器
├─ project.godot                可直接导入的独立示例项目
└─ README.md
```

许可证：MIT，见 `addons/inspector_labels/LICENSE`。


MIT © 2026 Soybean-milk。代码、文档及测试由 OpenAI Codex 辅助编写，已在 Godot 4.7 执行验证。
