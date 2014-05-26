var SPARQL = "http://localhost:5820/guidelines/query";
var PREFIXES = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"+
"PREFIX gl: <http://guidelines.data2semantics.org/vocab/>\n";


console.log(SPARQL);

$(function() {
    
    
    console.log( "ready!" );

    var q = PREFIXES + 'SELECT ?guideline ?recommendation ?rectype WHERE { ?guideline a gl:Guideline . OPTIONAL {?guideline gl:composedBy ?recommendation . ?recommendation rdf:type ?rectype }}';

    query(SPARQL,q, function(results){
        var prevGl = "";
        var prevRec = "";
        
        console.log(results);
        $.each(results, function(k,v){
            
            console.log(v.recommendation.value);
            var short_rec = v.recommendation.value.replace('http://guidelines.data2semantics.org/vocab/','')
            
            if (v.recommendation.value != prevRec){
                var glCol, recCol;
                var row = $("<div></div>");
                row.addClass('row');
            
                if (v.guideline.value != prevGl) {
                    glCol = $("<div class='col-md-3'>"+v.guideline.value.replace('http://guidelines.data2semantics.org/vocab/','') +"</div>");
                    prevGl = v.guideline.value;
                } else {
                    glCol = $("<div class='col-md-3'></div>");
                }
                
                recCol = $("<div class='col-md-3' id='"+short_rec+"'>"+ short_rec +"</div>");
                recCol.addClass('alert alert-info');
            
                recCol.click({'recommendation': v.recommendation.value},showRecommendation);
                
                row.append(glCol);
                row.append(recCol);
                
                prevRec = v.recommendation.value;
                $('#guidelines').append(row);
            } 
            
            if (v.rectype.value == 'http://guidelines.data2semantics.org/vocab/ContradictoryRecommendation') {
                $('#'+short_rec).addClass('alert-warning');
            }
            
        })
        
    });
    
    // var q = PREFIXES + 'SELECT ?s ?l WHERE { ?s a gl:CareActionType . OPTIONAL {?s gl:incompatibleWith ?l .} }';
    // 
    // query(SPARQL,q,function(results){
    //     
    //     $.each(results,function(k,v){
    //         var row = $('<div>');
    //         row.addClass('row');
    //         
    //         
    //         
    //         $.each(v, function(vk, vv){
    //             var col = $('<div>');
    //             col.addClass('col-md-3');
    //             col.html('<p>'+vv.value.replace('http://guidelines.data2semantics.org/vocab/','')+'</p>');
    //             row.append(col);
    //         });
    // 
    //         $('#care-actions').append(row);
    //     });
    // });

    console.log('Called GET');
});

function showRecommendation(e){
    var rec = e.data.recommendation;
    var q = PREFIXES + 'SELECT ?p ?o WHERE { <'+ rec +'> ?p ?o }';
    
    query(SPARQL,q,function(results){
        console.log(results);
    })
}

function query(endpoint, q, func){
    $.ajax({
        url: endpoint,      
        headers: {          
            Accept : "application/sparql-results+json",         
            "Content-Type": "text/plain; charset=utf-8",
            "SD-Connection-String": "reasoning=SL"  
        },
        data: {'query': q},
        success: function(data){
            console.log(data);
            func(data.results.bindings);
        }  
    });
}

