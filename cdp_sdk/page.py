"""
Page — 高层页面操作

基于 CDPClient 提供导航、等待、点击、滚动、内容提取等常用页面操作，
让爬虫脚本更简洁、更可读。
"""
import json
import time
from cdp_sdk.client import CDPClient


class Page:
    """
    高层页面操作封装。

    用法::

        client = CDPClient()
        client.find_session()       # 自动匹配任意 tab
        page = Page(client)

        page.navigate("https://example.com")
        page.wait_for_selector("h1")
        print(page.extract_text("h1"))
    """

    def __init__(self, client: CDPClient):
        self.client = client

    # -- 导航 ----------------------------------------------------------------

    def navigate(self, url: str, wait: float = 3.0,
                 wait_for_selector: str | None = None,
                 wait_for_js: str | None = None,
                 timeout: float = 15) -> None:
        """
        导航到指定 URL，可选等待页面元素或条件就绪。

        优先使用 wait_for_selector / wait_for_js 进行智能等待；
        都没传则使用固定 wait 秒数。

        Args:
            url: 目标 URL
            wait: 无智能等待时的固定等待时间（秒）
            wait_for_selector: 导航后等待此 CSS 选择器出现
            wait_for_js: 导航后等待此 JS 条件为真
            timeout: 智能等待的超时时间（秒）
        """
        self.client.navigate(url, wait=wait)
        if wait_for_selector:
            self.wait_for_selector(wait_for_selector, timeout=timeout)
        elif wait_for_js:
            self.wait_for_js(wait_for_js, timeout=timeout)

    # -- 等待 ----------------------------------------------------------------

    def wait_for_selector(self, selector: str, timeout: float = 15) -> bool:
        """
        轮询等待 CSS 选择器对应的元素出现。

        Returns:
            True 如果在超时前找到元素，False 如果超时
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            found = self.client.execute_js(
                f"return !!document.querySelector({json.dumps(selector)})"
            )
            if found:
                return True
            time.sleep(0.5)
        return False

    def wait_for_js(self, condition: str, timeout: float = 15) -> bool:
        """
        轮询等待 JS 条件为真。

        Args:
            condition: 返回 truthy 值的 JS 表达式，如 ``document.querySelectorAll('.item').length > 5``

        Returns:
            True 如果条件在超时前满足，False 如果超时
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                result = self.client.execute_js(f"return !!({condition})")
                if result:
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        return False

    # -- 交互 ----------------------------------------------------------------

    def click(self, selector: str) -> bool:
        """
        点击 CSS 选择器匹配的第一个元素。

        Returns:
            True 如果成功点击，False 如果元素不存在
        """
        return self.client.execute_js(
            f"(() => {{"
            f"  const el = document.querySelector({json.dumps(selector)});"
            f"  if (el) {{ el.click(); return true; }}"
            f"  return false;"
            f"}})()"
        ) or False

    def scroll_by(self, x: int = 0, y: int = 3000) -> None:
        """滚动页面指定偏移量"""
        self.client.execute_js(f"window.scrollBy({x}, {y})")

    def scroll_to_bottom(self) -> int:
        """滚动到页面底部，返回 scrollHeight"""
        return self.client.execute_js(
            "(() => {"
            "  window.scrollTo(0, document.body.scrollHeight);"
            "  return document.body.scrollHeight;"
            "})()"
        ) or 0

    # -- 提取 ----------------------------------------------------------------

    def extract_text(self, selector: str = "body") -> str:
        """提取匹配元素的 textContent，默认提取整个页面"""
        return self.client.execute_js(
            f"(() => {{"
            f"  const el = document.querySelector({json.dumps(selector)});"
            f"  return el ? el.textContent.trim() : '';"
            f"}})()"
        ) or ""

    def extract_html(self, selector: str = "body") -> str:
        """提取匹配元素的 innerHTML，默认提取整个页面"""
        return self.client.execute_js(
            f"(() => {{"
            f"  const el = document.querySelector({json.dumps(selector)});"
            f"  return el ? el.innerHTML : '';"
            f"}})()"
        ) or ""

    def query_all(self, selector: str, transform: str = "a => a.textContent.trim()") -> list:
        """
        对所有匹配元素执行转换函数，返回结果列表。

        Args:
            selector: CSS 选择器
            transform: JS 箭头函数，接收元素参数，如 ``el => ({title: el.textContent, href: el.href})``

        Returns:
            转换结果列表

        用法::

            # 提取所有链接
            links = page.query_all("a.article-link", "a => ({title: a.textContent.trim(), url: a.href})")

            # 提取所有段落文字
            texts = page.query_all("p", "el => el.textContent.trim()")
        """
        return self.client.execute_js(
            f"(() => {{"
            f"  const els = document.querySelectorAll({json.dumps(selector)});"
            f"  const fn = {transform};"
            f"  return Array.from(els).map(fn);"
            f"}})()"
        ) or []

    # -- 便捷属性 ------------------------------------------------------------

    @property
    def title(self) -> str:
        """当前页面标题"""
        return self.client.execute_js("return document.title") or ""

    @property
    def url(self) -> str:
        """当前页面 URL"""
        return self.client.execute_js("return window.location.href") or ""
