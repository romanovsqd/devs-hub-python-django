from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def review(request):
    return render(request, "repetitions/review.html")
