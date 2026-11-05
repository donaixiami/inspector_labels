"""Build local publishing materials from verified source and real editor captures."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "1.0.0"
AUTHOR = "Soybean-milk"
VERSION = "1.0.0"
BG = "#151b26"
FG = "#eef3fa"
MUTED = "#9aaabd"
ACCENT = "#66d6be"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def font(size: int, bold: bool = False, mono: bool = False):
    filename = "consolab.ttf" if mono and bold else "consola.ttf" if mono else "msyhbd.ttc" if bold else "msyh.ttc"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / filename), size)


def title(draw, position, text, size=32, fill=FG, bold=False, mono=False):
    draw.text(position, text, font=font(size, bold, mono), fill=fill)


def remove_cursor(image, box, ref_x):
    """Paint over the mouse cursor and its hover glow with each row's plain background.

    Rows in the Inspector are a single flat color, sampled from columns ref_x to the right."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        samples = sorted(image.getpixel((x, y)) for x in ref_x)
        color = samples[len(samples) // 2]
        for x in range(x0, x1):
            image.putpixel((x, y), color)


def make_media() -> None:
    media = OUT / "media"
    media.mkdir(parents=True, exist_ok=True)
    main = Image.open(ROOT / ".godot/publish-capture-main.png").convert("RGB")
    resource = Image.open(ROOT / ".godot/publish-capture-resource.png").convert("RGB")
    if main.size != (2560, 1392) or resource.size != (2560, 1392):
        raise ValueError("Capture dimensions changed; inspect and update crop bounds.")

    # Real screenshot crops. Exclude desktop overlays and irrelevant editor panes.
    main.crop((177, 99, 2552, 1002)).save(media / "screenshot-01-editor.png")
    code = main.crop((447, 272, 1025, 699))
    inspector = main.crop((2071, 210, 2551, 767))
    panel = Image.new("RGB", (1280, 720), BG)
    draw = ImageDraw.Draw(panel)
    title(draw, (40, 25), "Inspector Labels", 32, bold=True)
    title(draw, (41, 80), "GDScript comments", 20, MUTED)
    title(draw, (760, 80), "Native Inspector", 20, MUTED)
    code = code.resize((650, 480), Image.Resampling.LANCZOS)
    panel.paste(code, (40, 130))
    panel.paste(inspector, (760, 130))
    title(draw, (40, 650), "Real Godot 4.7 editor captures · cropped views", 17, MUTED)
    panel.save(media / "screenshot-02-comments-and-labels.png")

    # The cursor was left over the 武器配置 row in the capture; the label text ends at x=2152.
    remove_cursor(resource, (2153, 540, 2224, 690), range(2245, 2266))
    detail = resource.crop((2070, 420, 2542, 950))  # Top at 420 so the 外观与资源 header isn't clipped.
    card = Image.new("RGB", (1280, 720), BG)
    draw = ImageDraw.Draw(card)
    title(draw, (54, 56), "Resources & inheritance", 34, bold=True)
    title(draw, (54, 135), "Labels also apply to", 26)
    title(draw, (54, 177), "custom Resource exports", 26)
    title(draw, (54, 245), "and parent-script properties.", 23, MUTED)
    title(draw, (54, 602), "Godot 4.7 · real Inspector crop", 18, MUTED)
    card.paste(detail.resize((520, 584), Image.Resampling.LANCZOS), (706, 73))
    card.save(media / "screenshot-03-resources.png")

    # Original icon drawn from simple vector-style geometry; no Godot logo is used.
    scale = 2
    icon = Image.new("RGB", (512 * scale, 512 * scale), BG)
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((72*scale, 58*scale, 440*scale, 454*scale), radius=30*scale, fill="#222d3d", outline="#3e536d", width=3*scale)
    d.line((104*scale, 127*scale, 408*scale, 127*scale), fill="#3e536d", width=3*scale)
    for x in (112, 138, 164):
        d.ellipse(((x-5)*scale, 92*scale, (x+5)*scale, 102*scale), fill=ACCENT)
    d.rounded_rectangle((104*scale, 165*scale, 408*scale, 281*scale), radius=15*scale, fill=ACCENT)
    d.text((120*scale, 184*scale), "# label", font=font(55*scale, True, True), fill=BG)
    d.line((122*scale, 330*scale, 230*scale, 330*scale), fill="#becbdd", width=10*scale)
    d.line((122*scale, 380*scale, 210*scale, 380*scale), fill="#becbdd", width=10*scale)
    d.rounded_rectangle((278*scale, 310*scale, 388*scale, 350*scale), radius=8*scale, fill="#11212b", outline=ACCENT, width=2*scale)
    d.rounded_rectangle((278*scale, 361*scale, 388*scale, 401*scale), radius=8*scale, fill="#11212b", outline=ACCENT, width=2*scale)
    icon.resize((512, 512), Image.Resampling.LANCZOS).save(media / "icon-512.png")

    thumb = Image.new("RGB", (1280, 720), BG)
    thumb.paste(icon.resize((260, 260), Image.Resampling.LANCZOS), (98, 87))
    draw = ImageDraw.Draw(thumb)
    title(draw, (73, 371), "Inspector", 52, bold=True)
    title(draw, (73, 438), "Labels", 52, bold=True)
    focus = main.crop((2071, 210, 2551, 424))
    focus = focus.resize((720, 321), Image.Resampling.LANCZOS)
    thumb.paste(focus, (503, 232))
    thumb.save(media / "thumbnail-1280x720.png")
    icon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<rect width="512" height="512" fill="#151b26"/><rect x="72" y="58" width="368" height="396" rx="30" fill="#222d3d" stroke="#3e536d" stroke-width="3"/>
<path d="M104 127H408" stroke="#3e536d" stroke-width="3"/>
<g fill="#66d6be"><circle cx="112" cy="97" r="5"/><circle cx="138" cy="97" r="5"/><circle cx="164" cy="97" r="5"/><rect x="104" y="165" width="304" height="116" rx="15"/></g>
<text x="120" y="244" font-family="Consolas,monospace" font-size="55" font-weight="bold" fill="#151b26"># label</text>
<path d="M122 330H230M122 380H210" stroke="#becbdd" stroke-width="10"/>
<g fill="#11212b" stroke="#66d6be" stroke-width="2"><rect x="278" y="310" width="110" height="40" rx="8"/><rect x="278" y="361" width="110" height="40" rx="8"/></g></svg>'''
    write(media / "icon-source.svg", icon_svg)
    for path in media.glob("*.png"):
        shutil.copy2(path, ROOT / "screenshots" / path.name)
    shutil.copy2(media / "icon-source.svg", ROOT / "screenshots/icon-source.svg")
    write(media / "CAPTIONS.txt", """
thumbnail-1280x720.png — Main feature thumbnail. 1280 × 720, 16:9. Includes an original icon and a real Inspector crop.
icon-512.png — Square icon for the legacy Asset Library. 512 × 512.
screenshot-01-editor.png — Actual Godot editor with GDScript comments and translated Inspector labels; cropped to omit unrelated desktop UI.
screenshot-02-comments-and-labels.png — Two crops from the same real editor capture, placed side by side for readability. The interface content is unmodified.
screenshot-03-resources.png — Real Inspector crop showing custom Resource properties and an inherited property, with explanatory text beside it.
icon-source.svg — Editable source for the simple icon.
""")


EN_README = '''# Inspector Labels

[中文说明](README.zh-CN.md)

Set custom labels for GDScript exports with a `# @label` comment. Keep your variable names, saved property keys, and native Inspector controls unchanged.

```gdscript
# @label 射击间隔
@export var fire_interval: float = 0.1

# @label Maximum health
@export var max_health: int = 5
```

![Comment labels in the Godot Inspector](screenshots/screenshot-02-comments-and-labels.png)

## Features

- Custom labels from comments above exported properties, including Chinese text.
- Native number fields, range sliders, checkboxes, enums, vectors, colors, resource pickers, and arrays.
- Labels inherited from parent scripts and labels on custom Resource exports.
- No `@tool` annotation required on game scripts.
- Ordinary `##` documentation comments remain available as Godot tooltips.
- Refresh after script saves or filesystem reloads; a manual refresh command is also provided.
- Disable the plugin to restore the original labels without changing property values.

## Installation

1. Copy `addons/inspector_labels` into your project's `addons` folder.
2. Enable **Inspector Labels** in **Project > Project Settings > Plugins**.
3. Add `# @label Your label` above an exported variable, save the script, and select the node.

The comment is plugin syntax, not a built-in GDScript annotation. The text is used literally; this is not an automatic translation service.

## Label rules

Put the comment on its own line at script top level. Blank lines, documentation comments and export annotations may appear between the marker and its variable.

```gdscript
# @label Invincibility duration
## Duration in seconds after taking damage.
@export_range(0.0, 5.0, 0.1)
var invincible_duration: float = 0.6
```

`## @label` is also accepted, but `# @label` is recommended to avoid putting the marker in a documentation tooltip. The last consecutive marker wins. Empty labels and unmarked properties use the native name. Labels are read from saved source files.

If the Inspector has not refreshed, reselect the node or use **Project > Tools > 刷新检查器中文标签** (Refresh Inspector Labels).

## Demo and tests

The full source package includes `project.godot` and `examples/demo.tscn`. Import the project, open the scene, and select **Player**. The main store ZIP contains only the installable addon and its standalone documentation.

On Windows, run `tests/run_tests.ps1 -Godot 'path-to-Godot-console.exe'`. Tests execute in an isolated project copy. 35 parser/resource checks and 30 editor integration checks passed on Godot 4.7, including edit, undo/redo, save/reload, plugin disable/enable, and comment-only external saves.

## Compatibility and limitations

- Tested on Windows with Godot 4.7. Pure GDScript; .NET is not required. Other operating systems have not been tested.
- Supports exported variables at script top level. C#, function locals, and variables declared inside nested `class Inner:` blocks are outside this release's scope.
- Does not translate built-in Godot properties, enum options, node names, or individual array elements.
- Other Inspector plugins that take over the same property may affect label display; combined compatibility is not guaranteed.

## Development disclosure

Developed with AI assistance using OpenAI Codex for implementation, documentation, tests, and release preparation. Tests were executed in Godot 4.7. Screenshots are captures of the running editor; the icon and promotional layout were drawn programmatically with AI-authored code.

## License

[MIT](LICENSE) © 2026 Soybean-milk.
'''

ADDON_README = '''# Inspector Labels

Custom Inspector labels from GDScript comments. Tested on Godot 4.7.

## Install

Copy this folder into `addons/inspector_labels` in your Godot project. Enable **Inspector Labels** in **Project > Project Settings > Plugins**.

```gdscript
# @label 射击间隔
@export var fire_interval: float = 0.1

# @label Maximum health
@export var max_health: int = 5
```

The Inspector shows the comment label. Code and saved scenes continue to use `fire_interval` and `max_health`. Game scripts do not need `@tool`. This is literal label replacement, not automatic translation.

Put each marker on its own line at script top level before its exported variable. Blank lines, `##` documentation comments and export annotations may appear in between. `## @label` is accepted too. The last consecutive marker wins; empty labels and unmarked properties keep the native label.

Save the script to update labels. Reselect the node if necessary, or use **Project > Tools > 刷新检查器中文标签** (Refresh Inspector Labels).

Supports native number fields, range sliders, checkboxes, enums, vectors, colors, resources, arrays, and parent-script labels. Disabling the plugin restores native names and preserves values.

Does not cover C#, function locals, nested inner-class variables, built-in Godot property names, or enum/array item labels. Other plugins editing the same property may conflict. Tested on Windows/Godot 4.7; other platforms are unverified.

## 中文用法

1. 将此文件夹放到项目的 `addons/inspector_labels`。
2. 在「项目 → 项目设置 → 插件」启用 Inspector Labels。
3. 在导出变量上方单独写一行 `# @label 中文名称`。
4. 保存脚本，选中节点，检查器就会显示中文。代码中的英文变量名与已有数值不变。

标签不需要引号。支持与 `@export_range`、`@export_enum` 等注解搭配，游戏脚本无需添加 `@tool`。父脚本和自定义 Resource 的导出属性也支持。可通过「项目 → 工具 → 刷新检查器中文标签」手动刷新。

## Development disclosure and license

Implementation, documentation and tests were created with OpenAI Codex assistance. The plugin was tested in Godot 4.7. MIT © 2026 Soybean-milk. The full license is included in `LICENSE` in this folder.
'''

DESCRIPTION_EN = '''Inspector Labels lets you customize how GDScript export names appear in the Godot Inspector using a comment above the variable.

```gdscript
# @label 射击间隔
@export var fire_interval: float = 0.1
```

The Inspector displays 射击间隔 while code and saved scenes continue to use fire_interval.

### Features
- Custom labels, including Chinese text, with one comment.
- Native Inspector controls for numbers, ranges, booleans, enums, vectors, colors, resources and arrays.
- Parent-script labels and custom Resource exports.
- No @tool annotation required on game scripts.
- Save/reload refresh plus a manual refresh command.
- Disabling the plugin restores original labels without changing stored values.

### Installation
Copy addons/inspector_labels into your project and enable Inspector Labels in Project > Project Settings > Plugins. Add a # @label comment above a top-level exported variable, save, and select the node.

### Compatibility
Tested on Windows with Godot 4.7. Pure GDScript; no .NET or compiled dependency. Other operating systems are unverified.

This is literal label replacement, not automatic translation. C#, nested inner-class variables, built-in Godot property names and enum/array item labels are not supported. Other Inspector plugins overriding the same property may affect display.

MIT license. Author: Soybean-milk.
'''

DESCRIPTION_ZH = '''Inspector Labels 是一个 Godot 编辑器插件。只需在导出变量上方写一行注释，就能为检查器设置中文标签，同时保留英文变量名。

```gdscript
# @label 射击间隔
@export var fire_interval: float = 0.1
```

检查器显示「射击间隔」，代码和场景文件仍使用 fire_interval。

支持数字、范围滑块、复选框、枚举、向量、颜色、资源和数组等原生控件；支持父脚本继承和自定义 Resource。游戏脚本无需添加 @tool。

将 addons/inspector_labels 放入项目，在「项目 → 项目设置 → 插件」启用 Inspector Labels 即可。保存脚本后刷新，也可使用「项目 → 工具 → 刷新检查器中文标签」。关闭插件会恢复原生名称，已有数值不变。

已在 Windows / Godot 4.7 验证，纯 GDScript，无需 .NET。其他操作系统尚未验证。

此插件按注释原文显示标签，不提供自动翻译。不处理 C#、内部类变量、Godot 内置属性名、枚举选项或数组元素名称；与其他接管同一属性的检查器插件可能存在冲突。

作者：Soybean-milk。许可证：MIT。
'''


def make_documents() -> None:
    chinese = ROOT / "README.zh-CN.md"
    if not chinese.exists():
        original = (ROOT / "README.md").read_text(encoding="utf-8")
        start = original.index("例如，当前游戏项目的安装目标是：")
        end = original.index("## 先看示例")
        original = original[:start] + "安装时只复制 `addons/inspector_labels`，不需要复制示例项目的 `project.godot`。\n\n" + original[end:]
        write(chinese, original + "\n\nMIT © 2026 Soybean-milk。代码、文档及测试由 OpenAI Codex 辅助编写，已在 Godot 4.7 执行验证。\n")
    write(ROOT / "README.md", EN_README)
    write(ROOT / "addons/inspector_labels/README.md", ADDON_README)
    shutil.copy2(ROOT / "addons/inspector_labels/LICENSE", ROOT / "LICENSE")
    changelog = '''# Changelog

## 1.0.0

Initial release.

- Add custom Inspector labels with # @label comments.
- Support export annotations, parent scripts, and custom Resources.
- Retain native property editors, undo/redo, and original serialized property keys.
- Refresh labels after script saves and filesystem changes.
- Include English and Chinese documentation, an independent demo, and automated tests.

Validated with Godot 4.7 on Windows. Other operating systems have not been tested.
'''
    write(ROOT / "CHANGELOG.md", changelog)
    listing = OUT / "listing"
    write(listing / "summary.en.txt", "Custom Inspector labels from GDScript comments. Keep variable names unchanged and retain native property editors.")
    write(listing / "summary.zh-CN.txt", "用一行注释设置检查器中文标签，保留英文变量名和原生属性编辑控件。")
    write(listing / "description.en.md", DESCRIPTION_EN)
    write(listing / "description.zh-CN.md", DESCRIPTION_ZH)
    write(listing / "changelog.en.md", changelog)
    ai = """OpenAI Codex was used to generate and refine the plugin's GDScript implementation, automated tests, example code, documentation, store copy, and release tooling under the publisher's direction. Automated tests were executed in Godot 4.7, and the plugin was checked in the actual editor. Screenshots are captures of the running Godot editor, cropped and arranged for readability. The simple icon and promotional image layout were produced programmatically with AI-authored code. No generated image is presented as an actual software screenshot. The plugin itself does not call any AI service at runtime."""
    write(listing / "ai-disclosure.en.txt", ai)
    write(listing / "ai-disclosure.zh-CN.txt", "在发布者需求指导下，使用 OpenAI Codex 辅助生成和修改插件的 GDScript 实现、测试、示例、文档、商店文案和发布工具。自动测试已在 Godot 4.7 执行，并在实际编辑器中检查。截图来自真实 Godot 编辑器，只做裁切与排版；图标和宣传图布局由 AI 辅助编写的绘图代码制作。未将生成图片冒充软件运行截图。插件运行时不调用 AI 服务。")
    plain = DESCRIPTION_EN.replace("### ", "").replace("```gdscript\n", "").replace("```", "")
    write(listing / "legacy-description.en.txt", plain + "\nDevelopment disclosure: " + ai)
    metadata = {
        "asset_name": "Inspector Labels", "suggested_asset_slug": "inspector-labels",
        "publisher_display_name": AUTHOR, "publisher_slug": None,
        "publisher_slug_note": "If a publisher already exists for Markdown Docs Viewer, select it; otherwise use Soybean-milk as the display name. Verify the actual slug in your account.",
        "asset_type": "Addon", "legacy_category": "Tools", "license": "MIT",
        "version": VERSION, "minimum_godot_version": "4.7", "maximum_godot_version": None,
        "tested_platform": "Windows", "suggested_tags": ["editor", "tools", "gdscript", "inspector"],
        "tag_note": "Choose existing tags with matching spelling in the store.",
        "source_code_url": None, "issues_url": None, "download_commit": None,
        "ai_usage": True, "ai_disclosure_file": "ai-disclosure.en.txt",
        "upload_zip": "../dist/inspector-labels-1.0.0.zip",
        "thumbnail": "../media/thumbnail-1280x720.png",
        "legacy_icon": "../media/icon-512.png",
        "publication_status": "Local materials prepared; not submitted or published."
    }
    write(listing / "metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    write(OUT / "UPLOAD_GUIDE.zh-CN.md", '''# Inspector Labels 1.0.0 发布材料

作者沿用 Markdown Docs Viewer 的 **Soybean-milk**，许可证沿用 **MIT**。本目录为本地发布材料，尚未提交到市场。

## 直接上传到新版 Godot Asset Store

入口：https://store.godotengine.org/asset/new/

| 页面/字段 | 填写内容或文件 |
| --- | --- |
| Publisher | 若已有用于 Markdown Docs Viewer 的发布者，可选择它；否则创建或选择显示名 Soybean-milk 的发布者 |
| Asset Name | Inspector Labels |
| Asset URL / slug | inspector-labels；最终以网站可用性为准 |
| Asset Summary | 复制 listing/summary.en.txt |
| Detailed description | 复制 listing/description.en.md；可追加 description.zh-CN.md |
| Asset type | Addon |
| License | MIT |
| Tags | editor、tools、gdscript、inspector；优先选网站已有标签 |
| AI usage disclosure | 选择使用了 AI，并复制 listing/ai-disclosure.en.txt |
| Thumbnail | media/thumbnail-1280x720.png，1280 × 720，16:9 |
| Screenshots | media/screenshot-01-editor.png、screenshot-02-comments-and-labels.png、screenshot-03-resources.png |
| Version name | 1.0.0 |
| Version file | dist/inspector-labels-1.0.0.zip |
| Minimum Godot version | 4.7 |
| Maximum Godot version | 留空；不要宣称已经验证未来版本 |
| Changelog | 复制 listing/changelog.en.md |
| Source code / issue URL | 已有真实仓库后填写；本材料没有虚构链接 |

主上传 ZIP 内只有 `addons/inspector_labels/`，包含插件代码、README 和 LICENSE。无需将本发布材料目录整体作为插件上传。

公开条款要求名称、摘要和介绍至少包含英文；AI 使用需披露。新版商店缩略图为 16:9，不能用方形图标代替。每个版本最大 1 GB；本插件远低于此限制。

## 准备 GitHub 源码仓库

`source/inspector-labels/` 是已经整理好的公开源码目录，包括双语 README、MIT LICENSE、CHANGELOG、示例、测试、截图，以及 .gitignore/.gitattributes。

也可解压 `dist/inspector-labels-1.0.0-source.zip` 得到同样内容。将目录内容提交到你实际创建的仓库；建议仓库名 inspector-labels，发布标签 v1.0.0。此处的名字只是建议，不代表已创建仓库或标签。

提供仓库 URL 后，可填写商店的源码与问题反馈链接。仓库没有 .godot 缓存、本机绝对路径、测试日志或第三方游戏素材。

## 如果发布到旧 Godot Asset Library

入口：https://godotengine.org/asset-library/asset

- Asset Name：Inspector Labels；Category：Tools；Godot version：4.7；Version：1.0.0；License：MIT。
- Description：复制 listing/legacy-description.en.txt（纯文本）。
- 必须先托管源码，填写实际 Repository URL 和实际 Download Commit。
- Icon URL：使用 `media/icon-512.png` 对应的公开直链；方形 512 × 512 满足旧库的最低 128 × 128 要求。
- GitHub 图标直链格式为 `https://raw.githubusercontent.com/<账号>/<仓库>/<提交或标签>/screenshots/icon-512.png`。替换全部占位内容后才可提交。
- 三张截图放在源码仓库的 screenshots/ 下，用真实公开 URL 填写预览项。
- .gitattributes 已配置为 Git archive 下载只保留 addons/，源码仓库仍保留说明和截图。

## 最后需要你在网站确认的内容

1. 实际发布者账号和 URL slug；已确认作者显示名为 Soybean-milk。
2. 名称/slug 是否可用。
3. 若填写源码链接，必须使用实际存在的仓库。旧资产库还需真实提交哈希和图片直链。
4. 检查网站预览、阅读当前服务条款，再提交审核。

## 文件校验与来源

dist/SHA256SUMS.txt 保存两个 ZIP 的校验值。VALIDATION.md 保存发布包验证结果。媒体图片的说明在 media/CAPTIONS.txt。

本次规则核对日期：2026-11-02。以当前网站实际表单为准。

- 新商店规则：https://store.godotengine.org/guidelines/
- 新商店提交文档：https://docs.godotengine.org/en/stable/community/asset_store/submitting_to_asset_store.html
- AI 披露说明：https://store.godotengine.org/help/
- 旧资产库提交文档：https://docs.godotengine.org/en/stable/community/asset_library/submitting_to_assetlib.html
''')


def zip_files(path: Path, files: list[tuple[Path, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for file, arcname in sorted(files, key=lambda item: item[1]):
            info = zipfile.ZipInfo(arcname, date_time=(2026, 11, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, file.read_bytes())


def make_packages() -> None:
    source = OUT / "source/inspector-labels"
    source.mkdir(parents=True, exist_ok=True)
    files: list[tuple[Path, str]] = []
    for folder in ("addons", "examples", "tests", "screenshots"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and path.suffix not in (".tmp", ".log"):
                relative = path.relative_to(ROOT)
                dest = source / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                files.append((dest, str(relative).replace("\\", "/")))
    for name in ("project.godot", "README.md", "README.zh-CN.md", "LICENSE", "CHANGELOG.md", ".gitignore", ".gitattributes"):
        shutil.copy2(ROOT / name, source / name)
        files.append((source / name, name))
    addon_files = [(p, n) for p, n in files if n.startswith("addons/inspector_labels/")]
    zip_files(OUT / f"dist/inspector-labels-{VERSION}.zip", addon_files)
    zip_files(OUT / f"dist/inspector-labels-{VERSION}-source.zip", [(p, "inspector-labels/" + n) for p, n in files])
    sums = []
    for archive in sorted((OUT / "dist").glob("*.zip")):
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError("Corrupt ZIP: " + str(archive))
            for name in z.namelist():
                if ".godot/" in name or name.startswith("/") or ".." in Path(name).parts:
                    raise ValueError("Unexpected ZIP entry: " + name)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        sums.append(digest + "  " + archive.name)
    write(OUT / "dist/SHA256SUMS.txt", "\n".join(sums))
    # Public source must not contain private workstation paths.
    for p, _ in files:
        if p.suffix in (".md", ".gd", ".json", ".txt", ".ps1", ".cfg", ".tscn"):
            content = p.read_text(encoding="utf-8-sig")
            if "D:\\app\\godot" in content or str(Path.home()) in content:
                raise ValueError("Private path in public file: " + str(p))
    print(json.dumps({"release": str(OUT), "addon_files": len(addon_files), "source_files": len(files), "archives": [{"name": p.name, "bytes": p.stat().st_size} for p in (OUT / "dist").glob("*.zip")]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    (ROOT / "screenshots").mkdir(exist_ok=True)
    make_media()
    make_documents()
    make_packages()
