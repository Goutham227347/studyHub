from django.shortcuts import render

from materials.views import HomeView


class AboutView:
    pass


def about(request):
    return render(request, 'core/about.html')


# Re-export home
home = HomeView.as_view()
