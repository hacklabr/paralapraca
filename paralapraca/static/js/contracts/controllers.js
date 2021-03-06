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
                    window.alert(error.status + ' ' + error.data.error);
                });
            }
        }
    ]);

    app.controller('EditContractCtrl', ['$scope', '$location', '$routeParams', '$uibModal', 'FormUpload', 'ClassData', 'Contract', 'Groups', 'ContractRemoveUsers',
        function ($scope, $location, $routeParams, $uibModal, FormUpload, Classes, Contracts, Groups, ContractRemoveUsers) {
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
                    window.alert(error.status + ' ' + error.data.error);
                });
            }

            $scope.remove_users = function(contract) {
                var modalInstance = $uibModal.open({
                    templateUrl: 'removeUsersModal.html',
                    controller: ['$scope', '$uibModalInstance', 'contract',
                        function($scope, $uibModalInstance, contract) {
                            $scope.contract = contract;
                            $scope.data = {};

                            $scope.cancel = function() {
                                $uibModalInstance.dismiss();
                            };

                            $scope.bulk_remove = function() {
                                if($scope.data.bulk_remove_list){
                                    console.log(ContractRemoveUsers($scope.contract.id, $scope.data.bulk_remove_list));
                                } else {
                                    window.alert("É necessário adicionar pelo menos um e-mail válido")
                                }
                                $scope.data['bulk_remove_list'] = undefined;
                                $uibModalInstance.close();
                            };
                        }
                    ],
                    resolve: {
                        contract: function() {
                            return $scope.contract;
                        }
                    }
                });
            };

            $scope.uploadCSVData = function(){
                if (!$scope.c.hasOwnProperty('csv_data_file')) {
                    return window.alert('Arquivo não selecionado');
                }
                var fu = new FormUpload();
                fu.addField("file", $scope.c['csv_data_file']);
                fu.addField("contract_id", $scope.contract_id);

                var request = fu.sendTo('/paralapraca/admin/contracts/upload_data');
                request.then(function(res) {
                    var modalInstance = $uibModal.open({
                        templateUrl: 'statsModal.html',
                        controller: ['$scope', '$uibModalInstance', 'data',
                            function($scope, $uibModalInstance, data) {
                                $scope.errors = undefined;
                                $scope.stats = data.stats;
                                $scope.cancel = function () {
                                    $uibModalInstance.dismiss();
                                };
                            }
                        ],
                        resolve: {
                            data: function() {
                                return res.data;
                            }
                        }
                    });

                    $scope.contract = new Contracts(res.data.instance);
                    upload_complete();
                }, function(res) {
                    var modalInstance = $uibModal.open({
                        templateUrl: 'statsModal.html',
                        controller: ['$scope', '$uibModalInstance', 'data',
                            function($scope, $uibModalInstance, data) {
                                $scope.errors = data.errors;
                                $scope.stats = data.stats;
                                $scope.cancel = function () {
                                    $uibModalInstance.dismiss();
                                };
                            }
                        ],
                        resolve: {
                            data: function() {
                                return res.data;
                            }
                        }
                    });
                    upload_complete();
                });
                var upload_complete = function(){
                    $scope.c = {};
                    angular.element("#csv_file").val(null);
                }
        }
        }
    ]);


})(window.angular);
