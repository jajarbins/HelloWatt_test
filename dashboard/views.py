from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from dashboard.Context.context_results import ResultsContext

from dashboard.forms import ClientForm


class ClientFormView(View):  # class ClientFormView(View)
    def get(self, request):
        return render(request, 'dashboard/accueil.html')

    def post(self, request):
        client_form = ClientForm(request.POST)

        if client_form.is_valid():
            client_id = client_form.cleaned_data['client']

            return redirect('dashboard:results', client_id=client_id)


@csrf_exempt
def results(request, client_id):

    if request.is_ajax():
        context = ResultsContext(client_id=request.POST['client_id'], current_year=request.POST['selected_year'])
        gna = context.to_dict()
        gna = 2
        return JsonResponse(context.to_dict())

    elif request.method == "GET":
        context = ResultsContext(client_id=client_id)
        return render(request, 'dashboard/results.html', context.to_dict())













