
$("#year_selecter").change(function () {

    $.ajax({
        type: 'POST',
        url:'/results/${client_id}',
        data:{
            selected_year:$(this).val() ,
            client_id:client_id,
            },
        dataType: "json",
        success: function (result) {
            document.getElementById("annual_costs").innerHTML = `dépenses annuelles: ${result["annual_costs"]} €`;
            document.getElementById("conso_watt_graph").innerHTML = `<div> ${result['conso_watt_graph']}  </div>`;
            console.log(result["current_year"]);

        }
    })

});




