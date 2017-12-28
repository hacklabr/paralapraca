(function (angular) {
    'use strict';

    var app = angular.module('contracts.services', ['ngRoute', 'ngResource']);

    app.factory('Contracts', ['$resource', function($resource){
        return $resource('/paralapraca/api/contract/:id',
            {'id': '@id'});
    }]);

    app.factory('Groups', function($resource){
        return $resource('/api/group_admin/:id', {}, {
            update: {method: 'PUT'}
        });
    });

})(angular);
