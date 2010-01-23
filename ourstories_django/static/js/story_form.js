$(function() {
        var city_selector = $("select[name='city']");
        var city_p = city_selector.parents("p");
        var country_selector = $("select[name='country']");
        
        city_p.hide();


        function update_city() {
            var country_code = country_selector.val();

            if(country_code) {
                city_selector.load("/cities/"+country_code+"/",
                                      function() {
                                          city_p.show();
                                      });
                //alert("Country="+country_code);
            } else {
                city_p.hide();
            }
        }

        country_selector.bind("change", update_city);
        update_city();
    });