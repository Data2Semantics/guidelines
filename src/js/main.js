SPARQL = "http://localhost:5820/guidelines/query"
PREFIXES = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"+
"PREFIX gl: <http://guidelines.data2semantics.org/vocab/>\n";
console.log(SPARQL);

$(function() {
    
    
    console.log( "ready!" );

    var q = PREFIXES + 'SELECT ?s ?l WHERE { ?s a gl:Transition . OPTIONAL {?s rdfs:label ?l .}}';
    
    query(SPARQL,q,function(results){
        $.each(results,function(k,v){
            var row = $('<div>');
            row.addClass('row');
            
            $.each(v, function(vk, vv){
                var col = $('<div>');
                col.addClass('col-md-2');
                col.html('<p>'+vv.value.replace('http://guidelines.data2semantics.org/vocab/','')+'</p>');
                row.append(col);
            });

            $('#content').append(row);
        });
    });

    console.log('Called GET');
});

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