# 接口逆向

币安事件合约接口逆向，利用 API 下单，可实现批量化、自动化交易；项目仅供学习交流使用，请勿用于非法用途，否则后果自负。

币安最多可同时登录 1 个 App 端和 1 个 Web 端，可利用登录后的凭证进行接口调用。

- 对于 App 端，cURL bash 接口为

```shell
curl 'https://www.binance.com/bapi/futures/v2/private/future/event-contract/place-order' \
  -H 'content-type: application/json' \
  -H 'clienttype: android' \
  -H 'x-token: app.242414123.80946DCA4C235E37B129E4D387E11B51' \
  -X POST \
  --data-binary '{"orderAmount":"5","timeIncrements":"TEN_MINUTE","symbolName":"BTCUSDT","payoutRatio":"0.80","direction":"LONG"}'
```

- 对于 Web 端，cURL bash 接口为

```shell
curl 'https://www.binance.com/bapi/futures/v2/private/future/event-contract/place-order' \
  -H 'content-type: application/json' \
  -H 'clienttype: web' \
  -H 'csrftoken: 93126d6c61eca80cc05349E5d1a8bb4a' \
  -b 'p20t=web.242414123.70846DCA4C235E37B129E4D387E11D41' \
  -X POST \
  --data-binary '{"orderAmount":"5","timeIncrements":"TEN_MINUTE","symbolName":"BTCUSDT","payoutRatio":"0.80","direction":"LONG"}'
```

App 端的 `x-token` 可在抓包工具中获取，Web 端的 `p20t` 和 `csrftoken` 可在浏览器的开发者工具中获取；`x-token` 与 `p20t` 由 `登录方式.ID.Token` 的形式组成，`csrftoken` 为 www.binance.com 的 CSRF token；App 端凭证有效期未知，Web 端凭证最大有效期为 5 天。

本项目使用 Python 实现，模拟 Web 端登录以获取 Web 端凭证并下单，用户需使用币安 App 扫码登录。

---
# 安装依赖

在项目根目录下，执行

```shell
pip install -r requirements.txt 
```

为 `playwright` 安装浏览器驱动，执行

```shell
playwright install chromium
playwright install-deps
```

---
# 运行

在项目根目录下，执行

```shell
python main.py
```


即可运行脚本，脚本会在当前目录下生成 `token.json` 文件保存 Web 端凭证信息（`csrftoken`、`p20t`、`expirationTimestamp`）；用户可根据需要调用 `place_order_web()` 函数进行下单操作。
