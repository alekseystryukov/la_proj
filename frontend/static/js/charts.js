function unpack(rows, key) {
  return rows.map(function(row) {
    return row[key];
  });
}

var monthNames = [
    "Jan", "Feb", "Mar",
    "Apr", "May", "Jun", "Jul",
    "Aug", "Sep", "Oct",
    "Nov", "Dec"
];


function buildCandleChart(selector, data){
    var width = 800;
    var height = 500;
    var margin = 50;
    var chart = d3.select(selector).html("").append("svg:svg");
    chart.attr("class", "chart")
        .attr("width", width)
        .attr("height", height);

    function min(a, b){ return a < b ? a : b ; }
    function max(a, b){ return a > b ? a : b; }
    function color_func(d){ return d.buy_high ? "#009900" : "#ff9900" ;}
    var formatTime = d3.timeFormat('%H:%M');

    var y = d3.scaleLinear().domain([
        d3.min(data.map(function(x){ return x["low"]; })),
        d3.max(data.map(function(x){ return x["high"]; }))
    ])
    .range([ height-margin, margin ]);


    var x = d3.scaleLinear().domain([
        d3.min(data.map(function(d){return d.time;})),
        d3.max(data.map(function(d){return d.time;}))
    ])
    .range([margin, width-margin * 2]);

    chart.selectAll("line.x")
        .data(x.ticks(10))
        .enter().append("svg:line")
        .attr("class", "x")
        .attr("x1", x)
        .attr("x2", x)
        .attr("y1", margin)
        .attr("y2", height - margin)
        .attr("stroke", "#ccc");

    chart.selectAll("line.y")
        .data(y.ticks(10))
        .enter().append("svg:line")
        .attr("class", "y")
        .attr("x1", margin)
        .attr("x2", width - margin)
        .attr("y1", y)
        .attr("y2", y)
        .attr("stroke", "#ccc");

    chart.selectAll("text.xrule")
        .data(x.ticks(10))
        .enter().append("svg:text")
        .attr("class", "xrule")
        .attr("x", x)
        .attr("y", height - margin)
        .attr("dy", 20)
        .attr("text-anchor", "middle")
        .text(function(d){ return formatTime(d) });

    chart.selectAll("text.yrule")
        .data(y.ticks(10))
        .enter().append("svg:text")
        .attr("class", "yrule")
        .attr("x", width - margin)
        .attr("y", y)
        .attr("dy", 0)
        .attr("dx", 20)
        .attr("text-anchor", "middle")
        .text(String);

    chart.selectAll("rect")
        .data(data).enter().append("svg:rect")
        .attr("x", function(d) { return x(d.time); })
        .attr("y", function(d) {return y(max(d.open, d.close));})
        .attr("height", function(d) { return y(min(d.open, d.close))-y(max(d.open, d.close));})
        .attr("width", function(d) { return 0.5 * (width - 2*margin)/data.length; })
        .attr("fill", color_func)
        .attr("fill",function(d) { return d.open > d.close ? "red" : "green" ;});

    // strokes
    chart.selectAll("line.stem")
        .data(data)
        .enter().append("svg:line")
        .attr("class", "stem")
        .attr("x1", function(d) { return x(d.time) + 0.25 * (width - 2 * margin) / data.length;})
        .attr("x2", function(d) { return x(d.time) + 0.25 * (width - 2 * margin) / data.length;})
        .attr("y1", function(d) { return y(d.high);})
        .attr("y2", function(d) { return y(d.low); })
        .attr("stroke", color_func)
        .attr("stroke", function(d){ return d.open > d.close ? "red" : "green"; });


    var chart_obj = {
        display_peaks: function(data){
            var p1 = [x(d3.isoParse(data[0].time)), y(data[0].close)];
            var p2 = [x(d3.isoParse(data[1].time)), y(data[1].close)];

            if(isNaN(p1[0]) || isNaN(p1[1])) return;

            var is_up = p1[1] > p2[1];
            if (is_up){
                var p3 = [p2[0], p1[1]];
            }else{
                p3 = [p1[0], p2[1]];
            }
            chart.append("polygon")
                 .attr("points", [p1, p2, p3].map(p => p.join(",")).join(" "))
                 .style("fill", is_up ? "green" : "red")
                 .style("fill-opacity", 0.5);
        }
    };
    return chart_obj;
}

