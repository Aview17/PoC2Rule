# 检测模式指南

## HTTP 流量检测

### 请求行检测
- 异常 HTTP 方法
- 异常 URI 长度
- URI 中的特殊字符

### Header 检测
- 伪造的 User-Agent
- 异常的 Content-Type
- 过多的 Cookie
- 注入在 Header 中的攻击载荷

### Body 检测
- payload 中的 SQL 关键字
- payload 中的命令关键字
- payload 中的文件路径

## 编码绕过检测

### URL 编码
`%27` = `'`, `%20` = ` `, `%3B` = `;`
检测时应同时匹配原始字符和编码后的字符

### 双重编码
`%253C` = `%3C` = `<`
需要多次解码才能发现攻击

### Base64 编码
常见于 JWT token、Cookie 等

### Unicode 编码
`\u0027` = `'`

## 组合检测策略

1. **多特征组合**: 单个特征可能误报，使用多个 content 组合
2. **协议层 + 应用层**: 同时检测 TCP 标志位和 HTTP 内容
3. **正向 + 反向**: 使用 content 和 pcre 双重匹配
