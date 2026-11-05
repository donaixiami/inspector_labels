@tool
extends EditorInspectorPlugin
## Keeps property paths and native editing behavior; only the label is replaced.

const LabelProvider = preload("label_provider.gd")

var _provider := LabelProvider.new()
var _object_labels: Dictionary = {}
var _creating_editor := false


func clear_cache() -> void:
	_provider.clear_cache()
	_object_labels.clear()


func _can_handle(object: Object) -> bool:
	return not _creating_editor and object.get_script() is GDScript


func _parse_begin(object: Object) -> void:
	_object_labels[object.get_instance_id()] = _provider.labels_for_script(object.get_script())


func _parse_property(object: Object, type: Variant.Type, name: String,
		hint_type: PropertyHint, hint_string: String, usage_flags: int, wide: bool) -> bool:
	if _creating_editor:
		return false
	# Non-@tool scripts use placeholder instances; their exports may have usage=6.
	if (usage_flags & PROPERTY_USAGE_EDITOR) == 0:
		return false
	var labels: Dictionary = _object_labels.get(object.get_instance_id(), {})
	var label: String = labels.get(name, "")
	if label.is_empty():
		return false
	# The factory consults registered plugins too. Skip ourselves during this call.
	_creating_editor = true
	var editor := EditorInspector.instantiate_property_editor(
		object, type, name, hint_type, hint_string, usage_flags, wide)
	_creating_editor = false
	if editor == null:
		return false
	add_property_editor(name, editor, false, label)
	return true


func _parse_end(object: Object) -> void:
	_object_labels.erase(object.get_instance_id())
