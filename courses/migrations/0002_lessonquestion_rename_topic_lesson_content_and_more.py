# Generated by Django 5.1.3 on 2025-03-04 07:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('question_type', models.CharField(choices=[('mcq', 'Multiple Choice'), ('text', 'Text Input')], max_length=50)),
            ],
        ),
        migrations.RenameField(
            model_name='lesson',
            old_name='topic',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='created_at',
        ),
        migrations.AddField(
            model_name='course',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='course_videos/'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='lesson_videos/'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.course'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name='LessonAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='courses.lessonquestion')),
            ],
        ),
        migrations.CreateModel(
            name='LessonQuiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='courses.lesson')),
            ],
        ),
        migrations.AddField(
            model_name='lessonquestion',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='courses.lessonquiz'),
        ),
        migrations.DeleteModel(
            name='Quiz',
        ),
    ]
