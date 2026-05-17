use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TokenFile {
    pub csrftoken: String,
    pub p20t: String,
    #[serde(rename = "expirationTimestamp")]
    pub expiration_timestamp: i64,
}

#[derive(Debug, Clone, Serialize)]
pub struct PlaceOrderRequest<'a> {
    #[serde(rename = "orderAmount")]
    pub order_amount: &'a str,
    #[serde(rename = "timeIncrements")]
    pub time_increments: &'a str,
    #[serde(rename = "symbolName")]
    pub symbol_name: &'a str,
    #[serde(rename = "payoutRatio")]
    pub payout_ratio: &'a str,
    pub direction: &'a str,
}

#[derive(Debug, Clone, Default)]
pub struct CookieSnapshot {
    pub p20t: Option<(String, i64)>,
    pub csrftoken: Option<String>,
}