"""Generate an Arabic usage guide from the static command inventory."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/command_inventory.json"
OUTPUT = ROOT / "docs/دليل_الأوامر_الحالية.md"


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def usage_from_pattern(pattern: str) -> str:
    if pattern.startswith("<dynamic:"):
        return "أمر ديناميكي داخلي؛ راجع ملف الإضافة أو `.حالة الاوامر`."
    if pattern == "<missing-pattern>":
        return "مراقب تلقائي للأحداث؛ لا يُكتب كأمر يدوي."
    value = pattern
    value = value.removeprefix("^").removesuffix("$")
    value = value.replace(r"(?:\s|$)", "")
    value = value.replace("(?: |$)", "")
    value = value.replace(r"([\s\S]*)", " <النص>")
    value = value.replace("(.*)", " <النص>")
    value = value.replace(r"(\S*)", " <النص>")
    value = value.replace(r"([\S]*)", " <النص>")
    value = value.replace(r"(\d*)", " <رقم>")
    value = value.replace(r"(\d+)", " <رقم>")
    value = value.replace("([0-9]+)", " <رقم>")

    def clean_choices(match: re.Match[str]) -> str:
        choices = match.group(1).replace(r"\|", "|").replace("|", " أو ")
        return choices.replace(r"\s", " ").replace("$", "")

    value = re.sub(r"\(\?:([^()]+)\)", clean_choices, value)
    value = re.sub(r"\(([^()]+\|[^()]+)\)", clean_choices, value)
    value = value.replace(r"\s", " ").replace(r"\ ", " ")
    value = value.replace("\\", "")
    value = re.sub(r"\s+", " ", value).strip()
    return f"`.{value}`"


def note_from_pattern(pattern: str) -> str:
    if pattern.startswith("<dynamic:"):
        return "لا يمكن استخراج الاسم حرفياً لأن السورس يبنيه من إعداد داخلي."
    if pattern == "<missing-pattern>":
        return "هذا handler مراقبة تلقائية وليس أمراً نصياً."
    if "[\\s\\S]*" in pattern or ".*" in pattern:
        return "استبدل `<النص>` بالقيمة المطلوبة."
    if "\\d" in pattern or "[0-9]" in pattern:
        return "استبدل `<رقم>` برقم صحيح عند ظهوره."
    if "|" in pattern:
        return "يمكن استعمال أي صيغة ظاهرة بين البدائل."
    return "اكتب الأمر كما هو من نفس الحساب المرتبط بالجلسة."


def title_from_file(file_name: str) -> str:
    stem = Path(file_name).stem
    return f"إضافة: {stem}"


def main() -> None:
    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    handlers = [row for row in rows if "pattern" in row]
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in handlers:
        grouped[str(row["file"])].append(row)

    lines = [
        "# دليل الأوامر الحالية لـ ZTele",
        "",
        "> هذا الدليل مولّد من الأوامر المسجلة فعلياً في النسخة الحالية. ابدأ كل أمر بنقطة `.` ومن **نفس حساب Telegram المرتبط بالجلسة**، وليس من البوت المساعد.",
        "",
        "## قبل الاستخدام",
        "",
        "| الحالة | التوضيح |",
        "|---|---|",
        "| أمر عادي | اكتب الصيغة الظاهرة في عمود الاستخدام. |",
        "| `<النص>` | استبدله بالكلمة أو الرابط أو الاسم المطلوب. |",
        "| `<رقم>` | استبدله برقم صحيح مثل رقم رسالة أو مدة. |",
        "| أمر مجموعة | يحتاج أن تكون داخل مجموعة وقد يحتاج صلاحية مشرف. |",
        "| خدمة خارجية | بعض الأوامر تعتمد على الإنترنت أو خدمة عامة وقد تتأخر أو تفشل من جانب الخدمة. |",
        "",
        "## أوامر التشخيص والبداية",
        "",
        "| الأمر | الاستخدام |",
        "|---|---|",
        "| حالة التحميل | `.حالة الاوامر` — يعرض الإضافات التي نجح تحميلها أو فشلت. |",
        "| المساعدة | `.مساعدة` أو `.مساعده` — يعرض البداية. |",
        "| الفهرس | `.الاوامر` أو `.الأوامر` أو `.اوامري` — يعرض فهرس الأوامر الأساسي. |",
        "| فحص التشغيل | `.فحص` — يعرض حالة عامة للنسخة. |",
        "",
        f"## جميع المعالجات المسجلة ({len(handlers)})",
        "",
        "قد يظهر نفس الأمر في أكثر من موضع إذا كان له تنفيذ مختلف بحسب السياق. الأوامر الديناميكية أو مراقبات الرسائل مذكورة بوضوح ولا يلزم كتابتها يدوياً.",
        "",
    ]
    for file_name in sorted(grouped):
        rows_for_file = sorted(grouped[file_name], key=lambda row: int(row.get("line", 0)))
        lines.extend(
            [
                f"### {title_from_file(file_name)}",
                "",
                "| الأمر / النمط | الاستخدام | الملاحظة |",
                "|---|---|---|",
            ]
        )
        for row in rows_for_file:
            pattern = str(row["pattern"])
            handler = str(row["handler"])
            lines.append(
                "| "
                f"`{escape_cell(pattern)}` | {escape_cell(usage_from_pattern(pattern))} | "
                f"{escape_cell(note_from_pattern(pattern))} — handler: `{handler}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## أوامر الثيمات",
            "",
            "الأوامر المتاحة من أصول المستخدم المرفوعة هي `.ث1` للصورة و`.ث2` للفيديو. أما بقية أوامر الثيمات (`.ث3` إلى `.ث12` و`.ن1` إلى `.ن12`) فستظهر رسالة واضحة إلى أن يُضاف لها محتوى.",
            "",
            "## عند عدم استجابة أمر",
            "",
            "استخدم `.حالة الاوامر` أولاً. إذا كان الأمر يتطلب الرد على رسالة أو يكون خاصاً بالمجموعات أو يحتاج صلاحية مشرف، نفّذه في السياق الصحيح. عند ظهور رسالة الخطأ الجديدة، انسخ اسم الأمر وآخر سطور سجل Render لتحديد المتطلب الناقص بدقة.",
        ]
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"handlers={len(handlers)} files={len(grouped)} output={OUTPUT}")


if __name__ == "__main__":
    main()
