(function(angular){
    'use strict';
    var app = angular.module('contracts.controllers', []);

    app.controller('ContractsCtrl', ['$scope', 'Contract',
        function ($scope, Contracts) {
            $scope.contracts = Contracts.query({'simple' : true});
        }
    ]);

    app.controller('ContractDetailsCtrl', ['$scope', '$routeParams', 'Contract',
        function ($scope, $routeParams, Contracts) {
            $scope.contract_id = $routeParams.contractId;
            $scope.contract = Contracts.get({id: $scope.contract_id});
        }
    ]);

    app.controller('NewContractCtrl', ['$scope', 'ClassData', 'Contract', 'Groups',
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

    app.controller('EditContractCtrl', ['$scope', '$routeParams', 'ClassData', 'Contract', 'Groups',
        function ($scope, $routeParams, Classes, Contracts, Groups) {
            $scope.classes = Classes.query();
            $scope.groups = Groups.query();

            $scope.editing_mode = true;
            $scope.contract_id = $routeParams.contractId;
            Contracts.get({id: $scope.contract_id}, function(data){
                $scope.contract = data;
            });

            $scope.save_contract = function(){
                if (typeof $scope.contract.unities === 'string') {
                    $scope.contract.unities = $scope.contract.unities.split(',');
                }
                $scope.contract.$update({id : $scope.contract_id}, function(data){
                    // TODO Data handling
                }, function(error){
                    // TODO Error handling
                });
            }

        }
    ]);


})(window.angular);
