import os
import re
import json
import requests
import qrcode
import shutil
from http.cookies import SimpleCookie
from email.utils import parsedate_to_datetime
from playwright.sync_api import sync_playwright

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

WIN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

def launch_persistent_ctx(pw, reset=False, headless=True):
    user_data_dir = os.path.expanduser("~/.config/playwright-binance")
    if reset:
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)

    args = [
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1280,960",
    ]

    if headless:
        args += ["--headless=new", "--disable-gpu"]

    common_kwargs = dict(
        user_data_dir=user_data_dir,
        headless=headless,
        args=args,
        viewport={"width": 1280, "height": 960},
        locale="zh-CN",
        user_agent=WIN_UA,
        extra_http_headers={
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-mobile": "?0",
            "accept-language": "zh-CN,zh;q=0.9"
        },
    )

    return pw.chromium.launch_persistent_context(**common_kwargs)

def apply_windows_ua(ctx, page):
    page.add_init_script(f"""
        Object.defineProperty(navigator, 'userAgent', {{get: () => '{WIN_UA}' }});
        Object.defineProperty(navigator, 'platform', {{get: () => 'Win32' }});
        Object.defineProperty(navigator, 'vendor', {{get: () => 'Google Inc.' }});
        Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => 0 }});
    """)

    try:
        s = ctx.new_cdp_session(page)
        s.send("Emulation.setUserAgentOverride", {
            "userAgent": WIN_UA,
            "platform": "Windows",
            "acceptLanguage": "zh-CN,zh;q=0.9"
        })
    except:
        pass

    ctx.set_extra_http_headers({
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
        "accept-language": "zh-CN,zh;q=0.9"
    })

def print_qr(data):
    qr = qrcode.QRCode(border=0)
    qr.add_data(data)
    qr.make(fit=True)
    m = qr.get_matrix()

    black = "  "
    white = "██"
    scale = 1
    margin = 1
    w = len(m[0])

    for _ in range(margin * scale):
        print(white * (w + margin * 2))

    for row in m:
        line = white * margin
        for v in row:
            line += (black if v else white) * scale
        line += white * margin
        for _ in range(scale):
            print(line)

    for _ in range(margin * scale):
        print(white * (w + margin * 2))

def get_token(reset=False, headless=True):
    csrftoken = ""
    p20t = ""
    expirationTimestamp = -1
    with sync_playwright() as pw:
        ctx = launch_persistent_ctx(pw, reset=reset, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        apply_windows_ua(ctx, page)

        qr_results = []

        def update_p20t_from_context():
            try:
                cookies = ctx.cookies("https://www.binance.com")
                c = next((c for c in cookies if c.get("name") == "p20t"), None)
                token = c.get("value", "")
                if not token: return
                nonlocal p20t
                p20t = token
            except:
                pass

        def on_request(req):
            try:
                url = req.url
                if "https://www.binance.com/fapi/v1/ticker/24hr" in url:
                    token = req.headers.get("csrftoken", "")
                    if not token: return
                    nonlocal csrftoken
                    csrftoken = token
            except:
                pass

        def on_request_finished(req):
            try:
                url = req.url
                if "https://accounts.binance.com/bapi/accounts/v2/public/qrcode/login/get" in url:
                    resp = req.response()
                    if not resp: return
                    data = resp.json()
                    if not data.get("success"): return
                    code = data["data"]["qrCode"]
                    if code not in qr_results:
                        qr_results.append(code)
                        print("请使用 Binance App 扫描以下二维码登录")
                        print_qr(code)
                        img = qrcode.make(code).convert("RGB")
                        img.save("qrcode.jpg", format="JPEG", quality=100)
                elif "https://accounts.binance.com/bapi/accounts/v2/private/authcenter/setTrustDevice" in url:
                    resp = req.response()
                    if not resp: return
                    hdrs_arr = resp.headers_array()
                    date_hdr = resp.headers.get("date") or resp.header_value("date")
                    if not hdrs_arr or not date_hdr: return
                    sc_values = [h.get("value", "") for h in hdrs_arr if h.get("name", "").lower() == "set-cookie"]
                    m = next((m for sc in sc_values for m in SimpleCookie(sc).values() if m.key == "p20t"), None)
                    if not m: return
                    nonlocal p20t, expirationTimestamp
                    p20t = m.value
                    expirationTimestamp = int(m["max-age"]) + int(parsedate_to_datetime(date_hdr).timestamp())
            except:
                pass

        page.on("request", on_request)
        page.on("requestfinished", on_request_finished)
        ctx.on("request", on_request)
        ctx.on("requestfinished", on_request_finished)

        page.goto("https://accounts.binance.com/zh-CN/login?loginChannel=&return_to=", wait_until="domcontentloaded")

        while True:
            page.wait_for_timeout(1500)

            if csrftoken and p20t:
                token_dict = {"csrftoken": csrftoken, "p20t": p20t, "expirationTimestamp": expirationTimestamp}
                if os.path.exists("token.json"):
                    with open("token.json", "r") as f:
                        old_token_dict = json.load(f)
                    if token_dict["p20t"] != old_token_dict.get("p20t", "") or token_dict["csrftoken"] != old_token_dict.get("csrftoken", ""):
                        with open("token.json", "w") as f:
                            f.write(json.dumps(token_dict, indent=4, ensure_ascii=False))
                        print("检测到 p20t 或 csrftoken 变更, 已更新 token.json 文件")
                    elif token_dict["expirationTimestamp"] == -1:
                        expirationTimestamp = old_token_dict.get("expirationTimestamp", -1)
                print("csrftoken:", csrftoken)
                print("p20t:", p20t)
                print("expirationTimestamp:", expirationTimestamp)
                ctx.close()
                break

            try:
                if "accounts.binance.com" in page.url:
                    if page.get_by_text(re.compile("Understand")).count() > 0:
                        page.get_by_role("button", name=re.compile("Understand")).first.click(timeout=1200, force=True)

                    if page.get_by_text(re.compile("知道了")).count() > 0:
                        page.get_by_role("button", name=re.compile("知道了")).first.click(timeout=1200, force=True)

                    if page.get_by_text(re.compile("好的")).count() > 0:
                        page.get_by_role("button", name=re.compile("好的")).first.click(timeout=1200, force=True)

                    if page.get_by_text(re.compile("登录")).count() > 0 and page.get_by_text(re.compile("邮箱/手机号码")).count() > 0 and page.get_by_text(re.compile("用手机相机扫描")).count() == 0:
                        page.get_by_role("button", name=re.compile("登录")).first.click(timeout=1200, force=True)

                    if page.get_by_text(re.compile("刷新二维码")).count() > 0:
                        page.get_by_role("button", name=re.compile("刷新二维码")).first.click(timeout=1200, force=True)

                    if page.get_by_text(re.compile("保持登录状态")).count() > 0:
                        page.get_by_role("button", name=re.compile("是")).first.click(timeout=1200, force=True)
                else:
                    update_p20t_from_context()
            except:
                pass

def place_order_web(csrftoken, p20t, orderAmount, timeIncrements, symbolName, payoutRatio, direction):
    url = "https://www.binance.com/bapi/futures/v1/private/future/event-contract/place-order"
    headers = {
        "content-type": "application/json",
        "clienttype": "web",
        "csrftoken": csrftoken,
        "cookie": f"p20t={p20t}"
    }
    data = {
        "orderAmount": orderAmount,
        "timeIncrements": timeIncrements,
        "symbolName": symbolName,
        "payoutRatio": payoutRatio,
        "direction": direction
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    get_token(reset=False, headless=True) # 设置 reset=True 清除浏览器缓存, headless=False 显示浏览器界面
    # with open("token.json", "r") as f:
    #     token_dict = json.load(f)
    # csrftoken = token_dict["csrftoken"]
    # p20t = token_dict["p20t"]
    # result = place_order_web(csrftoken=csrftoken, p20t=p20t, orderAmount="5", timeIncrements="TEN_MINUTE", symbolName="BTCUSDT", payoutRatio="0.80", direction="LONG")
    # print("下单结果:", result)
