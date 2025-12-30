import os
import requests
import json
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务
mcp = FastMCP("AppFlowy Uploader")

# 配置常量（基础 URL）
BASE_HOST = "https://gatetest.shjinjia.com.cn"

def get_env_var(name: str) -> str:
    """获取环境变量，如果不存在则抛出清晰的错误"""
    val = os.environ.get(name)
    if not val:
        raise ValueError(f"缺少环境变量: {name}。请在运行前配置该变量。")
    return val

def get_auth_token():
    """获取访问 Token"""
    email = get_env_var("APPFLOWY_EMAIL")
    # 注意：如果你的服务器需要密码的 HASH 值，请将 HASH 值填入环境变量
    password = get_env_var("APPFLOWY_PASSWORD")
    
    url = f"{BASE_HOST}/appflowy/gotrue/token"
    params = {"grant_type": "password"}
    payload = {
        "email": email,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Claude-Skill/1.0"
    }

    try:
        response = requests.post(url, params=params, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # 通常 Token 在 access_token 字段，根据实际返回调整
        return data.get("access_token")
    except Exception as e:
        raise RuntimeError(f"登录失败: {str(e)}。服务器返回: {response.text}")

# -------------------------------------------------------------
# 请将下面的 parse_markdown_to_blocks 函数添加到你的脚本中
# -------------------------------------------------------------

def parse_markdown_to_blocks(content: str) -> list:
    """
    将 Markdown 文本解析为 AppFlowy 识别的 Block 结构列表
    """
    blocks = []
    lines = content.split('\n')
    
    in_code_block = False
    code_buffer = []
    code_lang = ""
    
    for line in lines:
        stripped = line.strip()
        
        # 1. 处理代码块 (Code Block)
        # ------------------------------------------------
        if stripped.startswith("```"):
            if in_code_block:
                # 代码块结束
                full_code = "\n".join(code_buffer)
                blocks.append({
                    "type": "code",
                    "data": {
                        "language": code_lang if code_lang else "text",
                        "delta": [{"insert": full_code}]
                    }
                })
                in_code_block = False
                code_buffer = []
                code_lang = ""
            else:
                # 代码块开始
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue
            
        if in_code_block:
            code_buffer.append(line)
            continue

        # 2. 处理分割线 (Divider)
        # ------------------------------------------------
        if stripped == "---" or stripped == "***":
            blocks.append({
                "type": "divider",
                "data": {}
            })
            continue

        # 3. 处理标题 (Heading)
        # ------------------------------------------------
        if stripped.startswith("# "):
            blocks.append({
                "type": "heading",
                "data": {
                    "level": 1,
                    "delta": [{"insert": stripped[2:]}]
                }
            })
            continue
        elif stripped.startswith("## "):
            blocks.append({
                "type": "heading",
                "data": {
                    "level": 2,
                    "delta": [{"insert": stripped[3:]}]
                }
            })
            continue
        elif stripped.startswith("### "):
            blocks.append({
                "type": "heading",
                "data": {
                    "level": 3,
                    "delta": [{"insert": stripped[4:]}]
                }
            })
            continue

        # 4. 处理待办事项 (Todo List)
        # ------------------------------------------------
        if stripped.startswith("- [ ] ") or stripped.startswith("- [x] "):
            is_checked = stripped.startswith("- [x] ")
            text = stripped[6:]
            blocks.append({
                "type": "todo_list",
                "data": {
                    "checked": is_checked,
                    "delta": [{"insert": text}]
                }
            })
            continue

        # 5. 处理无序列表 (Bulleted List)
        # ------------------------------------------------
        if stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append({
                "type": "bulleted_list",
                "data": {
                    "delta": [{"insert": stripped[2:]}]
                }
            })
            continue

        # 6. 处理有序列表 (Numbered List)
        # ------------------------------------------------
        # 简单判断 "1. " 这种格式
        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.' and stripped[2] == ' ':
            # 找到第一个空格的位置
            space_index = stripped.find(" ")
            text = stripped[space_index+1:]
            blocks.append({
                "type": "numbered_list",
                "data": {
                    "delta": [{"insert": text}]
                }
            })
            continue

        # 7. 处理引用 (Quote)
        # ------------------------------------------------
        if stripped.startswith("> "):
            blocks.append({
                "type": "quote",
                "data": {
                    "delta": [{"insert": stripped[2:]}]
                }
            })
            continue

        # 8. 默认处理：普通段落 (Paragraph)
        # ------------------------------------------------
        # 过滤掉完全空行，或者保留为空段落
        if not line:
            # 可选：如果你想保留空行作为间距
            blocks.append({"type": "paragraph", "data": {"delta": [{"insert": ""}]}})
        else:
            blocks.append({
                "type": "paragraph",
                "data": {
                    "delta": [{"insert": line}]
                }
            })
            
    # 如果结束时还在代码块里，把剩下的也flush出来
    if in_code_block and code_buffer:
        full_code = "\n".join(code_buffer)
        blocks.append({
            "type": "code",
            "data": {
                "language": code_lang if code_lang else "text",
                "delta": [{"insert": full_code}]
            }
        })
        
    return blocks

# -------------------------------------------------------------
# 更新后的主 Tool 函数
# -------------------------------------------------------------

@mcp.tool()
def upload_document_to_appflowy(title: str, content: str) -> str:
    """
    将生成的文本内容上传到 AppFlowy 文档中。
    会自动解析 Markdown 语法（标题、列表、代码块等）为 AppFlowy 的原生块。

    Args:
        title: 文档的标题
        content: 文档的正文内容（支持 Markdown）
    """
    try:
        workspace_id = get_env_var("APPFLOWY_WORKSPACE_ID")
        parent_view_id = get_env_var("APPFLOWY_PARENT_VIEW_ID")
        token = get_auth_token()
        
        url = f"{BASE_HOST}/appflowy/api/workspace/{workspace_id}/page-view"
        
        # ✅ 调用新的解析函数
        children_blocks = parse_markdown_to_blocks(content)

        page_data = {
            "type": "page",
            "children": children_blocks
        }

        payload = {
            "parent_view_id": parent_view_id,
            "layout": 0,
            "name": title,
            "page_data": page_data,
            "view_id": None,
            "collab_id": None
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Claude-Skill/1.0"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return f"文档 '{title}' 上传成功！包含 {len(children_blocks)} 个内容块。"

    except Exception as e:
        return f"上传文档失败: {str(e)}"

if __name__ == "__main__":
    mcp.run()