$( document ).ready(function() {
    $('#gl_list_row').hide();
    $('#rec_list_row').hide();
    
    $('#startButton').on('click',function(){
        $.get('/guidelines',function(data){
            $('#gl_list_row').hide();
            $('#rec_list_row').hide();
            $('#gl_list_col').html(data); 
           
            $('#gl_list_col a').on('click',function(){
                var uri = $(this).attr('uri');

                $.get('/recommendations',params={'uri': uri},function(data){
                    $('#rec_list_col').html(data);
                    
                    $("#rec_list_col span").on('mouseover',function(){
                        
                        var uri = $(this).attr('target');
                        
                        
                        $("a[uri=\""+uri+"\"]").addClass('list-group-item-warning');
                    })
                    $("#rec_list_col span").on('mouseout',function(){
                        
                        var uri = $(this).attr('target');
                        
                        
                        $("a[uri=\""+uri+"\"]").removeClass('list-group-item-warning');
                    })
                    $('#rec_list_row').show();
                })
            })
           
            $('#gl_list_row').show();
        });
    });
    
});