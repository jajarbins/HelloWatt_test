$("#year_selection").on("change", function(){
  var selected_year = $(this).text();

  $.ajax({
    url : "'^results/(?P<client_id>.+)$'",
    type : "GET",
    data : {"name" : selected_year},
    dataType : "json",
    success : function(){

    }
  });
});
