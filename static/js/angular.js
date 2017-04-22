/**
 * Controller for reconciliation/rs app
 */
var rsApp = angular.module("rsApp", []);
rsApp.controller("rsCtrl", function($scope, $http) {
	// initialize control variables
	$scope.error = false;	// true iff there is an error to report
	$scope.result = false;	// true iff there is a result to report
	
	
	// initialize functions
	$scope.updateBits = function() {
		$scope.N = $scope.input.n * $scope.input.m;
		n_max = Math.pow(2, $scope.input.m)-1;
		$("#in-n").attr("max", n_max);
	};

	$scope.updateSymbols = function() {
		$scope.N = $scope.input.n * $scope.input.m;
		$("#in-t").attr("max", $scope.input.n);
	};

	$scope.simulate = function() {
		$http.post("/erasure/rs/simulate", angular.toJson($scope.input))
			 .then(function(response) {
				 $scope.error = false;
				 $scope.output = response.data;
				 $scope.result = true;
			 }, function(response) {
				 $scope.result = false;
				 $scope.error = true;
			 });
	};
	
	$scope.clear_seed = function() {
		$('#seed').val('');
		delete $scope.input.seed
	}
});




/**
 * Controller for reconciliation/rn app
 */
var rnApp = angular.module("rnApp", []);
rnApp.controller("rnCtrl", function($scope, $http) {
	// initialize control variables
	$scope.error = false;	// true iff there is an error to report
	$scope.optimize_error = false;
	$scope.result = false;	// true iff there is a result to report
	
	
	// initialize functions
	$scope.updateBits = function() {
		$("#in-t").attr("max", $scope.input.n);
	};

	$scope.simulate = function() {
		$http.post("/erasure/rn/simulate", angular.toJson($scope.input))
			 .then(function(response) {
				 $scope.error = false;
				 $scope.output = response.data;
				 $scope.result = true;
			 }, function(response) {
				 $scope.result = false;
				 $scope.error = true;
			 });
	};
	
	$scope.optimize = function() {
		// ask server to calculate d which produces smallest effective excess communication complexity
		$http.post("/erasure/rn/optimize", angular.toJson($scope.input))
			.then(function(response) {
				$scope.optimize_error = false;
				$scope.input.d = response.data.d;
			}, function(response) {
				$scope.optimize_error = true;
			});
	}
	
	$scope.clear_seed = function() {
		$('#seed').val('');
		delete $scope.input.seed
	}
});