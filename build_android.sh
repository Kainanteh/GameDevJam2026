#!/bin/bash
set -e

# Use local workspace config for Godot editor settings to locate Java SDK and Android SDK
export XDG_CONFIG_HOME="$(pwd)/.config"

echo "=== 1. Exporting project assets via Godot ==="
godot --headless --export-release "Android" build/android/game.apk --install-android-build-template

echo "=== 2. Enforcing portrait orientation in AndroidManifest templates ==="
for manifest in android/build/src/main/AndroidManifest.xml android/build/src/debug/AndroidManifest.xml; do
  if [ -f "$manifest" ]; then
    sed -i 's/android:screenOrientation="landscape"/android:screenOrientation="portrait"/g' "$manifest"
  fi
done
python3 -c '
import os, re
manifests = ["android/build/src/main/AndroidManifest.xml", "android/build/src/debug/AndroidManifest.xml"]
for manifest in manifests:
    if os.path.exists(manifest):
        with open(manifest, "r") as f:
            text = f.read()
        
        # Encontrar la etiqueta <activity-alias ... .GodotAppLauncher ... >
        pattern = r"(<activity-alias[^>]*android:name=\".GodotAppLauncher\"[^>]*)(>)"
        match = re.search(pattern, text)
        if match:
            tag_content = match.group(1)
            # Limpiar cualquier atributo duplicado o previo de orientacion y tools:replace
            tag_content = re.sub(r"\s+android:screenOrientation=\"[^\"]+\"", "", tag_content)
            tag_content = re.sub(r"\s+tools:replace=\"[^\"]+\"", "", tag_content)
            # Añadir exactamente una instancia de cada uno de forma limpia
            tag_content += "\n            tools:replace=\"android:screenOrientation\"\n            android:screenOrientation=\"portrait\""
            text = text.replace(match.group(0), tag_content + ">")
            
        # Enforce Internet Permission for leaderboards
        if "android.permission.INTERNET" not in text:
            text = text.replace("<application", "<uses-permission android:name=\"android.permission.INTERNET\" />\n    <application", 1)

        with open(manifest, "w") as f:
            f.write(text)

# Patch GodotApp.java to force portrait orientation at OS level
java_file = "android/build/src/main/java/com/godot/game/GodotApp.java"
if os.path.exists(java_file):
    with open(java_file, "r") as f:
        content = f.read()
    if "public void setRequestedOrientation" not in content:
        old_block = "\t@Override\n\tpublic void onCreate(Bundle savedInstanceState) {\n\t\tSplashScreen.installSplashScreen(this);\n\t\tEdgeToEdge.enable(this);\n\t\tsuper.onCreate(savedInstanceState);\n\t}"
        new_block = "\t@Override\n\tpublic void setRequestedOrientation(int requestedOrientation) {\n\t\tsuper.setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);\n\t}\n\n\t@Override\n\tpublic void onCreate(Bundle savedInstanceState) {\n\t\tsetRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);\n\t\tSplashScreen.installSplashScreen(this);\n\t\tEdgeToEdge.enable(this);\n\t\tsuper.onCreate(savedInstanceState);\n\t}"
        content = content.replace(old_block, new_block)
        with open(java_file, "w") as f:
            f.write(content)
'

echo "=== 3. Compiling Android APK with Gradle (JDK 17) and signing ==="
export JAVA_HOME="/home/kainanteh/Android/jdk17"
export ANDROID_HOME="/home/kainanteh/Android/Sdk"
cd android/build
./gradlew assembleStandardRelease \
  -Pperform_signing=true \
  -Pperform_zipalign=true \
  -Pexport_enabled_abis="arm64-v8a" \
  -Prelease_keystore_file="/home/kainanteh/game-dev-jam-2026/android/release.keystore" \
  -Prelease_keystore_password="iwwyaaysbwia_secret" \
  -Prelease_keystore_alias="iwwyaaysbwia"

echo "=== 4. Copying final Signed Portrait APK to destination ==="
cd ../..
cp android/build/build/outputs/apk/standard/release/android_release.apk build/android/IWWYAAYSBWIA.apk

echo "=== Success! Android Portrait APK built and signed at: build/android/IWWYAAYSBWIA.apk ==="
