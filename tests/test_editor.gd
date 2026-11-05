@tool
extends EditorPlugin
## Copied into an isolated test project by run_tests.ps1.

var _checks := 0
var _failures := 0


func _enter_tree() -> void:
	if "--inspector-labels-test" in OS.get_cmdline_user_args():
		_run.call_deferred()


func _run() -> void:
	await get_tree().create_timer(2.0).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		await get_tree().create_timer(0.1).timeout
	EditorInterface.open_scene_from_path("res://examples/demo.tscn")
	await get_tree().create_timer(0.5).timeout
	var scene := EditorInterface.get_edited_scene_root()
	if scene == null:
		push_error("No edited scene")
		get_tree().quit(1)
		return
	var player := scene.get_node("Player")
	EditorInterface.edit_node(player)
	await get_tree().create_timer(0.5).timeout
	var inspector := EditorInterface.get_inspector()
	_expect(EditorInterface.is_plugin_enabled("inspector_labels"), "plugin enabled")
	var hp_editor := _find_property(inspector, player, "max_health")
	_expect(hp_editor != null and hp_editor.label == "最大生命值", "native integer editor with Chinese label")
	var expected := {
		"fire_interval": "射击间隔", "invincible_duration": "无敌持续时间",
		"can_attack": "允许攻击", "attack_type": "攻击类型",
		"display_name": "角色名称", "spawn_offset": "出生偏移",
		"tint": "角色颜色", "portrait": "角色贴图",
		"weapon": "武器配置", "starting_items": "初始道具",
		"movement_speed": "移动速度（继承自父脚本）",
	}
	for name in expected:
		var property := _find_property(inspector, player, name)
		_expect(property != null and property.label == expected[name], "label: " + name)
	var native := _find_property(inspector, player, "untranslated_value")
	_expect(native != null and native.label != "", "unlabeled property remains editable")
	if hp_editor != null:
		hp_editor.emit_changed("max_health", 9)
		await get_tree().create_timer(0.3).timeout
		_expect(player.get("max_health") == 9, "native property change writes original field")
		var host := EditorPlugin.new()
		var manager := host.get_undo_redo()
		var history := manager.get_history_undo_redo(manager.get_object_history_id(player))
		_expect(history.has_undo(), "property change records undo")
		history.undo()
		await get_tree().create_timer(0.2).timeout
		_expect(player.get("max_health") == 5, "undo restores previous value")
		history.redo()
		await get_tree().create_timer(0.2).timeout
		_expect(player.get("max_health") == 9, "redo restores edit")
		var packed := PackedScene.new()
		_expect(packed.pack(scene) == OK, "pack edited scene")
		var save_path := "res://.godot/inspector_labels_roundtrip.tscn"
		_expect(ResourceSaver.save(packed, save_path) == OK, "save edited scene")
		var saved_text := FileAccess.get_file_as_string(save_path)
		_expect(saved_text.contains("max_health = 9") and not saved_text.contains("最大生命值 ="), "serialization keeps English keys")
		var reloaded := ResourceLoader.load(save_path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
		var reloaded_scene := reloaded.instantiate()
		_expect(reloaded_scene.get_node("Player").get("max_health") == 9, "reloaded scene preserves edit")
		reloaded_scene.free()
		history.undo()
		host.free()

	var weapon: Resource = player.get("weapon")
	EditorInterface.inspect_object(weapon)
	await get_tree().create_timer(0.3).timeout
	var weapon_editor := _find_property(inspector, weapon, "base_damage")
	_expect(weapon_editor != null and weapon_editor.label == "基础伤害", "Resource inspector label")
	if weapon_editor != null:
		weapon_editor.emit_changed("base_damage", 20)
		await get_tree().create_timer(0.2).timeout
		_expect(weapon.get("base_damage") == 20, "Resource value remains editable")
		weapon.set("base_damage", 10)

	EditorInterface.edit_node(player)
	await get_tree().create_timer(0.3).timeout
	EditorInterface.set_plugin_enabled("inspector_labels", false)
	await get_tree().create_timer(0.4).timeout
	hp_editor = _find_property(inspector, player, "max_health")
	_expect(hp_editor != null and hp_editor.label != "最大生命值", "disable restores native label")
	_expect(player.get("max_health") == 5, "disable preserves data")
	EditorInterface.set_plugin_enabled("inspector_labels", true)
	await get_tree().create_timer(0.4).timeout
	hp_editor = _find_property(inspector, player, "max_health")
	_expect(hp_editor != null and hp_editor.label == "最大生命值", "reenable restores Chinese label")
	# Exercise a comment-only external save and the real filesystem reload event.
	var script_path := "res://examples/player.gd"
	var original := FileAccess.get_file_as_string(script_path)
	_write_text(script_path, original.replace("# @label 最大生命值", "# @label 生命上限"))
	EditorInterface.get_resource_filesystem().scan()
	await get_tree().create_timer(1.2).timeout
	hp_editor = _find_property(inspector, player, "max_health")
	_expect(hp_editor != null and hp_editor.label == "生命上限", "comment-only external save refreshes label")
	_expect(player.get("max_health") == 5, "label refresh preserves value")
	_write_text(script_path, original)
	EditorInterface.get_resource_filesystem().scan()
	await get_tree().create_timer(1.2).timeout
	hp_editor = _find_property(inspector, player, "max_health")
	_expect(hp_editor != null and hp_editor.label == "最大生命值", "restored comment refreshes label")
	print("Inspector Labels editor: %d checks, %d failures" % [_checks, _failures])
	get_tree().quit(1 if _failures else 0)


func _find_property(node: Node, object: Object, property: String) -> EditorProperty:
	if node is EditorProperty:
		if node.get_edited_object() == object and node.get_edited_property() == property:
			return node
	for child in node.get_children():
		var found := _find_property(child, object, property)
		if found != null:
			return found
	return null


func _expect(condition: bool, message: String) -> void:
	_checks += 1
	if condition:
		print("PASS: " + message)
	else:
		_failures += 1
		push_error("FAIL: " + message)


func _write_text(path: String, value: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(value)
	file.close()
