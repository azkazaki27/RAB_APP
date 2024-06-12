from django.contrib import admin
from .models import Pekerjaan, SubPekerjaan, Referensi, PDFHash, RAB

class SubPekerjaanInline(admin.TabularInline):
    model = SubPekerjaan
    extra = 1
    readonly_fields = ('harga_total',)
    
class PekerjaanAdmin(admin.ModelAdmin):
    list_display = ['nama_pekerjaan', 'harga_total_pekerjaan','tipe_pekerjaan']
    inlines = [SubPekerjaanInline]

class ReferensiAdmin(admin.ModelAdmin):
    list_display = ('nama_referensi', 'harga_satuan')  # Menampilkan kolom yang diinginkan di list view
    search_fields = ('nama_referensi',)  # Menambahkan search bar untuk mencari berdasarkan nama_referensi

class PDFHashAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'hash_code', 'created_at']
    search_fields = ['file_name', 'hash_code']
    readonly_fields = ['file_name', 'hash_code', 'created_at']

class RABAdmin(admin.ModelAdmin):
    list_display = ['nama_rab', 'tanggal', 'user']
    search_fields = ['nama_rab', 'user__username']
    list_filter = ['tanggal']

admin.site.register(Pekerjaan, PekerjaanAdmin)
admin.site.register(Referensi)
admin.site.register(PDFHash, PDFHashAdmin)
admin.site.register(RAB, RABAdmin)

