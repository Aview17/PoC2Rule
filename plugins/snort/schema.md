# Snort 规则格式说明

## 基本格式

```
<action> <protocol> <src_ip> <src_port> <direction> <dst_ip> <dst_port> (<options>)
```

## 字段说明

### action
- `alert`: 生成告警
- `log`: 记录数据包
- `pass`: 忽略数据包
- `drop`: 丢弃数据包并记录

### protocol
- `tcp`
- `udp`
- `icmp`
- `ip`

### IP 和端口
- IP 可以是具体 IP、`any`、`$HOME_NET`、`$EXTERNAL_NET` 等变量
- 端口可以是具体端口、`any`、`$HTTP_PORTS` 等变量
- 端口范围: `80:443`

### direction
- `->`: 单向（源到目标）
- `<>`: 双向

### options (常用)

| 选项 | 说明 |
|------|------|
| `msg:"..."` | 告警消息 |
| `content:"..."` | 匹配内容 |
| `nocase` | 不区分大小写 |
| `depth:N` | 搜索深度 |
| `offset:N` | 搜索起始偏移 |
| `distance:N` | 距离上一个 content 的距离 |
| `within:N` | 在 N 字节内搜索 |
| `flow:to_server,established` | 流方向 |
| `classtype:...` | 攻击类型 |
| `sid:N` | 规则 ID |
| `rev:N` | 规则版本 |
| `reference:...` | 参考链接 |
| `pcre:"/.../i"` | 正则匹配 |

## 规则编写指南

1. 尽量使用 `content` 关键字匹配精确特征
2. 使用 `nocase` 处理大小写不敏感的情况
3. 使用 `depth`、`offset`、`distance`、`within` 提高匹配精度
4. 每条规则使用唯一的 `sid`
5. 添加有意义的 `msg` 和适当的 `classtype`
