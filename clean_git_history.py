#!/usr/bin/env python3
"""
清理Git历史中的大文件
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ 命令失败: {cmd}")
            print(f"错误: {result.stderr}")
            return False
        return result
    except Exception as e:
        print(f"❌ 执行命令失败: {e}")
        return False

def check_git_status():
    """检查Git状态"""
    print("🔍 检查Git状态...")
    result = run_command("git status --porcelain")
    if not result:
        return False
    
    if result.stdout.strip():
        print("⚠️  有未提交的更改，请先提交或暂存")
        print("建议执行:")
        print("  git add .")
        print("  git commit -m '保存当前更改'")
        return False
    
    print("✅ Git工作区干净")
    return True

def find_large_files():
    """查找大文件"""
    print("🔍 查找大文件...")
    result = run_command("git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sed -n 's/^blob //p' | sort --numeric-sort --key=2 | tail -10")
    if not result:
        return []
    
    large_files = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 3:
                size = int(parts[1])
                filename = ' '.join(parts[2:])
                if size > 50 * 1024 * 1024:  # 50MB
                    large_files.append((filename, size))
    
    return large_files

def remove_file_from_history(file_path):
    """从Git历史中移除文件"""
    print(f"🗑️  从Git历史中移除: {file_path}")
    
    # 使用git filter-branch移除文件
    cmd = f'git filter-branch --force --index-filter "git rm --cached --ignore-unmatch {file_path}" --prune-empty --tag-name-filter cat -- --all'
    result = run_command(cmd, check=False)
    
    if result and result.returncode == 0:
        print(f"✅ 成功移除: {file_path}")
        return True
    else:
        print(f"❌ 移除失败: {file_path}")
        return False

def clean_git_repo():
    """清理Git仓库"""
    print("🧹 清理Git仓库...")
    
    # 强制垃圾回收
    run_command("git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin")
    run_command("git reflog expire --expire=now --all")
    run_command("git gc --prune=now --aggressive")
    
    print("✅ Git仓库清理完成")

def main():
    """主函数"""
    print("🧹 Git历史清理工具")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if not Path(".git").exists():
        print("❌ 当前目录不是Git仓库")
        return False
    
    # 检查Git状态
    if not check_git_status():
        return False
    
    # 查找大文件
    large_files = find_large_files()
    
    if not large_files:
        print("✅ 没有发现大文件")
        return True
    
    print(f"📁 发现 {len(large_files)} 个大文件:")
    for filename, size in large_files:
        size_mb = size / (1024 * 1024)
        print(f"   {filename} ({size_mb:.1f} MB)")
    
    # 确认操作
    print("\n⚠️  警告: 此操作将重写Git历史，可能会影响其他协作者")
    confirm = input("是否继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return False
    
    # 移除大文件
    success_count = 0
    for filename, size in large_files:
        if remove_file_from_history(filename):
            success_count += 1
    
    if success_count > 0:
        # 清理仓库
        clean_git_repo()
        
        print(f"\n🎉 清理完成! 成功移除 {success_count} 个大文件")
        print("\n💡 下一步:")
        print("1. 推送到远程仓库: git push --force-with-lease origin main")
        print("2. 通知其他协作者重新克隆仓库")
        print("3. 确保.gitignore文件已更新")
    else:
        print("❌ 没有成功移除任何文件")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 