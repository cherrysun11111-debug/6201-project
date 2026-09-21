from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from ecrisk.batch import analyze_rows, read_reviews, summarize
from ecrisk.predict import classify
from ecrisk.train import DEFAULT_DATA


FORM = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>E-commerce Complaint Risk</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #65717d;
      --line: #d9dee3;
      --panel: #ffffff;
      --canvas: #f4f6f8;
      --blue: #1f6feb;
      --green: #188038;
      --amber: #b26a00;
      --red: #c5221f;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: Arial, sans-serif; margin: 0; background: var(--canvas); color: var(--ink); }}
    header {{ border-bottom: 1px solid var(--line); background: #ffffff; }}
    .topbar {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 18px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    h1 {{ font-size: 22px; margin: 0; }}
    .status {{ color: var(--muted); font-size: 13px; }}
    main {{
      max-width: 1160px;
      margin: 24px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: minmax(320px, 1fr) minmax(340px, 0.9fr);
      gap: 20px;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    h2 {{ font-size: 16px; margin: 0 0 12px; }}
    textarea {{
      width: 100%;
      min-height: 260px;
      resize: vertical;
      padding: 14px;
      border: 1px solid #c8d0d8;
      border-radius: 6px;
      font: 15px/1.45 Arial, sans-serif;
      color: var(--ink);
    }}
    button {{
      margin-top: 14px;
      padding: 11px 16px;
      border: 0;
      border-radius: 6px;
      background: var(--blue);
      color: white;
      font-weight: 700;
      cursor: pointer;
    }}
    .hint {{ margin-top: 12px; color: var(--muted); font-size: 13px; line-height: 1.45; }}
    .placeholder {{ color: var(--muted); line-height: 1.5; }}
    .score {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0; }}
    .metric {{ border: 1px solid var(--line); border-radius: 8px; padding: 12px; background: #fbfcfd; }}
    .metric small {{ display: block; color: var(--muted); margin-bottom: 6px; }}
    .metric strong {{ font-size: 19px; line-height: 1.2; overflow-wrap: anywhere; }}
    .pill {{
      display: inline-block;
      padding: 5px 9px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      background: #eef2f7;
      margin: 0 6px 6px 0;
    }}
    .risk-high {{ color: var(--red); }}
    .risk-medium {{ color: var(--amber); }}
    .risk-low {{ color: var(--green); }}
    .row {{ border-top: 1px solid var(--line); padding-top: 12px; margin-top: 12px; }}
    .label {{ color: var(--muted); font-size: 13px; margin-bottom: 4px; }}
    .value {{ line-height: 1.45; }}
    .bars {{ display: grid; gap: 9px; }}
    .barline {{ display: grid; grid-template-columns: 70px 1fr 45px; gap: 8px; align-items: center; font-size: 13px; }}
    .track {{ height: 9px; background: #e8edf2; border-radius: 99px; overflow: hidden; }}
    .fill {{ height: 100%; background: var(--blue); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .nav a {{
      color: var(--blue);
      text-decoration: none;
      border: 1px solid #b9cdf8;
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 700; }}
    .wide {{ grid-column: 1 / -1; }}
    @media (max-width: 820px) {{
      main {{ grid-template-columns: 1fr; padding: 0 14px; }}
      .topbar {{ padding: 16px 14px; align-items: flex-start; flex-direction: column; }}
      .score {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<header>
  <div class="topbar">
    <h1>E-commerce Complaint Risk Analysis</h1>
    <div class="nav"><a href="/">Single review</a><a href="/queue">Priority queue</a></div>
  </div>
</header>
<main>
  <section>
    <h2>Customer Review</h2>
    <form method="post">
      <textarea name="review" placeholder="Paste one customer review or support complaint here">{review}</textarea>
      <br><button type="submit">Analyze risk</button>
    </form>
    <div class="hint">The tool classifies complaint risk, identifies the likely complaint type, and recommends the next support action. It does not make refund, penalty, or safety decisions automatically.</div>
  </section>
  <section>
    <h2>Triage Result</h2>
    {result}
  </section>
</main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/queue"):
            self.respond(render_queue_page())
            return
        self.respond(FORM.format(review="", result="<p class='placeholder'>Paste a review to see risk, complaint type, evidence, SLA, and response guidance.</p>"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        review = parse_qs(body).get("review", [""])[0]
        if not review.strip():
            result = "<p class='placeholder'>Please enter a review.</p>"
        else:
            prediction = classify(review)
            result = render_result(prediction)
        self.respond(FORM.format(review=escape(review), result=result))

    def respond(self, html: str):
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Open http://127.0.0.1:8000")
    server.serve_forever()


def render_result(prediction: dict[str, object]) -> str:
    risk = str(prediction["risk"])
    probabilities = prediction["probabilities"]
    evidence_terms = prediction["evidence_terms"] or ["No strong keyword evidence"]
    bars = "".join(
        f"<div class='barline'><span>{escape(label)}</span><div class='track'>"
        f"<div class='fill' style='width: {int(float(value) * 100)}%'></div></div>"
        f"<span>{float(value):.2f}</span></div>"
        for label, value in probabilities.items()
    )
    terms = "".join(f"<span class='pill'>{escape(str(term))}</span>" for term in evidence_terms)
    return (
        f"<div class='score'>"
        f"<div class='metric'><small>Risk</small><strong class='risk-{escape(risk)}'>{escape(risk)}</strong></div>"
        f"<div class='metric'><small>Confidence</small><strong>{prediction['confidence']}</strong></div>"
        f"<div class='metric'><small>SLA</small><strong>{escape(str(prediction['sla']))}</strong></div>"
        f"</div>"
        f"<div class='row'><div class='label'>Complaint type</div><div class='value'>{escape(str(prediction['complaint_type']))}</div></div>"
        f"<div class='row'><div class='label'>Recommended action</div><div class='value'>{escape(str(prediction['recommended_action']))}</div></div>"
        f"<div class='row'><div class='label'>Customer reply frame</div><div class='value'>{escape(str(prediction['customer_reply_frame']))}</div></div>"
        f"<div class='row'><div class='label'>Evidence terms</div><div>{terms}</div></div>"
        f"<div class='row'><div class='label'>Probability distribution</div><div class='bars'>{bars}</div></div>"
        f"<div class='row'><div class='label'>Baseline explanation</div><div class='value'>{escape(str(prediction['baseline_explanation']))}</div></div>"
        f"<div class='row'><div class='label'>Responsible use</div><div class='value'>{escape(str(prediction['responsible_use_note']))}</div></div>"
    )


def render_queue_page() -> str:
    all_rows = analyze_rows(read_reviews(DEFAULT_DATA))
    rows = all_rows[:25]
    summary = summarize(all_rows)
    risk_counts = summary["risk_counts"]
    type_counts = summary["complaint_type_counts"]
    body_rows = "".join(
        "<tr>"
        f"<td>{escape(row.get('id', ''))}</td>"
        f"<td><strong class='risk-{escape(row['predicted_risk'])}'>{escape(row['predicted_risk'])}</strong></td>"
        f"<td>{escape(row['complaint_type'])}</td>"
        f"<td>{escape(row['sla'])}</td>"
        f"<td>{escape(row['review_text'])}</td>"
        "</tr>"
        for row in rows
    )
    risk_pills = "".join(
        f"<span class='pill'>{escape(risk)}: {count}</span>"
        for risk, count in sorted(risk_counts.items())
    )
    type_pills = "".join(
        f"<span class='pill'>{escape(label)}: {count}</span>"
        for label, count in sorted(type_counts.items())
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Complaint Priority Queue</title>
  <style>{extract_styles()}</style>
</head>
<body>
<header>
  <div class="topbar">
    <h1>Complaint Priority Queue</h1>
    <div class="nav"><a href="/">Single review</a><a href="/queue">Priority queue</a></div>
  </div>
</header>
<main>
  <section class="wide">
    <h2>Batch Triage Summary</h2>
    <div class="score">
      <div class="metric"><small>Total analyzed</small><strong>{len(all_rows)}</strong></div>
      <div class="metric"><small>High priority</small><strong class="risk-high">{risk_counts.get('high', 0)}</strong></div>
      <div class="metric"><small>Abstentions</small><strong>{summary['abstention_count']}</strong></div>
    </div>
    <div class="row"><div class="label">Risk distribution</div><div>{risk_pills}</div></div>
    <div class="row"><div class="label">Complaint type distribution</div><div>{type_pills}</div></div>
  </section>
  <section class="wide">
    <h2>Top Priority Reviews</h2>
    <div class="hint">Showing the first {len(rows)} reviews after sorting all analyzed reviews by risk priority. The 40-row challenge set is used in evaluation, not this operational queue.</div>
    <table>
      <thead><tr><th>ID</th><th>Risk</th><th>Type</th><th>SLA</th><th>Review</th></tr></thead>
      <tbody>{body_rows}</tbody>
    </table>
  </section>
</main>
</body>
</html>"""


def extract_styles() -> str:
    start = FORM.index("<style>") + len("<style>")
    end = FORM.index("</style>")
    return FORM[start:end].replace("{{", "{").replace("}}", "}")


if __name__ == "__main__":
    main()
