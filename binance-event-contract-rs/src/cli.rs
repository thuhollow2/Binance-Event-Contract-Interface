use std::path::PathBuf;

use clap::{ArgAction, Args, Parser, Subcommand};

use crate::constants::{DEFAULT_TIMEOUT_SECS, DEFAULT_TOKEN_FILE};

#[derive(Parser)]
#[command(author, version, about = "Binance 事件合约接口的 Rust 版本")]
pub struct Cli {
    #[arg(short, long, action = ArgAction::Count, global = true, help = "增加日志详细程度，可重复使用，如 -vv")]
    pub verbose: u8,
    #[command(subcommand)]
    pub command: Option<Command>,
}

#[derive(Subcommand)]
pub enum Command {
    GetToken(GetTokenArgs),
    PlaceOrder(PlaceOrderArgs),
}

#[derive(Debug, Clone, Args)]
pub struct GetTokenArgs {
    #[arg(long, default_value_t = false, help = "清空本地浏览器配置目录")]
    pub reset: bool,
    #[arg(long, default_value_t = true, action = ArgAction::Set, help = "是否以 headless 模式运行")]
    pub headless: bool,
    #[arg(long, default_value_t = DEFAULT_TIMEOUT_SECS, help = "等待扫码登录的最长秒数")]
    pub timeout_secs: u64,
    #[arg(long, default_value = DEFAULT_TOKEN_FILE, help = "token 输出文件")]
    pub token_file: PathBuf,
}

impl Default for GetTokenArgs {
    fn default() -> Self {
        Self {
            reset: false,
            headless: true,
            timeout_secs: DEFAULT_TIMEOUT_SECS,
            token_file: PathBuf::from(DEFAULT_TOKEN_FILE),
        }
    }
}

#[derive(Debug, Clone, Args)]
pub struct PlaceOrderArgs {
    #[arg(long, help = "直接传入 csrftoken；为空时从 token-file 读取")]
    pub csrftoken: Option<String>,
    #[arg(long, help = "直接传入 p20t；为空时从 token-file 读取")]
    pub p20t: Option<String>,
    #[arg(long, default_value = DEFAULT_TOKEN_FILE, help = "token 文件路径")]
    pub token_file: PathBuf,
    #[arg(long, help = "下单金额，例如 5")]
    pub order_amount: String,
    #[arg(long, help = "时间粒度，例如 TEN_MINUTE")]
    pub time_increments: String,
    #[arg(long, help = "交易对，例如 BTCUSDT")]
    pub symbol_name: String,
    #[arg(long, help = "赔率，例如 0.80")]
    pub payout_ratio: String,
    #[arg(long, help = "方向，例如 LONG 或 SHORT")]
    pub direction: String,
}