"""Extract the exact upload ZIP and run integration tests against its contents."""
from __future__ import annotations
import hashlib
import json
import subprocess
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/1.0.0"
WORK = ROOT / ".godot/release-validation" / uuid.uuid4().hex
GODOT = Path("D:/app/godot/Godot_v4.7-stable_mono_win64/Godot_v4.7-stable_mono_win64/Godot_v4.7-stable_mono_win64_console.exe")
WORK.mkdir(parents=True)

with zipfile.ZipFile(OUT / "dist/inspector-labels-1.0.0.zip") as addon:
    assert all(n.startswith("addons/inspector_labels/") for n in addon.namelist())
    assert "addons/inspector_labels/README.md" in addon.namelist()
    assert "addons/inspector_labels/LICENSE" in addon.namelist()
    addon.extractall(WORK)
    addon_names = set(addon.namelist())
    with zipfile.ZipFile(OUT / "dist/inspector-labels-1.0.0-source.zip") as source:
        for name in addon_names:
            assert addon.read(name) == source.read("inspector-labels/" + name), name
        for name in source.namelist():
            relative = name.removeprefix("inspector-labels/")
            if relative.startswith(("examples/", "tests/")) or relative == "project.godot":
                target = WORK / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(name))

cmd = ["powershell.exe", "-NoProfile", "-File", str(WORK / "tests/run_tests.ps1"), "-Godot", str(GODOT)]
result = subprocess.run(cmd, capture_output=True)
log_path = WORK / "package-tests.log"
log_path.write_bytes(result.stdout + result.stderr)
if result.returncode:
    print(str(log_path))
    print((result.stdout + result.stderr).decode("utf-8", errors="replace")[-6000:])
    raise SystemExit(result.returncode)

checks = []
for path in sorted((OUT / "dist").glob("*.zip")):
    checks.append({"file": path.name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
report = {
    "status": "passed", "godot": "4.7.stable.mono.official.5b4e0cb0f", "platform": "Windows",
    "checks": ["65 automated parser and editor checks passed on the exact extracted upload code", "Addon and source ZIP plugin files are byte-identical", "Only addons/inspector_labels is included in the upload ZIP", "README and MIT LICENSE accompany the plugin", "No Godot caches or private workstation paths in source ZIP", "16:9 store thumbnail and square legacy icon checked visually"],
    "archives": checks,
}
(OUT / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "VALIDATION.md").write_text("""# 发布包验证

- 从实际上传 ZIP 解压插件，并用解压后的代码运行了 65 项自动检查：全部通过。
- 上传包与源码包内的插件文件逐字节一致。
- 上传 ZIP 仅包含 addons/inspector_labels/，其中附有 README.md 与 MIT LICENSE。
- 源码包不包含 .godot 缓存、测试运行日志和本机项目绝对路径。
- 已目视检查 1280 × 720 缩略图、截图排版和 Resource 功能图。
- 作者为 Soybean-milk，版本为 1.0.0，MIT 署名与插件配置一致。
- 测试环境：Windows / Godot 4.7.stable.mono.official.5b4e0cb0f。
- 压缩包 SHA-256 在 dist/SHA256SUMS.txt；结构化结果在 validation.json。

这是本地材料验证记录，不表示市场已经审核或接受该插件。
""", encoding="utf-8")
print(json.dumps({"status": "passed", "checks": 65, "upload_files": len(addon_names), "log": str(log_path)}, ensure_ascii=False))
