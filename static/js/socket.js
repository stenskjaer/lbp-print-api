$(function () {
    // Connect to the Socket.IO server. For now we run without namespace, as this is the only connection in the app.
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    var first_form_response = true;

    socket.on('server_form_response', function (msg) {
        if (first_form_response) {
            $('#form_section').addClass('stream');
            $('#form_section').empty();
            $('#form_section').append($('<div/>').text(
                'Upload: ' + msg.xml_upload_or_remote
                + '; XML File: ' + msg.xml_file
                + '; SCTA ID: ' + msg.scta_id
                + '; XSLT upload/remote: ' + msg.xslt_upload_or_remote
                + '; XSLT file: ' + msg.xslt_file
                + '; Tex of PDF: ' + msg.tex_or_pdf
            ).html());
            first_form_response = false;
        }
        message_lines = msg.content.split(/\n/g);
        $.each(message_lines, function(index, value) {
            // If we get more than one line in a log output, subsequent lines will be indented.
            if (index < 1) {
                $('#form_section').append(value + '<br>');
            } else {
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
            xml_file: $('#xml_upload_list').find('p').text(),
            scta_id: $('#scta_id').val(),
            xslt_default_or_remote: $('input[type=radio][name=xslt_upload_default]:checked').val(),
            xslt_file: $('#xslt_upload_list').find('p').text(),
            tex_or_pdf: $('input[type=radio][name=pdf_tex]:checked').val(),
        });
        return false;
    });

    socket.on('redirect', function (data) {
        window.location = data.url;
    });

    $('#xml_upload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $('<p/>').text(file.name).appendTo('#xml_upload_list');
            });
        }
    });

    $('#xslt_upload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $('<p/>').text(file.name).appendTo('#xslt_upload_list');
            });
        }
    });
});