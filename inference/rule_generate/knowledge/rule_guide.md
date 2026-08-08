# Snort 规则编写指南

## 最佳实践

### 1. 使用精确的 content 匹配
不好的规则：
```
content:"cmd";
```
好的规则：
```
content:"wget%20"; nocase; content:"http"; nocase; distance:0; within:20;
```

### 2. 合理使用 depth/offset/distance/within
- `depth:N` - 限制搜索深度，减少误报
- `offset:N` - 从指定偏移开始搜索
- `distance:N` - 必须在上一个匹配后 N 字节内匹配
- `within:N` - 在 N 字节范围内匹配

### 3. 避免使用 `content:""`
空 content 匹配所有数据包，会导致大量误报。

### 4. 使用 `fast_pattern` 提高性能
```snort
content:"GET"; http_method; content:"/admin"; fast_pattern:only;
```

### 5. HTTP 特定匹配
```snort
content:"POST"; http_method;
content:"/login"; http_uri;
content:"User-Agent|3a|"; http_header;
```

### 6. pcre 慎用
pcre 性能开销大，优先使用 content 组合。
仅在复杂模式匹配时使用。

### 7. SID 范围
- 1-999999: Snort 官方规则
- 1000000-1999999: Snort 社区规则
- 4200000-4299999: 自定义规则（建议使用）
