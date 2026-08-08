# PoC 常见模式

## SQL 注入特征

- 使用 `' OR '1'='1` 等万能密码
- 使用 `UNION SELECT`
- 使用 `SLEEP()` 或 `BENCHMARK()` 进行时间盲注
- 使用 `INFORMATION_SCHEMA` 查询数据库信息
- 请求中包含 `--`、`#`、`'`、`"` 等 SQL 注释符

## 命令注入特征

- 使用 `|`、`;`、`&&`、`||` 连接系统命令
- 调用 `system()`、`exec()`、`popen()`
- 请求中包含 `wget`、`curl`、`nslookup` 等命令
- 使用反引号 `` ` `` 或 `$()` 执行命令

## XSS 特征

- 注入 `<script>` 标签
- 使用 `onerror`、`onload`、`onclick` 等事件处理器
- 使用 `javascript:` 协议
- 使用 `alert()`、`document.cookie` 等 JS 代码

## 文件包含特征

- 使用 `../` 路径遍历
- 使用 `php://filter`、`php://input` 等 PHP 包装器
- 使用 `file://`、`http://` 协议

## SSRF 特征

- 在 URL/参数中指定内网地址（127.0.0.1、10.x.x.x、172.16.x.x、192.168.x.x）
- 使用 `file://`、`gopher://`、`dict://` 等协议
- 在请求参数中包含完整 URL
