# 使用 GitHub Actions 自动打包

本项目已配置 GitHub Actions，可以自动在云端生成 Windows 和 macOS 的可执行文件，**无需Mac电脑**！

## 🚀 快速开始

### 步骤 1：将代码推送到 GitHub

```bash
# 如果还没有初始化 git
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/gy19951022/xm-assets.git
git branch -M main
git push -u origin main
```

### 步骤 2：等待自动打包

推送代码后，GitHub Actions 会自动开始打包：

1. 访问你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 可以看到正在运行的工作流
4. 等待几分钟，打包完成后显示绿色 ✓

### 步骤 3：下载可执行文件

1. 点击完成的工作流运行记录
2. 滚动到页面底部的 **Artifacts** 区域
3. 下载需要的文件：
   - `Windows-招标公告抓取工具` - Windows 版本 (.exe)
   - `macOS-招标公告抓取工具-App` - Mac 应用 (.app)
   - `macOS-招标公告抓取工具-DMG` - Mac 安装包 (.dmg)

## 📦 发布正式版本

如果想创建正式发布版本（带版本号）：

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

这会自动创建一个 GitHub Release，所有可执行文件会自动附加到 Release 页面。

## ⚙️ 手动触发打包

也可以在 GitHub 网页上手动触发：

1. 进入仓库的 **Actions** 页面
2. 选择左侧的 **Build Executables** 工作流
3. 点击右侧的 **Run workflow** 按钮
4. 选择分支，点击 **Run workflow**

## 📋 工作流说明

| 触发条件 | 效果 |
|---------|------|
| 推送到 main/master | 自动打包，生成 Artifacts |
| 创建 Pull Request | 自动打包，用于测试 |
| 推送版本标签 (v*) | 打包并创建 Release |
| 手动触发 | 自动打包 |

## ⚠️ 注意事项

1. **首次使用**：确保仓库的 Actions 功能已启用（Settings → Actions → 允许所有操作）

2. **私有仓库**：GitHub Actions 对私有仓库有使用时间限制（免费账户每月2000分钟）

3. **Artifacts 保留**：生成的文件默认保留 90 天，过期后需要重新打包

4. **Mac应用签名**：生成的 .app 未经 Apple 签名，首次运行需右键点击打开

## 🔧 自定义配置

编辑 `.github/workflows/build.yml` 可以：

- 修改 Python 版本
- 更改应用名称
- 添加应用图标
- 调整打包参数

---

有问题？检查 Actions 运行日志查看详细错误信息。

