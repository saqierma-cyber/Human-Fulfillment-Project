import json
import re
from html import unescape

import httpx
from openai import OpenAI

from app.core.config import get_settings
from app.core.prompts import ANALYSIS_SYSTEM_PROMPT


class AnalysisService:
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.llm_api_key:
            raise ValueError("LLM_API_KEY 未配置，无法调用大模型。")
        if not self.settings.llm_chat_model or self.settings.llm_chat_model == "replace_me":
            raise ValueError("LLM_CHAT_MODEL 未配置，请在 .env 中填写实际模型名。")
        self.client = OpenAI(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            http_client=httpx.Client(timeout=120.0, trust_env=False),
        )

    def build_context(self, citations: list[dict]) -> str:
        blocks = []
        for idx, item in enumerate(citations, start=1):
            blocks.append(
                "\n".join(
                    [
                        f"[引用 {idx}]",
                        f"书名：{item['document_title']}",
                        f"位置：{item.get('page_label') or '未知'}",
                        f"内容：{item['content']}",
                    ]
                )
            )
        return "\n\n".join(blocks)

    def _extract_json(self, text: str) -> dict:
        cleaned = text.strip()
        cleaned = re.sub(r"<think>.*?</think>", " ", cleaned, flags=re.S | re.I)
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        if not cleaned.startswith("{"):
            match = re.search(r"\{.*\}", cleaned, re.S)
            if match:
                cleaned = match.group(0)
        return json.loads(cleaned)

    def _clean_text(self, value: str) -> str:
        text = value or ""
        text = unescape(text)
        text = re.sub(r"</?div[^>]*>", " ", text, flags=re.I)
        text = re.sub(r"</?span[^>]*>", " ", text, flags=re.I)
        text = re.sub(r"</?strong[^>]*>", " ", text, flags=re.I)
        text = re.sub(r"</?p[^>]*>", " ", text, flags=re.I)
        text = re.sub(r"</?br[^>]*>", " ", text, flags=re.I)
        text = re.sub(r"</?[^>]+>", " ", text)
        text = re.sub(r"\bclass\s*=\s*['\"][^'\"]+['\"]", " ", text, flags=re.I)
        text = re.sub(r"```+", " ", text)
        text = re.sub(r"[{}\\[\\]<>]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _sanitize_payload(self, payload):
        if isinstance(payload, dict):
            return {key: self._sanitize_payload(value) for key, value in payload.items()}
        if isinstance(payload, list):
            return [self._sanitize_payload(item) for item in payload]
        if isinstance(payload, str):
            return self._clean_text(payload)
        return payload

    @classmethod
    def has_markup_artifacts(cls, payload) -> bool:
        if isinstance(payload, dict):
            return any(cls.has_markup_artifacts(value) for value in payload.values())
        if isinstance(payload, list):
            return any(cls.has_markup_artifacts(item) for item in payload)
        if isinstance(payload, str):
            text = payload.lower()
            suspicious = ("<div", "</div", "<span", "</span", "class=", "&lt;div", "&lt;/div")
            return any(flag in text for flag in suspicious)
        return False

    @staticmethod
    def _question_terms(question: str) -> list[str]:
        candidates = re.findall(r"[\u4e00-\u9fff]{2,6}", question)
        stop_terms = {"现在", "已经", "还是", "但是", "觉得", "不知道", "什么", "自己", "想要"}
        deduped: list[str] = []
        seen = set()
        for item in candidates:
            if item in stop_terms or item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        return deduped[:12]

    @classmethod
    def _extract_evidence_lines(cls, question: str, citations: list[dict], theme: dict) -> list[str]:
        terms = cls._question_terms(question)
        terms.extend(theme.get("matched_terms", []))
        terms.extend(theme.get("actor_tags", []))
        terms.extend(theme.get("expanded_terms", [])[:8])

        scored: list[tuple[float, str]] = []
        for item in citations:
            content = item.get("content", "")
            parts = re.split(r"[。\n；!?！？]+", content)
            for raw in parts:
                line = re.sub(r"\s+", " ", raw).strip(" \t-:：")
                if len(line) < 14:
                    continue
                if any(flag in line for flag in ("第 ", "JZ5U", "绿色下载", "〔原文〕", "〔注释〕")):
                    continue
                score = 0.0
                for term in terms:
                    if term and term in line:
                        score += 3.0 + min(len(term), 4) * 0.4
                if any(mark in line for mark in ("合理", "分寸", "关系", "顺从", "父母", "上司", "同事", "孝", "礼")):
                    score += 1.5
                if score > 0:
                    scored.append((score, line))

        scored.sort(key=lambda item: item[0], reverse=True)
        results: list[str] = []
        seen = set()
        for _, line in scored:
            if line in seen:
                continue
            seen.add(line)
            results.append(line)
            if len(results) >= 8:
                break
        return results

    @classmethod
    def build_fallback_analysis(cls, question: str, citations: list[dict], theme: dict, reason: str = "") -> dict:
        primary_theme = theme.get("primary_theme", "综合关系分析")
        actor_tags = theme.get("actor_tags", [])
        evidence = cls._extract_evidence_lines(question, citations, theme)

        key_people = [{"name": "用户", "role": "提问者", "state": "处于事件中心，希望看清局面", "motive": "想减少内耗，找到更合理的处理方式"}]
        for tag in actor_tags:
            if tag == "我":
                continue
            key_people.append(
                {
                    "name": tag,
                    "role": "关系相关方",
                    "state": "与用户存在持续互动",
                    "motive": "按照其角色与立场维护自身秩序或利益",
                }
            )

        if len(key_people) == 1 and "父母" in primary_theme:
            key_people.append({"name": "父母", "role": "家庭中的长辈", "state": "对用户选择仍有较强影响", "motive": "希望维持熟悉的家庭秩序与安全感"})
        if len(key_people) == 1 and "职场" in primary_theme:
            key_people.append({"name": "同事/上级", "role": "职场相关方", "state": "与用户存在利益和分寸互动", "motive": "维护位置、关系和局面稳定"})

        decision_map = []
        for person in key_people[1:]:
            relation = "家庭影响" if "父母" in primary_theme else "职场互动"
            decision_map.append(
                {
                    "from_actor": "用户",
                    "to_actor": person["name"],
                    "relation": relation,
                    "tension": "中",
                    "note": "当前关系并未真正理顺，用户既想调整，又顾虑代价。",
                }
            )

        if "父母家庭关系" in primary_theme:
            summary = "已检索到相关材料。结合命中的家庭关系与孝道材料，当前更像是“长期顺从形成惯性，自我意志没有被单独安顿”，所以表面稳定，内里压抑。"
            cause = [
                {
                    "title": "顺从模式已经形成",
                    "detail": evidence[0] if evidence else "命中的家庭材料反复强调，孝要讲合理，不是盲目顺从。现在更像是长期顺从之后，自我选择能力没有真正长出来。",
                },
                {
                    "title": "孝与边界混在一起了",
                    "detail": evidence[1] if len(evidence) > 1 else "这件事的根子不只在父母强势，也在于你把“尊重父母”与“凡事照办”混成了一件事。",
                },
            ]
            conflicts = [
                {
                    "title": "想独立，但还不敢承担独立后的关系波动",
                    "detail": "真正的矛盾不是不知道做什么，而是即使开始知道，也还没有准备好承受表达自我之后可能出现的不满、指责或冲突。",
                },
                {
                    "title": "生活稳定与内在不甘并存",
                    "detail": "表面上工作、地点、节奏都稳定，但稳定并没有带来心安，说明问题不在客观条件本身，而在选择权没有回到自己手里。",
                },
            ]
            judgment = [
                {
                    "title": "问题不在孝，而在失了分寸",
                    "detail": "从已命中的书段看，曾仕强的角度更接近“合理为度”。对父母可以尊重，但不应把不加分寸的顺从当成孝。",
                },
                {
                    "title": "先把自己立起来，关系才会重新归位",
                    "detail": "如果你始终不表达、不选择，父母就会继续代行你的选择权，因为旧秩序对他们更省力、更安心。",
                },
            ]
            predictions = [
                {
                    "trend": "如果继续压着不说，内耗会继续增加",
                    "probability": "高",
                    "signal": "你会越来越不开心，但外部生活仍维持表面稳定。",
                },
                {
                    "trend": "如果开始表达边界，短期会有阻力，中期才可能转向",
                    "probability": "中",
                    "signal": "父母一开始未必接受，但关系会从“替你决定”慢慢转向“开始协商”。",
                },
            ]
            actions = [
                {
                    "priority": "高",
                    "action": "先不要谈抽象的人生理想，先提出一个具体而小的自主决定",
                    "reason": "你现在最缺的不是大道理，而是把选择权一点点拿回来的实际动作。",
                    "avoid": "不要一上来就全面反抗，也不要继续什么都不说。",
                },
                {
                    "priority": "中",
                    "action": "把诉求改写成“我想先自己试一次某件具体的事”",
                    "reason": "越具体，越容易谈；越抽象，越容易被父母解释成冲动或不成熟。",
                    "avoid": "不要用情绪化控诉去替代清楚表达。",
                },
            ]
            risk_note = "这是基于已命中书段整理出的有限分析，不是直接逐字原文结论。当前最关键的是把“尊重父母”和“放弃选择”分开。"
        elif "职场权力关系" in primary_theme or "团队管理" in primary_theme:
            summary = "已检索到相关材料。结合命中的职场与人际关系材料，当前更像是“关系、分寸、利益和位置”交织在一起，不是单纯对错题。"
            cause = [
                {
                    "title": "职场不是只看能力，也看关系与位阶",
                    "detail": evidence[0] if evidence else "命中的材料强调，上下、平行同事之间都要讲分寸，不能只按表面平等来处理。",
                },
                {
                    "title": "关系越近，越容易让判断变得犹豫",
                    "detail": evidence[1] if len(evidence) > 1 else "你现在的迟疑，往往不是不知道利害，而是怕处理不好关系，留下后手问题。",
                },
            ]
            conflicts = [
                {
                    "title": "利害判断与人情判断在打架",
                    "detail": "一方面你知道机会很重要，另一方面你又顾虑同事关系和后续相处，所以一直拿不定主意。",
                },
                {
                    "title": "怕失去关系，也怕失去机会",
                    "detail": "这说明问题不是要不要争，而是怎么争得不伤和气、又不让自己长期吃亏。",
                },
            ]
            judgment = [
                {
                    "title": "中国式关系里，平行同事不能过分熟不拘礼",
                    "detail": "命中的《圆通的人际关系》材料已经很直接：平行同事要拿捏轻重，不能因为关系不错，就把关键利益问题处理得过于含糊。",
                },
                {
                    "title": "该争的事要争，但要争得有分寸",
                    "detail": "更接近曾仕强视角的做法，不是硬拼，也不是退让，而是让对方知道你有立场，同时不给彼此留太难看的局面。",
                },
            ]
            predictions = [
                {
                    "trend": "如果一直犹豫不表达，结果大概率由别人替你决定",
                    "probability": "高",
                    "signal": "机会窗口会过去，之后你会更不甘心。",
                },
                {
                    "trend": "如果表达得体，短期有摩擦，中期更容易把关系放回正常位置",
                    "probability": "中",
                    "signal": "对方未必高兴，但会重新判断你的边界和分量。",
                },
            ]
            actions = [
                {
                    "priority": "高",
                    "action": "先分清这是“机会分配”还是“关系维护”问题，再决定怎么谈",
                    "reason": "问题性质不清，动作就容易乱。",
                    "avoid": "不要把关键机会完全交给模糊关系去决定。",
                },
                {
                    "priority": "中",
                    "action": "先私下表达你对机会的认真态度，再谈彼此后续如何相处",
                    "reason": "先立场，后关系，比一开始就讲感情更稳。",
                    "avoid": "不要一上来就指责对方抢机会，也不要装作无所谓。",
                },
            ]
            risk_note = "这是基于已命中书段整理出的有限分析。当前真正要避免的，是把需要立场的问题处理成纯人情问题。"
        else:
            summary = "已检索到相关材料，但模型结构化阶段失败，当前根据命中书段返回有限分析。"
            cause = [{"title": "相关材料已经命中", "detail": evidence[0] if evidence else "当前已找到相近书段。"}]
            conflicts = [{"title": "问题仍需结合具体局面判断", "detail": evidence[1] if len(evidence) > 1 else "仅凭当前问题，还不足以展开更细的角色推演。"}]
            judgment = [{"title": "先看关系，再看动作", "detail": theme.get("zeng_lens", "从角色、关系与分寸来分析。")}]
            predictions = [{"trend": "如果局面不调整，原有模式会延续", "probability": "中", "signal": "当前问题描述里的冲突点会反复出现。"}]
            actions = [{"priority": "中", "action": "把人物、冲突、目标写得更具体", "reason": "这样才能把命中的书段用得更准。", "avoid": "不要只写感受，不写关系结构。"}]
            risk_note = "本次为本地回退生成，不是模型完整分析结果。"

        return {
            "event_summary": summary,
            "key_people": key_people[:4],
            "decision_map": decision_map[:4],
            "cause_analysis": cause,
            "core_conflicts": conflicts,
            "zeng_judgment": judgment,
            "predictions": predictions,
            "actions": actions,
            "risk_note": risk_note,
        }

    def analyze(self, question: str, citations: list[dict], theme: dict) -> dict:
        context = self.build_context(citations)
        user_prompt = f"""
用户问题：
{question}

问题主题分类：
- 主主题：{theme['primary_theme']}
- 次主题：{', '.join(theme['secondary_themes']) if theme['secondary_themes'] else '无'}
- 命中词：{', '.join(theme['matched_terms']) if theme['matched_terms'] else '无'}
- 角色词：{', '.join(theme['actor_tags']) if theme['actor_tags'] else '无'}
- 分析视角：{theme['zeng_lens']}

知识库引用：
{context}

请严格基于这些知识库片段进行分析。
"""

        response = self.client.chat.completions.create(
            model=self.settings.llm_chat_model,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.6,
            extra_body={"reasoning_split": True},
        )
        raw = response.choices[0].message.content or "{}"
        parsed = self._extract_json(raw)
        return self._sanitize_payload(parsed)
