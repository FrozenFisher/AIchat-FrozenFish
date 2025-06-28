@echo off
chcp 65001 >nul
echo 🛠️  Git LFS 问题修复工具
echo ==========================================

echo.
echo 🔍 当前问题:
echo - 文件 Agenttest/BRETrain/saved_model/model.safetensors 超过100MB
echo - GitHub拒绝推送大文件
echo.

echo 💡 解决方案:
echo 1. 从Git历史中移除大文件
echo 2. 更新.gitignore防止再次提交
echo 3. 强制推送清理后的历史
echo.

echo ⚠️  警告: 此操作将重写Git历史
echo 如果有其他协作者，请先通知他们
echo.

set /p confirm="是否继续? (y/N): "
if /i not "%confirm%"=="y" (
    echo ❌ 操作已取消
    pause
    exit /b 1
)

echo.
echo 🧹 开始清理Git历史...

:: 检查Git状态
echo 🔍 检查Git状态...
git status --porcelain >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  有未提交的更改，正在提交...
    git add .
    git commit -m "保存当前更改"
)

:: 移除大文件
echo 🗑️  从Git历史中移除大文件...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch Agenttest/BRETrain/saved_model/model.safetensors" --prune-empty --tag-name-filter cat -- --all
if errorlevel 1 (
    echo ❌ 移除文件失败
    pause
    exit /b 1
)

:: 清理仓库
echo 🧹 清理Git仓库...
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

:: 强制推送
echo 🚀 强制推送到远程仓库...
git push --force-with-lease origin main
if errorlevel 1 (
    echo ❌ 推送失败
    echo 请检查网络连接和权限
    pause
    exit /b 1
)

echo.
echo 🎉 修复完成!
echo.
echo 💡 后续步骤:
echo 1. 确保.gitignore文件已更新
echo 2. 通知其他协作者重新克隆仓库
echo 3. 大文件已从历史中移除，但本地文件仍然存在
echo.
echo 📝 注意: 如果需要分享大文件，建议使用:
echo - Git LFS (Large File Storage)
echo - 云存储服务 (百度网盘、阿里云等)
echo - 模型托管平台 (Hugging Face等)
echo.

pause 