---
id: hugo
name: Hugo（静态博客）
layer: service
priority: P2
requires: {arch: [x86_64, aarch64], substrate: [bare-metal, vm, container]}
conflicts: []
risk: none
needs_human: false
verify: |
  # 从【另一台设备】访问（站点是静态文件，本机测不出反代/路径配错）
  curl -s -o /dev/null -w '%{http_code}\n' https://blog.example.com/
  # 期望: 200
  # 再点开一篇文章和一个标签页——首页能开不代表路由和相对路径是对的
rollback: |
  # 改回反代的上一份配置即可；静态文件删不掉源码
---

# Hugo

静态站点生成器。**它不是常驻服务**——这一点决定了它和本目录里其它服务完全不同。

## 形态

```
Markdown 源文件  →  hugo 构建  →  一堆静态 HTML/CSS/JS  →  由反向代理直接提供
```

所以：

- **没有需要常驻的进程**，没有数据库，没有内存占用
- **攻击面几乎为零**——没有动态代码在跑
- 备份就是备份源码（进 git 就行）

## 构建放哪

本地构建后同步产物、服务器上定时拉源码构建、CI 构建后推送——三种都行，按习惯选。
**服务器上只需要能提供静态文件，不需要装 Hugo。**

## 架构

单个二进制，各架构都有官方构建。
