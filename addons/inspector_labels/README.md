# Inspector Labels

Custom Inspector labels from GDScript comments. Tested on Godot 4.7.

## Install

Copy this folder into `addons/inspector_labels` in your Godot project. Enable **Inspector Labels** in **Project > Project Settings > Plugins**.

```gdscript
# @label 射击间隔
@export var fire_interval: float = 0.1

# @label Maximum health
@export var max_health: int = 5
```

The Inspector shows the comment label. Code and saved scenes continue to use `fire_interval` and `max_health`. Game scripts do not need `@tool`. This is literal label replacement, not automatic translation.

Put each marker on its own line at script top level before its exported variable. Blank lines, `##` documentation comments and export annotations may appear in between. `## @label` is accepted too. The last consecutive marker wins; empty labels and unmarked properties keep the native label.

Save the script to update labels. Reselect the node if necessary, or use **Project > Tools > 刷新检查器中文标签** (Refresh Inspector Labels).

Supports native number fields, range sliders, checkboxes, enums, vectors, colors, resources, arrays, and parent-script labels. Disabling the plugin restores native names and preserves values.

Does not cover C#, function locals, nested inner-class variables, built-in Godot property names, or enum/array item labels. Other plugins editing the same property may conflict. Tested on Windows/Godot 4.7; other platforms are unverified.

## 中文用法

1. 将此文件夹放到项目的 `addons/inspector_labels`。
2. 在「项目 → 项目设置 → 插件」启用 Inspector Labels。
3. 在导出变量上方单独写一行 `# @label 中文名称`。
4. 保存脚本，选中节点，检查器就会显示中文。代码中的英文变量名与已有数值不变。

标签不需要引号。支持与 `@export_range`、`@export_enum` 等注解搭配，游戏脚本无需添加 `@tool`。父脚本和自定义 Resource 的导出属性也支持。可通过「项目 → 工具 → 刷新检查器中文标签」手动刷新。

## Development disclosure and license

Implementation, documentation and tests were created with OpenAI Codex assistance. The plugin was tested in Godot 4.7. MIT © 2026 Soybean-milk. The full license is included in `LICENSE` in this folder.
