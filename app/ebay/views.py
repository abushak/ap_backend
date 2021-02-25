from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .services import EbayService, EbayServiceError


@login_required(login_url='/admin/login/')
def search(request):
    # Deny from all except is_staff user
    if not request.user.is_staff:
        raise PermissionDenied

    # Error messages queue
    error_messages: list = []

    search_results = []
    query = request.GET.get('query', '')
    per_page = request.GET.get('per_page', 50)
    page = request.GET.get('page', 1)

    try:
        ebay = EbayService(auto_save=True)
    except EbayServiceError as error:
        error_messages.append(error.__str__())

    if request.GET and query != '':
        try:
            search_results = ebay.search(keywords=query, per_page=per_page, page=page, owner=request.user.pk)
        except EbayServiceError as error:
            error_messages.append(error.__str__())

    return render(request, "ebay/search/index.html", {
        'error_messages': error_messages,
        'response': search_results,
        'form': {
            'query': query,
            'per_page': int(per_page),
            'page': int(page)
        }
    })
