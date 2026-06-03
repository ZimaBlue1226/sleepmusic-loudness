# sleepmusic-loudness

[中文版](./README.zh.md) | [English](./README.md)

一个自包含的 Claude Code / Agent skill，用 FFmpeg 测量、判断和调整 **VelaSleep Sleep Music** 最终音频响度。

它面向 `audio_generation/sleepmusic/` 下的长时睡眠铺底音乐，适用于 `lofi`、`ambient`、`piano` 以及后续可能新增的 sleepmusic 风格流派，不只服务 lofi。

---

## 文件分工

本包同时包含**给人看的文档**和**给 agent 看的指令**，不要混淆：

| 文件 | 读者 | 作用 |
|---|---|---|
| `README.md` / `README.zh.md` | **人** | 安装、用法、自定义说明。Agent 运行时不读它们。 |
| `SKILL.md` | **Agent** | Skill 的执行指令与触发元数据。 |
| `scripts/sleepmusic_loudness.py` | **Agent 可执行辅助脚本** | 测响度、生成试听版、保留 44.1 kHz 输出，并打印可填表检查信息。 |
| `agents/openai.yaml` | **Codex UI 元数据** | 展示名称、简短描述和默认提示。 |

> 一句话：**README 给人看，`SKILL.md` 给 agent 看**；Python 脚本是 agent 用来稳定执行 FFmpeg 流程的确定性辅助工具。

---

## 它做什么

这个 skill 支持两类操作：

1. **测量** sleepmusic 音频文件，输出 LUFS / true peak / LRA / 采样格式等信息。
2. **生成** 安静的响度调整试听版，使用 FFmpeg `loudnorm`，不覆盖源文件，并遵守 VelaSleep 命名规则。

每次完成后都会输出可直接填入表格的字段：

```text
实测文件：
响度优化目标：
综合响度 Integrated LUFS：
True Peak dBTP：
LRA 动态范围：
响度门限：
采样率：
声道：
位深：
时长：
```

---

## 目录结构

本仓库的**根目录就是 skill 包本身**——`SKILL.md` 在仓库顶层，而不是套在某个子文件夹里。skill 名、仓库名、clone 出来的文件夹名三者一致，都是 `sleepmusic-loudness`。

```
sleepmusic-loudness/                    # 仓库根目录 = skill 包 = clone 出来的目录
  README.md                             # 给人看的文档，英文
  README.zh.md                          # 给人看的文档，中文
  SKILL.md                              # 给 agent 看的执行指令：触发元数据 + 工作流
  agents/
    openai.yaml                         # Codex UI 元数据
  scripts/
    sleepmusic_loudness.py              # FFmpeg 辅助脚本
```

这个包是可移植的。它不依赖 VelaSleep 仓库路径，但示例会使用 VelaSleep 的 `audio_generation/sleepmusic/<style>/<Music Title>/` 结构。

---

## 依赖

- Python 3.10+
- FFmpeg 和 FFprobe 在 `PATH` 中可用，或安装在辅助脚本已知的本地路径之一：
  - `D:\ffmpeg-8.1.1-essentials_build\bin`
  - `C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin`

---

## 安装

> 这是**私密**仓库。先配好 git 认证（被加为协作者 + `gh auth login` / SSH key / PAT），否则 clone 和 `npx skills add` 都会失败。

Skill 最终必须以一个名为 `sleepmusic-loudness` 的文件夹存在于可被发现的 skills 目录中。

### A. 人工安装 —— 给人看

clone 仓库后直接复制进 skills 目录：

```bash
git clone https://github.com/ZimaBlue1226/sleepmusic-loudness.git

# 个人 Codex skills
cp -r sleepmusic-loudness ~/.codex/skills/
```

如果希望在 clone 里改动能实时生效，可用软链代替复制。

### B. 自动安装 —— 给 agent 看

跨 agent 安装器会识别根目录的 `SKILL.md`，并按其 frontmatter `name` 安装：

```bash
npx skills add https://github.com/ZimaBlue1226/sleepmusic-loudness
```

如果你是正在**手动**安装本 skill 的 agent，请遵循以下指令：

- 这是一个**自包含 skill**，且**仓库根目录即 skill**。
- 把仓库内容放进目标 agent skills 目录下的 `sleepmusic-loudness/` 文件夹。
- 入口文件是 `SKILL.md`。
- `SKILL.md`、`agents/` 和 `scripts/` 必须保持在一起。
- **不要**靠读 `README.md` / `README.zh.md` 来运行 skill——它们是给人看的文档。运行只依据 `SKILL.md`。

---

## 用法

测量：

```powershell
python scripts/sleepmusic_loudness.py measure "E:\path\to\audio.wav"
```

生成更保守的睡眠铺底试听版：

```powershell
python scripts/sleepmusic_loudness.py render "E:\path\to\audio.wav" --i -22 --tp -2 --lra 11
```

生成命名规则：

```text
音乐名-YYYYMMDDHHMM.wav
```

音乐名默认取父级目录名，符合 VelaSleep 当前结构：

```text
audio_generation/sleepmusic/<style>/<Music Title>/<Music Title>-YYYYMMDDHHMM.wav
```

---

## 自定义

修改工作流口径、响度目标建议或收尾检查字段时，编辑 `SKILL.md`。

只有当 FFmpeg 命令行为、文件命名逻辑或检查字段打印格式需要改变时，才编辑 `scripts/sleepmusic_loudness.py`。改完任何文件后记得重新 push 仓库，保持安装同步。
