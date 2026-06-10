from datetime import datetime


# ============================================================
# MARKDOWN REPORT GENERATOR
# ============================================================

def build_markdown_report(final_data: list[dict]) -> str:
    """
    Input:
        final_data: output from summary stage

    Process:
        - Formats results into clean markdown
        - Adds headings + structure

    Output:
        str (markdown content)
    """

    print("[REPORT] Building markdown output")

    md = []

    md.append("# AI Research Report\n")

    md.append(f"Generated: {datetime.now()}\n")

    for item in final_data:

        md.append("\n---\n")

        md.append(f"## {item.get('title', 'No Title')}\n")

        md.append(f"**URL:** {item['url']}\n")

        md.append("### Summary\n")
        md.append(item.get("summary", ""))

        md.append("\n")

    return "\n".join(md)


# ============================================================
# SAVE FILE
# ============================================================

def save_markdown(content: str, filename: str = "report.md") -> None:
    """
    Writes markdown file to disk.
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[REPORT] Saved -> {filename}")