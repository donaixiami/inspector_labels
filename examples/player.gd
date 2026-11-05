extends "base_actor.gd"
## Select Player in demo.tscn to inspect the translated property labels.

const WeaponData = preload("weapon_data.gd")

@export_group("战斗属性")

# @label 射击间隔
## 两次射击之间的间隔，单位：秒。
@export var fire_interval: float = 0.1

# @label 最大生命值
@export var max_health: int = 5 

# @label 无敌持续时间
@export_range(0.0, 5.0, 0.1)
var invincible_duration: float = 0.6

# @label 允许攻击
@export var can_attack: bool = true

# @label 攻击类型
@export_enum("近战", "远程", "魔法")
var attack_type: int = 1

@export_group("外观与资源")

# @label 角色名称
@export var display_name: String = "冒险者"

# @label 出生偏移
@export var spawn_offset: Vector2 = Vector2(8, 16)

# @label 角色颜色
@export var tint: Color = Color(0.35, 0.65, 1.0)

# @label 角色贴图
@export var portrait: Texture2D

# @label 武器配置
@export var weapon: WeaponData

# @label 初始道具
@export var starting_items: Array[String] = ["药水", "钥匙"]

@export_group("对照：没有标签")
@export var untranslated_value: int = 42
