use std::{fs, path::Path};

use anyhow::{Context, Result};
use headless_chrome::{
    Tab,
    browser::tab::element::Element,
    protocol::cdp::Page::CaptureScreenshotFormatOption,
};
use log::{debug, warn};

const QR_MARKER_ATTR: &str = "data-rs-qr-candidate";
const QR_MARKER_SELECTOR: &str = "[data-rs-qr-candidate='true']";

const MARK_QR_CANDIDATE_SCRIPT: &str = r#"
(() => {
  const marker = 'data-rs-qr-candidate';
  const normalize = (value) => (value || '').toLowerCase();
  document.querySelectorAll(`[${marker}]`).forEach((node) => node.removeAttribute(marker));

  const isVisible = (element, rect) => {
    if (!rect || rect.width < 80 || rect.height < 80) return false;
    const style = window.getComputedStyle(element);
    return style.display !== 'none'
      && style.visibility !== 'hidden'
      && Number(style.opacity || 1) > 0.05
      && rect.bottom > 0
      && rect.right > 0
      && rect.top < window.innerHeight
      && rect.left < window.innerWidth;
  };

  const scoreCandidate = (element) => {
    const rect = element.getBoundingClientRect();
    if (!isVisible(element, rect)) return null;

    const attrs = [
      element.id,
      element.className,
      element.getAttribute('data-testid'),
      element.getAttribute('aria-label'),
      element.getAttribute('alt'),
      element.getAttribute('title'),
      element.getAttribute('src'),
    ].map(normalize).join(' ');

    const parentText = [];
    let parent = element;
    for (let depth = 0; depth < 4 && parent; depth += 1, parent = parent.parentElement) {
      parentText.push(normalize(parent.innerText));
    }
    const hints = `${attrs} ${parentText.join(' ')}`;

    const minSide = Math.min(rect.width, rect.height);
    const ratioPenalty = Math.abs(rect.width - rect.height);
    if (minSide < 120) return null;

    const tagScore = ['CANVAS', 'IMG', 'SVG'].includes(element.tagName) ? 30 : 0;
    const hintScore = /qr|二维码|扫码|scan/.test(hints) ? 60 : 0;
    const sizeScore = Math.max(0, 320 - Math.abs(minSide - 240));
    const centerPenalty = Math.abs((rect.left + rect.width / 2) - window.innerWidth / 2) * 0.05;

    let score = tagScore + hintScore + sizeScore;
    score -= ratioPenalty * 4;
    score -= centerPenalty;

    if (element.tagName === 'DIV' && !element.querySelector('canvas, img, svg')) {
      score -= 30;
    }

    return { score, element };
  };

  const selectors = [
    'canvas',
    'img',
    'svg',
    '[class*="qr"]',
    '[class*="QR"]',
    '[id*="qr"]',
    '[id*="QR"]',
    '[data-testid*="qr"]',
  ];

  const candidates = Array.from(document.querySelectorAll(selectors.join(',')))
    .map(scoreCandidate)
    .filter(Boolean)
    .sort((left, right) => right.score - left.score);

  if (!candidates.length) {
    return false;
  }

  candidates[0].element.setAttribute(marker, 'true');
  return true;
})();
"#;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QrCaptureMode {
    FocusedElement,
    FullPageFallback,
}

pub fn save_qr_snapshot(tab: &Tab, output: &Path) -> Result<QrCaptureMode> {
    if let Err(err) = annotate_qr_candidate(tab) {
        debug!("二维码候选标注失败，将继续走回退路径: {err:#}");
    }

    if let Some(element) = find_qr_candidate(tab) {
        if let Err(err) = element.scroll_into_view() {
            debug!("滚动二维码元素到视口失败: {err:#}");
        }

        match capture_element(element, output) {
            Ok(()) => return Ok(QrCaptureMode::FocusedElement),
            Err(err) => warn!("抓取二维码元素截图失败，回退到整页截图: {err:#}"),
        }
    }

    capture_full_page(tab, output)?;
    Ok(QrCaptureMode::FullPageFallback)
}

fn annotate_qr_candidate(tab: &Tab) -> Result<()> {
    tab.evaluate(MARK_QR_CANDIDATE_SCRIPT, false)
        .context("执行二维码候选定位脚本失败")?;
    Ok(())
}

fn find_qr_candidate<'a>(tab: &'a Tab) -> Option<Element<'a>> {
    let selectors = [
        QR_MARKER_SELECTOR,
        "img[alt*='qr']",
        "img[src^='data:image']",
        "canvas",
        "[class*='qr']",
        "[class*='QR']",
        "[id*='qr']",
        "[id*='QR']",
    ];

    for selector in selectors {
        if let Ok(element) = tab.find_element(selector) {
            if element.is_visible().unwrap_or(false) {
                return Some(element);
            }
        }
    }

    None
}

fn capture_element(element: Element<'_>, output: &Path) -> Result<()> {
    let bytes = element
        .capture_screenshot(CaptureScreenshotFormatOption::Png)
        .context("抓取二维码元素截图失败")?;
    fs::write(output, bytes)
        .with_context(|| format!("写入二维码截图失败: {}", output.display()))?;
    Ok(())
}

fn capture_full_page(tab: &Tab, output: &Path) -> Result<()> {
    let bytes = tab
        .capture_screenshot(CaptureScreenshotFormatOption::Png, None, None, true)
        .context("抓取整页截图失败")?;
    fs::write(output, bytes)
        .with_context(|| format!("写入二维码截图失败: {}", output.display()))?;
    Ok(())
}

pub fn clear_qr_marker(tab: &Tab) {
    let script = format!(
        "document.querySelectorAll('[{QR_MARKER_ATTR}]').forEach((node) => node.removeAttribute('{QR_MARKER_ATTR}'));"
    );
    tab.evaluate(&script, false).ok();
}