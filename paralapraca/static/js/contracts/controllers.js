(function(angular){
    'use strict';
    var app = angular.module('contracts.controllers', []);

    app.controller('ContractsCtrl', ['$scope', 'Contracts',
        function ($scope, Contracts) {
            $scope.contracts = Contracts.query();
        }
    ]);

    app.controller('ContractDetailsCtrl', ['$scope', '$routeParams', 'Contracts',
        function ($scope, $routeParams, Contracts) {
            $scope.contract_id = $routeParams.contractId;
            $scope.contract = Contracts.get({id: $scope.contract_id});
        }
    ]);

    app.controller('NewContractCtrl', ['$scope', 'Class', 'Contracts', 'Groups',
        function ($scope, Classes, Contracts, Groups) {
            $scope.classes = Classes.query();
            $scope.groups = Groups.query();

            $scope.editing_mode = false;
            $scope.contract = {
                description: '',
                name: ''
            };
        }
    ]);

    app.controller('EditContractCtrl', ['$scope', '$routeParams', 'Class', 'Contracts', 'Groups',
        function ($scope, $routeParams, Classes, Contracts, Groups) {
            $scope.classes = Classes.query();
            $scope.groups = Groups.query();

            $scope.editing_mode = true;
            $scope.contract_id = $routeParams.contractId;
            $scope.contract = Contracts.get({id: $scope.contract_id});
        }
    ]);


})(window.angular);
