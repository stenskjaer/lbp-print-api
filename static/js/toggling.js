/**
 * Created by michael on 18/03/2017.
 */

var scta_button = document.getElementById('label-xml_upload_remote-0');
var xml_upload_button = document.getElementById('label-xml_upload_remote-1');
var xslt_remote_button = document.getElementById('label-xslt_upload_default-0');
var xslt_upload_button = document.getElementById('label-xslt_upload_default-1');

scta_button.onclick = function() {
    document.getElementById('scta_id_container').style.display = 'block';
    document.getElementById('xml_upload_container').style.display = 'none';
};

xml_upload_button.onclick = function() {
    document.getElementById('scta_id_container').style.display = 'none';
    document.getElementById('xml_upload_container').style.display = 'block';
};

xslt_remote_button.onclick = function() {
    document.getElementById('xslt_upload_container').style.display = 'none';
};

xslt_upload_button.onclick = function() {
    document.getElementById('xslt_upload_container').style.display = 'block';
};

