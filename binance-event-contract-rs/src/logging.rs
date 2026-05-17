use env_logger::{Builder, Env};

pub fn init_logger(verbose: u8) {
    let default_filter = match verbose {
        0 => "info",
        1 => "debug",
        _ => "trace",
    };

    let mut builder = Builder::from_env(Env::default().default_filter_or(default_filter));
    builder.format_timestamp_millis();
    builder.format_target(false);
    builder.format_module_path(false);
    let _ = builder.try_init();
}