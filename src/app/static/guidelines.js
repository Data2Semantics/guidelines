$( document ).ready(function() {
    $('#gl_list_row').hide();
    $('#rec_list_row').hide();
    
    $('#inferenceButton').on('click',function(){
        $.get('/inference',function(data){
            console.log(data);
            // $('#inferenceButton').text(data['status']);
        });
    });
    
    $('#startButton').on('click',function(){
        $.get('/guidelines',function(data){
            $('#gl_list_row').hide();
            $('#rec_list_row').hide();
            $('#gl_list_col').html(data); 
           
            $('#gl_list_col a').on('click',function(){
                var uri = $(this).attr('uri');

                $('#rec_list_col').html('Loading...');
                $('#rec_list_row').show();
                
                $.get('/recommendations',data={'uri': uri},function(data){
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
                        $.get('/transitions', data={'uri': uri}, function(data){
                            console.log(this);
                            $("div[transitions_for=\""+ uri +"\"]").html(data);
                        })
                    })
                    
                })
            })
           
            $('#gl_list_row').show();
        });
    });
    
});