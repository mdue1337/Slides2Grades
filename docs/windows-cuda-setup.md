# Windows: cuBLAS/cuDNN setup for transcription

`scripts/transcribe.py` has no CPU fallback (by design — see CLAUDE.md), so
`WHISPER_DEVICE=cuda` requires a working CUDA runtime. On Windows, a driver alone
(check with `nvidia-smi`) is not enough — `faster-whisper`'s `ctranslate2` backend
needs the CUDA 12 cuBLAS/cuDNN *runtime libraries*, and unlike Linux, Windows won't
find them automatically even after `pip install -r requirements.txt`.

## Symptom

```
RuntimeError: Library cublas64_12.dll is not found or cannot be loaded
```

This happens even with a recent NVIDIA driver and successful `nvidia-smi` output,
because the driver ships GPU support, not the CUDA 12 userspace libraries
`ctranslate2` links against.

## Fix

Install the redistributable NVIDIA wheels (lighter than the full CUDA Toolkit
installer) and put their DLL directories on `PATH`:

```powershell
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Then add these to your **user** `PATH` (adjust the Python version segment to match
your interpreter):

```
%LOCALAPPDATA%\Python\pythoncore-<version>\Lib\site-packages\nvidia\cublas\bin
%LOCALAPPDATA%\Python\pythoncore-<version>\Lib\site-packages\nvidia\cudnn\bin
```

Via PowerShell (persists across sessions; a new terminal is required to pick it up):

```powershell
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = $userPath + ";<cublas\bin path>;<cudnn\bin path>"
setx PATH $newPath
```

Note: `setx` silently truncates the written value at 1024 characters. Check
`[Environment]::GetEnvironmentVariable("Path", "User").Length` first — if you're
close to the limit, use `[Environment]::SetEnvironmentVariable("Path", $newPath,
"User")` instead, which has no such limit.

## Why this isn't in the main setup instructions

This repo is also used on Linux, where pip-installed NVIDIA wheels are typically
discoverable without a manual `PATH` step. This doc is Windows-machine-specific
rather than folded into the shared `README.md` Setup section.
