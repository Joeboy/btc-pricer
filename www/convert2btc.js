$(function() {
    var api_url = "http://btcpricer.com";
    var btc_price, cur, ss = {};
    $('[class^="convert-"]').each(function() {
        this.orig_price = parseFloat($(this).text());
        cur = $(this).attr('class').split('-')[1];
        if (cur in ss) ss[cur].push(this);
        else ss[cur] = [this];
    });

    var update = function() {
        for (cur in ss) {
            $.ajax({url: api_url + '/rate/' + cur.toUpperCase() + '/?callback=?',
                    context: ss[cur],
                    dataType: 'jsonp'}).done(function(data) {
                for (var i=0;i<this.length;i++) {
                    btc_price = this[i].orig_price / data.btc_price;
                    $(this[i]).html(this[i].orig_price + " (~" + btc_price.toPrecision(4) + " BTC)");
                }
            });
        }
    }
    update();
    setInterval(update, 300000);
});
