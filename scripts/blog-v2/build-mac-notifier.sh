#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
  echo 'Usage: build-mac-notifier.sh /path/to/OPCBlogNotifier.app' >&2
  exit 1
fi
app="$1"
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$app/Contents/MacOS"
cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>com.oakpark.blogreview.notifier</string>
<key>CFBundleExecutable</key><string>OPCBlogNotifier</string>
<key>CFBundleName</key><string>OPC Blog Review</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>LSUIElement</key><true/>
</dict></plist>
PLIST
cache_dir="$(dirname -- "$app")/swift-module-cache"
mkdir -p "$cache_dir"
CLANG_MODULE_CACHE_PATH="$cache_dir" swiftc -module-cache-path "$cache_dir" -parse-as-library -O "$source_dir/mac-notifier.swift" -o "$app/Contents/MacOS/OPCBlogNotifier"
codesign --force --sign - "$app"
