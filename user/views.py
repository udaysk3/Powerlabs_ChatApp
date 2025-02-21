from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from user.models import ExtendedUser
import json

@csrf_exempt
def temp_login(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            password = request.POST["password"]
            print(email, password)
            user = ExtendedUser.objects.filter(email=email, password=password).first()
            if user is not None:
                login(request, user)  # This logs in the user
                return redirect("/chat/")    
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    elif request.method == "GET":
        return render(request, "login.html")
    
    return JsonResponse({"error": "Method not allowed"}, status=405)
