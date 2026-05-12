"""
CDPClient — CDP-Bridge HTTP 底层客户端

封装与本地 CDP-Bridge 服务（http://127.0.0.1:18766/link）的通信协议，
提供 execute_js、navigate、session 管理等基础能力。
"""
import json
import time
import requests


class CDPError(Exception):
    """CDP-Bridge 调用异常"""


class CDPClient:
    """
    CDP-Bridge HTTP 客户端。

    通过 CDP-Bridge 控制已打开的 Chrome 浏览器，复用其登录态和 Cookie，
    无需额外鉴权。

    用法::

        client = CDPClient()
        client.find_session("github")       # 匹配包含 "github" 的 tab
        print(client.execute_js("document.title"))
    """

    DEFAULT_BASE_URL = "http://127.0.0.1:18766/link"

    def __init__(self, base_url: str = DEFAULT_BASE_URL, session_id: str | None = None):
        self.base_url = base_url
        self.session_id = session_id

    # ── 连接管理 ──────────────────────────────────────────────────────────────

    def check_alive(self) -> bool:
        """检测 CDP-Bridge 服务是否在线"""
        try:
            r = requests.post(self.base_url, json={"cmd": "ping"}, timeout=5)
            return r.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def get_sessions(self) -> list[dict]:
        """获取所有浏览器 tab 的 session 列表"""
        r = requests.post(self.base_url, json={"cmd": "get_all_sessions"}, timeout=10)
        data = r.json()
        sessions = data.get("r", [])
        if isinstance(sessions, list):
            return sessions
        return []

    def find_session(self, url_pattern: str | None = None) -> str:
        """
        自动发现并设置 session_id。

        Args:
            url_pattern: 可选的 URL 匹配模式（子串匹配），如 "github"、"baidu"。
                         不传则使用第一个 tab。

        Returns:
            找到的 session_id

        Raises:
            CDPError: 没有可用的 session
        """
        sessions = self.get_sessions()
        if not sessions:
            raise CDPError("没有找到任何浏览器 session，请确认 Chrome 已打开且 CDP-Bridge 扩展已连接")

        if url_pattern:
            for s in sessions:
                if url_pattern in s.get("url", ""):
                    self.session_id = s["id"]
                    return self.session_id

        # fallback: 使用第一个 session
        self.session_id = sessions[0]["id"]
        return self.session_id

    # ── 核心操作 ──────────────────────────────────────────────────────────────

    def execute_js(self, code: str, timeout: int = 15) -> any:
        """
        在当前页面执行 JavaScript 并返回结果。

        支持两种写法：
        1. ``return document.title`` — 自动原样发送
        2. ``document.querySelector('.foo').textContent`` — 自动补 return

        Args:
            code: JavaScript 代码
            timeout: 执行超时（秒）

        Returns:
            JS 执行结果（Python 原生类型：str/int/float/list/dict/None）

        Raises:
            CDPError: 未设置 session_id 或执行失败
        """
        if not self.session_id:
            raise CDPError("session_id 未设置，请先调用 find_session() 或在构造时传入")

        # 自动补 return
        stripped = code.strip()
        if not stripped.startswith("return") and not stripped.startswith("(("):
            stripped = f"return {stripped}"

        try:
            r = requests.post(
                self.base_url,
                json={
                    "cmd": "execute_js",
                    "sessionId": self.session_id,
                    "code": stripped,
                    "timeout": timeout,
                },
                timeout=timeout + 5,
            )
            result = r.json()
            data = result.get("r")
            # 兼容 {"r": {"data": ...}} 和 {"r": value} 两种响应格式
            if isinstance(data, dict) and "data" in data and len(data) == 1:
                return data["data"]
            return data
        except requests.ConnectionError as e:
            raise CDPError(f"CDP-Bridge 连接失败: {e}") from e
        except requests.Timeout as e:
            raise CDPError(f"JS 执行超时 ({timeout}s): {code[:80]}") from e
        except json.JSONDecodeError as e:
            raise CDPError(f"CDP-Bridge 响应解析失败: {e}") from e

    def navigate(self, url: str, wait: float = 3.0) -> None:
        """
        导航到指定 URL。

        通过 JS 设置 window.location.href 实现，复用当前 tab 的 Cookie 和登录态。

        Args:
            url: 目标 URL
            wait: 导航后等待时间（秒）
        """
        self.execute_js(f"window.location.href = {json.dumps(url)}", timeout=10)
        time.sleep(wait)
