from django.urls import path
from.import views
from django.views.generic import TemplateView
from .views import get_referensi_harga
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.home, login_url='/login/') , name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("tambah-pekerjaan2/", login_required(views.tambah_pekerjaan, login_url='/login/'), name='tambah_pekerjaan2'),
    path("pekerjaan-sukses/", views.pekerjaan_sukses, name='pekerjaan_sukses'),
    path('daftar-pekerjaan/', login_required(views.daftar_pekerjaan, login_url='/login/'), name='daftar_pekerjaan'),
    path('pdf-view/<int:rab_id>/', views.ViewPDF.as_view(), name="pdf_view"),
    path('pdf-download/<int:rab_id>/', views.DownloadPDF.as_view(), name="pdf_download"),
    path("admin/", views.admin, name="admin"),
    path('get_referensi_harga/<int:referensi_id>/', get_referensi_harga, name='get_referensi_harga'),

    path('rabs/tambah/', views.tambah_rab, name='tambah_rab'),
    path('rabs/<int:rab_id>/', views.detail_rab, name='detail_rab'),
    path('rabs/<int:rab_id>/tambah_pekerjaan2/', views.tambah_pekerjaan, name='tambah_pekerjaan'),

    path('approval-list/', views.approval_list, name='approval_list'),
    path('rab/<int:rab_id>/approve/<int:approval_id>/', views.approve_rab, name='approve_rab'),
    
    
]