# Generated by Django 4.1.5 on 2023-01-12 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_orca", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="userrole",
            index=models.Index(
                fields=["role_class"], name="django_orca_role_cl_3e0010_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="userrole",
            index=models.Index(fields=["user"], name="django_orca_user_id_2cf44e_idx"),
        ),
        migrations.AddIndex(
            model_name="userrole",
            index=models.Index(
                fields=["content_type"], name="django_orca_content_6c1ac7_idx"
            ),
        ),
    ]
