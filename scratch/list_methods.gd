extends SceneTree

func _init():
	var platform = ClassDB.instantiate("EditorExportPlatformAndroid")
	if not platform:
		print("Could not instantiate EditorExportPlatformAndroid")
		quit()
		return
	print("Methods:")
	var methods = platform.get_method_list()
	for m in methods:
		if "option" in m.name.to_lower() or "preset" in m.name.to_lower() or "export" in m.name.to_lower():
			print(m.name)
	quit()
