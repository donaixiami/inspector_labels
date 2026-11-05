extends SceneTree

const Provider = preload("res://addons/inspector_labels/label_provider.gd")

var _checks := 0
var _failures := 0


func _initialize() -> void:
	var provider := Provider.new()
	var cases := [
		["basic", "# @label 射击间隔\n@export var fire_interval: float = 0.1", {"fire_interval": "射击间隔"}],
		["range on next line", "# @label 时间\n@export_range(0, 5, 0.1)\nvar duration = 0.6", {"duration": "时间"}],
		["multiline annotation", "# @label 类型\n@export_enum(\n\t\"a)\",\n\t\"b(#\"\n) var kind: int", {"kind": "类型"}],
		["multiple annotations", "# @label 数字\n@export @onready var count = 0", {"count": "数字"}],
		["docs between marker and export", "# @label 血量\n## 说明\n\n@export var hp = 5", {"hp": "血量"}],
		["double hash marker", "## @label 血量\n@export var hp = 5", {"hp": "血量"}],
		["marker after annotation", "@export\n# @label 血量\nvar hp = 5", {"hp": "血量"}],
		["no marker", "@export var hp = 5", {}],
		["empty marker", "# @label   \n@export var hp = 5", {}],
		["marker boundary", "# @label_wrong 错误\n@export var hp = 5", {}],
		["one declaration only", "# @label 血量\n@export var hp = 5\n@export var damage = 10", {"hp": "血量"}],
		["consume on nonexport", "# @label 无效\nvar local = 1\n@export var hp = 5", {}],
		["consume on function", "# @label 无效\nfunc foo():\n\tpass\n@export var hp = 5", {}],
		["ignore function local", "func foo():\n\t# @label 局部\n\tvar hp = 1\n@export var hp = 5", {}],
		["ignore inner class", "class Inner:\n\t# @label 内部\n\t@export var hp = 1\n@export var hp = 5", {}],
		["ignore string marker", "var text = \"# @label 伪造\"\n@export var hp = 5", {}],
		["ignore triple quoted content", "var text = \"\"\"\n# @label 伪造\n@export var fake = 1\n\"\"\"\n@export var hp = 5", {}],
		["ignore single triple content", "var text = '''\n# @label 伪造\n@export var fake = 1\n'''\n@export var hp = 5", {}],
		["CRLF", "# @label 血量\r\n@export var hp = 5\r\n", {"hp": "血量"}],
		["last marker wins", "# @label 旧\n# @label 新\n@export var hp = 5", {"hp": "新"}],
		["unicode and punctuation", "# @label 无敌时间（秒） / 秒数\n@export var _duration2: float", {"_duration2": "无敌时间（秒） / 秒数"}],
		["getter block", "# @label 血量\n@export var hp: int:\n\tget:\n\t\treturn 5\n@export var damage = 1", {"hp": "血量"}],
		["quoted escaped values", "# @label 文件\n@export_file(\"a\\\")#.txt\") var file: String", {"file": "文件"}],
	]
	for item in cases:
		_expect(provider.parse_source(item[1]) == item[2], item[0])

	var player_script := load("res://examples/player.gd") as Script
	var labels := provider.labels_for_script(player_script)
	_expect(labels.get("fire_interval") == "射击间隔", "real player labels")
	_expect(labels.get("movement_speed") == "移动速度（继承自父脚本）", "base script labels")
	_expect(not labels.has("untranslated_value"), "unlabeled field stays native")
	_expect(labels.size() == 12, "all scalar, resource, array, inherited labels")
	var weapon_script := load("res://examples/weapon_data.gd") as Script
	_expect(provider.labels_for_script(weapon_script).get("weapon_name") == "武器名称", "resource labels")
	_expect(provider.labels_for_script(player_script) == labels, "cached labels stable")
	provider.clear_cache()
	_expect(provider.labels_for_script(player_script) == labels, "refresh retains labels")

	var transient := GDScript.new()
	transient.source_code = "extends RefCounted\n# @label 旧名称\n@export var hp = 5\n"
	_expect(provider.labels_for_script(transient).get("hp") == "旧名称", "in-memory script")
	transient.source_code = "extends RefCounted\n# @label 新名称\n@export var hp = 5\n"
	_expect(provider.labels_for_script(transient).get("hp") == "新名称", "changed source invalidates cache")

	var packed := load("res://examples/demo.tscn") as PackedScene
	var scene := packed.instantiate()
	var player := scene.get_node("Player")
	_expect(player.get("fire_interval") == 0.1, "original property path unchanged")
	_expect(player.get("max_health") == 5, "default value unchanged")
	_expect(player.get_script().is_tool() == false, "game script does not need tool mode")
	scene.free()
	print("Inspector Labels: %d checks, %d failures" % [_checks, _failures])
	quit(1 if _failures else 0)


func _expect(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures += 1
		push_error("FAIL: " + message)
