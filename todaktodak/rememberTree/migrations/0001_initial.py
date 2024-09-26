# Generated by Django 5.0.7 on 2024-08-02 05:08

import datetime
import django.db.models.deletion
import django.utils.timezone
import rememberTree.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question_text", models.CharField(max_length=200)),
                (
                    "question_type",
                    models.CharField(
                        choices=[
                            ("DENIAL", "Denial"),
                            ("ANGER", "Anger"),
                            ("BARGAINING", "Bargaining"),
                            ("DEPRESSION", "Depression"),
                            ("ACCEPTANCE", "Acceptance"),
                        ],
                        default="",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="rememberTree",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("treeName", models.CharField(max_length=20)),
                ("myName", models.CharField(default="토닥토닥", max_length=100)),
                (
                    "flowerType",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("growth_period", models.DateField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trees",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Photo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rememberPhoto",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=rememberTree.models.user_photo_upload_to,
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                (
                    "rememberDate",
                    models.DateField(
                        blank=True, default=datetime.date.today, null=True
                    ),
                ),
                ("comment", models.CharField(blank=True, max_length=2000, null=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "remember_tree",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="rememberTree.remembertree",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Letters",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(max_length=780)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "writer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="letters",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "remember_tree",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="letters",
                        to="rememberTree.remembertree",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserQuestionAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("answer_text", models.TextField()),
                ("date_answered", models.DateField(default=django.utils.timezone.now)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_question_answers",
                        to="rememberTree.question",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_question_answers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "date_answered")},
            },
        ),
    ]
