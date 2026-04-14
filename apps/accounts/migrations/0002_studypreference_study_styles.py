from django.db import migrations, models


def default_study_styles():
    return ["visual"]


def populate_study_styles(apps, schema_editor):
    StudyPreference = apps.get_model("accounts", "StudyPreference")
    for preference in StudyPreference.objects.all():
        legacy_style = getattr(preference, "study_style", None) or "visual"
        preference.study_styles = [legacy_style]
        preference.save(update_fields=["study_styles"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="studypreference",
            name="study_styles",
            field=models.JSONField(blank=True, default=default_study_styles),
        ),
        migrations.RunPython(populate_study_styles, migrations.RunPython.noop),
    ]
