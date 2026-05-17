use std::time::Duration;

use anyhow::{Context, Result, bail};
use log::{debug, info};
use reqwest::{
    blocking::Client,
    header::{CONTENT_TYPE, COOKIE},
};
use serde_json::Value;

use crate::{
    cli::PlaceOrderArgs,
    constants::{PLACE_ORDER_URL, WIN_UA},
    models::{PlaceOrderRequest, TokenFile},
    token_store::read_token_file,
};

pub fn place_order(args: PlaceOrderArgs) -> Result<Value> {
    let token = resolve_token(&args)?;
    let request = PlaceOrderRequest {
        order_amount: &args.order_amount,
        time_increments: &args.time_increments,
        symbol_name: &args.symbol_name,
        payout_ratio: &args.payout_ratio,
        direction: &args.direction,
    };

    let client = Client::builder()
        .timeout(Duration::from_secs(30))
        .user_agent(WIN_UA)
        .build()
        .context("创建 HTTP 客户端失败")?;

    let response = client
        .post(PLACE_ORDER_URL)
        .header(CONTENT_TYPE, "application/json")
        .header("clienttype", "web")
        .header("csrftoken", &token.csrftoken)
        .header(COOKIE, format!("p20t={}", token.p20t))
        .json(&request)
        .send()
        .context("下单请求发送失败")?;

    let status = response.status();
    debug!(
        "下单请求已返回，symbol={}, direction={}, status={status}",
        args.symbol_name, args.direction
    );
    let text = response.text().context("读取下单响应失败")?;
    if !status.is_success() {
        bail!("下单请求失败: {status} {text}");
    }

    let json: Value = serde_json::from_str(&text).context("下单响应不是有效 JSON")?;
    info!("下单请求成功");
    println!(
        "{}",
        serde_json::to_string_pretty(&json).context("格式化下单响应失败")?
    );
    Ok(json)
}

fn resolve_token(args: &PlaceOrderArgs) -> Result<TokenFile> {
    let existing = if args.token_file.exists() {
        Some(read_token_file(&args.token_file)?)
    } else {
        None
    };

    let csrftoken = args
        .csrftoken
        .clone()
        .or_else(|| existing.as_ref().map(|token| token.csrftoken.clone()))
        .context("缺少 csrftoken，请通过 --csrftoken 提供或先执行 get-token")?;
    let p20t = args
        .p20t
        .clone()
        .or_else(|| existing.as_ref().map(|token| token.p20t.clone()))
        .context("缺少 p20t，请通过 --p20t 提供或先执行 get-token")?;

    Ok(TokenFile {
        csrftoken,
        p20t,
        expiration_timestamp: existing
            .map(|token| token.expiration_timestamp)
            .unwrap_or(-1),
    })
}