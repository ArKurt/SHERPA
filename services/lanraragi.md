---
id: lanraragi
name: LANraragi
layer: service
priority: P2
category: media
goals: [多媒体影音]
summary: 漫画与图集库
blurb: |
  把压缩包形式的漫画、画集丢进去，它负责整理、生成缩略图、提供在线阅读。
  手机和平板浏览器里直接看，不用先解压再传来传去。
docs:
  - type: official
    title: LANraragi 项目与文档
    url: https://github.com/Difegue/LANraragi
requires: {arch: [x86_64, aarch64], substrate: [bare-metal, vm, container]}
conflicts: []
risk: low
needs_human: false
verify: |
  curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.10:3000/
  # 期望: 200
rollback: |
  docker compose down
---

# LANraragi

漫画 / 图集库，吃压缩包（zip/cbz/rar）而不是解压后的目录。

## 存储

- **内容目录**：宽松，外接盘可以
- **元数据（Redis）**：小，放本地盘

⚠️ 内容目录建议**只读挂载**——它会做元数据提取，只读能避免意外改动源文件。

## 注意

- 首次导入大量压缩包时会有一轮缩略图生成，比较吃 I/O
- 有中文优化的社区分支，按需选择；**用非官方镜像前确认更新活跃度**

## 架构

有 multi-arch 镜像；社区分支不一定，用前确认。
