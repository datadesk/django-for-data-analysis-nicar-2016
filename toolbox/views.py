from django.http import HttpResponse

def app_status(request):
    """
    Page for Varnish to check the server/app status
    """
    return HttpResponse("ok")