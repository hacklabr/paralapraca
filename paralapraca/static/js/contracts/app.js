(function(angular){
    'use strict';

    var app = angular.module('contracts', [
        'contracts.controllers',
        'contracts.services',
        'ngFileUpload',
        'ngRoute',
        'ngSanitize',
        'ui.bootstrap',
        'ui.select',
        'ui.tinymce',
        'core.services',
        'header',
    ]);

    app.config(['$locationProvider', '$routeProvider',
        function config($locationProvider, $routeProvider) {
            $locationProvider.hashPrefix('!');

            $routeProvider.
                when('/new', {
                    templateUrl: '/paralapraca/contract-edit.html',
                    controller: 'NewContractCtrl'
                }).
                when('/:contractId/edit', {
                    templateUrl: '/paralapraca/contract-edit.html',
                    controller: 'EditContractCtrl'
                }).
                when('/:contractId', {
                    templateUrl: '/paralapraca/contract-edit.html',
                    controller: 'EditContractCtrl'
                }).
                when('/', {
                    templateUrl: '/paralapraca/contracts-list.html',
                    controller: 'ContractsCtrl'
                }).
                otherwise('/');
        }
    ]);


})(angular);
