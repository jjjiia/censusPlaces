$(function() {
	queue()
		.defer(d3.csv,"../data/openpaths_jjjiia_withgid.csv")
		.defer(d3.json,"../data/socialExplorer_data.json")
		.defer(d3.json,"../data/socialExplorer_dictionary.json")
		.defer(d3.json,"../data/socialExplorer_dictionary_selected.json")
		.defer(d3.json,"../data/nyc_outline.geojson")
		.await(dataDidLoad);
})

var totalTimeSpan = 0
var pointsData = null
var dictionary = null
function dataDidLoad(error,points,data,dictionary,dictionarySelected,nyc) {
    pointsData = data
    dictionary = dictionary
//map
    drawDots(points)
    drawBuildings(nyc)
//days
    startDate = parseDate(points[0].date.split(" ")[0])
    endDate = parseDate(points[points.length-1].date.split(" ")[0])
    totalTimeSpan = String(daydiff(startDate, endDate))+" days"
//charts
    drawControls()
    //console.log(Object.keys(dictionarySelected))
    //var topics = ["SE_T057_001","SE_T002_002","SE_T007_013","SE_T013_002","SE_T007_002","SE_T128_006"]
    var topics = Object.keys(dictionarySelected);
    for(var i in topics){
        var topic = topics[i]
//        drawLineGraph(points,data,topic,dictionary)
    //    var dataByDay = formatByDay(points,data,topic)
       // drawByDay(dataByDay)
        var durationData = formatWithDuration(points,data,"SE_"+topic)
        var totalDurations = calculateTotalDurations(durationData)
        
        //var range = "week"
        //var dataByRange = dataByDateRange(durationData,range)
        drawDuration(durationData,"SE_"+topic,dictionary,totalDurations)
    }
    
    d3.select("#chronological")
        .on("click",function(){
            console.log("chronological")
            d3.selectAll("#line1 svg").remove()
            chrono = true
            for(var i in topics){
                var topic = topics[i]
                var durationData = formatWithDuration(points,data,"SE_"+topic)
                drawDuration(durationData,"SE_"+topic,dictionary,totalDurations)
            }
        })
    d3.select("#value")
        .on("click",function(){
            chrono = false
            d3.selectAll("#line1 svg").remove()
            for(var i in topics){
                var topic = topics[i]
                var durationData = formatWithDuration(points,data,"SE_"+topic)
                var sortedData = sortedByValue(durationData)
                drawDuration(sortedData,"SE_"+topic,dictionary,totalDurations)
            }
        })
}
function dataByDateRange(data,range){
    var lastEntry = data[data.length-1].minutesTotal
    var translateRange = {
        "week":60*24*7,
        "day":60*24,
        "month":60*24*30
    }
    var startMinute = lastEntry-translateRange[range]
    var filteredData = []
    for(var d in data){
        var entry = data[d]
        var minutesTotal = entry.minutesTotal
        if(minutesTotal>startMinute){
            filteredData.push(data[d])
        }
    }
    return filteredData
}
function drawControls(){
    d3.select("#sort").append("div").attr("id","chronological").html("chronological")
    d3.select("#sort").append("div").attr("id","value").html("value")
   // d3.select("#sort").append("div").attr("id","duration").html("duration")
}

function drawBuildings(geoData){
    //need to generalize projection into global var later
	var projection = d3.geo.mercator().scale(60000).center([-73.68,40.65])
    //d3 geo path uses projections, it is similar to regular paths in line graphs
	var path = d3.geo.path().projection(projection);
    
    var svg=d3.select("#map svg")
    //push data, add path
	svg.selectAll(".buildings")
		.data(geoData.features)
        .enter()
        .append("path")
		.attr("class","buildings")
		.attr("d",path)
		.style("fill","none")
		.style("stroke","#000")
		.style("stroke-width",.5)
	    .style("opacity",1)
}
function drawDots(data){
    var svg = d3.select("#map").append("svg").attr("width",300).attr("height",300)
	var projection = d3.geo.mercator().scale(60000).center([-73.68,40.65])
    var startDate = data[0]["date"]
    var endDate = data[data.length-1]["date"]
    d3.select("#dateRange").html(startDate+ " - "+endDate)
   // console.log(data)
    svg.selectAll(".dots")
        .data(data)
        .enter()
        .append("circle")
        .attr("class","dots")
        .attr("r",3)
        .attr("cx",function(d){
            var lat = parseFloat(d.lat)
            var lng = parseFloat(d.lng)
            //to get projected dot position, use this basic formula
            var projectedLng = projection([lng,lat])[0]
            return projectedLng
        })
        .attr("cy",function(d){
            var lat = parseFloat(d.lat)
            var lng = parseFloat(d.lng)
            var projectedLat = projection([lng,lat])[1]
            return projectedLat
        })
        .attr("class",function(d){
            return "_"+d.bgid
        })
	    .style("opacity",0)
        //on mouseover prints dot data
        .on("mouseover",function(d){            
            d3.selectAll("._"+d.bgid).attr("fill","red")
        })
        .on("mouseout",function(){
            d3.selectAll("circle").attr("fill","black")
            d3.selectAll("rect").attr("fill","black")
        })
        .transition()
        .delay(function(d,i){
            return i*20
        })   
	    .style("opacity",.5)
        
}
function drawLine(data){
    var svg = d3.select("#map").append("svg").attr("width",400).attr("height",400)
	var projection = d3.geo.mercator().scale(90000).center([-73.8,40.7])
    var startDate = data[0]["date"]
    var endDate = data[data.length-1]["date"]
    svg.append("text").text(startDate+ " to "+endDate).attr("x",20).attr("y",20)
   // console.log(data)
    

    var path = d3.geo.path()
        .projection(projection);
    
    
  var city = g.selectAll(".city")
      .data(data)
      .enter().append("g")
        .attr("class", "city");

    city.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d); })
    
        
}

function parseDate(str) {
    var mdy = str.split('-');
    return new Date(mdy[0], mdy[1], mdy[2]);
}

function daydiff(first, second) {
    return Math.round((second-first)/(1000*60*60*24));
}
function formatWithDuration(points,data,topic){
    var pointsDuration = []
    var startDate = points[0].date.split(" ")[0]
    for(var d in points){
        var bgid = points[d].bgid
        var timestamp = points[d].date
        var date = timestamp.split(" ")[0]
        var dayNumber = Math.round((parseDate(date)-parseDate(startDate))/(1000*60*60*24))
        var time = timestamp.split(" ")[1]
        var hour = parseInt(time.split(":")[0])
        var minute = parseInt(time.split(":")[1])
        var minutesTotal = hour*60+minute+dayNumber*24*60
        
        if(topic.split("_")[2]=="001"){
            var value = parseFloat(data[bgid][topic])
        }else{
            var totalCode =topic.split("_")[0]+"_"+topic.split("_")[1]+"_001"
            var total = parseFloat(data[bgid][totalCode])
            var value = parseFloat(data[bgid][topic])/total*100
        }
        if(isNaN(value)==true){
            value = 0
        }
        
        if(d<points.length-1){
            //console.log(d)
            //console.log(points[1])
            var nextTimestamp = points[parseInt(d)+1].date
            var nextDate = nextTimestamp.split(" ")[0]
            var nextDayNumber = Math.round((parseDate(nextDate)-parseDate(startDate))/(1000*60*60*24))
            var nextTime = nextTimestamp.split(" ")[1]
            var nextHour = parseInt(nextTime.split(":")[0])
            var nextMinute = parseInt(nextTime.split(":")[1])
            var nextMinutesTotal = nextHour*60+nextMinute+nextDayNumber*24*60
            var duration = nextMinutesTotal-minutesTotal
        }
        
        //console.log([bgid,date,hour,minute,minutesTotal,value])
       // pointsByDate[bgid]={}
       
       pointsDuration.push({"topic":topic,"minutesTotal":minutesTotal,"value":value, "duration":duration,"bgid":bgid})
        
    }
    return pointsDuration
}
function calculateTotalDurations(data){
    var durationByBgid = {}
    for(var d in data){
        var id = data[d].bgid
        var duration = data[d].duration
        if(durationByBgid[id]==undefined){
            durationByBgid[id]=duration
        }else{
            durationByBgid[id]=durationByBgid[id]+duration
        }
    }
    return durationByBgid   
}
function sortedByValue(data){
    data.sort(function(a, b) {
        return parseFloat(b.value)-parseFloat(a.value);
    });
    var newMinutesTotal = 0
    for(var d in data){
        data[d]["minutesTotal"]=newMinutesTotal
        newMinutesTotal+=data[d].duration
    }
    return data
}
function drawDuration(data,topic,dictionary,totalDurations){
    var width = 700
    var height = 80
    var wMargin = 20
    var hMargin = 20
    
    var valueArray = []
    for(var d in data){
        valueArray.push(data[d].value)
    } 
    var maxV = d3.max(valueArray)
    var minV = d3.min(valueArray)
    var extentV = d3.extent(valueArray)
    var minR = minV*height/maxV
    var y = d3.scale.linear().domain([0,maxV]).range([minR,height-hMargin-hMargin])
    var minutesSpan = data[data.length-1].minutesTotal-data[0].minutesTotal
    var x = d3.scale.linear()
            .domain([data[0].minutesTotal,data[data.length-1].minutesTotal])
            .range([0,width-wMargin])
  //  console.log([data[0].minutesTotal,data[data.length-1].minutesTotal])
//    console.log(minutesSpan)
    var xHour = d3.scale.linear()
            .domain([data[data.length-1].minutesTotal, data[0].minutesTotal])
            .range([0,width-wMargin])

    var durationS = d3.scale.linear().domain([0, minutesSpan]).range([0,width-wMargin])
 //   var line = d3.line()
 //       .curve(d3.curveBasis)
 //       .x(function(d,i) { return i; })
 //       .y(function(d) { return y(d.temperature); });
   
    var svg = d3.select("#line1").append("svg").attr("width",width).attr("height",height).attr("class",topic)
    svg.append("text").text(dictionary[topic.replace("SE_","")]).attr("x",width-wMargin).attr("y",15).attr("text-anchor","end")
    
    var xAxis = d3.svg.axis()
                  .scale(xHour)
                  .orient("bottom");
    svg.append("g")        	
        .attr("class", "axis")
        .attr("transform", "translate(0," + (height - 20) + ")")
        .call(xAxis);
          
    var tip = d3.tip()
        .attr('class', 'd3-tip')
          .offset([-20, 0])
          .html(function(d) {
            return "test"
          })
          svg.call(tip);
    var colorScale = d3.scale.linear()
            .domain([0,1*7*24*60])
          .range([.2,1])
    svg.selectAll(".points")
        .data(data)
        .enter()
        .append("rect")
        .attr("width",function(d){
            //return 5
            if( x(d.duration)>2){
                return durationS(d.duration)
            }else{
                return 1
            }
        })
        .attr("x",function(d,i){
            var id = d.bgid
            return x(d.minutesTotal)
        })
        .attr("height",function(d){
            if(isNaN(d.value) == true){
                return 0
            }else{
                return y(d.value)
            }
        })
        .attr("y",function(d){
            if(isNaN(d.value) == true){
                return 0
            }else{
                return height-hMargin-y(d.value)
            }
        })
        .attr("value",function(d){return d.value})
        .attr("class",function(d){
            return "_"+d.bgid+" "+d.topic
        })
        .on("mouseover",function(d){            
            var dollarSigned = ["T104_001","T059_001","T057_001"]
            var notSigned =["T002_002"]
            d3.selectAll("._"+d.bgid).attr("fill","#69cd54")
            var hours = Math.round(d.duration/60)
            if(totalDurations[d.bgid]>60*24){
                var totalTime = String(Math.round(totalDurations[d.bgid]/60/24*100)/100)+" days"
            }else if(totalDurations[d.bgid]>60){
                var totalTime = String(Math.round(totalDurations[d.bgid]/60*100)/100)+" hours"
            }else{
                var totalTime = String(Math.round(totalDurations[d.bgid]*100)/100)+" minutes"
            }            
            var value =d3.select(this).attr("value")
            if(dollarSigned.indexOf(d.topic.replace("SE_",""))>-1){
                var formattedValue = "$"+String(Math.round(d.value))
            }else if(notSigned.indexOf(d.topic.replace("SE_",""))>-1){
                var formattedValue = String(Math.round(d.value))
            }else{
                var formattedValue = String(Math.round(d.value))+"%"
            }
            tip.html("total of "+totalTime+" out of "+totalTimeSpan+" spent at "+formattedValue)
            tip.show()
            
            var sentence = ""
            for(var i in pointsData[d.bgid]){
                if(i.split("_")[0]=="SE"){
                    var key = dictionary[i.replace("SE_","")]
                    var value = pointsData[d.bgid][i]
                    sentence = sentence+key+": "+value+"</br>"
                }
            }
            
            d3.select("#text").html("SUMMARY:<br/>"+"total of "+totalTime+" out of "+totalTimeSpan
                    +"<br/>"+sentence)
        })
        .on("mouseout",function(){
            d3.selectAll("circle").attr("fill","black")
            d3.selectAll("rect").attr("fill","black")
            tip.hide()
        })
        .attr("opacity",0)
        .transition()
        .delay(function(d,i){
            return i*10
        })
        .attr("opacity",1)   
        //.attr("opacity",function(d){
        //    //totalDurations[d.bgid]
        //    return colorScale(totalDurations[d.bgid])
        //})        
}


function formatByDay(points,data,topic){
    var pointsByDate = {}
    for(var d in points){
        var bgid = points[d].bgid
        var timestamp = points[d].date
        var date = timestamp.split(" ")[0]
        var time = timestamp.split(" ")[1]
        var hour = parseInt(time.split(":")[0])
        var minute = parseInt(time.split(":")[1])
        var minutesTotal = hour*60+minute
        var value = parseFloat(data[bgid][topic])

        if(pointsByDate[date] == undefined){
            pointsByDate[date] = []
            if(isNaN(value)!=true){
                pointsByDate[date].push({"minutesTotal":minutesTotal,"value":value})
            }
        }else{
            if(isNaN(value)!=true){
                pointsByDate[date].push({"minutesTotal":minutesTotal,"value":value})
            }
        }
    }
    return pointsByDate
}
function drawByDay(data){
    var svg = d3.select("#dayChart").append("svg").attr("width",500).attr("height",60)
    
   // var svg = d3.select("#dayChart").append("svg").attr("width",500).attr("height",400)
    for(var d in data){
        var dayData = data[d]
        drawOneDay(d,dayData)
    }
    
}
function drawOneDay(day,data){
    var x = d3.scale.linear().domain([0,60*24]).range([0,500])
    var y = d3.scale.linear().domain([0,400000]).range([0,50])
    var line = d3.svg.line()    
        .x(function(d) { return x(d.minutesTotal);})
        .y(function(d) { return y(d.value); })
    var svg = d3.select("#dayChart svg")
    svg.append("text").text("8am").attr("x",x(10*60)).attr("y","100")
    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#000")
        .attr("opacity",5)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("stroke-width", 1)
        .attr("d", line);
}