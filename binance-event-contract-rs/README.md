# Rust 版本

这是原 Python 脚本的独立 Rust 子工程，目录位于 `binance-event-contract-rs/`。

当前代码已经按职责拆成多模块，便于后续继续维护：

- `src/app.rs`：程序入口调度
- `src/cli.rs`：命令行参数
- `src/browser.rs`：浏览器启动与通用配置
- `src/login.rs`：扫码登录、Cookie 轮询与恢复逻辑
- `src/qr.rs`：二维码元素定位与截图回退策略
- `src/token_store.rs`：token 文件读写
- `src/trade.rs`：下单请求
- `src/logging.rs`：日志初始化

当前实现保留了原项目的核心流程：

- 启动 Chromium/Chrome 并复用本地浏览器配置目录
- 打开 Binance 登录页，辅助切换到二维码登录
- 优先截取二维码元素，失败时回退整页截图到 `qrcode.png`
- 轮询浏览器 Cookie，提取 `p20t` 和 `csrftoken`
- 写入 `token.json`
- 调用 Web 端事件合约下单接口

与 Python 版的差异：

- Rust 版不再拦截二维码接口响应并在终端绘制二维码，而是保存页面截图到 `qrcode.png`
- `csrftoken` 通过额外打开一次 Binance 首页触发写入 Cookie，而不是从网络请求头里抓取
- 登录循环增加了日志、连续失败重试、登录页重开和首页刷新恢复逻辑

## 环境要求

- 已安装 Rust toolchain
- 本机可启动 Chrome 或 Chromium

## 编译

```shell
cargo check
```

## 获取 token

```shell
cargo run -- get-token
```

如果需要更详细的诊断日志，可附加 `-v` 或 `-vv`：

```shell
cargo run -- -v get-token
```

常用参数：

```shell
cargo run -- get-token --headless false
cargo run -- get-token --reset true
cargo run -- get-token --timeout-secs 900 --token-file token.json
```

成功后会在当前目录输出 `token.json` 和 `qrcode.png`。

## 下单

先执行一次 `get-token`，然后：

```shell
cargo run -- place-order --order-amount 5 --time-increments TEN_MINUTE --symbol-name BTCUSDT --payout-ratio 0.80 --direction LONG
```

也可以直接传 token：

```shell
cargo run -- place-order --csrftoken your_csrf --p20t your_p20t --order-amount 5 --time-increments TEN_MINUTE --symbol-name BTCUSDT --payout-ratio 0.80 --direction LONG
```