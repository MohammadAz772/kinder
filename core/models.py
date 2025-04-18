from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'
        PARENT = 'PARENT', 'Parent'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=10, choices=Role.choices, verbose_name="Role")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    pin_code = models.CharField(max_length=10, blank=True, verbose_name="PIN Code")

    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Room"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Parent"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Room Name")
    description = models.TextField(blank=True, verbose_name="Description")
    main_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': User.Role.TEACHER},
        related_name='main_rooms',
        verbose_name="Main Teacher"
    )

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return self.name


class LearningStage(models.Model):
    stage_name = models.CharField(max_length=100, verbose_name="Stage Name")
    progress = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Progress (%)"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.STUDENT},
        verbose_name="Student"
    )

    class Meta:
        verbose_name = "Learning Stage"
        verbose_name_plural = "Learning Stages"

    def __str__(self):
        return f"{self.stage_name} - {self.progress}%"


class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(blank=True, verbose_name="Description")
    url = models.URLField(verbose_name="Video URL")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Upload Date")
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.TEACHER},
        verbose_name="Teacher"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Room")

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        return self.title


class Exam(models.Model):
    title = models.CharField(max_length=200, verbose_name="Exam Title")
    description = models.TextField(blank=True, verbose_name="Exam Description")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.TEACHER},
        verbose_name="Created By"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Room")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'MC', 'Multiple Choice'
        TRUE_FALSE = 'TF', 'True/False'
        SHORT_ANSWER = 'SA', 'Short Answer'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="Exam")
    text = models.TextField(verbose_name="Question Text")
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
        verbose_name="Question Type"
    )
    points = models.PositiveIntegerField(default=1, verbose_name="Points")

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"{self.exam.title} - {self.text[:50]}..."


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Question")
    text = models.TextField(verbose_name="Answer Text")
    is_correct = models.BooleanField(default=False, verbose_name="Is Correct")

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text[:30]}..."


class Grade(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.STUDENT},
        verbose_name="Student"
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="Exam")
    score = models.FloatField(verbose_name="Score")
    feedback = models.TextField(blank=True, verbose_name="Feedback")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student} - {self.exam}: {self.score}"


class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name="Task Title")
    description = models.TextField(blank=True, verbose_name="Task Description")
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.TEACHER},
        verbose_name="Teacher"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Room")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title


class StudentTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'P', 'Pending'
        IN_PROGRESS = 'IP', 'In Progress'
        COMPLETED = 'C', 'Completed'
        LATE = 'L', 'Late'

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.STUDENT},
        verbose_name="Student"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Task")
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status"
    )
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name="Submission Date")
    attachment = models.FileField(upload_to='task_submissions/', null=True, blank=True, verbose_name="Attachment")

    class Meta:
        verbose_name = "Student Task"
        verbose_name_plural = "Student Tasks"
        unique_together = ('student', 'task')

    def __str__(self):
        return f"{self.student} - {self.task}"



class Complaint(models.Model):
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.PARENT},
        verbose_name="Parent"
    )
    subject = models.CharField(max_length=255, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def __str__(self):
        return f"{self.parent.get_full_name()} - {self.subject}"
