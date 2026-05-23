extends SceneTree

func _init():
	var platform = ClassDB.instantiate("EditorExportPlatformAndroid")
	if not platform:
		print("Could not instantiate EditorExportPlatformAndroid")
		quit()
		return
	print("Properties:")
	var properties = platform.get_property_list()
	for p in properties:
		print(p)
	quit()
