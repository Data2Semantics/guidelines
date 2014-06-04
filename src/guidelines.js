if (Meteor.isClient) {
    var PREFIXES = "PREFIX gl: <http://guidelines.data2semantics.org/vocab/>\n";

    Template.buttons.greeting = function() {
        return "Welcome to Guidelines.";
    };

    Template.buttons.events({
        'click #startButton': function() {
            console.log("Fetching guidelines");
            $('#startButton').attr('disabled', 'true').text('Loading...');

            var query = PREFIXES + 'SELECT DISTINCT ?gl WHERE {?gl gl:composedBy ?rec }';

            Meteor.call('querySPARQL', query, function(err, response) {
                if (err) {
                    window.alert("Error: " + err.reason);
                    console.log("error occured on receiving data on server. ", err);
                } else {
                    console.log("Response: ", response);
                    //window.alert(respJson.length + ' tweets received.');
                    Session.set("guidelines", response);
                }
                $('#startButton').removeAttr('disabled').text('Start');
            });
        },
    });

    Template.guidelines.results = function() {
        return Session.get("guidelines");
    };

    Template.guidelines.events({
        'click .guideline': function() {
            var gl = "<" + this.value.value + ">";

            console.log(gl);

            var query = PREFIXES + 'SELECT DISTINCT ?rec ?crec WHERE {' + gl + ' gl:composedBy ?rec . OPTIONAL {?rec gl:contradictsRecommendation ?crec}}';

            Meteor.call('querySPARQL', query, function(err, response) {
                if (err) {
                    window.alert("Error: " + err.reason);
                    console.log("error occured on receiving data on server. ", err);
                } else {
                    console.log("Response: ", response);
                    //window.alert(respJson.length + ' tweets received.');
                    Session.set("recommendations", response);
                }
            });
        }
    });

    Template.recommendations.results = function() {
        return Session.get("recommendations");
    };
    
    Template.recommendations.register_recommendation = function() {
        Session.set("current_recommendation", this.rec.value);
    }
    
    Template.recommendations.isunchanged = function() {
        console.log("Checking whether recommendation is unchanged");
        Session.setDefault("current_recommendation", "none")
        var current = Session.get("current_recommendation");
        console.log(current + this.rec.value);
        return (current == this.rec.value);
    }

    Template.recommendations.events({
        'click .recommendation': function() {
            console.log(this.rec.value);
        }
    });


    Handlebars.registerHelper('shortform', function() {
        console.log(this);
        return this.value.value.replace('http://guidelines.data2semantics.org/vocab/', '')
    });

    Handlebars.registerHelper('shortform_str', function(txt) {
        console.log(txt);
        return txt.replace('http://guidelines.data2semantics.org/vocab/', '')
    });

    Handlebars.registerHelper('arrayify', function(obj) {
        result = [];
        for (var key in obj) result.push({
            name: key,
            value: obj[key]
        });
        return result;
    });
}



if (Meteor.isServer) {
    var ENDPOINT = "http://localhost:5820/guidelines/query";

    Meteor.startup(function() {
        // code to run on server at startup
    });

    Meteor.methods({
        querySPARQL: function(query) {
            var result = Meteor.http.get(ENDPOINT, {
                'headers': {
                    'Accept': 'application/sparql-results+json',
                    'SD-Connection-String': 'reasoning=SL'
                },
                'params': {
                    'query': query
                }
            });

            if (result.statusCode === 200) {
                var parsed = JSON.parse(result.content);
                console.log(parsed.results.bindings);
                return parsed.results.bindings;
            } else {
                console.log("Response issue: ", result.statusCode);
                var errorJson = JSON.parse(result.content);
                throw new Meteor.Error(result.statusCode, errorJson.error);
            };
        }
    });
}
