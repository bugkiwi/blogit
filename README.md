# Blogit

把最近的 Codex 或 Claude 编程会话，整理成一篇有事实依据、以第一人称讲述的 Markdown 文章。

Blogit 不会简单地把聊天记录压缩成摘要。它会从会话里找出真正值得写的主线：最初的问题、改变判断的证据、关键决策、踩过的坑，以及读者可以复用的经验。生成过程中会先让你选择会话，再确认标题和大纲，最后才写完整文章。

## 它能做什么

- 发现本机最近的 Codex 或 Claude 会话；
- 只提取用户和助手可见的对话，过滤系统提示、推理、工具调用和工具输出；
- 将多个相关会话合并为同一篇文章；
- 默认写成 1,200–2,000 字的第一人称 Markdown；
- 每篇文章都带固定的 YAML front matter，包括标题、日期、描述、标签、slug 和草稿状态；
- 默认将 Markdown 和相对路径图片资源整理到用户的 Documents/blogit 目录，也支持指定其他文件夹；
- 在写作前提供 2–3 个标题、核心观点、读者定位和分节大纲；
- 对敏感内容进行脱敏，并区分已验证事实与尚未证实的判断；
- 只在确实有助于解释架构、状态变化或前后对比时规划配图。

## 工作流程

```text
发现最近会话 → 你选择会话 → 提取可见对话 → 找到文章主线
      → 你确认标题与大纲 → 撰写文章 → 隐私与事实核查 → 输出 Markdown
```

Blogit 会在两个关键节点停下来等你确认：

1. 选择要使用的会话；
2. 批准标题、核心观点和大纲。

这样可以避免选错历史记录，也不会在方向尚未确定时直接生成一篇长文。

在客户端提供真正的原生多选工具时，第一步会直接使用客户端的多选 UI。Blogit 会检查工具能力，而不是只根据“桌面端”作判断；如果客户端只支持单选，或没有暴露结构化提问工具，则自动降级为编号文本选择，不会用 Markdown 复选框模拟界面。

## 安装

### 环境要求

- 支持 Skills 的 Codex App、Codex CLI 或 IDE 扩展；
- Python 3.10 或更高版本；
- 本机已有 Codex 或 Claude 的会话记录。

先检查 Python 版本：

```bash
python3 --version
```

如果版本低于 3.10，请先安装新版本，并确保终端中的 `python3` 指向该版本。Blogit 只使用 Python 标准库，不需要额外安装依赖。

### 让 Codex 安装（推荐）

在 Codex 中发送下面这句话：

```text
使用 $skill-installer 从 https://github.com/bugkiwi/blogit/tree/main/skills/blogit 安装 Blogit。
```

安装器会在临时目录下载仓库，只把 `skills/blogit` 中的运行时文件放入 Skills 目录，不会保留 Git 历史、README 或测试文件。安装完成后，在下一条消息中即可使用 `$blogit`。

如果 Blogit 没有出现在 Skill 列表中，请重启 Codex；在 Codex CLI 或 IDE 中也可以使用 `/skills` 检查是否已发现。

### 使用 Skills CLI

如果你希望用命令行安装，并且需要方便地更新或卸载，可以使用开源的 [Skills CLI](https://github.com/vercel-labs/skills)。它需要 Node.js 18 或更高版本。

安装到当前用户，供 Codex 在所有项目中使用：

```bash
npx skills add bugkiwi/blogit --skill blogit --global --agent codex --yes
```

更新到最新版本：

```bash
npx skills update blogit --global --yes
```

卸载：

```bash
npx skills remove blogit --global --yes
```

只想在当前项目中启用时，去掉 `--global`：

```bash
npx skills add bugkiwi/blogit --skill blogit --agent codex --yes
```

Skills CLI 会把真正的 Skill 子目录作为安装单元，因此上述命令同样不会把仓库的 README、tests 或 `.git` 目录装进去。

### 从本地源码开发

如果你正在修改 Blogit，可以使用软链接，改动会立即生效：

```bash
git clone https://github.com/bugkiwi/blogit.git
cd blogit
mkdir -p "$HOME/.agents/skills"
ln -s "$(pwd)/skills/blogit" "$HOME/.agents/skills/blogit"
```

如果目标路径已经存在，请先确认它是否是旧版本或已有软链接，再自行决定是否替换。

Codex 支持用户级和项目级 Skill，也会跟随指向 Skill 目录的软链接。目录选择规则见 [Codex Skills 官方文档](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)。

## 使用方法

在 Codex 中直接提到 `$blogit`，并说明想写什么即可：

```text
使用 $blogit，把我最近一次排查缓存失效的 Codex 会话写成中文技术文章。
面向有后端经验的工程师，控制在 1500 字左右，不需要配图。
```

也可以让 Blogit 从多个会话中寻找同一条主线：

```text
使用 $blogit，把最近几次关于重试和幂等性的 Claude 会话整理成一篇文章。
先帮我判断哪些会话适合合并，不相关的不要硬凑在一起。
```

如果没有显式写 `$blogit`，当你的请求明确提到“根据最近的 Codex/Claude 会话写博客、复盘或技术文章”时，Codex 也可以自动启用它。

## 完整示例

下面是一段典型交互。会话标题和 ID 仅为示意。

**你：**

```text
使用 $blogit，把我最近修复重复扣款问题的工作写成一篇中文技术文章。
读者是做支付系统的后端工程师。
```

**Blogit：**

```text
最近的会话：

1. Add idempotency keys         2026-07-12  payments-api
2. Debug duplicate charges      2026-07-11  payments-api
3. Update landing page          2026-07-10  marketing-site

请选择一个或多个编号。
```

**你：**

```text
选 1 和 2。第三个不要。
```

**Blogit：**

```text
标题候选：
1. 一次重复扣款事故，让我重新理解了幂等性
2. 重试不是再执行一次：支付接口的幂等改造
3. 从重复扣款到安全重放：我给支付接口补上的约束

核心观点：可靠的重试不只依赖一个幂等键，还需要稳定的请求身份、
原子写入，以及对“处理中”状态的明确处理。

大纲：
1. 重复扣款是如何出现的
2. 第一个方案为什么仍然有竞态
3. 幂等记录与业务写入如何保持原子性
4. 用重放测试证明修复有效
5. 可以复用到其他系统的检查清单

配图：无
输出：~/Documents/blogit/payments-idempotency.md
```

**你：**

```text
用标题 2，大纲通过。
```

Blogit 随后会生成文章，并返回最终标题、文件路径、近似字数，以及必要的脱敏或未验证信息说明。

生成的 Markdown 会从下面的固定结构开始，字段顺序保持不变：

```yaml
---
title: xxx
date: YYYY-MM-DD
description: yyy
tags: [aaa, bbb, ]
slug: xxxxx
draft: true
---
```

其中 `xxx`、`yyy`、标签和 slug 会替换为文章的实际内容，`draft` 默认保持为布尔值 `true`。macOS 和 Linux 默认输出到 `~/Documents/blogit/<slug>.md`；Windows 默认使用当前用户的 Documents 已知文件夹下的 `blogit\<slug>.md`。如果文章需要图片，则保存到同一输出根目录的 `assets/<slug>/`，Markdown 使用相对路径引用。用户在请求中指定的目录始终优先。

## 底层命令

通常不需要手动运行脚本，Codex 会按照 `SKILL.md` 完成这些步骤。排查会话发现或解析问题时，可以直接使用 CLI。

列出最近十个 Codex 会话：

```bash
python3 skills/blogit/scripts/blogit.py list --agent codex --limit 10
```

列出最近十个 Claude 会话：

```bash
python3 skills/blogit/scripts/blogit.py list --agent claude --limit 10
```

提取一个或多个会话中的可见对话：

```bash
python3 skills/blogit/scripts/blogit.py extract \
  --agent codex \
  --session <session-id-1> \
  --session <session-id-2> \
  --output /tmp/blogit-transcript.md
```

如需指定非默认配置目录，可在 `list` 或 `extract` 后增加 `--home <path>`。

## 隐私说明

会话历史可能包含代码、内部地址、账号信息或其他敏感内容。Blogit 的解析器只读取本机会话文件，并过滤系统提示、隐藏推理、工具调用、工具结果和附件占位内容；写作流程还要求在分析前移除凭据、令牌、私钥、个人联系方式、内部 URL 和无关隐私信息。

解析器本身不会把会话内容发送给搜索、图片生成或其他第三方工具。生成的临时对话文件也不会包含在最终回复中。即便如此，发布文章前仍建议人工检查一次正文和生成的资源。

## 开发与测试

```bash
python3 -m unittest discover -s tests -v
```

项目结构：

```text
blogit/
├── README.md
├── skills/blogit/          # 实际安装的精简 Skill 目录
│   ├── SKILL.md            # Skill 的核心工作流
│   ├── agents/openai.yaml  # Codex UI 元数据
│   ├── scripts/            # 会话发现、提取与解析 CLI
│   └── references/         # 写作与格式适配说明
└── tests/                  # 仓库测试，不进入安装目录
```
