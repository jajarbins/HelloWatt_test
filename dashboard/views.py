from django.shortcuts import render, redirect
from django.views.generic import View

from enum import Enum
import plotly.graph_objects as go
import plotly.offline as opy

from .forms import ClientForm
from .models import Conso_eur, Conso_watt


class ClientFormView(View):  # class ClientFormView(View)
    def get(self, request):
        return render(request, 'dashboard/accueil.html')

    def post(self, request):
        client_form = ClientForm(request.POST)
        # conso_watt_form = ConsoWattForm

        if client_form.is_valid():
            client_id = client_form.cleaned_data['client']

            return redirect('dashboard:results', client_id=client_id)


def results(request, client_id):
    annual_costs = EuroCostDealer(client_id).set_annual_cost(Years.SECOND.value)
    conso_watt = []
    conso_watt_graph = ConsoWattDealer(client_id).get_conso_watt_graph(Years.SECOND.value)
    is_elec_heating = ConsoWattDealer(client_id).is_electric_heating()
    dysfunction_detected = ConsoWattDealer(client_id).set_dysfunctional_string()

    ###################################
    # ----> YOUR CODE GOES HERE <---- #
    ###################################

    gna = 4

    context = {
        "conso_watt": conso_watt,
        "annual_costs": annual_costs,
        "is_elec_heating": is_elec_heating,
        "dysfunction_detected": dysfunction_detected,
        "client_id": client_id,
        "conso_watt_graph": conso_watt_graph
    }
    return render(request, 'dashboard/results.html', context)


# noinspection SpellCheckingInspection
class Months(Enum):
    """
        in order to set constants properly and be able to iterate through values
    """
    JANVIER = "janvier"
    FEVRIER = "fevrier"
    MARS = "mars"
    AVRIL = "avril"
    MAI = "mai"
    JUIN = "juin"
    JUILLET = "juillet"
    AOUT = "aout"
    SEPTEMBRE = "septembre"
    OCTOBRE = "octobre"
    NOVEMBRE = "novembre"
    DECEMBRE = "decembre"


class Years(Enum):
    """
        in order to set constants properly and be able to iterate through values

        Note: We should not use an Enum but ask to the db the available years.
    """
    FIRST = 2016
    SECOND = 2017


class EuroCostDealer:
    """
        Deal with the annual cost calculation
    """

    def __init__(self, client_id):
        self.client_id = client_id

    def set_annual_cost(self, year):
        """
            get monthly cost (€) of the electric consumption for a given client and year and sum it to have the annual cost

        :param (int) year: the year you want the annual consumption
        :return (float): the annual cost
        """

        annual_cost = 0

        # get euro cost data from dashboard_conso_euro db for the given client_id and year
        conso_euro = Conso_eur.objects.get(client_id=self.client_id, year=year)

        # sum the monthly euro cost for  all the month in the year
        for month in Months:
            annual_cost += conso_euro.__getattribute__(month.value)

        return round(annual_cost, 2)

    # def set_annuals_cost(self):
    #     """
    #         list all the annual cost of the electric consumption for the available years

    #     :return (list): all the annual cost
    #     """

    #     return [self.set_annual_cost(year.value) for year in Years]


class ConsoWattDealer:
    def __init__(self, client_id):
        self.client_id = client_id

    def set_monthly_conso_watt(self, year):
        """
        set the monthly watt consumption for the given client_id and year

        :param (int) year: the year you want the annual consumption
        :return (list): the monthly watt consumption for a year
        """

        conso_euro = Conso_watt.objects.get(client_id=self.client_id, year=year)
        return [round(conso_euro.__getattribute__(month.value), 2) for month in Months]

    def get_conso_watt_graph(self, year):
        """
            get list of month ( x(t) ) and list of watt consumption for a year( y(t) ), and create a simple line plot ( y(t) = x(t) )

        :return (): the html of a graph (plotly) of the monthly electric consumption over a year ready to be embed in a template
        """

        monthly_conso_watt_graph = go.Figure({
            "data": [{
                "type": "scatter",
                "x": [month.value for month in Months],
                "y": self.set_monthly_conso_watt(year)
            }],
            "layout": {
                "title": {
                    "text": "Electricity consumption in 2017",
                    "font_size": 30
                },
                "yaxis": {"title": "Watt Consumption"},
                "xaxis": {"title": "Month"}
            }
        })

        # turn it into html
        return opy.plot(monthly_conso_watt_graph, auto_open=False, output_type='div')

    def is_electric_heating(self):
        """
        Check if the client is using an electric heating

        :return (boolean): True if the client uses electric heating, False otherwise
        """
        # higher_electric_consumption_coefficient represent the increase of the electric consumption during winter
        # due the use of the electric heating. I choose a coefficient rather than an offset to

        # The average of the electric heating represent 60% of the electric consumption during winter months (source: https://particuliers.engie.fr/electricite/conseils-electricite/prix-electricite/consommation-electrique-moyenne-logement-par-superficie.html#Quatre%20postes%20de%20consommation%20%C3%A9lectrique%20dans%20une%20maison )
        # It is a 1.5 higher consumption.

        # If the housing is in a building, or well isolated, theses values will decrease. Moreover, the choice in the
        # calculation of the winter and summer average consumption is not perfect for several reasons:
        # latitude of the housing; exposure of the housing; does it have a veranda; weather during the year ...

        # so we take a higher_electric_consumption_coefficient equal to 1.3 to have margin.

        # Note: We should take into account months where clients are in holidays.
        # If it happen during winter months, it will decrease the "winter_average_conso" and we would not be able
        # to detect if the client use electric heating. To avoid this problem, I remove the lower moth in term of
        # electric consumption. But we should look at the weekly, or even better, the daily electric consumption to
        # be able to correctly overpass this problem.

        # Note2: Arbitrary say that electric heating is used during november, december, january, february, march and april

        higher_electric_consumption_coefficient = 1.3
        using_elec_heating = []

        for year in Years:

            # GET DATA
            conso = self.set_monthly_conso_watt(year.value)

            # PREPROCESS DATA:
            # split winter months and summer months
            winter_months_conso = [
                conso.pop(-1) +
                conso.pop(-1) +
                conso.pop(0) +
                conso.pop(0) +
                conso.pop(0) +
                conso.pop(0)
            ]

            # remove lower month for each part of the year
            winter_months_conso.remove(min(winter_months_conso))
            conso.remove(min(conso))

            # average calculation
            winter_average_conso = sum(winter_months_conso)/5  # 5 month are take into account
            summer_average_conso = sum(conso)/5  # 5 month are taken into account

            # ARBITRATION
            # check if there is a significant increase of the electric consumption during winter months.
            if winter_average_conso > summer_average_conso*higher_electric_consumption_coefficient:
                using_elec_heating.append(True)
            else:
                using_elec_heating.append(False)

        # we should have an increase of the electric consumption during winter months for all the available years to conclude
        if using_elec_heating.__contains__(False):
            return False
        return True

    def is_dysfunctional(self):
        """
        for each available year, check if there is a dysfunction.

        There is a dysfunction when the electricity consumption of each month of a year is significally (10% or more)
        greater than the consumption of each month of the following year.

        To avoid to count as not dysfunctional a dysfunctional year where the client consumed less than the previous
        year for several reasons (in vacation, or whatever), we tolerate 1 month in the year where the consumption
        increase is lower than 10%.

        :return (List): a list of tuples containing the years where dysfunction have been detected
        """

        dysfunctional_watt_margin = 0.1  # the increase of the watt consumption for a given month over two consecutive year, for the month to be classified as problematic
        dysfunctional_month_margin = 1  # the number of months tolerated where, for a given month, the consumption of the following year is lower than 110% of the previous year
        dysfunctional_years = []  # list of tuples containing the years where problems have been detected

        # GET DATA
        # all_years_conso is a list of watt consumption by month for each year (list of list)
        all_years_conso = [self.set_monthly_conso_watt(year.value) for year in Years]

        # we iterates through each year of monthly watt consumption, to compare it with the monthly consumption of the following year
        # and also through each available year (hardcoded in Years) to be able to know when was the dysfunction
        for i, (year_conso, year)in enumerate(zip(all_years_conso, Years.__iter__())):

            # as we can't compare the last year we have with the following one (doesn't exist), we stop the iteration at this point
            if i == len(all_years_conso) - 1:
                break

            # higher_conso store a boolean for each month comparison, True if the consumption
            # is 10% higher that previous year, Otherwise, False
            higher_conso = []

            # we iterate through each month of the current and next year to be able to compare them
            for current_year_month_conso, next_year_month_conso in zip(all_years_conso[i], all_years_conso[i + 1]):

                # check if the next year consumption is, at least, 10% higher than
                # next year consumption for the given month
                if next_year_month_conso > current_year_month_conso*(1 + dysfunctional_watt_margin):
                    higher_conso.append(True)
                else:
                    higher_conso.append(False)

            # if in the following year, all month are or 11 months consumptions is higher than the one for the
            # same month for the year before, then there is a dysfunction and we store the concerned years
            if higher_conso.count(False) < 1 + dysfunctional_month_margin:
                dysfunctional_years.append((year.value, year.value + 1))

        return dysfunctional_years

    def set_dysfunctional_string(self):
        """
        create the string to display if their is a dysfunctional

        :return (str): the string ready to be sent to html
        """

        string = "Il y a un dysfonctionnement entre les années: "
        dysfunctional_years = self.is_dysfunctional()

        if dysfunctional_years:

            for i, years in enumerate(dysfunctional_years):

                if len(dysfunctional_years) > 1:

                    if i == 0:
                        string += f"{years[0]}/{years[1]}"
                    elif i == len(dysfunctional_years) - 1:
                        string += f" et {years[0]}/{years[1]}"
                    else:
                        string += f", {years[0]}/{years[1]}"

                else:
                    string += f"{years[0]}/{years[1]}"

            return string
        return ""






