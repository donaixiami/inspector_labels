@tool
extends EditorPlugin
## Registers the label inspector and refreshes it when scripts are saved.

const LabelInspector = preload("inspector_plugin.gd")
const REFRESH_MENU := "刷新检查器中文标签"

var _inspector: LabelInspector
var _refresh_queued := false


func _enter_tree() -> void:
	_inspector = LabelInspector.new()
	add_inspector_plugin(_inspector)
	resource_saved.connect(_on_resource_saved)
	EditorInterface.get_resource_filesystem().resources_reload.connect(_on_resources_reload)
	EditorInterface.get_resource_filesystem().filesystem_changed.connect(_queue_refresh)
	add_tool_menu_item(REFRESH_MENU, _queue_refresh)
	_queue_refresh()


func _exit_tree() -> void:
	remove_tool_menu_item(REFRESH_MENU)
	if resource_saved.is_connected(_on_resource_saved):
		resource_saved.disconnect(_on_resource_saved)
	var filesystem := EditorInterface.get_resource_filesystem()
	if filesystem.resources_reload.is_connected(_on_resources_reload):
		filesystem.resources_reload.disconnect(_on_resources_reload)
	if filesystem.filesystem_changed.is_connected(_queue_refresh):
		filesystem.filesystem_changed.disconnect(_queue_refresh)
	if _inspector != null:
		remove_inspector_plugin(_inspector)
		_inspector = null
	_refresh_edited_object()


func _on_resource_saved(resource: Resource) -> void:
	if resource is GDScript:
		_queue_refresh()


func _on_resources_reload(paths: PackedStringArray) -> void:
	for path in paths:
		if path.get_extension() == "gd":
			_queue_refresh()
			return


func _queue_refresh() -> void:
	if _refresh_queued or _inspector == null:
		return
	_refresh_queued = true
	_refresh.call_deferred()


func _refresh() -> void:
	_refresh_queued = false
	if _inspector == null:
		return
	_inspector.clear_cache()
	_refresh_edited_object()


func _refresh_edited_object() -> void:
	var object := EditorInterface.get_inspector().get_edited_object()
	if is_instance_valid(object):
		object.notify_property_list_changed()
