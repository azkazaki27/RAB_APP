from django.db import models
from django.contrib.auth.models import User

class RAB(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_rab = models.CharField(max_length=255)
    tanggal = models.DateField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return self.nama_rab

    def check_approval_status(self):
        approvals = self.approval_set.all()
        if all(approval.status == 'Approved' for approval in approvals):
            self.status = 'Approved'
        elif any(approval.status == 'Rejected' for approval in approvals):
            self.status = 'Rejected'
        else:
            self.status = 'Pending'
        self.save()

class Approval(models.Model):
    rab = models.ForeignKey(RAB, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    order = models.IntegerField()

    def __str__(self):
        return f"{self.rab.nama_rab} - {self.approver.username} - {self.status}"
    
class Referensi(models.Model):
    nama_referensi = models.CharField(max_length=255)
    harga_satuan = models.DecimalField(max_digits=18, decimal_places=0)

    def __str__(self):
        return self.nama_referensi

class Pekerjaan(models.Model):
    rab = models.ForeignKey(RAB, on_delete=models.CASCADE)
    nama_pekerjaan = models.CharField(max_length=255)
    harga_total_pekerjaan = models.DecimalField(max_digits=18, decimal_places=0, default=0.00, editable=False)
    tipe_pekerjaan = models.CharField(max_length=50, choices=[('Konstruksi', 'Konstruksi'), ('Pra Konstruksi', 'Pra Konstruksi')])

    def __str__(self):
        return self.nama_pekerjaan

    def update_harga_total(self):
        total = sum(sub.harga_total for sub in self.subpekerjaan_set.all())
        self.harga_total_pekerjaan = total
        self.save()

class SubPekerjaan(models.Model):
    SATUAN_CHOICES = [
        ('KMS', 'KMS'),
        ('Bay', 'Bay'),
        ('Lot', 'Lot'),
        ('Set', 'Set'),
        ('Unit', 'Unit'),
        ('LS', 'LS'),
        ('m2', 'm2'),
        ('KMR', 'KMR'),
        ('DIA', 'DIA'),
        ('Bank', 'Bank'),
        ('CB', 'CB'),
    ]

    pekerjaan = models.ForeignKey(Pekerjaan, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    kuantiti = models.DecimalField(max_digits=10, decimal_places=0)
    satuan = models.CharField(max_length=50, choices=SATUAN_CHOICES)
    harga_satuan = models.DecimalField(max_digits=18, decimal_places=0)
    harga_total = models.DecimalField(max_digits=18, decimal_places=0, editable=False)
    referensi_harga = models.ForeignKey(Referensi, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.pekerjaan.nama_pekerjaan} - {self.nama}"

    def save(self, *args, **kwargs):
        if self.referensi_harga and not self.harga_satuan:
            self.harga_satuan = self.referensi_harga.harga_satuan
        self.harga_total = self.kuantiti * self.harga_satuan
        super(SubPekerjaan, self).save(*args, **kwargs)
        self.pekerjaan.update_harga_total()

class PDFHash(models.Model):
    hash_code = models.CharField(max_length=64, unique=True)
    file_name = models.CharField(max_length=255, default="aa")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} - {self.hash_code}"