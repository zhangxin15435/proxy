#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests

def main():
    print(" GitHub Actions 工作流部署验证")
    print("=" * 60)
    
    # 检查环境变量
    token = os.getenv('ACCESS_TOKEN') or os.getenv('GITHUB_TOKEN')
    if not token:
        print(" 未找到ACCESS_TOKEN环境变量")
        print("请先运行: setup_env.bat 或 setup_env.ps1")
        return False
    
    # 检查仓库连接
    repo_url = "https://api.github.com/repos/zhangxin15435/proxy"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(repo_url, headers=headers)
        if response.status_code == 200:
            print(" GitHub仓库连接成功")
            
            # 检查Actions工作流
            workflows_url = f"{repo_url}/actions/workflows"
            workflow_response = requests.get(workflows_url, headers=headers)
            
            if workflow_response.status_code == 200:
                workflows = workflow_response.json()['workflows']
                print(f" 找到 {len(workflows)} 个工作流")
                
                proxy_workflow = next((w for w in workflows if "代理池" in w['name']), None)
                if proxy_workflow:
                    print(" 代理池自动更新工作流已部署")
                    print(f"   状态: {proxy_workflow['state']}")
                    print(f"   访问: https://github.com/zhangxin15435/proxy/actions")
                    return True
                else:
                    print(" 未找到代理池工作流")
            else:
                print(f" 获取工作流失败: {workflow_response.status_code}")
        else:
            print(f" 仓库连接失败: {response.status_code}")
    except Exception as e:
        print(f" 连接错误: {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n GitHub Actions工作流部署成功！")
    else:
        print("\n 部署验证失败，请检查配置")
