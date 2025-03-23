from django.db import models

class Case(models.Model):
    case_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    crime_execution = models.TextField()
    culprit_actions = models.TextField()
    is_solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Suspect(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="suspects")
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    alibi = models.TextField()
    is_guilty = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidence")
    description = models.TextField()
    is_key_evidence = models.BooleanField(default=False)

    def __str__(self):
        return self.description
