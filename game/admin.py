from django.contrib import admin
from .models import Case, Suspect, Evidence

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id','title', 'is_solved', 'created_at')
    list_filter = ('is_solved', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'case', 'is_guilty')
    list_filter = ('is_guilty', 'case')
    search_fields = ('name', 'alibi')

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('case', 'description', 'is_key_evidence')
    list_filter = ('is_key_evidence', 'case')
    search_fields = ('description',)
