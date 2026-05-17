use std::{
    env, fs,
    sync::Arc,
    thread,
    time::{Duration, Instant},
};

use anyhow::{Context, Result, bail};
use headless_chrome::{Browser, Tab, protocol::cdp::Network};
use log::{debug, info, warn};

use crate::{
    browser::{configure_tab, launch_browser},
    cli::GetTokenArgs,
    constants::{BINANCE_HOME_URL, DEFAULT_PROFILE_DIR, DEFAULT_QR_FILE, LOGIN_URL},
    models::{CookieSnapshot, TokenFile},
    qr::{QrCaptureMode, clear_qr_marker, save_qr_snapshot},
    token_store::{merge_existing_expiration, write_token_file},
};

pub fn get_token(args: GetTokenArgs) -> Result<TokenFile> {
    let working_dir = env::current_dir().context("读取当前工作目录失败")?;
    let profile_dir = working_dir.join(DEFAULT_PROFILE_DIR);
    let qr_file = working_dir.join(DEFAULT_QR_FILE);

    if args.reset && profile_dir.exists() {
        fs::remove_dir_all(&profile_dir).with_context(|| {
            format!("删除浏览器配置目录失败: {}", profile_dir.display())
        })?;
    }

    fs::create_dir_all(&profile_dir).with_context(|| {
        format!("创建浏览器配置目录失败: {}", profile_dir.display())
    })?;

    let browser = launch_browser(&profile_dir, args.headless)?;
    let login_tab = browser.new_tab().context("创建登录标签页失败")?;
    configure_tab(login_tab.as_ref())?;
    login_tab
        .navigate_to(LOGIN_URL)
        .context("打开 Binance 登录页失败")?;
    login_tab.wait_until_navigated().ok();

    info!("已打开 Binance 登录页");
    if args.headless {
        info!(
            "当前为 headless 模式，会持续刷新 {DEFAULT_QR_FILE}，请打开该文件并用 Binance App 扫码。"
        );
    } else {
        info!("如浏览器界面未显示二维码，可打开 {DEFAULT_QR_FILE} 扫码。");
    }

    let start = Instant::now();
    let mut qr_announced = false;
    let mut landing_tab: Option<Arc<Tab>> = None;
    let mut qr_fallback_streak = 0u32;
    let mut cookie_error_streak = 0u32;
    let mut no_progress_streak = 0u32;
    let mut csrftoken_wait_streak = 0u32;

    loop {
        if should_restore_login_page(login_tab.as_ref(), landing_tab.is_none()) {
            restore_login_page(login_tab.as_ref(), "检测到登录页异常或跳出 Binance 域名");
        }

        click_known_buttons(login_tab.as_ref());

        match save_qr_snapshot(login_tab.as_ref(), &qr_file) {
            Ok(QrCaptureMode::FocusedElement) => {
                if qr_fallback_streak > 0 {
                    debug!("二维码元素定位已恢复正常");
                }
                qr_fallback_streak = 0;
                if !qr_announced {
                    info!("二维码截图已保存到 {}", qr_file.display());
                    qr_announced = true;
                }
            }
            Ok(QrCaptureMode::FullPageFallback) => {
                qr_fallback_streak += 1;
                if qr_fallback_streak == 1 || qr_fallback_streak % 3 == 0 {
                    warn!(
                        "未能稳定定位二维码元素，已回退为整页截图: {}",
                        qr_file.display()
                    );
                }
            }
            Err(err) => {
                qr_fallback_streak += 1;
                warn!("更新二维码截图失败: {err:#}");
            }
        }

        let snapshot = match collect_cookie_snapshot(login_tab.as_ref()) {
            Ok(snapshot) => {
                cookie_error_streak = 0;
                snapshot
            }
            Err(err) => {
                cookie_error_streak += 1;
                warn!("读取 Cookie 失败，第 {cookie_error_streak} 次重试: {err:#}");

                if cookie_error_streak >= 3 {
                    restore_login_page(login_tab.as_ref(), "连续读取 Cookie 失败");
                    cookie_error_streak = 0;
                }

                if start.elapsed() > Duration::from_secs(args.timeout_secs) {
                    bail!(
                        "在 {} 秒内未获取到 token，请确认已经完成扫码、信任设备与登录流程；当前二维码文件位于 {}",
                        args.timeout_secs,
                        qr_file.display()
                    );
                }

                thread::sleep(Duration::from_millis(1500));
                continue;
            }
        };

        debug!(
            "Cookie 快照: has_p20t={}, has_csrftoken={}",
            snapshot.p20t.is_some(),
            snapshot.csrftoken.is_some()
        );

        let has_p20t = snapshot.p20t.is_some();
        let has_csrftoken = snapshot.csrftoken.is_some();

        if has_p20t && !has_csrftoken && landing_tab.is_none() {
            landing_tab = Some(open_home_tab(&browser)?);
            login_tab.bring_to_front().ok();
            info!("已补开 Binance 首页以触发 csrftoken");
        }

        if has_p20t && !has_csrftoken {
            csrftoken_wait_streak += 1;
            if csrftoken_wait_streak % 5 == 0 {
                if let Some(tab) = landing_tab.as_ref() {
                    refresh_home_tab(tab.as_ref());
                }
            }
        } else {
            csrftoken_wait_streak = 0;
        }

        if let (Some((p20t, expiration_timestamp)), Some(csrftoken)) =
            (snapshot.p20t.clone(), snapshot.csrftoken.clone())
        {
            clear_qr_marker(login_tab.as_ref());
            let token = merge_existing_expiration(
                &args.token_file,
                TokenFile {
                    csrftoken,
                    p20t,
                    expiration_timestamp,
                },
            )?;
            write_token_file(&args.token_file, &token)?;
            info!("成功获取 token，已写入 {}", args.token_file.display());
            println!("csrftoken: {}", token.csrftoken);
            println!("p20t: {}", token.p20t);
            println!("expirationTimestamp: {}", token.expiration_timestamp);
            return Ok(token);
        }

        if has_p20t || has_csrftoken {
            no_progress_streak = 0;
        } else {
            no_progress_streak += 1;
        }

        if !has_p20t && qr_fallback_streak >= 5 {
            restore_login_page(login_tab.as_ref(), "连续未稳定定位到二维码");
            qr_fallback_streak = 0;
        } else if no_progress_streak > 0 && no_progress_streak % 20 == 0 {
            restore_login_page(login_tab.as_ref(), "长时间未观察到登录进展");
        }

        if start.elapsed() > Duration::from_secs(args.timeout_secs) {
            bail!(
                "在 {} 秒内未获取到 token，请确认已经完成扫码、信任设备与登录流程；当前二维码文件位于 {}",
                args.timeout_secs,
                qr_file.display()
            );
        }

        thread::sleep(Duration::from_millis(1500));
    }
}

fn click_known_buttons(tab: &Tab) {
    let script = r#"
(() => {
  const normalize = (value) => (value || '').replace(/\s+/g, '');
  const exact = ['二维码登录', '刷新二维码', '登录失败', '是'];
  const partial = ['Understand', '知道了', '好的', '已知晓'];
  const nodes = Array.from(document.querySelectorAll('button, [role="button"], a, span'));

  for (const node of nodes) {
    const text = normalize(node.innerText || node.textContent || '');
    if (!text) continue;
    if (exact.includes(text) || partial.some((item) => text.includes(item))) {
      node.click();
      continue;
    }
    if (text === '登录' && !document.body.innerText.includes('用手机相机扫描')) {
      node.click();
    }
  }
})();
"#;

    if let Err(err) = tab.evaluate(script, false) {
        debug!("自动点击登录页按钮失败: {err:#}");
    }
}

fn collect_cookie_snapshot(tab: &Tab) -> Result<CookieSnapshot> {
    let all_cookies = tab
        .call_method(Network::GetAllCookies(None))
        .context("读取浏览器 Cookie 失败")?;

    let mut snapshot = CookieSnapshot::default();
    for cookie in all_cookies.cookies {
        if !cookie.domain.contains("binance.com") {
            continue;
        }

        match cookie.name.as_str() {
            "p20t" => {
                let expiration_timestamp = cookie_expiration_timestamp(&cookie);
                snapshot.p20t = Some((cookie.value, expiration_timestamp));
            }
            "csrftoken" => {
                snapshot.csrftoken = Some(cookie.value);
            }
            _ => {}
        }
    }

    Ok(snapshot)
}

fn cookie_expiration_timestamp(cookie: &Network::Cookie) -> i64 {
    if cookie.session {
        -1
    } else {
        cookie.expires.floor() as i64
    }
}

fn open_home_tab(browser: &Browser) -> Result<Arc<Tab>> {
    let tab = browser.new_tab().context("创建 Binance 首页标签页失败")?;
    configure_tab(tab.as_ref())?;
    tab.navigate_to(BINANCE_HOME_URL)
        .context("打开 Binance 首页失败")?;
    tab.wait_until_navigated().ok();
    Ok(tab)
}

fn refresh_home_tab(tab: &Tab) {
    warn!("仍未拿到 csrftoken，尝试刷新 Binance 首页");
    if let Err(err) = tab.navigate_to(BINANCE_HOME_URL) {
        warn!("重新打开 Binance 首页失败: {err:#}");
        tab.reload(false, None).ok();
    }
    tab.wait_until_navigated().ok();
}

fn should_restore_login_page(tab: &Tab, awaiting_login: bool) -> bool {
    if !awaiting_login {
        return false;
    }

    let url = tab.get_url();
    url.is_empty()
        || url.starts_with("chrome-error://")
        || url.starts_with("about:blank")
        || (!url.contains("binance.com") && !url.contains("accounts.binance.com"))
}

fn restore_login_page(tab: &Tab, reason: &str) {
    warn!("{reason}，重新打开 Binance 登录页");
    if let Err(err) = tab.navigate_to(LOGIN_URL) {
        warn!("重新打开 Binance 登录页失败: {err:#}");
        tab.reload(false, None).ok();
    }
    tab.wait_until_navigated().ok();
}