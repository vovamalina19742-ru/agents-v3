---
name: skill-video-workflow-automator
description: Screen recording & video workflow automation engine using FFmpeg frame slicing, audio narration analysis, and automated script generation.
version: 1.0.0
last_verified_date: 2026-09-08
success_rate: 100%
---

# 🎬 Video Workflow Automator & Screen-to-Code Engine

Автоматический разбор видеозаписей рутинных действий пользователя на экране. Извлекает ключевые кадры (0.5 fps), звуковое сопровождение (Whisper) и генерирует готовые автоматизирующие Python/Shell скрипты.

---

## 🔬 Архитектура пайплайна

1. **FFmpeg Slicing:** Нарезка видео на кадры с частотой 1 кадр / 2 сек в защищенную изолированную директорию.
2. **Audio Track Extraction:** Извлечение 16kHz WAV аудиодорожки для локальной транскрибации через Whisper.
3. **Workflow Reconstruction:** Восстановление последовательности действий (клики, формы, API-эндпоинты).
4. **Script Generation:** Автоматическая генерация Python/Shell скриптов автоматизации.

---

## 🛠 Запуск инструмента

```python
from media-downloader.research.video_workflow_automator import VideoWorkflowAutomator

automator = VideoWorkflowAutomator()
result = automator.process("path/to/screen_recording.mp4", fps=0.5)

print("Восстановленные шаги:", result["reconstructed_steps"])
print("Скрипт автоматизации:\n", result["automation_scripts"]["python"])
```
