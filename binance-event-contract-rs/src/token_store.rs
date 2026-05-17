use std::{fs, path::Path};

use anyhow::{Context, Result};
use log::info;

use crate::models::TokenFile;

pub fn merge_existing_expiration(path: &Path, mut token: TokenFile) -> Result<TokenFile> {
    if token.expiration_timestamp != -1 {
        return Ok(token);
    }

    if let Ok(existing) = read_token_file(path) {
        token.expiration_timestamp = existing.expiration_timestamp;
    }

    Ok(token)
}

pub fn write_token_file(path: &Path, token: &TokenFile) -> Result<()> {
    if let Some(parent) = path.parent().filter(|parent| !parent.as_os_str().is_empty()) {
        fs::create_dir_all(parent)
            .with_context(|| format!("创建 token 输出目录失败: {}", parent.display()))?;
    }

    let content = serde_json::to_string_pretty(token).context("序列化 token 失败")?;
    let changed = read_token_file(path)
        .map(|existing| existing != *token)
        .unwrap_or(true);
    fs::write(path, content).with_context(|| format!("写入 token 失败: {}", path.display()))?;

    if changed {
        info!("已写入 token 文件: {}", path.display());
    } else {
        info!("token 未变化，已覆盖写回: {}", path.display());
    }

    Ok(())
}

pub fn read_token_file(path: &Path) -> Result<TokenFile> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("读取 token 文件失败: {}", path.display()))?;
    serde_json::from_str(&content)
        .with_context(|| format!("解析 token 文件失败: {}", path.display()))
}