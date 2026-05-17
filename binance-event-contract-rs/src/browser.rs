use std::{collections::HashMap, ffi::OsStr, path::Path, time::Duration};

use anyhow::{Context, Result};
use headless_chrome::{Browser, LaunchOptionsBuilder, Tab};

use crate::constants::WIN_UA;

pub fn launch_browser(profile_dir: &Path, headless: bool) -> Result<Browser> {
    let args = vec![
        OsStr::new("--no-first-run"),
        OsStr::new("--no-default-browser-check"),
        OsStr::new("--window-size=1280,960"),
        OsStr::new("--lang=zh-CN"),
    ];

    let mut builder = LaunchOptionsBuilder::default();
    builder
        .headless(headless)
        .sandbox(false)
        .enable_gpu(false)
        .window_size(Some((1280, 960)))
        .idle_browser_timeout(Duration::from_secs(120))
        .user_data_dir(Some(profile_dir.to_path_buf()))
        .args(args);

    let options = builder.build().context("构建浏览器启动参数失败")?;
    Browser::new(options)
        .context("启动 Chromium/Chrome 失败，请确认本机已安装 Chrome 或 Chromium")
}

pub fn configure_tab(tab: &Tab) -> Result<()> {
    let mut headers = HashMap::new();
    headers.insert("accept-language", "zh-CN,zh;q=0.9");
    headers.insert("sec-ch-ua-mobile", "?0");
    headers.insert("sec-ch-ua-platform", "\"Windows\"");

    tab.set_default_timeout(Duration::from_secs(3));
    tab.set_user_agent(WIN_UA, Some("zh-CN,zh;q=0.9"), Some("Windows"))
        .context("设置 User-Agent 失败")?;
    tab.set_extra_http_headers(headers)
        .context("设置额外请求头失败")?;
    tab.enable_stealth_mode().ok();
    Ok(())
}