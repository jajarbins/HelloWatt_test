$("#year_selecter").change(function () {

    $.ajax({
        type: 'POST',
        url:'/results/${client_id}',
        data:{
            current_year:$(this).val() ,
            client_id:client_id,
        },
        dataType: "json",
        success: function (result) {

            document.getElementById("annual_costs").innerHTML = `dépenses annuelles: ${result["annual_costs"]} €`;
            make_graph(result["graph_setup"]);

        }
    })

});

$(window).on('load', function() {
    var graph_setup_escaped = graph_setup.replace(/&#39;/gi, '"');
    graph_setup_escaped = JSON.parse(graph_setup_escaped);
    make_graph(graph_setup_escaped);
});

function make_graph(current_graph_setup){

    let data = [{
      "type": "scatter",
      "x": current_graph_setup["x"],
      "y": current_graph_setup["y"]
    }];

    let layout = {
        "title": {
            "text": current_graph_setup["title-text"],
            "font_size": current_graph_setup["title-font_size"]
        },
        "yaxis": {"title": current_graph_setup["yaxis-title"]},
        "xaxis": {"title": current_graph_setup["xaxis-title"]}
    };

    return Plotly.newPlot('conso_watt_graph', data, layout, {showSendToCloud: false});
}




