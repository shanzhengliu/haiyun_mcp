docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t samliu960522/haiyun_mcp:latest \
  --push \
  .