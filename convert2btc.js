$(document).ready(function() {
    var api_url = "http://localhost:8000";
    var ss = [];
    $('[class^="convert-"]').each(function() {
        this.orig_price = parseFloat($(this).text());
        this.orig_cur = $(this).attr('class').split('-')[1].toUpperCase();
        ss.push(this);
    });

    var update = function() {
        var ex_rates = {};
        var update_next_price = function(si) {
            if (si >= ss.length) return;
            var s = ss[si];
            var update_price = function () {
                s.btc_price = s.orig_price / ex_rates[s.orig_cur];
                $(s).html(s.orig_price + " (~" + s.btc_price.toPrecision(4) + " BTC)");
                update_next_price(1 + si);
            }
            if (s.orig_cur in ex_rates) {
                update_price();
            } else {
                $.getJSON(api_url + '/' + s.orig_cur + '/?callback=?', function(data) {
                    ex_rates[s.orig_cur] = data.btc_price;
                    update_price();
                });
            }
        }
        update_next_price(0);
    };
    update();
    setInterval(update, 300000);
});
