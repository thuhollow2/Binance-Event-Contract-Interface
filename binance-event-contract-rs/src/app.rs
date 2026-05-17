use anyhow::Result;
use clap::Parser;
use log::info;

use crate::{
    cli::{Cli, Command, GetTokenArgs},
    login::get_token,
    logging::init_logger,
    trade::place_order,
};

pub fn run() -> Result<()> {
    let cli = Cli::parse();
    init_logger(cli.verbose);

    match cli.command.unwrap_or(Command::GetToken(GetTokenArgs::default())) {
        Command::GetToken(args) => {
            info!("开始执行 get-token");
            get_token(args)?;
        }
        Command::PlaceOrder(args) => {
            info!("开始执行 place-order");
            place_order(args)?;
        }
    }

    Ok(())
}