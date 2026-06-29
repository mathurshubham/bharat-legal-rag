// Client-side "download as PDF" with no extra dependency: open a print window
// containing the already-rendered HTML and trigger the browser's print dialog
// (user picks "Save as PDF"). `html` is the innerHTML of a rendered markdown node.
export function printHtmlToPdf(title: string, html: string): void {
  const win = window.open("", "_blank", "width=820,height=1000")
  if (!win) return
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title>
<style>
  @page { margin: 18mm 16mm; }
  body { font: 13px/1.55 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color: #111; }
  h1 { font-size: 19px; } h2 { font-size: 16px; margin-top: 1.1em; }
  h3 { font-size: 14px; } h1,h2,h3 { color:#111; }
  table { border-collapse: collapse; width: 100%; margin: 8px 0; }
  th, td { border: 1px solid #999; padding: 4px 7px; text-align: left; vertical-align: top; }
  pre, code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; }
  pre { background:#f5f5f5; padding:8px; border-radius:6px; white-space:pre-wrap; }
  blockquote { border-left:3px solid #ccc; margin:6px 0; padding-left:10px; color:#444; }
  hr { border:0; border-top:1px solid #ddd; margin:14px 0; }
  ul,ol { padding-left: 20px; }
</style></head><body>${html}</body></html>`)
  win.document.close()
  win.focus()
  // give the new window a tick to lay out before printing
  setTimeout(() => { win.print() }, 300)
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string))
}
