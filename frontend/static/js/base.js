
var socket;


function connect(symbols, on_message, functions){
    functions = functions || [];
    console.log("connect to " + symbols);

    var reconnectTimeout;
    function reconnect(){
        if(reconnectTimeout) return;
        reconnectTimeout = setTimeout(function(){
            socket = null;
            connect(symbols);
            reconnectTimeout = null;
        }, 1000);
    }
    function subscribe(){
        console.log("subscribe to " + symbols);
        socket.send(JSON.stringify({subscribe: symbols, functions: functions}));
    }
    socket = socket || new WebSocket("ws://" + location.host + "/api/changes_ws");

    if(socket.readyState == 1){
        subscribe();
    }
	socket.onopen = function() {
      console.log("Connected");
      subscribe();
    };
    socket.onmessage = function(event) {
      if(event.type == "message"){
        var msg = JSON.parse(event.data);
        on_message(msg);
      }
    };

    socket.onerror = function(error) {
      console.log("Error " + error.message);
      reconnect();
    };
    socket.onclose = function(event) {
       console.log("Connection closed event");
       reconnect();
    };

    // connection health-check
    var interval = setInterval(function(){
        if(socket.readyState > 1){
            console.log("Detected closed connection. Reconnect");
            clearInterval(interval);
            reconnect();
        }
    }, 1000);
}

function error(msg){
    $("#content").append(
        '<div class="alert alert-danger col-12" role="alert">' + msg +'</div>'
    );
}

function highlight_menu(page_name){
    $("#menu li a").each(function(e, v){
        var e = $(this);
        if (e.text().toLowerCase() === page_name){
            e.addClass("active");
        }
    })
}


// COMPANIES

function on_list_item_click(elem){
    elem.addClass("active");
    company_details(elem.text(), elem.data("name"));
}


function companies_list(){
    $.get( "/api/symbols", function( data ) {
        if (data.length == 0){
            error("Symbols list for this page is empty");
        }else{
            var list = $("#company-list");
            for(var i=0; i<data.length;i++){
                list.append(
                    '<button type="button" class="list-group-item list-group-item-action" data-name="'
                    + data[i]["name"] + '" >' + data[i]["id"] + '</button>'
                );
            }
            var active_button = list.children().first();
            on_list_item_click(active_button);

            $('#company-list button').on('click', function (e) {
              e.preventDefault()
              active_button.removeClass("active");
              active_button = $(this);
              on_list_item_click(active_button);
            });
        }

    });
}
function company_details(uid, name){
    $("#company-details").html(
        '<h4>' + name + '</h4><div id="chart"></div>'
    );
    connect(uid);
}

/// end companies

/// FUTURES
function init_futures(){
    console.log("init futures");
    const FUTURES = ["^RUT", "^IXIC", "^DJI", "^GSPC"];

    var box = $("#futures");
    for(var i=0;i<FUTURES.length;i++){
        var label = FUTURES[i];
        box.append("<div><label>" + label + '</label><div class="chart" data-symbol="' + label + '"></div></div>');
    }

    var chart_data = {};
    function on_chart_data(msg){
        var symbol = msg.symbol;
        $(".chart").each(function(){
            var e = $(this);
            if(e.data("symbol") === symbol){
                var new_data = msg.data;
                new_data.forEach(function(d) {
                    if(typeof d.time === "string"){
                        d.time = d3.isoParse(d.time);
                    }
                });
                symbol_data = chart_data[symbol];
                if(symbol_data){
                    for(var i=0; i<new_data.length;i++){
                        var e = new_data[i];
                        for(var j=symbol_data.length - 1; j >= 0; --j) {
                            var o = symbol_data[j];
                            if (o.time == e.time){
                                symbol_data[j] = e; // replace the element
                                break;
                            } else if (o.time < e.time){
                                symbol_data[j + 1] = e;
                                // can replace an existing element ?
                                break;
                            }   // o.time > e.time
                        }
                    }
                    // fix max data size, only last day data
                    if (symbol_data.length > 1440){
                        symbol_data= symbol_data.slice(test.length - limit);
                    }
                }else{
                    chart_data[symbol] = new_data;
                }
                //console.log(chart_data[symbol]);
                //chart_data[symbol] = (chart_data[symbol] || []).concat(msg.data);
                var chart = buildCandleChart(this, chart_data[symbol]);
                if(msg.peaks && msg.peaks.length == 2){
                    chart.display_peaks(msg.peaks);
                }
            }
        })
    }

    connect(FUTURES, on_chart_data, ["peaks"]);
}
/// END FUTURES

function run_route(){
    const pages = {
        all: {
            template: `
                <div class="col-2">
                  <div id="company-list"></div>
                </div>
                <div class="col-10">
                  <div id="company-details"></div>
                  <div id="chart"></div>
                </div>
            `,
            init: companies_list,
        },
        futures: {
            template: `
                <div class="col-12" id="futures">
                </div>
            `,
            init: init_futures,
        }
    }
    // parsing page name
    var pathname = window.location.pathname.split("/").filter(e => e.length > 0);
    if (pathname.length === 0){
        page_name = "futures"; // default page
    }else{
        page_name = pathname[0];
    }

    // init page
    var page = pages[page_name];
    if(page === undefined){
        error('404 page "' + page_name + '" not found');
    }else{
        highlight_menu(page_name);
        $("#content").append(page.template);
        page.init();
    }
}

$(document).ready(function() {
    run_route();
});