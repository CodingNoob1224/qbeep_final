from django.contrib import admin
from .models import Winner, Question, Form, Response, Answer

# 中獎者後台
@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'draw_time')
    list_filter = ('event',)

# 問題內嵌在 Form 中
class QuestionInline(admin.TabularInline):  # 或改用 StackedInline 也行
    model = Question
    extra = 1  # 顯示幾個空白欄位讓管理員填新題目

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'event')
    inlines = [QuestionInline]

# 其他直接註冊
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Answer)
