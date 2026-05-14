# PyPI 发布指南

本文档记录 `cdp-browse` 包的 PyPI 发布全流程，使用 `uv` 管理。

## 首次配置（只需一次）

### 1. 注册 PyPI 账户

1. 访问 https://pypi.org/account/register/
2. 填写用户名、邮箱、密码
3. 验证邮箱
4. **必须开启 2FA**：Settings → Account settings → Two factor authentication

### 2. 生成 API Token

1. 登录 PyPI → https://pypi.org/manage/account/token/
2. Token name: 随意填（如 `cdp-browse-publish`）
3. Scope: 选 "Entire account"（或指定项目 "cdp-browse"）
4. 点击 **Generate token**
5. **立即复制保存**，token 只显示一次

### 3. 配置 Token

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
export UV_PUBLISH_TOKEN=pypi-你的token内容
```

然后 `source ~/.zshrc`（或重启终端）。

> **安全提示：** Token 通过环境变量传递，不会出现在代码或 git 中。AI 助手无法读取 token 值。

## 发布新版本

### 1. 更新版本号

编辑 `pyproject.toml`：

```toml
version = "0.3.0"  # 从 0.2.0 改为新版本
```

版本号规则（语义化版本）：
- **补丁** `0.2.0 → 0.2.1`：修 bug，不改 API
- **小版本** `0.2.0 → 0.3.0`：新增功能，向后兼容
- **大版本** `0.2.0 → 1.0.0`：破坏性变更

### 2. 发布

```bash
./publish.sh
```

脚本会自动：清理 `dist/` → `uv build` 构建 → `uv publish` 发布。

也可以临时传入 token：

```bash
./publish.sh --token pypi-xxx
```

> PyPI 不允许重复上传同一版本号。如果上传失败需要改版本号重新构建。

### 3. 验证

发布成功后访问：`https://pypi.org/project/cdp-browse/{version}/`

本地验证：
```bash
uvx --from cdp-browse cdp-browse --help
```

## 完整更新流程速查

```bash
# 1. 改版本号
vim pyproject.toml  # version = "x.y.z"

# 2. 发布
./publish.sh

# 3. 提交
git add -A
git commit -m "release: vx.y.z"
git push
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `403 Forbidden` | 包名被占用或 token 无效 | 换包名，或重新生成 token |
| `400 File already exists` | 同一版本号已发布 | 改版本号重新构建 |
| `UV_PUBLISH_TOKEN not set` | 未配置环境变量 | 在 `~/.zshrc` 中添加 export |
| `ModuleNotFoundError` | 包结构不对 | 检查 `pyproject.toml` 的 `[tool.setuptools.packages.find]` |
