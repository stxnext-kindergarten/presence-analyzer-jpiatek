function load_users() {
    var loading = $('#loading');
    $.getJSON("/api/v1/users", function(result) {
        var dropdown = $("#user_id");
        $.each(result, function(item) {
            dropdown.append($("<option />").val(this.user_id).text(this.name));
        });
        dropdown.show();
        loading.hide();
    });
}

function select_user() {
    var loading = $('#loading');
    var selected_user = $("#user_id").val();
    var chart_div = $('#chart_div');
    if(selected_user) {
        loading.show();
        chart_div.hide();
      return selected_user;
    }
}