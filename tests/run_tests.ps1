param(
    [Parameter(Mandatory = $true)]
    [string]$Godot
)

$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskRun = Join-Path $taskRoot ('.godot/test-runs/' + [guid]::NewGuid().ToString('N'))
$taskAddons = Join-Path $taskRun 'addons'
$taskDriver = Join-Path $taskAddons 'inspector_labels_tests'
$taskTests = Join-Path $taskRun 'tests'
New-Item -ItemType Directory -Path $taskDriver, $taskTests -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $taskRoot 'addons/inspector_labels') -Destination $taskAddons -Recurse
Copy-Item -LiteralPath (Join-Path $taskRoot 'examples') -Destination $taskRun -Recurse
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'test_labels.gd') -Destination $taskTests
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'test_editor.gd') -Destination $taskDriver
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'editor_plugin.cfg') -Destination (Join-Path $taskDriver 'plugin.cfg')
$taskProject = @'
config_version=5
[application]
config/name="Inspector Labels Tests"
config/features=PackedStringArray("4.7", "GL Compatibility")
[editor_plugins]
enabled=PackedStringArray("res://addons/inspector_labels/plugin.cfg", "res://addons/inspector_labels_tests/plugin.cfg")
[rendering]
renderer/rendering_method="gl_compatibility"
'@
[IO.File]::WriteAllText((Join-Path $taskRun 'project.godot'), $taskProject, [Text.UTF8Encoding]::new($false))

& $Godot --headless --editor --path $taskRun --import --log-file (Join-Path $taskRun 'import.log')
if ($LASTEXITCODE -ne 0) { throw 'Godot import failed.' }
& $Godot --headless --path $taskRun --script res://tests/test_labels.gd --log-file (Join-Path $taskRun 'parser.log')
if ($LASTEXITCODE -ne 0) { throw 'Label parser tests failed.' }
& $Godot --headless --editor --path $taskRun --log-file (Join-Path $taskRun 'editor.log') -- --inspector-labels-test
if ($LASTEXITCODE -ne 0) { throw 'Inspector integration tests failed.' }
$taskErrors = Select-String -LiteralPath (Join-Path $taskRun 'import.log'), (Join-Path $taskRun 'parser.log'), (Join-Path $taskRun 'editor.log') -Pattern 'SCRIPT ERROR:|ERROR:'
if ($taskErrors) { $taskErrors | Write-Output; throw 'Errors found in Godot logs.' }
Write-Output "All tests passed. Logs: $taskRun"
