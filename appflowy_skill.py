import os
import requests
import json
import re
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
        return data.get("access_token")
    except Exception as e:
        raise RuntimeError(f"登录失败: {str(e)}。服务器返回: {response.text}")

# -----------------------------------------------------------------------------
# ✅ 核心新增：行内样式解析器 (Rich Text Parser)
# -----------------------------------------------------------------------------
def parse_rich_text(text: str) -> list:
    """
    解析单行文本中的 Markdown 行内样式，转换为 AppFlowy 的 Delta 格式。
    支持：Bold, Italic, Strikethrough, Code, Link
    """
    if not text:
        return [{"insert": ""}]

    # 定义正则模式 (优先级：Code > Link > Bold > Italic > Strike)
    # 注意：这里使用简单的正则，不支持极度复杂的嵌套，但足够日常使用
    pattern = re.compile(
        r"(?P<code>`[^`]+`)|"               # `code`
        r"(?P<link>\[[^\]]+\]\([^)]+\))|"   # [text](url)
        r"(?P<bold>\*\*[^*]+\*\*)|"         # **bold**
        r"(?P<italic>\*[^*]+\*)|"           # *italic*
        r"(?P<strike>~~[^~]+~~)"            # ~~strike~~
    )

    deltas = []
    last_end = 0

    for match in pattern.finditer(text):
        start, end = match.span()
        
        # 1. 添加匹配项之前的普通文本
        if start > last_end:
            deltas.append({"insert": text[last_end:start]})

        # 2. 处理匹配到的样式文本
        kind = match.lastgroup
        value = match.group()
        attributes = {}
        content = value

        if kind == "code":
            attributes["code"] = True
            attributes["bg_color"] = "0x00000000" # 可选：给代码块加个默认透明背景或其他色
            content = value[1:-1] # 去除 `

        elif kind == "link":
            # 解析 [text](url)
            m_link = re.match(r"\[(?P<text>[^\]]+)\]\((?P<url>[^\)]+)\)", value)
            if m_link:
                content = m_link.group("text")
                attributes["href"] = m_link.group("url")
                attributes["font_color"] = "0xff00b5ff" # 可选：给链接加个蓝色

        elif kind == "bold":
            attributes["bold"] = True
            content = value[2:-2] # 去除 **

        elif kind == "italic":
            attributes["italic"] = True
            content = value[1:-1] # 去除 *

        elif kind == "strike":
            attributes["strikethrough"] = True
            content = value[2:-2] # 去除 ~~

        # 添加带属性的片段
        deltas.append({
            "insert": content,
            "attributes": attributes
        })
        
        last_end = end

    # 3. 添加剩余的普通文本
    if last_end < len(text):
        deltas.append({"insert": text[last_end:]})

    return deltas

# -----------------------------------------------------------------------------
# 块解析器 (Block Parser)
# -----------------------------------------------------------------------------
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
        
        # --- 处理代码块 (Code Block) ---
        if stripped.startswith("```"):
            if in_code_block:
                full_code = "\n".join(code_buffer)
                blocks.append({
                    "type": "code",
                    "data": {
                        "language": code_lang if code_lang else "text",
                        "delta": [{"insert": full_code}] # 代码块内部通常不解析富文本
                    }
                })
                in_code_block = False
                code_buffer = []
                code_lang = ""
            else:
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue
            
        if in_code_block:
            code_buffer.append(line)
            continue

        # --- 处理分割线 ---
        if stripped == "---" or stripped == "***":
            blocks.append({"type": "divider", "data": {}})
            continue

        # --- 处理标题 ---
        if stripped.startswith("# "):
            blocks.append({
                "type": "heading",
                "data": {
                    "level": 1,
                    "delta": parse_rich_text(stripped[2:]) # ✅ 使用富文本解析
                }
            })
            continue
        elif stripped.startswith("## "):
            blocks.append({
                "type": "heading",
                "data": {
                    "level": 2,
                    "delta": parse_rich_text(stripped[3:]) # ✅ 使用富文本解析
                }
            })
            continue
        elif stripped.startswith("### "):
            blocks.append({
                "type": "heading",
                "data": {
                    "level": 3,
                    "delta": parse_rich_text(stripped[4:]) # ✅ 使用富文本解析
                }
            })
            continue

        # --- 处理列表 ---
        if stripped.startswith("- [ ] ") or stripped.startswith("- [x] "):
            is_checked = stripped.startswith("- [x] ")
            blocks.append({
                "type": "todo_list",
                "data": {
                    "checked": is_checked,
                    "delta": parse_rich_text(stripped[6:]) # ✅ 使用富文本解析
                }
            })
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append({
                "type": "bulleted_list",
                "data": {
                    "delta": parse_rich_text(stripped[2:]) # ✅ 使用富文本解析
                }
            })
            continue

        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.' and stripped[2] == ' ':
            space_index = stripped.find(" ")
            blocks.append({
                "type": "numbered_list",
                "data": {
                    "delta": parse_rich_text(stripped[space_index+1:]) # ✅ 使用富文本解析
                }
            })
            continue

        # --- 处理引用 ---
        if stripped.startswith("> "):
            blocks.append({
                "type": "quote",
                "data": {
                    "delta": parse_rich_text(stripped[2:]) # ✅ 使用富文本解析
                }
            })
            continue

        # --- 默认段落 ---
        if not line:
            # 这里的空行可以忽略，或者插入空的 text
             blocks.append({"type": "paragraph", "data": {"delta": [{"insert": ""}]}})
        else:
            blocks.append({
                "type": "paragraph",
                "data": {
                    "delta": parse_rich_text(line) # ✅ 使用富文本解析（不strip，保留缩进体验可能更好，或者按需strip）
                }
            })
            
    # Flush residual code block
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

@mcp.tool()
def upload_document_to_appflowy(title: str, content: str) -> str:
    """
    将生成的文本内容上传到 AppFlowy 文档中。
    会自动解析 Markdown 语法（标题、列表、代码块、加粗、链接等）。

    Args:
        title: 文档的标题
        content: 文档的正文内容（支持 Markdown）
    """
    try:
        workspace_id = get_env_var("APPFLOWY_WORKSPACE_ID")
        parent_view_id = get_env_var("APPFLOWY_PARENT_VIEW_ID")
        token = get_auth_token()
        
        url = f"{BASE_HOST}/appflowy/api/workspace/{workspace_id}/page-view"
        
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