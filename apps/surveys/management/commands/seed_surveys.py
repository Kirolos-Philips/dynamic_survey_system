from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.surveys.models import (
    Question,
    QuestionChoice,
    QuestionLogic,
    Section,
    Survey,
)
from apps.users.models import SurveyManager

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Seeds the database with a high-detail Relationship and "
        "Divorce assessment survey."
    )

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError(
                "This command can only be run in the local environment (DEBUG=True)."
            )

        self.stdout.write("Seeding Rich Relationship Assessment data...")

        with transaction.atomic():
            # Clean up existing data to avoid clashes
            Survey.objects.filter(title_en__icontains="Relationship").delete()

            # 1. Create a Survey Manager
            manager, _ = SurveyManager.objects.get_or_create(
                username="survey_admin",
                defaults={
                    "email": "admin@survey.com",
                    "is_staff": True,
                },
            )

            # 2. Create the Survey
            survey = Survey.objects.create(
                title_en="Comprehensive Relationship Diagnostic",
                title_ar="التشخيص الشامل للعلاقة الزوجية",
                description_en=(
                    "This clinical-grade diagnostic is designed to identify "
                    "communication patterns, conflict roots, and trust levels "
                    "to better facilitate counseling sessions."
                ),
                description_ar=(
                    "تم تصميم هذا التشخيص بالمستوى العيادي لتحديد أنماط التواصل، "
                    "جذور الخلاف، ومستويات الثقة لتسهيل جلسات الاستشارة الزوجية "
                    "بشكل أفضل."
                ),
                created_by=manager,
                is_active=True,
            )

            # 3. Create Sections
            # Section 1: Demographics & Context
            sec_context = Section.objects.create(
                survey=survey,
                title_en="Relationship Context",
                title_ar="سياق العلاقة",
                description_ar="فهم الهيكل الأساسي لزواجك.",
                order=1,
            )

            # Section 2: Communication & Intimacy
            sec_comm = Section.objects.create(
                survey=survey,
                title_en="Communication & Intimacy",
                title_ar="التواصل والمودة",
                description_en="Evaluating how you connect and express affection.",
                description_ar="تقييم كيفية تواصلكم والتعبير عن المودة.",
                order=2,
            )

            # Section 3: Conflict & Triggers
            sec_conflict = Section.objects.create(
                survey=survey,
                title_en="Conflicts & Triggers",
                title_ar="الخلافات والمحفزات",
                description_en="Deep dive into recurring arguments and their causes.",
                description_ar="تعمق في الخلافات المتكررة وأسبابها.",
                order=3,
            )

            # 4. Questions for Section 1 (Context)
            q_status = Question.objects.create(
                section=sec_context,
                identifier="rel_status",
                text_en="What is your current living arrangement?",
                text_ar="ما هو ترتيب معيشتم الحالية؟",
                question_type=Question.QuestionType.RADIO,
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_status,
                value="together",
                label_en="Living Together",
                label_ar="نعيش معاً",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_status,
                value="separate_rooms",
                label_en="Living Together (Separate Rooms)",
                label_ar="نعيش معاً (غرف منفصلة)",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_status,
                value="separated",
                label_en="Legally Separated / Not living together",
                label_ar="منفصلين قانونياً / لا نعيش معاً",
                order=3,
            )

            q_children = Question.objects.create(
                section=sec_context,
                identifier="has_children",
                text_en="Do you have children together?",
                text_ar="هل لديكم أطفال معاً؟",
                question_type=Question.QuestionType.RADIO,
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_children,
                value="yes",
                label_en="Yes",
                label_ar="نعم",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_children, value="no", label_en="No", label_ar="لا", order=2
            )

            q_child_count = Question.objects.create(
                section=sec_context,
                identifier="child_count",
                text_en="Number of children",
                text_ar="عدد الأطفال",
                question_type=Question.QuestionType.NUMBER,
                required=False,
                order=3,
            )

            # 5. Questions for Section 2 (Communication)
            q_affection = Question.objects.create(
                section=sec_comm,
                identifier="affection_level",
                text_en=(
                    "How often do you express physical affection "
                    "(hugging, holding hands)?"
                ),
                text_ar="كم مرة تعبرون عن المودة الجسدية (عناق، إمساك أيدي)؟",
                question_type=Question.QuestionType.DROPDOWN,
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_affection,
                value="daily",
                label_en="Daily",
                label_ar="يومياً",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_affection,
                value="weekly",
                label_en="Weekly",
                label_ar="أسبوعياً",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_affection,
                value="monthly",
                label_en="A few times a month",
                label_ar="مرات قليلة في الشهر",
                order=3,
            )
            QuestionChoice.objects.create(
                question=q_affection,
                value="never",
                label_en="Never or almost never",
                label_ar="أبداً أو تقريباً لا يحدث",
                order=4,
            )

            q_listening = Question.objects.create(
                section=sec_comm,
                identifier="listening_quality",
                text_en=(
                    "I feel my partner truly listens when I talk about my feelings."
                ),
                text_ar="أشعر أن شريكي يستمع لي حقاً عندما أتحدث عن مشاعري.",
                question_type=Question.QuestionType.RADIO,
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_listening,
                value="agree",
                label_en="Strongly Agree",
                label_ar="أوافق بشدة",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_listening,
                value="neutral",
                label_en="Neutral",
                label_ar="محايد",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_listening,
                value="disagree",
                label_en="Strongly Disagree",
                label_ar="لا أوافق بشدة",
                order=3,
            )

            q_shared_goals = Question.objects.create(
                section=sec_comm,
                identifier="shared_goals",
                text_en="Do you feel you and your partner share the same life goals?",
                text_ar="هل تشعر أنك وشريكك تشتركان في نفس أهداف الحياة؟",
                question_type=Question.QuestionType.RADIO,
                order=3,
            )
            QuestionChoice.objects.create(
                question=q_shared_goals,
                value="yes",
                label_en="Yes, definitely",
                label_ar="نعم، بالتأكيد",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_shared_goals,
                value="mostly",
                label_en="Mostly",
                label_ar="غالباً",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_shared_goals,
                value="no",
                label_en="No, we have different visions",
                label_ar="لا، لدينا رؤى مختلفة",
                order=3,
            )

            q_trust_level = Question.objects.create(
                section=sec_comm,
                identifier="trust_level",
                text_en="How would you rate your trust in your partner?",
                text_ar="كيف تقيم مستوى ثقتك في شريكك؟",
                question_type=Question.QuestionType.RADIO,
                order=4,
            )
            QuestionChoice.objects.create(
                question=q_trust_level,
                value="high",
                label_en="High Trust",
                label_ar="ثقة عالية",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_trust_level,
                value="medium",
                label_en="Medium Trust",
                label_ar="ثقة متوسطة",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_trust_level,
                value="low",
                label_en="Low Trust",
                label_ar="ثقة منخفضة",
                order=3,
            )

            q_trust_reason = Question.objects.create(
                section=sec_comm,
                identifier="trust_reason",
                text_en="What is the primary reason for low trust?",
                text_ar="ما هو السبب الرئيسي لانخفاض الثقة؟",
                question_type=Question.QuestionType.DROPDOWN,
                required=False,
                order=5,
            )
            QuestionChoice.objects.create(
                question=q_trust_reason,
                value="infidelity",
                label_en="Past Infidelity",
                label_ar="خيانة سابقة",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_trust_reason,
                value="dishonesty",
                label_en="Frequent Dishonesty",
                label_ar="عدم الأمانة المتكرر",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_trust_reason,
                value="secrecy",
                label_en="Financial Secrecy",
                label_ar="سرية مالية",
                order=3,
            )

            # 6. Questions for Section 3 (Conflict)
            q_conflict_root = Question.objects.create(
                section=sec_conflict,
                identifier="conflict_root",
                text_en="Which of these areas causes the MOST tension?",
                text_ar="أياً من هذه المناطق تسبب أكبر قدر من التوتر؟",
                question_type=Question.QuestionType.RADIO,
                order=1,
            )
            c_finance = QuestionChoice.objects.create(
                question=q_conflict_root,
                value="finance",
                label_en="Finances & Spending",
                label_ar="المالية والإنفاق",
                order=1,
            )
            c_inlaws = QuestionChoice.objects.create(
                question=q_conflict_root,
                value="inlaws",
                label_en="Relationship with In-laws",
                label_ar="العلاقة مع أهل الزوج/الزوجة",
                order=2,
            )
            c_parenting = QuestionChoice.objects.create(
                question=q_conflict_root,
                value="parenting",
                label_en="Parenting Styles",
                label_ar="أسلوب تربية الأطفال",
                order=3,
            )
            c_housework = QuestionChoice.objects.create(
                question=q_conflict_root,
                value="housework",
                label_en="Division of Housework",
                label_ar="توزيع المهام المنزلية",
                order=4,
            )

            q_violence = Question.objects.create(
                section=sec_conflict,
                identifier="has_violence",
                text_en=(
                    "Has there been any instance of physical violence in the last year?"
                ),
                text_ar="هل حدثت أي حالة من العنف الجسدي في العام الماضي؟",
                question_type=Question.QuestionType.RADIO,
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_violence,
                value="yes",
                label_en="Yes",
                label_ar="نعم",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_violence, value="no", label_en="No", label_ar="لا", order=2
            )

            q_resolution = Question.objects.create(
                section=sec_conflict,
                identifier="resolution_method",
                text_en="How do you usually resolve conflicts?",
                text_ar="كيف تحلون النزاعات عادة؟",
                question_type=Question.QuestionType.DROPDOWN,
                order=3,
            )
            QuestionChoice.objects.create(
                question=q_resolution,
                value="talk",
                label_en="Calm discussion",
                label_ar="نقاش هادئ",
                order=1,
            )
            QuestionChoice.objects.create(
                question=q_resolution,
                value="shout",
                label_en="Shouting/Arguing",
                label_ar="صراخ/جدال",
                order=2,
            )
            QuestionChoice.objects.create(
                question=q_resolution,
                value="avoid",
                label_en="Avoidance/Silence",
                label_ar="تجنب/صمت",
                order=3,
            )
            QuestionChoice.objects.create(
                question=q_resolution,
                value="third_party",
                label_en="Mediator/Third Party",
                label_ar="وسيط/طرف ثالث",
                order=4,
            )

            q_safety_msg = Question.objects.create(
                section=sec_conflict,
                identifier="safety_info",
                text_en=(
                    "CONFIDENTIAL: Would you like information on local "
                    "safety resources?"
                ),
                text_ar=(
                    "سري: هل ترغب في الحصول على معلومات حول موارد السلامة المحلية؟"
                ),
                question_type=Question.QuestionType.RADIO,
                required=False,
                order=4,
            )
            QuestionChoice.objects.create(
                question=q_safety_msg,
                value="yes",
                label_en="Yes, please",
                label_ar="نعم، من فضلك",
                order=1,
            )

            # Logic 1: Show child_count only if has_children == 'yes'
            QuestionLogic.objects.create(
                trigger_question=q_children,
                target_question=q_child_count,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="yes",
                action=QuestionLogic.ActionChoices.SHOW,
            )

            # Logic 2: Filter 'Parenting Styles' choice in conflict_root ONLY if they have children
            l_parent_choice = QuestionLogic.objects.create(
                trigger_question=q_children,
                target_question=q_conflict_root,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="yes",
                action=QuestionLogic.ActionChoices.INCLUDE_CHOICES,
            )
            l_parent_choice.target_choices.add(
                c_finance, c_inlaws, c_parenting, c_housework
            )

            # Logic 3: If NO children, exclude 'Parenting Styles' from the conflict roots
            l_no_parent_choice = QuestionLogic.objects.create(
                trigger_question=q_children,
                target_question=q_conflict_root,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="no",
                action=QuestionLogic.ActionChoices.INCLUDE_CHOICES,
            )
            l_no_parent_choice.target_choices.add(c_finance, c_inlaws, c_housework)

            # Logic 4: Show safety resources question only if violence == 'yes'
            QuestionLogic.objects.create(
                trigger_question=q_violence,
                target_question=q_safety_msg,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="yes",
                action=QuestionLogic.ActionChoices.SHOW,
            )

            # Logic 5: Show trust_reason only if trust_level == 'low'
            QuestionLogic.objects.create(
                trigger_question=q_trust_level,
                target_question=q_trust_reason,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="low",
                action=QuestionLogic.ActionChoices.SHOW,
            )

            # Logic 6: Filter resolution methods for 'separated' couples
            l_sep_resolution = QuestionLogic.objects.create(
                trigger_question=q_status,
                target_question=q_resolution,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="separated",
                action=QuestionLogic.ActionChoices.INCLUDE_CHOICES,
            )
            # Only allow Calm discussion and Third party
            talk_choice = QuestionChoice.objects.get(
                question=q_resolution, value="talk"
            )
            tp_choice = QuestionChoice.objects.get(
                question=q_resolution, value="third_party"
            )
            l_sep_resolution.target_choices.add(talk_choice, tp_choice)

            self.stdout.write(
                self.style.SUCCESS("Highly detailed seed data created successfully!")
            )
