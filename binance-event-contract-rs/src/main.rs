mod app;
mod browser;
mod cli;
mod constants;
mod login;
mod logging;
mod models;
mod qr;
mod token_store;
mod trade;

use anyhow::Result;

fn main() -> Result<()> {
    app::run()
}
