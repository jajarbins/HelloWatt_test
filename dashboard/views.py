from django.shortcuts import render, redirect
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


def results(request, client_id):

    # we should check client_id type, availability (...) here

    context = ResultsContext(client_id=int(client_id))
    return render(request, 'dashboard/results.html', context.to_dict())












