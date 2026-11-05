@tool
extends RefCounted
## Reads comment labels without instantiating or executing game scripts.

const CACHE_LIMIT := 128

var _cache: Dictionary = {}
var _label_regex := RegEx.new()
var _member_regex := RegEx.new()
var _annotation_regex := RegEx.new()


func _init() -> void:
	_label_regex.compile("^#{1,2}\\s*@label(?:\\s+|$)(.*)$")
	_member_regex.compile("^var\\s+([\\p{L}_][\\p{L}\\p{N}_]*)")
	_annotation_regex.compile("^@[a-zA-Z_][a-zA-Z0-9_]*")


func clear_cache() -> void:
	_cache.clear()


func labels_for_script(script: Script) -> Dictionary:
	var chain: Array[Script] = []
	var current := script
	while current is GDScript:
		chain.push_front(current)
		current = current.get_base_script()
	var result: Dictionary = {}
	for item in chain:
		result.merge(_labels_for_one_script(item), true)
	return result


func _labels_for_one_script(script: Script) -> Dictionary:
	var source := script.get_source_code()
	# Comment-only saves may not replace the loaded Script resource immediately.
	var path := script.resource_path
	if path.ends_with(".gd") and FileAccess.file_exists(path):
		source = FileAccess.get_file_as_string(path)
	var key := script.get_instance_id()
	var entry: Dictionary = _cache.get(key, {})
	if entry.get("source") == source:
		return entry["labels"]
	var labels := parse_source(source)
	if _cache.size() >= CACHE_LIMIT:
		_cache.clear()
	_cache[key] = {"source": source, "labels": labels}
	return labels


func parse_source(source: String) -> Dictionary:
	var labels: Dictionary = {}
	var pending_label := ""
	var has_export := false
	var annotation_depth := 0
	var state := {"quote": "", "triple": false}
	for raw_line in source.replace("\r\n", "\n").split("\n"):
		var inside_string: bool = not state["quote"].is_empty()
		var clean := _mask_strings_and_comments(raw_line, state)
		var stripped := raw_line.strip_edges()
		var indented := raw_line.begins_with(" ") or raw_line.begins_with("\t")
		# Only class-level variables of this script; never function locals or inner classes.
		if not inside_string and not indented and stripped.begins_with("#"):
			var marker := _label_regex.search(stripped)
			if marker != null:
				pending_label = marker.get_string(1).strip_edges()
			continue
		if annotation_depth > 0:
			var rest := _consume_arguments(clean, annotation_depth)
			annotation_depth = rest["depth"]
			if annotation_depth > 0:
				continue
			clean = rest["tail"]
		elif inside_string or indented:
			continue
		if clean.strip_edges().is_empty():
			continue
		var remaining := clean.strip_edges()
		while remaining.begins_with("@"):
			var annotation := _annotation_regex.search(remaining)
			if annotation == null:
				break
			var token := annotation.get_string()
			has_export = has_export or token == "@export" or token.begins_with("@export_")
			remaining = remaining.substr(annotation.get_end()).strip_edges()
			if remaining.begins_with("("):
				var rest := _consume_arguments(remaining.substr(1), 1)
				annotation_depth = rest["depth"]
				remaining = rest["tail"].strip_edges()
				if annotation_depth > 0:
					break
		if annotation_depth > 0 or remaining.is_empty():
			continue
		var member := _member_regex.search(remaining)
		if member != null and has_export and not pending_label.is_empty():
			labels[member.get_string(1)] = pending_label
		# Any real declaration consumes the marker, including non-exported variables.
		pending_label = ""
		has_export = false
	return labels


func _consume_arguments(text: String, starting_depth: int) -> Dictionary:
	var depth := starting_depth
	for index in text.length():
		if text[index] == "(":
			depth += 1
		elif text[index] == ")":
			depth -= 1
			if depth == 0:
				return {"depth": 0, "tail": text.substr(index + 1)}
	return {"depth": depth, "tail": ""}


func _mask_strings_and_comments(line: String, state: Dictionary) -> String:
	var result := ""
	var index := 0
	while index < line.length():
		var quote: String = state["quote"]
		var character := line[index]
		if not quote.is_empty():
			var delimiter := quote.repeat(3) if state["triple"] else quote
			if character == "\\":
				result += "  "
				index += 2
				continue
			if line.substr(index, delimiter.length()) == delimiter:
				result += " ".repeat(delimiter.length())
				index += delimiter.length()
				state["quote"] = ""
				state["triple"] = false
				continue
			result += " "
		elif character == "#":
			break
		elif character == "\"" or character == "'":
			var triple := line.substr(index, 3) == character.repeat(3)
			state["quote"] = character
			state["triple"] = triple
			var width := 3 if triple else 1
			result += " ".repeat(width)
			index += width
			continue
		else:
			result += character
		index += 1
	return result
