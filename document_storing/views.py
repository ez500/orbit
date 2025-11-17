from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document

def upload_pdf(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("pdf_list")
    else:
        form = DocumentForm()
    return render(request, "upload_pdf.html", {"form": form})

def pdf_list(request):
    documents = Document.objects.all()
    return render(request, "pdf_list.html", {"documents": documents})
    