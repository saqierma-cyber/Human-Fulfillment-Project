import requests
import streamlit as st
from html import escape, unescape
import re
import pandas as pd


API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="曾仕强视角分析智能体", layout="wide")
st.markdown(
    """
    <style>
    .tag {
        display:inline-block;
        padding:5px 10px;
        margin:4px 6px 4px 0;
        border-radius:999px;
        background:#eef4fb;
        color:#244b69;
        font-size:12px;
        font-weight:600;
        border:1px solid #d5e1ee;
    }
    .card {
        border-radius:14px;
        padding:16px 18px;
        margin:10px 0;
        background:#ffffff;
        border:1px solid #e5ebf2;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }
    .section-title {
        font-size:17px;
        font-weight:800;
        color:#15324b;
        margin-bottom:10px;
    }
    .summary {
        font-size:14px;
        line-height:1.8;
        color:#2b4052;
    }
    .mini-meta {
        font-size: 12px;
        color: #708196;
        line-height: 1.7;
    }
    .panel {
        background: #ffffff;
        border: 1px solid #E5EBF2;
        border-radius: 16px;
        padding: 14px 16px;
        margin: 8px 0 14px 0;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }
    .note {
        background: #FAFCFF;
        border: 1px solid #E5ECF4;
        border-left: 4px solid #86A7C4;
        border-radius: 12px;
        padding: 12px 14px;
        margin: 8px 0;
    }
    .note-warn {
        background: #FFF9F1;
        border: 1px solid #F2DEC4;
        border-left: 4px solid #D7A85A;
    }
    .note-title {
        font-size: 14px;
        font-weight: 700;
        color: #17344C;
        margin-bottom: 4px;
    }
    .note-body {
        font-size: 13px;
        line-height: 1.8;
        color: #465B6F;
    }
    .major-title {
        font-size: 22px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 28px 0 12px 0;
        letter-spacing: 0.3px;
    }
    .section-panel {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 14px 16px;
        margin: 10px 0 18px 0;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        border: 1px solid #E5EBF2;
        border-radius: 14px;
        overflow: hidden;
        background: #FFFFFF;
    }
    .data-table th,
    .data-table td {
        border-bottom: 1px solid #E8EEF5;
        padding: 10px 12px;
        text-align: left;
        vertical-align: top;
        white-space: normal;
        word-break: break-word;
        overflow-wrap: anywhere;
        line-height: 1.7;
        font-size: 13px;
        color: #2B4052;
    }
    .data-table th {
        background: #F7FAFD;
        color: #17344C;
        font-weight: 700;
    }
    .data-table tr:last-child td {
        border-bottom: none;
    }
    .flow-box {
        background: #FFFFFF;
        border: 1px solid #E5EBF2;
        border-radius: 14px;
        padding: 8px 10px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("曾仕强视角分析智能体")
st.caption("本地 MVP：基于书籍知识库分析职场与家庭事件")

question = st.text_area(
    "请输入你正在经历或已经经历的事情",
    height=220,
    placeholder="例如：我最近和直属领导关系很紧张，他表面客气，但不断架空我。我不知道是该继续忍，还是主动谈一次。",
)

st.caption("提问建议：尽量写清 1. 涉及谁 2. 发生了什么 3. 你最在意什么 4. 你想解决什么。长段情绪描述容易检索不到。")

if st.button("开始分析", type="primary"):
    if not question.strip():
        st.warning("请先输入问题。")
    else:
        try:
            with st.spinner("正在分析..."):
                resp = requests.post(f"{API_BASE}/chat/ask", json={"question": question}, timeout=180)
                resp.raise_for_status()
                data = resp.json()
        except requests.HTTPError as exc:
            body = ""
            try:
                body = exc.response.text[:400]
            except Exception:
                body = ""
            st.error("后端返回了错误，当前没有完成分析。")
            if body:
                st.code(body)
            st.stop()
        except requests.RequestException as exc:
            st.error(f"无法连接后端服务：{exc}")
            st.stop()

        theme_tags = [f'<span class="tag">主主题：{data["theme"]["primary_theme"]}</span>']
        theme_tags.extend([f'<span class="tag">次主题：{item}</span>' for item in data["theme"]["secondary_themes"]])
        theme_tags.extend([f'<span class="tag">{item}</span>' for item in data["theme"]["matched_terms"][:8]])

        analysis = data["analysis"]

        def clean_text(v: str) -> str:
            text = v or ""
            prev = None
            # 连续反转义几次，处理 &amp;lt;div 这类双重转义脏数据。
            for _ in range(4):
                if text == prev:
                    break
                prev = text
                text = unescape(text)
            text = re.sub(r"</?div[^>]*>", " ", text, flags=re.I)
            text = re.sub(r"</?span[^>]*>", " ", text, flags=re.I)
            text = re.sub(r"</?strong[^>]*>", " ", text, flags=re.I)
            text = re.sub(r"</?p[^>]*>", " ", text, flags=re.I)
            text = re.sub(r"</?br[^>]*>", " ", text, flags=re.I)
            text = re.sub(r"</?[^>]+>", " ", text)
            text = re.sub(r"\bclass\s*=\s*['\"][^'\"]+['\"]", " ", text, flags=re.I)
            text = re.sub(r"&[a-z]+;", " ", text, flags=re.I)
            text = re.sub(r"[{}\\[\\]<>]+", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text

        def safe(v: str) -> str:
            return escape(clean_text(v))

        def text(v: str) -> str:
            return clean_text(v)

        if not data["citations"]:
            st.info("这次没有命中直接引用。系统已经识别了主题，但还没有在书中段落里找到足够接近的表述。建议把问题改成更短的关系句式后再试。")

        def render_table(title: str, rows: list[dict], columns: list[str], rename: dict[str, str] | None = None) -> None:
            st.markdown(f'<div class="panel"><div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
            if not rows:
                st.markdown("</div>", unsafe_allow_html=True)
                st.info("当前没有足够材料展开这一模块。")
                return
            cleaned_rows = []
            for row in rows:
                cleaned = {}
                for col in columns:
                    cleaned[col] = text(str(row.get(col, "")))
                cleaned_rows.append(cleaned)
            frame = pd.DataFrame(cleaned_rows)
            if rename:
                frame = frame.rename(columns=rename)
            header_cells = "".join(f"<th>{escape(str(col))}</th>" for col in frame.columns)
            body_rows = []
            for _, row in frame.iterrows():
                body_rows.append(
                    "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row.tolist()) + "</tr>"
                )
            st.markdown(
                f"""
                <table class="data-table">
                    <thead><tr>{header_cells}</tr></thead>
                    <tbody>{''.join(body_rows)}</tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        def render_note_group(title: str, items: list[dict], warn: bool = False) -> None:
            st.markdown(f'<div class="panel"><div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
            if not items:
                st.markdown("</div>", unsafe_allow_html=True)
                st.info("当前没有足够材料支撑这一模块的可靠展开。")
                return
            klass = "note note-warn" if warn else "note"
            for item in items:
                head = text(item.get("title") or item.get("trend") or item.get("action") or "要点")
                body = text(item.get("detail") or item.get("signal") or item.get("reason") or "")
                extra = []
                if "probability" in item:
                    extra.append(f"概率：{text(item['probability'])}")
                if "priority" in item:
                    extra.append(f"优先级：{text(item['priority'])}")
                if "avoid" in item:
                    extra.append(f"不要这样做：{text(item['avoid'])}")
                extra_html = ""
                if extra:
                    extra_html = f'<div class="mini-meta">{" | ".join(escape(x) for x in extra)}</div>'
                st.markdown(
                    f"""
                    <div class="{klass}">
                        <div class="note-title">{escape(head)}</div>
                        <div class="note-body">{escape(body)}</div>
                        {extra_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        def build_relation_graph(people: list[dict], edges: list[dict]) -> str:
            lines = [
                "digraph G {",
                'rankdir=LR;',
                'graph [bgcolor="transparent", splines=true, pad="0.2"];',
                'node [shape=box, style="rounded,filled", color="#D9E4EF", fillcolor="#F8FBFF", fontname="PingFang SC"];',
                'edge [color="#7A8FA3", fontname="PingFang SC"];',
            ]
            seen = set()
            for person in people:
                name = text(person.get("name", ""))
                if not name or name in seen:
                    continue
                seen.add(name)
                role = text(person.get("role", ""))
                label = f"{name}\\n{role}" if role else name
                lines.append(f'"{name}" [label="{label}"];')
            for edge in edges:
                source = text(edge.get("from_actor", ""))
                target = text(edge.get("to_actor", ""))
                if not source or not target:
                    continue
                relation = text(edge.get("relation", ""))
                tension = text(edge.get("tension", ""))
                label = relation if not tension else f"{relation} / {tension}"
                lines.append(f'"{source}" -> "{target}" [label="{label}"];')
            lines.append("}")
            return "\n".join(lines)

        def build_analysis_graph(analysis_data: dict) -> str:
            def first(items: list[dict], title_key: str, detail_key: str) -> tuple[str, str]:
                if not items:
                    return "", ""
                return text(items[0].get(title_key, "")), text(items[0].get(detail_key, ""))

            cause_title, _ = first(analysis_data["cause_analysis"], "title", "detail")
            conflict_title, _ = first(analysis_data["core_conflicts"], "title", "detail")
            judgment_title, _ = first(analysis_data["zeng_judgment"], "title", "detail")
            action_title = text(analysis_data["actions"][0].get("action", "")) if analysis_data["actions"] else ""

            lines = [
                "digraph G {",
                'rankdir=LR;',
                'graph [bgcolor="transparent", splines=ortho, pad="0.2"];',
                'node [shape=box, style="rounded,filled", color="#D9E4EF", fillcolor="#FFFFFF", fontname="PingFang SC"];',
                'edge [color="#7A8FA3", fontname="PingFang SC"];',
                f'"事件" [label="{text(analysis_data["event_summary"])[:36]}"];',
            ]
            if cause_title:
                lines.append(f'"前因" [label="前因\\n{cause_title[:28]}"];')
                lines.append('"事件" -> "前因";')
            if conflict_title:
                lines.append(f'"矛盾" [label="矛盾\\n{conflict_title[:28]}"];')
                lines.append('"前因" -> "矛盾";' if cause_title else '"事件" -> "矛盾";')
            if judgment_title:
                lines.append(f'"判断" [label="判断\\n{judgment_title[:28]}"];')
                lines.append('"矛盾" -> "判断";' if conflict_title else '"事件" -> "判断";')
            if action_title:
                lines.append(f'"动作" [label="动作\\n{action_title[:28]}"];')
                lines.append('"判断" -> "动作";' if judgment_title else '"事件" -> "动作";')
            lines.append("}")
            return "\n".join(lines)

        st.markdown('<div class="major-title">总览</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="section-panel">
                <div class="card">
                    <div class="section-title">主题识别</div>
                    <div>{''.join(theme_tags)}</div>
                    <div class="summary"><strong>分析镜头：</strong>{escape(data["theme"]["zeng_lens"])}</div>
                </div>
                <div class="card">
                    <div class="section-title">事件摘要</div>
                    <div class="summary">{safe(analysis['event_summary'])}</div>
                </div>
                <div class="card">
                    <div class="section-title">风险提示</div>
                    <div class="summary">{safe(analysis['risk_note'])}</div>
                </div>
                <div class="card">
                    <div class="section-title">检索概况</div>
                    <div class="mini-meta">命中引用：{len(data["citations"])} 条</div>
                    <div class="mini-meta">主主题：{escape(data["theme"]["primary_theme"])}</div>
                    <div class="mini-meta">命中词：{escape('、'.join(data["theme"]["matched_terms"][:6]) or '无')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="major-title">关系</div>', unsafe_allow_html=True)
        render_table(
            "关键人物",
            analysis["key_people"],
            ["name", "role", "state", "motive"],
            {"name": "人物", "role": "角色", "state": "当前状态", "motive": "可能动机"},
        )
        st.markdown('<div class="panel"><div class="section-title">关系拓扑图</div><div class="flow-box">', unsafe_allow_html=True)
        if analysis["decision_map"] or analysis["key_people"]:
            st.graphviz_chart(build_relation_graph(analysis["key_people"], analysis["decision_map"]), use_container_width=True)
        else:
            st.info("当前没有足够材料展开关系拓扑。")
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown('<div class="major-title">分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="section-title">分析导图</div><div class="flow-box">', unsafe_allow_html=True)
        st.graphviz_chart(build_analysis_graph(analysis), use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        render_note_group("前因分析", analysis["cause_analysis"])
        render_note_group("当前局面的关键矛盾", analysis["core_conflicts"], warn=True)
        render_note_group("基于曾仕强著作视角的判断", analysis["zeng_judgment"])

        st.markdown('<div class="major-title">策略</div>', unsafe_allow_html=True)
        render_table(
            "后续走向预判",
            analysis["predictions"],
            ["trend", "probability", "signal"],
            {"trend": "走向", "probability": "概率", "signal": "信号"},
        )
        render_table(
            "建议动作",
            analysis["actions"],
            ["priority", "action", "reason", "avoid"],
            {"priority": "优先级", "action": "动作", "reason": "原因", "avoid": "不要这样做"},
        )

        st.markdown('<div class="major-title">引用</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="section-title">引用依据</div>', unsafe_allow_html=True)
        for idx, item in enumerate(data["citations"], start=1):
            with st.expander(f"{idx}. {item['document_title']} / {item.get('page_label') or '未知位置'}"):
                st.write(item["content"])
        st.markdown("</div>", unsafe_allow_html=True)
