(function(angular){
    'use strict';

    var app = angular.module('ui.tinymce');

    // If you want to cutomize uiTinymceConfig for your theme, please copy this file to you theme in the
    // same path (static/js/). This are the default setting for timtec
    app.value('uiTinymceConfig', {
        base_url: '/static/tinymce-dist/',
        related_url: true,
        inline: false,
        menubar: false,
        relative_urls: false,
        remove_script_host: false,
        plugins : 'advlist lists autoresize',
        toolbar: 'bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat',
        skin: 'lightgray',
        theme : 'modern',
        language: 'pt_BR',
        language_url : '/static/vendor/tinymce/langs/pt_BR.js',
        resize: true,
        elementpath: false,

        format: {
          removeformat: [
            {selector: 'font', remove : 'all', split : true, expand : false, block_expand: true, deep : true},
            {selector: 'span', attributes : ['style', 'class'], remove : 'all', split : true, expand : false, deep : true},
            {selector: '*', attributes : ['style', 'class'], split : false, expand : false, deep : true}
          ]
        },
    });

})(window.angular);
