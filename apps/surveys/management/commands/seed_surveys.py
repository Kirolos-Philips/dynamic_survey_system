from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.surveys.models import Question, QuestionLogic, Section, Survey
from apps.users.models import SurveyManager

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with example survey data."

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError(
                "This command can only be run in the local environment (DEBUG=True)."
            )

        self.stdout.write("Seeding data...")

        with transaction.atomic():
            # 1. Create a Survey Manager
            manager, created = SurveyManager.objects.get_or_create(
                username="survey_admin",
                defaults={
                    "email": "admin@survey.com",
                    "first_name": "Survey",
                    "last_name": "Admin",
                    "is_staff": True,
                },
            )
            if created:
                manager.set_password("admin123")
                manager.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created manager: {manager.username} (pass: admin123)"
                    )
                )

            # 2. Create the Survey
            survey, created = Survey.objects.get_or_create(
                title_en="Customer Feedback Survey",
                defaults={
                    "title_ar": "استطلاع رأي العملاء",
                    "description_en": (
                        "Help us improve our service by providing your feedback."
                    ),
                    "description_ar": "ساعدنا في تحسين خدمتنا من خلال تقديم ملاحظاتك.",
                    "created_by": manager,
                    "is_active": True,
                },
            )
            if not created:
                self.stdout.write(
                    self.style.WARNING("Survey already exists, skipping creation.")
                )
                return

            self.stdout.write(self.style.SUCCESS(f"Created survey: {survey.title_en}"))

            # 3. Create Sections
            sec1 = Section.objects.create(
                survey=survey,
                title_en="General Experience",
                title_ar="التجربة العامة",
                description_en="Tell us about your general feeling.",
                description_ar="أخبرنا عن شعورك العام.",
                order=1,
            )

            sec2 = Section.objects.create(
                survey=survey,
                title_en="Product Details",
                title_ar="تفاصيل المنتج",
                description_en="Technical questions about the product.",
                description_ar="أسئلة تقنية حول المنتج.",
                order=2,
            )

            # 4. Create Questions for Section 1
            q1 = Question.objects.create(
                section=sec1,
                text_en="How satisfied are you with our service?",
                text_ar="ما مدى رضاك عن خدمتنا؟",
                question_type=Question.QuestionType.RADIO,
                configuration={
                    "options": [
                        {
                            "value": "very_happy",
                            "label_en": "Very Happy",
                            "label_ar": "سعيد جداً",
                        },
                        {
                            "value": "neutral",
                            "label_en": "Neutral",
                            "label_ar": "محايد",
                        },
                        {
                            "value": "unhappy",
                            "label_en": "Unhappy",
                            "label_ar": "غير سعيد",
                        },
                    ]
                },
                order=1,
            )

            q2 = Question.objects.create(
                section=sec1,
                text_en="Why are you unhappy? (Conditional)",
                text_ar="لماذا أنت غير سعيد؟ (سؤال مشروط)",
                question_type=Question.QuestionType.TEXT,
                required=False,
                order=2,
            )

            # Add Logic: Show Q2 if Q1 is 'unhappy'
            QuestionLogic.objects.create(
                trigger_question=q1,
                target_question=q2,
                operator=QuestionLogic.OperatorChoices.EQUALS,
                value="unhappy",
                action=True,  # Show
            )

            # 5. Create Questions for Section 2
            Question.objects.create(
                section=sec2,
                text_en="Which features do you use most?",
                text_ar="ما هي المميزات التي تستخدمها كثيراً؟",
                question_type=Question.QuestionType.CHECKBOX,
                configuration={
                    "options": [
                        {
                            "value": "mobile",
                            "label_en": "Mobile App",
                            "label_ar": "تطبيق الموبايل",
                        },
                        {
                            "value": "web",
                            "label_en": "Web Dashboard",
                            "label_ar": "لوحة التحكم",
                        },
                        {
                            "value": "api",
                            "label_en": "REST API",
                            "label_ar": "واجهة البرمجة",
                        },
                    ]
                },
                order=1,
            )

            Question.objects.create(
                section=sec2,
                text_en="When did you last purchase from us?",
                text_ar="متى كان آخر شراء لك منا؟",
                question_type=Question.QuestionType.DATE,
                order=2,
            )

            self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
