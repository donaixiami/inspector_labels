extends Resource
## A custom Resource also works without @tool.

# @label 武器名称
@export var weapon_name: String = "训练用法杖"

# @label 基础伤害
@export_range(0, 100, 1) var base_damage: int = 10
