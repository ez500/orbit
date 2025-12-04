from django.shortcuts import render, get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import os

from .serializers import FileListSerializer
from rest_framework.parsers import MultiPartParser

def home(request):
    return render(request, "home.html")

def list(request):
    directory_path = os.path.join(settings.BASE_DIR, 'static\\zip') # Example: a folder named 'my_files' in your project root
    print(directory_path)

    # Get the list of entries in the directory
    try:
        entries = os.listdir(directory_path)
    except FileNotFoundError:
        entries = [] # Handle cases where the directory might not exist

    context = {
        'directory_entries': entries,
        'directory_name': os.path.basename(directory_path),
    }
    return render(request, 'pdf_list.html', context)

#def serve_pdf(request, pk):
    #pdf_instance = get_object_or_404(MyPdfModel, pk=pk)
    #pdf_file_path = pdf_instance.pdf_file.path  # Assuming 'pdf_file' is your FileField
    #return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')

def download(request, uid):
    return render(request, "download.html", context={"uid": uid})

class HandleFileUpload(APIView):
    parser_classes = [MultiPartParser]
    def post(self, request):
        try:
            data = request.data

            serializer = FileListSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": 200,
                    "message": "files uploaded successfully",
                    "data": serializer.data
                })
            
            return Response({
                "status": 400,
                "message": "something went wrong",
                "data": serializer.errors
            })
        except Exception as e:
            print(e)