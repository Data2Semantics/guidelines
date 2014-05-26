if (Meteor.isClient) {
  Template.hello.greeting = function () {
    return "Welcome to Guidelines.";
  };

  Template.hello.events({
    'click input': function () {
      // template data, if any, is available in 'this'
      if (typeof console !== 'undefined')
        console.log("You pressed the button");
    }
  });
  
  Template.guidelines.guidelines = function(){
      Meteor.http.get("http://localhost:5820/guidelines/query", { 'headers':  {'Accept': 'application/sparql-results+json', 'params': {'query': 'SELECT * WHERE {?s ?p ?o .}'}}}, function(error, result){
          
         var parsed = EJSON.parse(result.content);
         console.log(parsed);
         return parsed.results.bindings; 
      });
      
  }
}

if (Meteor.isServer) {
  Meteor.startup(function () {
    // code to run on server at startup
  });
}
