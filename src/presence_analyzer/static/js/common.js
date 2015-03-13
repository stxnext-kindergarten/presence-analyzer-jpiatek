if (typeof PRESENCE == "undefined") {
    PRESENCE = new Object();
    PRESENCE.CUSTOM = new Object();
}

PRESENCE.CUSTOM.load_users = function () {
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

PRESENCE.CUSTOM.select_user  = function () {
    var loading = $('#loading');
    var selected_user = $("#user_id").val();
    var chart_div = $('#chart_div');
    if(selected_user) {
        loading.show();
        chart_div.hide();
        return selected_user;
    }
}
    
PRESENCE.CUSTOM.get_url_photo = function(user_id) {
    return $.getJSON('/api/v1/get_url_photo/'+user_id);
}

