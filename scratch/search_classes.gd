extends SceneTree

func _init():
	print("Classes found:")
	var classes = ClassDB.get_class_list()
	for c in classes:
		if "Export" in c:
			print(c)
	quit()
