from dataclasses import dataclass


@dataclass
class ThemeDefinition:
    name: str
    keywords: list[str]
    expansion_terms: list[str]
    zeng_lens: str


class ThemeService:
    def __init__(self) -> None:
        self.themes = [
            ThemeDefinition(
                name="职场权力关系",
                keywords=[
                    "领导", "上级", "直属领导", "老板", "架空", "削权", "边缘化", "越级",
                    "权力", "位置", "失势", "汇报", "派系", "办公室政治", "同事", "下属",
                ],
                expansion_terms=[
                    "上下关系", "分寸", "位阶", "权责", "阳奉阴违", "表面顺从", "人情",
                    "中道", "进退", "拿捏", "试探", "权威", "信任",
                ],
                zeng_lens="从上下关系、位阶、分寸、人情与权责边界来分析局面。",
            ),
            ThemeDefinition(
                name="团队管理",
                keywords=[
                    "团队", "带团队", "管理", "配合", "执行", "老员工", "新人", "激励",
                    "考核", "协作", "目标", "内耗", "负责", "推责",
                ],
                expansion_terms=[
                    "带人", "带队伍", "奖惩", "分工", "统御", "组织", "士气",
                    "责任", "用人", "识人", "协调",
                ],
                zeng_lens="从带队伍、用人、责任归位、统御与激励角度分析。",
            ),
            ThemeDefinition(
                name="父母家庭关系",
                keywords=[
                    "父母", "妈妈", "爸爸", "长辈", "婆婆", "公婆", "岳父", "岳母",
                    "爸妈", "爹妈", "家人",
                    "家庭", "家里", "控制", "孝顺", "顶嘴", "代际", "听话", "乖",
                    "不敢反抗", "不敢违背", "没主见", "安排", "替我决定", "人生被安排",
                    "压抑", "顺从", "不开心", "稳定工作", "本地工作",
                ],
                expansion_terms=[
                    "家风", "孝", "边界", "角色", "长幼有序", "家庭秩序", "尊重",
                    "亲情", "关系失衡", "自我意志", "父母控制", "人生选择", "顺从模式",
                    "家庭施压", "不敢表达", "内在压抑", "人生方向", "被安排的人生",
                ],
                zeng_lens="从家庭秩序、角色边界、孝与尊重的平衡来分析。",
            ),
            ThemeDefinition(
                name="伴侣婚姻关系",
                keywords=[
                    "伴侣", "老公", "老婆", "婚姻", "夫妻", "冷战", "出轨", "离婚",
                    "结婚", "感情", "吵架", "猜疑", "信任",
                ],
                expansion_terms=[
                    "夫妻关系", "互动失衡", "角色期待", "沟通破裂", "情感账户",
                    "面子", "让步", "关系修复",
                ],
                zeng_lens="从夫妻角色、信任、互动平衡与长久关系经营来分析。",
            ),
            ThemeDefinition(
                name="亲子教育",
                keywords=[
                    "孩子", "儿子", "女儿", "亲子", "教育", "教养", "叛逆", "学习",
                    "管教", "青春期", "作业", "学校",
                ],
                expansion_terms=[
                    "父母角色", "教养", "引导", "亲子关系", "成长节奏", "界限", "陪伴",
                ],
                zeng_lens="从亲子关系、教养方式、角色定位与引导而非硬控来分析。",
            ),
            ThemeDefinition(
                name="人际沟通",
                keywords=[
                    "沟通", "误会", "说话", "表达", "冲突", "人际", "面子", "关系",
                    "合作", "试探", "尴尬", "相处",
                ],
                expansion_terms=[
                    "说话分寸", "给台阶", "留余地", "面子", "关系维护", "进退",
                    "会说话", "圆通",
                ],
                zeng_lens="从沟通分寸、给台阶、留余地与关系维护来分析。",
            ),
            ThemeDefinition(
                name="情绪管理",
                keywords=[
                    "情绪", "生气", "愤怒", "焦虑", "委屈", "崩溃", "压抑", "冲动",
                    "忍不住", "发火", "内耗",
                ],
                expansion_terms=[
                    "不生气", "情绪失控", "情绪来源", "自我调整", "情绪传导", "反应模式",
                ],
                zeng_lens="从情绪来源、情绪传导、反应模式与克制拿捏来分析。",
            ),
            ThemeDefinition(
                name="个人修身与处世",
                keywords=[
                    "做人", "处世", "修养", "修身", "自我", "原则", "选择", "取舍",
                    "成长", "格局", "命运",
                ],
                expansion_terms=[
                    "中道", "自处", "分寸", "持经达变", "安人", "自我定位",
                ],
                zeng_lens="从修身、自处、中道、进退取舍来分析。",
            ),
        ]

        self.actor_terms = [
            "我", "领导", "上级", "老板", "同事", "下属", "老员工", "新人",
            "父母", "爸妈", "妈妈", "爸爸", "长辈", "婆婆", "公婆", "伴侣", "老公", "老婆",
            "夫妻", "孩子", "儿子", "女儿", "母亲", "母亲大人",
        ]

    def classify(self, question: str) -> dict:
        text = question.strip()
        scored: list[tuple[int, ThemeDefinition, list[str]]] = []

        for theme in self.themes:
            matched = [kw for kw in theme.keywords if kw in text]
            score = len(matched) * 3
            score += sum(1 for term in theme.expansion_terms if term in text)
            if score:
                scored.append((score, theme, matched))

        scored.sort(key=lambda item: item[0], reverse=True)

        if scored:
            primary = scored[0][1]
            secondary = [item[1].name for item in scored[1:3]]
            matched_terms = list(dict.fromkeys([term for _, _, terms in scored for term in terms]))
        else:
            primary = ThemeDefinition(
                name="综合关系分析",
                keywords=[],
                expansion_terms=["关系", "角色", "分寸", "前因后果", "局面", "中道"],
                zeng_lens="从关系、角色、分寸、中道与前因后果综合分析。",
            )
            secondary = []
            matched_terms = []

        actor_tags = [term for term in self.actor_terms if term in text]

        expanded_terms = list(dict.fromkeys(primary.expansion_terms + matched_terms + actor_tags))

        return {
            "primary_theme": primary.name,
            "secondary_themes": secondary,
            "matched_terms": matched_terms[:12],
            "expanded_terms": expanded_terms[:18],
            "actor_tags": actor_tags[:10],
            "zeng_lens": primary.zeng_lens,
        }
