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

    app.controller('NewContractCtrl', ['$scope', '$location', 'ClassData', 'Contract', 'Groups',
        function ($scope, $location, Classes, Contract, Groups) {
            $scope.classes = Classes.query();
            $scope.groups = Groups.query();

            $scope.editing_mode = false;
            $scope.contract = new Contract({
                description: '',
                name: ''
            });

            $scope.save_contract = function(){
                if (typeof $scope.contract.unities === 'string') {
                    $scope.contract.unities = $scope.contract.unities.split(',');
                }
                $scope.contract.$save({}, function(data){
                    $location.path('/');
                }, function(error){
                    // TODO Error handling
                });
            }
        }
    ]);

    app.controller('EditContractCtrl', ['$scope', '$location', '$routeParams', 'FormUpload', 'ClassData', 'Contract', 'Groups',
        function ($scope, $location, $routeParams, FormUpload, Classes, Contracts, Groups) {
            $scope.classes = Classes.query();
            $scope.groups = Groups.query();

            $scope.editing_mode = true;
            $scope.contract_id = $routeParams.contractId;
            Contracts.get({id: $scope.contract_id}, function(data){
                $scope.contract = data;
            });

            $scope.c = {}

            $scope.save_contract = function(){
                if (typeof $scope.contract.unities === 'string') {
                    $scope.contract.unities = $scope.contract.unities.split(',');
                }
                $scope.contract.$update({id : $scope.contract_id}, function(data){
                    $location.path('/');
                }, function(error){
                    // TODO Error handling
                });
            }

            $scope.uploadCSVData = function(){
                var fu = new FormUpload();
                fu.addField("file", $scope.c['csv_data_file']);
                fu.addField("contract_id", $scope.contract_id);

                var request = fu.sendTo('/paralapraca/admin/contracts/upload_data');
                request.then(function(data){
                    // TODO Data handling
                    $scope.contract = data.instance;
                }, function(error){
                    // TODO Error handling
                    $scope.contract = data.instance;
                })
            }
        }
    ]);


})(window.angular);
