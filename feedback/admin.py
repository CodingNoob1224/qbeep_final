# from django.contrib import admin
# from .models import Registration, Attendance, Question, Response

# admin.site.register(Registration)
# admin.site.register(Attendance)
# admin.site.register(Question)
# admin.site.register(Response)
from django.contrib import admin
from .models import Winner

@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'draw_time')  # 在後台顯示這些欄位
    list_filter = ('event',)  # 允許依活動篩選
