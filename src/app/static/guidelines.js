$( document ).ready(function() {
    $('#gl_list_row').hide();
    $('#rec_list_row').hide();
    
    $('#inferenceButton').on('click',function(){
        $.get('/getinference',function(data){
            console.log(data);
            
            if (data['status'] == 'true') {
                $('#inferenceButton').text('Success');
            } else {
                $('#inferenceButton').text('Something went wrong');
            }
            
            $('#inferenceButton').text('Status: '+ data['status']);
        });
    });
    
    $('#startButton').on('click',function(){
        $.get('/getguidelines',function(data){
            $('#gl_list_row').hide();
            $('#rec_list_row').hide();
            $('#gl_list_col').html(data); 
           
            $('#gl_list_col a').on('click',function(){
                var uri = $(this).attr('uri');
                var label = $(this).attr('label');

                $('#rec_list_col').html('Loading...');
                $('#rec_list_row').show();
                
                $.get('/getrecommendations',data={'uri': uri, 'label': label},function(data){
                    $('#rec_list_col').html(data);
                    
                    $("#rec_list_col span").on('mouseover',function(){
                        var uri = $(this).attr('target');

                        $("a[uri=\""+uri+"\"]").addClass('list-group-item-warning');
                    });

                    $("#rec_list_col span").on('mouseout',function(){
                        var uri = $(this).attr('target');
                        
                        $("a[uri=\""+uri+"\"]").removeClass('list-group-item-warning');
                    });
                    
                    $("#rec_list_col a").on('click', function(){
                        var uri = $(this).attr('uri');
                        $.each(".transition").hide();
                        $.get('/gettransitions', data={'uri': uri}, function(data){
                            console.log(this);
                            $("div[transitions_for=\""+ uri +"\"]").show();
                            $("div[transitions_for=\""+ uri +"\"]").html(data);
                        })
                    })
                    
                })
            })
           
            $('#gl_list_row').show();
        });
    });
    
});