$(function () {
    // Connect to the Socket.IO server. For now we run without namespace, as this is the only connection in the app.
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    var first_form_response = true;

    socket.on('server_form_response', function (msg) {
        if (first_form_response) {
            $('#form_section').addClass('stream');
            $('#form_section').empty();
            first_form_response = false;
        }
        message_lines = msg.content.split(/\n/g);
        $.each(message_lines, function(index, value) {
            // If we get more than one line in a log output, subsequent lines will be indented.
            if (index < 1) {
                if (value.indexOf("ERROR") >= 0) {
                   // We have an error, so stop the cursor from spinning to indicate halted process.
                    $('#form_section').append(value + '<br>');
                    $('#form_section').append(
                        '<h4><a onclick="location.reload();">Return to form</a></h4>');
                    $("body").css("cursor", "default");
                } else {
                    $('#form_section').append(value + '<br>');
                }
            } else if (index >= 1) {
                $('#form_section').append('<span class="console-indent">' + value + '</span><br>');
            }
            $('#form_section').scrollTop($('#form_section')[0].scrollHeight);
        });
    });

    socket.on('server_error', function (msg) {
        $('#log').append($('<div/>').text('ERROR: ' + msg.content).html());
    });

    // Emit the content of the form for processing.
    $('form#transcription_form').submit(function (event) {
        socket.emit('submit_form', {
            xml_upload_or_remote: $('input[type=radio][name=xml_upload_remote]:checked').val(),
            xml_file: $('#xml_upload_list').find('#filename').text(),
            scta_id: $('#scta_id').val(),
            xslt_default_or_remote: $('input[type=radio][name=xslt_upload_default]:checked').val(),
            xslt_file: $('#xslt_upload_list').find('p').text(),
            tex_or_pdf: $('input[type=radio][name=pdf_tex]:checked').val()
        });
        var target = document.getElementById('form_section');
        var spinner = new Spinner().spin(target);
        return false;
    });

    socket.on('redirect', function (data) {
        window.location = data.url;
    });

    $('#xml_upload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                var result =  $(
                    '<p class="text-success"> ✓ Uploaded: ' +
                    '<span id="filename">' + file.name + '</span></p>'
                );
                result.appendTo('#xml_upload_list');
            });
        }
    });

    $('#xslt_upload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                var result =  $(
                    '<p class="text-success"> ✓ Uploaded: ' +
                    '<span id="filename">' + file.name + '</span></p>'
                );
                result.appendTo('#xslt_upload_list');
            });
        }
    });
});