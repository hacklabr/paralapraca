(function (angular) {
    'use strict';

    var app = angular.module('contracts.services', ['ngRoute', 'ngResource']);

    app.factory('Contract', ['$resource', function($resource){
       return $resource('/paralapraca/api/contract/:id', {}, {
           'update' : {method : 'PUT'}
       });
    }]);


    app.factory('Contracts', ['$resource', function($resource){
        return $resource('/paralapraca/api/contract/:id',
            {'id': '@id'});
    }]);

    app.factory('Groups', function($resource){
        return $resource('/paralapraca/api/group/:id', {}, {
            update: {method: 'PUT'}
        });
    });

    app.factory('ClassData', function($resource){
        return $resource('/paralapraca/api/class/:id', {}, {
             update: {method: 'PUT'}
        });
    });


    app.factory('ContractRemoveUsers', ['$http', function($http){
        return function(contract_id, user_list) {
            return $http.post('/paralapraca/admin/contracts/remove_users', {
                contract: contract_id,
                users: user_list,
            });
        };
    }]);

})(angular);
