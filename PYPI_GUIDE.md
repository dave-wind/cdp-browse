# PyPI 发布指南

本文档记录 `cdp-browse` 包的 PyPI 发布全流程，包括首次配置和后续更新。

## 首次配置（只需一次）

### 1. 注册 PyPI 账户

1. 访问 https://pypi.org/account/register/
2. 填写用户名、邮箱、密码
3. 验证邮箱
4. **必须开启 2FA**：Settings → Account settings → Two factor authentication
   - 推荐使用 Authenticator App（Google Authenticator / 1Password / Authy）
   - 扫码绑定后，每次登录需要输入动态码

### 2. 生成 API Token

1. 登录 PyPI → https://pypi.org/manage/account/token/
2. Token name: 随意填（如 `cdp-browse-publish`）
3. Scope: 选 "Entire account"（或指定项目 "cdp-browse"）
4. 点击 **Generate token**
5. **立即复制保存**，token 只显示一次

### 3. 配置本地认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-你的token内容
```

设置文件权限（仅自己可读）：

```bash
chmod 600 ~/.pypirc
```

### 4. 安装构建工具

```bash
pip install build twine
```

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

### 2. 清理旧构建产物

```bash
rm -rf dist build cdp_sdk.egg-info
```

### 3. 构建

```bash
python -m build
```

成功后 `dist/` 目录会出现：
- `cdp_browse-{version}-py3-none-any.whl`（wheel 包）
- `cdp_browse-{version}.tar.gz`（源码包）

### 4. 检查包内容（可选）

```bash
# 检查包是否正确
twine check dist/*

# 查看包里包含哪些文件
unzip -l dist/cdp_browse-*.whl
```

### 5. 发布

```bash
twine upload dist/*
```

发布成功后会显示：`https://pypi.org/project/cdp-browse/{version}/`

> PyPI 不允许重复上传同一版本号。如果上传失败需要改版本号重新构建。

### 6. 更新本地安装

```bash
pip install --upgrade cdp-browse
```

## 测试发布（推荐）

正式发布前可以先发到 TestPyPI 验证：

### 配置 TestPyPI

在 `~/.pypirc` 中追加：

```ini
[testpypi]
username = __token__
password = pypi-你的testpypi-token
```

TestPyPI 是独立环境，需要单独注册：https://test.pypi.org/account/register/

### 发布到 TestPyPI

```bash
twine upload --repository testpypi dist/*
```

### 从 TestPyPI 安装测试

```bash
pip install --index-url https://test.pypi.org/simple/ cdp-browse
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `403 Forbidden` | 包名被占用或 token 无效 | 换包名，或重新生成 token |
| `400 File already exists` | 同一版本号已发布 | 改版本号重新构建 |
| `Invalid API token` | token 配置错误 | 检查 `~/.pypirc`，确认 username 是 `__token__` |
| `ModuleNotFoundError` | 包结构不对 | 检查 `pyproject.toml` 的 `[tool.setuptools.packages.find]` |
| `Multiple top-level packages` | setuptools 发现多余目录 | 在 `include` 中只保留 `["cdp_sdk*"]` |

## 完整更新流程速查

```bash
# 1. 改版本号
vim pyproject.toml  # version = "x.y.z"

# 2. 清理 + 构建
rm -rf dist build cdp_sdk.egg-info
python -m build

# 3. 发布
twine upload dist/*

# 4. 更新本地
pip install --upgrade cdp-browse

# 5. 清理 + 提交
rm -rf dist build cdp_sdk.egg-info
git add -A
git commit -m "release: vx.y.z"
git push
```
