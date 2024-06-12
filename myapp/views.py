from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views import View
from .models import Pekerjaan, SubPekerjaan, Referensi, PDFHash, RAB, Approval
from .forms import PekerjaanForm, SubPekerjaanForm, LoginForm, RABForm
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

#for pdf generator
from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from datetime import datetime
import hashlib

@login_required(login_url='/login/')
def home(request):
    rabs = RAB.objects.filter(user=request.user)
    return render(request, 'home.html', {'rabs': rabs})

def admin(request):
    return render(request, "admin.html")

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You have been logged in as {username}.')
                return redirect('home')
            else:
                form.add_error(None, 'Username atau password salah.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required(login_url='/login/')
def pekerjaan_sukses(request):
    return render(request, "pekerjaan_sukses.html")

def get_referensi_harga(request, referensi_id):
    referensi = Referensi.objects.get(id=referensi_id)
    data = {
        'harga_satuan': referensi.harga_satuan,
    }
    return JsonResponse(data)

@login_required(login_url='/login/')
def daftar_pekerjaan(request):
    konstruksi_pekerjaan = Pekerjaan.objects.filter(tipe_pekerjaan='Konstruksi')
    pra_konstruksi_pekerjaan = Pekerjaan.objects.filter(tipe_pekerjaan='Pra Konstruksi')

    total_harga_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in konstruksi_pekerjaan)
    total_harga_pra_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in pra_konstruksi_pekerjaan)
    total_konstruksi = total_harga_konstruksi + total_harga_pra_konstruksi

    form = SubPekerjaanForm()
    form_main = PekerjaanForm()
    edit_item_id = None
    
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if pk:
                sub = SubPekerjaan.objects.get(id=pk)
                form = SubPekerjaanForm(request.POST, instance=sub)
            else:
                form = SubPekerjaanForm(request.POST)
            if form.is_valid():
                sub = form.save(commit=False)
                if not pk:  # Only set pekerjaan if this is a new instance
                    pekerjaan_id = request.POST.get('pekerjaan_id')
                    if pekerjaan_id:
                        pekerjaan = Pekerjaan.objects.get(id=pekerjaan_id)
                        sub.pekerjaan = pekerjaan
                form.save()
            form = SubPekerjaanForm()
        elif 'save_main' in request.POST:
            pk = request.POST.get('save_main')
            if pk:
                main = Pekerjaan.objects.get(id=pk)
                form_main = PekerjaanForm(request.POST, instance=main)
            else:
                form_main = PekerjaanForm(request.POST)
            if form_main.is_valid():
                main = form_main.save(commit=False)
                if not pk:  # Only set pekerjaan if this is a new instance
                    pekerjaan_id = request.POST.get('pekerjaan_id')
                    if pekerjaan_id:
                        pekerjaan = Pekerjaan.objects.get(id=pekerjaan_id)
                        main.pekerjaan = pekerjaan
                form_main.save()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            sub = SubPekerjaan.objects.get(id=pk)
            sub.delete()
        elif 'delete_main' in request.POST:
            pk = request.POST.get('delete_main')
            main = Pekerjaan.objects.get(id=pk)
            main.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            sub = SubPekerjaan.objects.get(id=pk)
            form = SubPekerjaanForm(instance=sub)
            edit_item_id = pk
        elif 'edit_main' in request.POST:
            pk = request.POST.get('edit_main')
            main = Pekerjaan.objects.get(id=pk)
            form_main = PekerjaanForm(instance=main)
            edit_item_id = pk

    context = {
        'konstruksi_pekerjaan': konstruksi_pekerjaan,
        'pra_konstruksi_pekerjaan': pra_konstruksi_pekerjaan,
        'total_harga_konstruksi': total_harga_konstruksi,
        'total_harga_pra_konstruksi': total_harga_pra_konstruksi,
        'total_konstruksi' : total_konstruksi,
        'form': form,
        'form_main' : form_main,
        'edit_item_id': edit_item_id,
    }
    
    return render(request, 'daftar_pekerjaan.html', context)

@login_required(login_url='/login/')
def tambah_pekerjaan(request, rab_id):
    rab = get_object_or_404(RAB, id=rab_id, user=request.user)
    SubPekerjaanFormSet = inlineformset_factory(Pekerjaan, SubPekerjaan, form=SubPekerjaanForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form_main = PekerjaanForm(request.POST)
        formset = SubPekerjaanFormSet(request.POST)

        if form_main.is_valid() and formset.is_valid():
            pekerjaan = form_main.save(commit=False)
            pekerjaan.rab = rab
            pekerjaan.save()
            subpekerjaans = formset.save(commit=False)
            for subpekerjaan in subpekerjaans:
                subpekerjaan.pekerjaan = pekerjaan
                subpekerjaan.save()
            pekerjaan.update_harga_total()
            return redirect('detail_rab', rab_id=rab.id)
    else:
        form_main = PekerjaanForm()
        formset = SubPekerjaanFormSet()

    context = {
        'form_main': form_main,
        'formset': formset,
    }
    return render(request, "tambah_pekerjaan2.html", context)

########## NEW MODELS ############
@login_required(login_url='/login/')
def tambah_rab(request):
    if request.method == 'POST':
        form = RABForm(request.POST)
        if form.is_valid():
            rab = form.save(commit=False)
            rab.user = request.user
            rab.save()

            # Mendapatkan approvers dari form dan menambahkan dengan urutan
            approvers = request.POST.getlist('approvers')
            for index, approver_id in enumerate(approvers):
                approver = User.objects.get(id=approver_id)
                Approval.objects.create(rab=rab, approver=approver, order=index + 1)

            return redirect('detail_rab', rab_id=rab.id)
    else:
        form = RABForm()
        # Filter out the current user from the list of potential approvers
        users = User.objects.exclude(id=request.user.id)
    return render(request, 'tambah_rab.html', {'form': form, 'users': users})

@login_required(login_url='/login/')
def detail_rab(request, rab_id):
    # Mengambil RAB tanpa memeriksa user
    rab = get_object_or_404(RAB, id=rab_id)
    
    # Memeriksa apakah user yang sedang login adalah pemilik RAB atau approver
    if rab.user != request.user and not Approval.objects.filter(rab=rab, approver=request.user).exists():
        return HttpResponseForbidden("You do not have permission to view this RAB.")

    konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Konstruksi')
    pra_konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Pra Konstruksi')

    total_harga_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in konstruksi_pekerjaan)
    total_harga_pra_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in pra_konstruksi_pekerjaan)
    total_konstruksi = total_harga_konstruksi + total_harga_pra_konstruksi

    form = SubPekerjaanForm()
    form_main = PekerjaanForm()
    edit_item_id = None

    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if pk:
                sub = SubPekerjaan.objects.get(id=pk)
                form = SubPekerjaanForm(request.POST, instance=sub)
            else:
                form = SubPekerjaanForm(request.POST)
            if form.is_valid():
                sub = form.save(commit=False)
                if not pk:  # Only set pekerjaan if this is a new instance
                    pekerjaan_id = request.POST.get('pekerjaan_id')
                    if pekerjaan_id:
                        pekerjaan = Pekerjaan.objects.get(id=pekerjaan_id)
                        sub.pekerjaan = pekerjaan
                form.save()
            form = SubPekerjaanForm()
        elif 'save_main' in request.POST:
            pk = request.POST.get('save_main')
            if pk:
                main = Pekerjaan.objects.get(id=pk)
                form_main = PekerjaanForm(request.POST, instance=main)
            else:
                form_main = PekerjaanForm(request.POST)
            if form_main.is_valid():
                main = form_main.save(commit=False)
                if not pk:  # Only set pekerjaan if this is a new instance
                    pekerjaan_id = request.POST.get('pekerjaan_id')
                    if pekerjaan_id:
                        pekerjaan = Pekerjaan.objects.get(id=pekerjaan_id)
                        main.pekerjaan = pekerjaan
                form_main.save()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            sub = SubPekerjaan.objects.get(id=pk)
            sub.delete()
        elif 'delete_main' in request.POST:
            pk = request.POST.get('delete_main')
            main = Pekerjaan.objects.get(id=pk)
            main.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            sub = SubPekerjaan.objects.get(id=pk)
            form = SubPekerjaanForm(instance=sub)
            edit_item_id = pk
        elif 'edit_main' in request.POST:
            pk = request.POST.get('edit_main')
            main = Pekerjaan.objects.get(id=pk)
            form_main = PekerjaanForm(instance=main)
            edit_item_id = pk

    approvals = rab.approval_set.all()
    can_download_pdf = rab.status == 'Approved'

    context = {
        'rab': rab,
        'konstruksi_pekerjaan': konstruksi_pekerjaan,
        'pra_konstruksi_pekerjaan': pra_konstruksi_pekerjaan,
        'total_harga_konstruksi': total_harga_konstruksi,
        'total_harga_pra_konstruksi': total_harga_pra_konstruksi,
        'total_konstruksi': total_konstruksi,
        'form': form,
        'form_main': form_main,
        'edit_item_id': edit_item_id,
        'approvals': approvals,
        'can_download_pdf': can_download_pdf,
    }
    return render(request, 'detail_rab.html', context)

@login_required(login_url='/login/')
def approve_rab(request, rab_id, approval_id):
    rab = get_object_or_404(RAB, id=rab_id)
    approval = get_object_or_404(Approval, id=approval_id, approver=request.user)

    # Cek apakah semua approvers sebelumnya telah memberikan persetujuan
    previous_approvals = Approval.objects.filter(rab=rab, order__lt=approval.order).order_by('order')
    for prev_approval in previous_approvals:
        if prev_approval.status != 'Approved':
            return HttpResponseForbidden("You cannot approve this RAB yet. Previous approvals are pending or rejected.")

    approval_done = approval.status in ['Approved', 'Rejected']

    if request.method == 'POST' and not approval_done:
        if 'approve' in request.POST:
            approval.status = 'Approved'
        elif 'reject' in request.POST:
            approval.status = 'Rejected'
        approval.save()

        # Check if all approvals are complete
        all_approvals = rab.approval_set.all()
        if all_approvals.filter(status='Rejected').exists():
            rab.status = 'Rejected'
        elif all_approvals.filter(status='Pending').exists():
            rab.status = 'Pending'
        else:
            rab.status = 'Approved'
        rab.save()

        return redirect('approval_list')

    # Mengambil data yang sama seperti di detail_rab
    konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Konstruksi')
    pra_konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Pra Konstruksi')

    total_harga_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in konstruksi_pekerjaan)
    total_harga_pra_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in pra_konstruksi_pekerjaan)
    total_konstruksi = total_harga_konstruksi + total_harga_pra_konstruksi

    approvals = rab.approval_set.all()

    context = {
        'rab': rab,
        'approval': approval,
        'konstruksi_pekerjaan': konstruksi_pekerjaan,
        'pra_konstruksi_pekerjaan': pra_konstruksi_pekerjaan,
        'total_harga_konstruksi': total_harga_konstruksi,
        'total_harga_pra_konstruksi': total_harga_pra_konstruksi,
        'total_konstruksi': total_konstruksi,
        'approvals': approvals,
        'user_pembuat': rab.user,
        'approval_done': approval_done,  # Tambahkan variabel ini ke konteks
    }
    return render(request, 'approve_rab.html', context)

@login_required(login_url='/login/')
def approval_list(request):
    approvals = Approval.objects.filter(approver=request.user, status='Pending')
    rabs = [approval.rab for approval in approvals]
    return render(request, 'approval_list.html', {'rabs': rabs})

########## PDF CLASS #############
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        pdf_content = result.getvalue()
        hash_code = generate_hash(pdf_content)
        return pdf_content, hash_code
    return None, None

def generate_hash(content):
    return hashlib.sha256(content).hexdigest()

def save_pdf_hash(pdf_hash, file_name):
    from .models import PDFHash
    if not PDFHash.objects.filter(hash_code=pdf_hash).exists():
        PDFHash.objects.create(hash_code=pdf_hash, file_name=file_name)
    else:
        # Optionally update the file name if the hash already exists
        pdf_record = PDFHash.objects.get(hash_code=pdf_hash)
        pdf_record.file_name = file_name
        pdf_record.save()

class ViewPDF(View):
    def get(self, request, *args, **kwargs):
        rab_id = kwargs.get('rab_id')
        rab = get_object_or_404(RAB, id=rab_id)
        konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Konstruksi')
        pra_konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Pra Konstruksi')

        total_harga_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in konstruksi_pekerjaan)
        total_harga_pra_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in pra_konstruksi_pekerjaan)
        total_konstruksi = total_harga_konstruksi + total_harga_pra_konstruksi

        data = {
            'rab':rab,
            'konstruksi_pekerjaan': konstruksi_pekerjaan,
            'pra_konstruksi_pekerjaan': pra_konstruksi_pekerjaan,
            'total_harga_konstruksi': total_harga_konstruksi,
            'total_harga_pra_konstruksi': total_harga_pra_konstruksi,
            'total_konstruksi': total_konstruksi,
        }
        pdf, hash_code = render_to_pdf('pdf_template.html', data)
        
        # Save hash_code and filename to database
        if pdf:
            file_name = "preview.pdf"
            save_pdf_hash(hash_code, file_name)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="preview.pdf"'
        return response

class DownloadPDF(View):
    def get(self, request, *args, **kwargs):
        rab_id = kwargs.get('rab_id')
        rab = get_object_or_404(RAB, id=rab_id)
        konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Konstruksi')
        pra_konstruksi_pekerjaan = Pekerjaan.objects.filter(rab=rab, tipe_pekerjaan='Pra Konstruksi')

        total_harga_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in konstruksi_pekerjaan)
        total_harga_pra_konstruksi = sum(pekerjaan.harga_total_pekerjaan for pekerjaan in pra_konstruksi_pekerjaan)
        total_konstruksi = total_harga_konstruksi + total_harga_pra_konstruksi

        nama_rab = rab.nama_rab
        date_time = datetime.now()
        format = f'RAB {nama_rab}.PDF'
        file_name = date_time.strftime(format)

        data = {
            'rab' : rab,
            'konstruksi_pekerjaan': konstruksi_pekerjaan,
            'pra_konstruksi_pekerjaan': pra_konstruksi_pekerjaan,
            'total_harga_konstruksi': total_harga_konstruksi,
            'total_harga_pra_konstruksi': total_harga_pra_konstruksi,
            'total_konstruksi': total_konstruksi,
        }
        pdf, hash_code = render_to_pdf('pdf_template.html', data)

        if pdf:
            # Save hash_code and filename to database
            save_pdf_hash(hash_code, file_name)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        content = f"attachment; filename={file_name}"
        response['Content-Disposition'] = content
        return response